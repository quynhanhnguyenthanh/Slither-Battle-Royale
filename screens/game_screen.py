# -*- coding: utf-8 -*-
"""
screens/game_screen.py

Trái tim của game.
- GameWidget: trạng thái thế giới (rắn, mồi), vòng lặp, va chạm, camera
  cuộn theo người chơi, và VẼ MỌI THỨ BẰNG SPRITE (assets/images).
- GameScreen: bọc GameWidget + lớp vignette + HUD (điểm, coin, số bot, tạm dừng).

Thể hiện: TƯƠNG TÁC ĐỐI TƯỢNG, thuật toán va chạm, QUẢN LÝ TRẠNG THÁI.
"""

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
from entities import PlayerSnake, BotSnake, Food, Loot, UP, DOWN, LEFT, RIGHT

# Góc quay đầu rắn theo hướng (sprite mặc định hướng LÊN)
_HEAD_ANGLE = {UP: 0, LEFT: 90, DOWN: 180, RIGHT: 270}


class GameWidget(Widget):
    """Vùng chơi: mô phỏng và vẽ thế giới lưới bằng sprite."""

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

        self.running = False
        self.paused = False
        self._acc = 0.0
        self.elapsed = 0.0
        self.bots_killed = 0
        self.coins_earned = 0
        self._start_bots = 0

    # ---------------- Khởi tạo màn chơi ----------------
    def reset(self, data, audio):
        self.data = data
        self.audio = audio
        self.snakes = []
        self.foods = []
        self._acc = 0.0
        self.elapsed = 0.0
        self.bots_killed = 0
        self.coins_earned = 0
        self.paused = False

        # Người chơi ở giữa bản đồ, dùng skin đang chọn.
        skin = config.get_skin(self.data.get_current_skin())
        self.player = PlayerSnake(
            config.WORLD_W // 2, config.WORLD_H // 2,
            direction=RIGHT, length=config.START_LENGTH,
            skin_id=skin["id"],
            head_color=skin["fallback_head"], body_color=skin["fallback_body"],
            name="You",
        )
        self.snakes.append(self.player)

        # Bot: skin ngẫu nhiên trong pool.
        for i in range(config.NUM_BOTS):
            pos = self._random_free_cell(margin=3)
            if pos is None:
                break
            bskin = config.get_skin(random.choice(config.BOT_SKIN_POOL))
            bot = BotSnake(
                pos[0], pos[1],
                direction=random.choice([UP, DOWN, LEFT, RIGHT]),
                length=config.START_LENGTH,
                skin_id=bskin["id"],
                head_color=bskin["fallback_head"], body_color=bskin["fallback_body"],
                name="Bot%d" % (i + 1),
            )
            self.snakes.append(bot)

        self._start_bots = len(self.snakes) - 1
        for _ in range(config.FOOD_COUNT):
            self._spawn_food()

    def start(self):
        self.running = True
        self.paused = False
        Clock.unschedule(self.update)
        Clock.schedule_interval(self.update, 1.0 / config.FPS)
        self._bind_keys()

    def stop(self):
        self.running = False
        Clock.unschedule(self.update)
        self._unbind_keys()

    def toggle_pause(self):
        self.paused = not self.paused
        return self.paused

    # ---------------- Trợ giúp không gian ----------------
    def _all_occupied(self):
        cells = set()
        for s in self.snakes:
            cells.update(s.body)
        cells.update(f.pos for f in self.foods)
        return cells

    def _random_free_cell(self, margin=1):
        occupied = self._all_occupied()
        for _ in range(200):
            x = random.randint(margin, config.WORLD_W - 1 - margin)
            y = random.randint(margin, config.WORLD_H - 1 - margin)
            if (x, y) not in occupied:
                return (x, y)
        return None

    def _spawn_food(self):
        pos = self._random_free_cell()
        if pos:
            self.foods.append(Food(pos[0], pos[1]))

    def cell_blocked(self, cell, ignore_snake=None):
        """Dùng cho AI của bot: ô có phải tường / thân rắn không?"""
        x, y = cell
        if x < 0 or x >= config.WORLD_W or y < 0 or y >= config.WORLD_H:
            return True
        for s in self.snakes:
            if s.occupies(cell):
                return True
        return False

    # ---------------- Vòng lặp game ----------------
    def update(self, dt):
        if not self.running or self.paused:
            self.draw()
            return
        self.elapsed += dt
        self._acc += dt
        while self._acc >= config.MOVE_INTERVAL:
            self._acc -= config.MOVE_INTERVAL
            self._logic_step()
            if not self.running:
                break
        self.draw()

    def _logic_step(self):
        alive = [s for s in self.snakes if s.alive]

        for s in alive:                 # 1) chọn hướng (đa hình)
            s.update_direction(self)
        for s in alive:                 # 2) di chuyển
            s.move()

        # 3) ăn mồi
        food_map = {f.pos: f for f in self.foods}
        for s in alive:
            f = food_map.get(s.head)
            if f and f in self.foods:
                s.grow()
                s.score += f.score
                self.foods.remove(f)
                del food_map[f.pos]
                if s is self.player:
                    self.data.add_coins(f.coin)
                    self.coins_earned += f.coin
                    self.audio.play_sfx("eat")

        # 4) va chạm -> danh sách chết
        dead = self._resolve_collisions(alive)

        # 5) xử lý chết
        for s in dead:
            s.die()
            self._drop_loot(s)
            if s in self.snakes:
                self.snakes.remove(s)
            if s is not self.player:
                self.bots_killed += 1
                self.data.add_coins(config.KILL_BONUS_COIN)
                self.coins_earned += config.KILL_BONUS_COIN
                self.audio.play_sfx("kill")

        # 6) duy trì số mồi
        while len(self.foods) < config.FOOD_COUNT:
            before = len(self.foods)
            self._spawn_food()
            if len(self.foods) == before:
                break

        # 7) HUD + thắng/thua
        bots_left = sum(1 for s in self.snakes if s is not self.player)
        if self.on_hud_update:
            self.on_hud_update(self.player.score, self.data.get_coins(), bots_left)
        if not self.player.alive:
            self._finish(won=False)
        elif bots_left == 0:
            self._finish(won=True)

    def _resolve_collisions(self, snakes):
        dead = []
        for s in snakes:
            hx, hy = s.head
            if hx < 0 or hx >= config.WORLD_W or hy < 0 or hy >= config.WORLD_H:
                dead.append(s)
                continue
            hit = False
            for other in snakes:
                if other is s:
                    if s.head in s.body[1:]:
                        hit = True
                        break
                else:
                    if s.head == other.head or s.head in other.body:
                        hit = True
                        break
            if hit:
                dead.append(s)
        return dead

    def _drop_loot(self, snake):
        occupied = {f.pos for f in self.foods}
        for i, cell in enumerate(snake.body):
            if i % 2 != 0:
                continue
            x, y = cell
            if 0 <= x < config.WORLD_W and 0 <= y < config.WORLD_H and cell not in occupied:
                self.foods.append(Loot(x, y))
                occupied.add(cell)

    def _finish(self, won):
        if not self.running:
            return
        self.running = False
        Clock.unschedule(self.update)
        self._unbind_keys()
        best = self.data.update_best_score(self.player.score)
        stats = {
            "score": self.player.score,
            "coins_earned": self.coins_earned,
            "time": self.elapsed,
            "bots_killed": self.bots_killed,
            "total_bots": self._start_bots,
            "new_best": best,
            "best_score": self.data.get_best_score(),
        }
        if won:
            self.audio.play_sfx("win")
            if self.on_game_win:
                self.on_game_win(stats)
        else:
            self.audio.play_sfx("die")
            if self.on_game_over:
                self.on_game_over(stats)

    # ---------------- Vẽ (camera cuộn theo player) ----------------
    def draw(self):
        self.canvas.clear()
        if self.player is None:
            return
        cam_x, cam_y = self.player.head
        cx, cy = self.center_x, self.center_y
        cell = config.CELL

        def to_screen(gx, gy):
            return (cx + (gx - cam_x) * cell, cy + (gy - cam_y) * cell)

        circle_tex = assets.circle_texture()

        with self.canvas:
            # Nền
            Color(*config.COLOR_BG)
            Rectangle(pos=self.pos, size=self.size)

            # Lưới
            Color(*config.COLOR_GRID)
            ox = (cx - cam_x * cell) % cell
            oy = (cy - cam_y * cell) % cell
            x = self.x + ox
            while x < self.right:
                Line(points=[x, self.y, x, self.top], width=1)
                x += cell
            y = self.y + oy
            while y < self.top:
                Line(points=[self.x, y, self.right, y], width=1)
                y += cell

            # Tường (viền bản đồ)
            Color(*config.COLOR_WALL)
            lx, ly = to_screen(-0.5, -0.5)
            rx, ry = to_screen(config.WORLD_W - 0.5, config.WORLD_H - 0.5)
            Line(rectangle=(lx, ly, rx - lx, ry - ly), width=2.5)

            # Mồi (sprite circle tô màu)
            for f in self.foods:
                sx, sy = to_screen(f.x, f.y)
                if sx < self.x - cell or sx > self.right or sy < self.y - cell or sy > self.top:
                    continue
                r = cell * f.radius_ratio
                Color(*f.color)
                if circle_tex:
                    Rectangle(texture=circle_tex,
                              pos=(sx - r, sy - r), size=(2 * r, 2 * r))
                else:
                    Ellipse(pos=(sx - r, sy - r), size=(2 * r, 2 * r))

            # Rắn (bot trước, người chơi vẽ sau -> nổi trên cùng)
            ordered = [s for s in self.snakes if s is not self.player]
            if self.player:
                ordered.append(self.player)
            for s in ordered:
                self._draw_snake(s, to_screen, cell)

    def _draw_snake(self, snake, to_screen, cell):
        skin = config.get_skin(snake.skin_id)
        body_tex = assets.skin_body_texture(skin)
        head_tex = assets.skin_head_texture(skin)

        bs = cell * 1.30  # sprite hơi to hơn ô để các đốt gối lên nhau
        # Thân (vẽ từ đuôi lên để đốt gần đầu nằm trên)
        for seg in reversed(snake.body[1:]):
            sx, sy = to_screen(*seg)
            if sx < self.x - cell or sx > self.right or sy < self.y - cell or sy > self.top:
                continue
            if body_tex:
                Color(1, 1, 1, 1)
                Rectangle(texture=body_tex, pos=(sx - bs / 2, sy - bs / 2), size=(bs, bs))
            else:
                Color(*snake.body_color)
                Ellipse(pos=(sx - cell / 2, sy - cell / 2), size=(cell, cell))

        # Đầu (quay theo hướng, kèm mắt nếu skin không có mặt sẵn)
        hx, hy = to_screen(*snake.head)
        hs = cell * 1.40
        angle = _HEAD_ANGLE.get(snake.direction, 0)
        PushMatrix()
        Rotate(angle=angle, origin=(hx, hy))
        if head_tex:
            Color(1, 1, 1, 1)
            Rectangle(texture=head_tex, pos=(hx - hs / 2, hy - hs / 2), size=(hs, hs))
        else:
            Color(*snake.head_color)
            Ellipse(pos=(hx - cell / 2, hy - cell / 2), size=(cell, cell))
        if skin.get("eyes"):
            eye_l, eye_r = assets.eye_textures()
            es = cell * 0.58
            ey = hy + cell * 0.16  # về phía trước (LÊN trong hệ chưa quay)
            if eye_l and eye_r:
                Color(1, 1, 1, 1)
                Rectangle(texture=eye_l, pos=(hx - cell * 0.36, ey - es / 2), size=(es, es))
                Rectangle(texture=eye_r, pos=(hx + cell * 0.36 - es, ey - es / 2), size=(es, es))
        PopMatrix()
        Color(1, 1, 1, 1)  # reset màu

    # ---------------- Điều khiển ----------------
    def steer_towards(self, tx, ty):
        if self.player is None or not self.player.alive:
            return
        dx = tx - self.center_x
        dy = ty - self.center_y
        if abs(dx) > abs(dy):
            self.player.set_input_direction(RIGHT if dx > 0 else LEFT)
        else:
            self.player.set_input_direction(UP if dy > 0 else DOWN)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.steer_towards(*touch.pos)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            self.steer_towards(*touch.pos)
            return True
        return super().on_touch_move(touch)

    _KEYCODES = {273: UP, 274: DOWN, 275: RIGHT, 276: LEFT}  # phím mũi tên
    _KEYCHARS = {"w": UP, "s": DOWN, "a": LEFT, "d": RIGHT}

    def _bind_keys(self):
        Window.bind(on_key_down=self._on_key_down)

    def _unbind_keys(self):
        Window.unbind(on_key_down=self._on_key_down)

    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        d = self._KEYCODES.get(key)
        if d is None and codepoint:
            d = self._KEYCHARS.get(codepoint.lower())
        if self.player and d:
            self.player.set_input_direction(d)
            return True
        return False


class GameScreen(Screen):
    """Màn chơi: GameWidget + vignette + HUD."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = FloatLayout()

        self.game = GameWidget(size_hint=(1, 1))
        root.add_widget(self.game)

        # Lớp phủ vignette (làm tối viền) - không chặn chạm
        vig = assets.ui_path(config.UI["vignette"])
        if vig:
            root.add_widget(Image(source=vig, allow_stretch=True,
                                  keep_ratio=False, size_hint=(1, 1)))

        # HUD trên cùng
        top = BoxLayout(size_hint=(1, None), height=54, padding=10, spacing=10,
                        pos_hint={"top": 1})
        self.lbl_score = Label(text="Điểm: 0", font_size=20, bold=True)
        self.lbl_coins = Label(text="Coin: 0", font_size=20, bold=True)
        self.lbl_bots = Label(text="Bot: 0", font_size=20, bold=True)
        self.btn_pause = Button(text="II", size_hint=(None, 1), width=54,
                                background_normal="", background_color=(0.2, 0.4, 0.9, 1))
        self.btn_pause.bind(on_release=self._on_pause)
        for w in (self.lbl_score, self.lbl_coins, self.lbl_bots, self.btn_pause):
            top.add_widget(w)
        root.add_widget(top)

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

    # ---------------- Vòng đời ----------------
    def on_enter(self, *args):
        app = self.manager.app
        self.game.reset(app.data, app.audio)
        self.game.start()

    def on_leave(self, *args):
        self.game.stop()

    # ---------------- Sự kiện ----------------
    def _update_hud(self, score, coins, bots_left):
        self.lbl_score.text = "Điểm: %d" % score
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

