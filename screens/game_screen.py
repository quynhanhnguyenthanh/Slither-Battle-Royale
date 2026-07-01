# -*- coding: utf-8 -*-
"""
screens/game_screen.py

Gameplay LIÊN TỤC 360° (giống slither.io).
- GameWidget: mô phỏng thế giới liên tục + vẽ bằng sprite, camera bám đầu rắn
  (có thu phóng theo độ dài), điều khiển bằng con trỏ/chạm, tăng tốc + vệt sáng.
- GameScreen: GameWidget + vignette + HUD (điểm, coin, độ dài, số bot) + nút BOOST.
"""

import math
import random

from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import (Color, Rectangle, Ellipse, Line,
                           PushMatrix, PopMatrix, Rotate)
from kivy.clock import Clock
from kivy.core.window import Window

import config
from utils import assets
from entities import PlayerSnake, BotSnake, Food, Loot

TWO_PI = 2 * math.pi


class GameWidget(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = None
        self.audio = None
        self.on_game_over = None
        self.on_game_win = None
        self.on_hud_update = None

        self.player = None
        self.snakes = []
        self.foods = []
        self.arena = config.ARENA_RADIUS

        self.running = False
        self.paused = False
        self.elapsed = 0.0
        self.bots_killed = 0
        self.coins_earned = 0
        self._start_bots = 0

        # Điều khiển
        self._touch_steer = False
        self._last_mouse = None
        self._boost_sources = set()
        self._was_boosting = False

    # ---------------- Khởi tạo ----------------
    def reset(self, data, audio):
        self.data = data
        self.audio = audio
        self.snakes = []
        self.foods = []
        self.elapsed = 0.0
        self.bots_killed = 0
        self.coins_earned = 0
        self.paused = False
        self._boost_sources = set()
        self._was_boosting = False
        self._touch_steer = False
        self._last_mouse = None

        skin = config.get_skin(self.data.get_current_skin())
        self.player = PlayerSnake(
            0, 0, angle=0.0, length=config.START_LENGTH,
            skin_id=skin["id"],
            head_color=skin["fallback_head"], body_color=skin["fallback_body"],
            name="You")
        self.snakes.append(self.player)

        for i in range(config.NUM_BOTS):
            x, y = self._random_point(0.85)
            bskin = config.get_skin(random.choice(config.BOT_SKIN_POOL))
            self.snakes.append(BotSnake(
                x, y, angle=random.uniform(0, TWO_PI),
                length=random.randint(config.START_LENGTH, config.START_LENGTH + 40),
                skin_id=bskin["id"],
                head_color=bskin["fallback_head"], body_color=bskin["fallback_body"],
                name="Bot%d" % (i + 1)))

        self._start_bots = len(self.snakes) - 1
        while len(self.foods) < config.FOOD_COUNT:
            self._spawn_food()

    def start(self):
        self.running = True
        self.paused = False
        Clock.unschedule(self.update)
        Clock.schedule_interval(self.update, 1.0 / config.FPS)
        self._bind_input()

    def stop(self):
        self.running = False
        Clock.unschedule(self.update)
        self._unbind_input()

    def toggle_pause(self):
        self.paused = not self.paused
        return self.paused

    # ---------------- Sinh vị trí / mồi ----------------
    def _random_point(self, frac=0.97):
        r = math.sqrt(random.random()) * self.arena * frac
        a = random.uniform(0, TWO_PI)
        return (math.cos(a) * r, math.sin(a) * r)

    def _spawn_food(self):
        x, y = self._random_point(0.97)
        self.foods.append(Food(x, y))

    # ---------------- Trợ giúp cho AI bot ----------------
    def nearest_food(self, x, y):
        best = None
        bd = 1e18
        for f in self.foods:
            d = (f.x - x) ** 2 + (f.y - y) ** 2
            if d < bd:
                bd = d
                best = f
        return best

    def point_blocked(self, x, y, ignore=None):
        if x * x + y * y > (self.arena - 18) ** 2:
            return True
        for s in self.snakes:
            if s is ignore or not s.alive:
                continue
            thr = s.radius + 16
            t2 = thr * thr
            for (px, py) in s.points[::3]:
                if (px - x) ** 2 + (py - y) ** 2 < t2:
                    return True
        return False

    # ---------------- Vòng lặp ----------------
    def update(self, dt):
        if not self.running or self.paused:
            self.draw()
            return
        dt = min(dt, 1.0 / 30.0)
        self.elapsed += dt

        # 1) Lái theo con trỏ chuột (nếu chuột di chuyển và không đang chạm)
        mp = Window.mouse_pos
        if self._last_mouse is None:
            self._last_mouse = mp
        if (not self._touch_steer) and mp != self._last_mouse:
            self._last_mouse = mp
            self._aim_at(mp)

        # 2) Tăng tốc theo nguồn input + phát tiếng boost khi bắt đầu/kết thúc
        boosting = len(self._boost_sources) > 0
        if self.player:
            self.player.boosting = boosting
        if boosting and not self._was_boosting:
            self.audio.play_sfx("boost_on")
        elif not boosting and self._was_boosting:
            self.audio.play_sfx("boost_off")
        self._was_boosting = boosting

        # 3) AI + di chuyển
        for s in self.snakes:
            if s.alive and s is not self.player:
                s.update_direction(self)
        for s in self.snakes:
            if s.alive:
                s.move(dt)

        # 4) Ăn mồi
        self._eat()

        # 5) Va chạm -> chết
        dead = [s for s in self.snakes if s.alive and self._collides(s)]
        for s in dead:
            s.die()
            self._drop_loot(s)
            if s is not self.player:
                self.snakes.remove(s)
                self.bots_killed += 1
                self.data.add_coins(config.KILL_BONUS_COIN)
                self.coins_earned += config.KILL_BONUS_COIN
                self.audio.play_sfx("kill")

        # 6) Bù mồi
        while len(self.foods) < config.FOOD_COUNT:
            self._spawn_food()

        # 7) HUD + thắng/thua
        bots_left = sum(1 for s in self.snakes if s is not self.player)
        if self.on_hud_update:
            self.on_hud_update(self.player.score, self.data.get_coins(),
                               int(self.player.length), bots_left)
        if not self.player.alive:
            self._finish(False)
        elif bots_left == 0:
            self._finish(True)

        self.draw()

    def _eat(self):
        for s in self.snakes:
            if not s.alive:
                continue
            hx, hy = s.head
            reach = s.radius
            remaining = []
            for f in self.foods:
                if (f.x - hx) ** 2 + (f.y - hy) ** 2 <= (reach + f.radius) ** 2:
                    s.grow(f.grow)
                    s.score += f.score
                    if s is self.player:
                        self.data.add_coins(f.coin)
                        self.coins_earned += f.coin
                        self.audio.play_sfx("eat")
                else:
                    remaining.append(f)
            self.foods = remaining

    def _collides(self, snake):
        hx, hy = snake.head
        hr = snake.radius
        if hx * hx + hy * hy > (self.arena - hr) ** 2:
            return True
        for other in self.snakes:
            if other is snake or not other.alive:
                continue
            thr = hr + other.radius * 0.85
            t2 = thr * thr
            for (px, py) in other.points[::3]:
                if (hx - px) ** 2 + (hy - py) ** 2 < t2:
                    return True
        return False

    def _drop_loot(self, snake):
        for (px, py) in snake.points[::4]:
            jx = px + random.uniform(-4, 4)
            jy = py + random.uniform(-4, 4)
            self.foods.append(Loot(jx, jy))

    def _finish(self, won):
        if not self.running:
            return
        self.running = False
        Clock.unschedule(self.update)
        self._unbind_input()
        best = self.data.update_best_score(self.player.score)
        self.data.save()
        stats = {
            "score": self.player.score,
            "coins_earned": self.coins_earned,
            "time": self.elapsed,
            "bots_killed": self.bots_killed,
            "total_bots": self._start_bots,
            "new_best": best,
            "best_score": self.data.get_best_score(),
            "length": int(self.player.length),
        }
        if won:
            self.audio.play_sfx("win")
            if self.on_game_win:
                self.on_game_win(stats)
        else:
            self.audio.play_sfx("die")
            if self.on_game_over:
                self.on_game_over(stats)

    # ---------------- Vẽ ----------------
    def draw(self):
        self.canvas.clear()
        if self.player is None:
            return
        hx, hy = self.player.head
        cx, cy = self.center_x, self.center_y
        zoom = config.snake_zoom(self.player.length)

        def to_screen(wx, wy):
            return (cx + (wx - hx) * zoom, cy + (wy - hy) * zoom)

        circle_tex = assets.circle_texture()
        blur_tex = assets._texture("ui", "blur.png")

        # phạm vi thế giới nhìn thấy (để cull)
        half_w = self.width / (2 * zoom) + 60
        half_h = self.height / (2 * zoom) + 60

        def visible(wx, wy, pad=0):
            return (abs(wx - hx) <= half_w + pad and abs(wy - hy) <= half_h + pad)

        with self.canvas:
            Color(*config.COLOR_BG)
            Rectangle(pos=self.pos, size=self.size)

            # Lưới nền cuộn theo camera
            Color(*config.COLOR_GRID)
            step = config.BG_GRID * zoom
            if step >= 8:
                ox = (cx - hx * zoom) % step
                oy = (cy - hy * zoom) % step
                gx = self.x + ox
                while gx < self.right:
                    Line(points=[gx, self.y, gx, self.top], width=1)
                    gx += step
                gy = self.y + oy
                while gy < self.top:
                    Line(points=[self.x, gy, self.right, gy], width=1)
                    gy += step

            # Viền sân (hình tròn)
            Color(*config.COLOR_WALL)
            bx, by = to_screen(0, 0)
            Line(circle=(bx, by, self.arena * zoom), width=3)

            # Mồi
            for f in self.foods:
                if not visible(f.x, f.y):
                    continue
                sx, sy = to_screen(f.x, f.y)
                r = f.radius * zoom
                Color(*f.color)
                if circle_tex:
                    Rectangle(texture=circle_tex, pos=(sx - r, sy - r), size=(2 * r, 2 * r))
                else:
                    Ellipse(pos=(sx - r, sy - r), size=(2 * r, 2 * r))

            # Rắn: bot trước, player sau (nổi trên)
            ordered = [s for s in self.snakes if s is not self.player]
            ordered.append(self.player)
            for s in ordered:
                self._draw_snake(s, to_screen, zoom, visible, circle_tex, blur_tex)

            Color(1, 1, 1, 1)

    def _draw_snake(self, snake, to_screen, zoom, visible, circle_tex, blur_tex):
        skin = config.get_skin(snake.skin_id)
        body_tex = assets.skin_body_texture(skin)
        head_tex = assets.skin_head_texture(skin)
        r = snake.radius * zoom
        pts = snake.points

        # bước lấy mẫu để số vòng tròn hợp lý khi rắn to
        step = max(1, int(snake.radius * 0.9 / config.SEG_SPACING))

        # Vệt sáng khi tăng tốc (ở phần đuôi)
        if snake.boosting and blur_tex:
            gr = r * 2.6
            Color(snake.body_color[0], snake.body_color[1], snake.body_color[2], 0.5)
            for (px, py) in pts[-14::2]:
                if not visible(px, py, 40):
                    continue
                sx, sy = to_screen(px, py)
                Rectangle(texture=blur_tex, pos=(sx - gr, sy - gr), size=(2 * gr, 2 * gr))

        # Thân: từ đuôi -> đầu để đốt gần đầu nằm trên
        bs = r * 2.3
        for i in range(len(pts) - 1, 0, -step):
            px, py = pts[i]
            if not visible(px, py):
                continue
            sx, sy = to_screen(px, py)
            if body_tex:
                Color(1, 1, 1, 1)
                Rectangle(texture=body_tex, pos=(sx - bs / 2, sy - bs / 2), size=(bs, bs))
            else:
                Color(*snake.body_color)
                Ellipse(pos=(sx - r, sy - r), size=(2 * r, 2 * r))

        # Đầu (xoay theo góc) + mắt
        hx, hy = pts[0]
        sx, sy = to_screen(hx, hy)
        hs = r * 3.0
        angle_deg = math.degrees(snake.angle) - 90.0  # sprite mặc định hướng LÊN
        PushMatrix()
        Rotate(angle=angle_deg, origin=(sx, sy))
        if head_tex:
            Color(1, 1, 1, 1)
            Rectangle(texture=head_tex, pos=(sx - hs / 2, sy - hs / 2), size=(hs, hs))
        else:
            Color(*snake.head_color)
            Ellipse(pos=(sx - r, sy - r), size=(2 * r, 2 * r))
        if skin.get("eyes"):
            eye_l, eye_r = assets.eye_textures()
            es = r * 1.05
            ey = sy + r * 0.42  # về phía trước (LÊN trong hệ chưa quay)
            ox = r * 0.52
            if eye_l and eye_r:
                Color(1, 1, 1, 1)
                Rectangle(texture=eye_l, pos=(sx - ox - es / 2, ey - es / 2), size=(es, es))
                Rectangle(texture=eye_r, pos=(sx + ox - es / 2, ey - es / 2), size=(es, es))
        PopMatrix()
        Color(1, 1, 1, 1)

    # ---------------- Điều khiển ----------------
    def _aim_at(self, win_pos):
        if self.player is None or not self.player.alive:
            return
        dx = win_pos[0] - self.center_x
        dy = win_pos[1] - self.center_y
        if dx * dx + dy * dy > 4:
            self.player.set_target_angle(math.atan2(dy, dx))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_steer = True
            self._aim_at(touch.pos)
            if getattr(touch, "button", None) == "left":
                self._boost_sources.add("mouse")
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            self._aim_at(touch.pos)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self._boost_sources.discard("mouse")
        self._touch_steer = False
        return super().on_touch_up(touch)

    def set_boost(self, on, source="btn"):
        if on:
            self._boost_sources.add(source)
        else:
            self._boost_sources.discard(source)

    def _bind_input(self):
        Window.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)

    def _unbind_input(self):
        Window.unbind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)

    def _on_key_down(self, window, key, *args):
        if key == 32:  # Space
            self._boost_sources.add("space")
            return True
        return False

    def _on_key_up(self, window, key, *args):
        if key == 32:
            self._boost_sources.discard("space")
            return True
        return False

class GameScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = FloatLayout()

        self.game = GameWidget(size_hint=(1, 1))
        root.add_widget(self.game)

        # HUD trên
        top = BoxLayout(size_hint=(1, None), height=52, padding=8, spacing=8,
                        pos_hint={"top": 1})
        self.lbl_score = Label(text="Điểm: 0", font_size=18, bold=True)
        self.lbl_len = Label(text="Dài: 0", font_size=18, bold=True)
        self.lbl_coins = Label(text="Coin: 0", font_size=18, bold=True)
        self.lbl_bots = Label(text="Bot: 0", font_size=18, bold=True)
        self.btn_pause = Button(text="II", size_hint=(None, 1), width=50,
                                background_normal="", background_color=(0.2, 0.4, 0.9, 1))
        self.btn_pause.bind(on_release=self._on_pause)
        for w in (self.lbl_score, self.lbl_len, self.lbl_coins, self.lbl_bots, self.btn_pause):
            top.add_widget(w)
        root.add_widget(top)

        # Nút BOOST (giữ để tăng tốc) - tiện cho cảm ứng
        self.btn_boost = Button(text="BOOST", size_hint=(None, None), size=(96, 96),
                                pos_hint={"right": 0.97, "y": 0.03},
                                background_normal="", background_color=(0.95, 0.55, 0.2, 0.9),
                                bold=True)
        self.btn_boost.bind(on_press=lambda *a: self.game.set_boost(True),
                            on_release=lambda *a: self.game.set_boost(False))
        root.add_widget(self.btn_boost)

        # Lớp phủ tạm dừng
        self.pause_overlay = self._build_pause_overlay()
        self.pause_overlay.opacity = 0
        self.pause_overlay.disabled = True
        root.add_widget(self.pause_overlay)

        self.add_widget(root)

        self.game.on_hud_update = self._update_hud
        self.game.on_game_over = self._on_over
        self.game.on_game_win = self._on_win

    def _build_pause_overlay(self):
        box = BoxLayout(orientation="vertical", size_hint=(None, None),
                        size=(260, 240), pos_hint={"center_x": 0.5, "center_y": 0.5},
                        spacing=12, padding=16)
        box.add_widget(Label(text="TẠM DỪNG", font_size=28, bold=True))
        b_resume = Button(text="Tiếp tục", background_normal="",
                          background_color=(0.2, 0.7, 0.3, 1))
        b_resume.bind(on_release=self._on_pause)
        b_menu = Button(text="Về Menu chính", background_normal="",
                        background_color=(0.8, 0.3, 0.3, 1))
        b_menu.bind(on_release=self._go_menu)
        box.add_widget(b_resume)
        box.add_widget(b_menu)
        return box

    def on_enter(self, *args):
        app = self.manager.app
        self.game.reset(app.data, app.audio)
        self.game.start()

    def on_leave(self, *args):
        self.game.stop()

    def _update_hud(self, score, coins, length, bots_left):
        self.lbl_score.text = "Điểm: %d" % score
        self.lbl_len.text = "Dài: %d" % length
        self.lbl_coins.text = "Coin: %d" % coins
        self.lbl_bots.text = "Bot: %d" % bots_left

    def _on_pause(self, *args):
        paused = self.game.toggle_pause()
        self.pause_overlay.opacity = 1 if paused else 0
        self.pause_overlay.disabled = not paused

    def _go_menu(self, *args):
        self.game.stop()
        self.pause_overlay.opacity = 0
        self.pause_overlay.disabled = True
        self.manager.app.audio.play_sfx("navigate")
        self.manager.current = "menu"

    def _on_over(self, stats):
        self.manager.get_screen("game_over").set_stats(stats)
        self.manager.current = "game_over"

    def _on_win(self, stats):
        self.manager.get_screen("game_win").set_stats(stats)
        self.manager.current = "game_win"
