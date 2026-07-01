# -*- coding: utf-8 -*-
"""
entities/snake.py

Rắn CHUYỂN ĐỘNG LIÊN TỤC 360° (giống slither.io).
Thuần logic (không import Kivy) -> có thể test headless.

- BaseSnake: xương sống là danh sách điểm; đầu đi theo góc `angle`,
  góc quay dần về `target_angle` với tốc độ tối đa TURN_RATE (mượt).
  Các đốt thân bám theo đầu theo kiểu chuỗi (khoảng cách cố định).
- PlayerSnake: target_angle do input (chuột/chạm) đặt từ bên ngoài.
- BotSnake: ghi đè update_direction() -> tự tính target_angle
  (tìm mồi gần nhất + bẻ lái né va chạm). => ĐA HÌNH.
"""

import math
import random

import config

TWO_PI = 2 * math.pi


class BaseSnake:
    def __init__(self, x, y, angle=0.0, length=None, skin_id="main",
                 head_color=(1, 1, 1, 1), body_color=(0.7, 0.7, 0.7, 1),
                 name="snake"):
        self.angle = float(angle)
        self.target_angle = float(angle)
        self.skin_id = skin_id
        self.head_color = head_color     # màu dự phòng nếu thiếu ảnh
        self.body_color = body_color
        self.name = name

        self.alive = True
        self.score = 0
        self.boosting = False
        self.length = float(length if length is not None else config.START_LENGTH)

        # Xương sống: điểm 0 là ĐẦU, kéo dài về phía sau theo hướng -angle.
        n = max(config.MIN_LENGTH, int(self.length))
        self.points = [(x - math.cos(angle) * config.SEG_SPACING * i,
                        y - math.sin(angle) * config.SEG_SPACING * i)
                       for i in range(n)]

    # ---------------- Thuộc tính ----------------
    @property
    def head(self):
        return self.points[0]

    @property
    def radius(self):
        return config.snake_radius(self.length)

    def set_target_angle(self, a):
        self.target_angle = a

    # ---------------- Đa hình: lớp con ghi đè ----------------
    def update_direction(self, world):
        """Lớp cơ sở: giữ nguyên hướng. PlayerSnake/BotSnake ghi đè."""
        pass

    # ---------------- Vật lý ----------------
    def _turn_toward(self, dt):
        # chênh lệch góc gói về [-pi, pi]
        da = (self.target_angle - self.angle + math.pi) % TWO_PI - math.pi
        max_turn = config.TURN_RATE * dt
        if da > max_turn:
            da = max_turn
        elif da < -max_turn:
            da = -max_turn
        self.angle = (self.angle + da) % TWO_PI

    def move(self, dt):
        if not self.alive:
            return
        self._turn_toward(dt)

        # Tăng tốc: nhanh hơn nhưng trừ dần độ dài
        boosting = self.boosting and self.length > config.BOOST_MIN_LENGTH
        speed = config.BOOST_SPEED if boosting else config.BASE_SPEED
        if boosting:
            self.length -= config.BOOST_DRAIN * dt
        else:
            self.boosting = False

        hx, hy = self.points[0]
        hx += math.cos(self.angle) * speed * dt
        hy += math.sin(self.angle) * speed * dt
        self.points[0] = (hx, hy)

        # Thân bám theo đầu (chuỗi cứng: mỗi đốt cách đốt trước SEG_SPACING)
        sp = config.SEG_SPACING
        pts = self.points
        for i in range(1, len(pts)):
            px, py = pts[i - 1]
            cx, cy = pts[i]
            dx, dy = px - cx, py - cy
            d = math.hypot(dx, dy) or 1e-6
            pts[i] = (px - dx / d * sp, py - dy / d * sp)

        self._fit_length()

    def _fit_length(self):
        target = max(config.MIN_LENGTH, int(self.length))
        pts = self.points
        while len(pts) < target:
            if len(pts) >= 2:
                ax, ay = pts[-1]
                bx, by = pts[-2]
                dx, dy = ax - bx, ay - by
                d = math.hypot(dx, dy) or 1e-6
                pts.append((ax + dx / d * config.SEG_SPACING,
                            ay + dy / d * config.SEG_SPACING))
            else:
                pts.append(pts[-1])
        while len(pts) > target and len(pts) > config.MIN_LENGTH:
            pts.pop()

    def grow(self, amount):
        self.length += amount

    def die(self):
        self.alive = False


class PlayerSnake(BaseSnake):
    """Người chơi: hướng đi bám theo con trỏ/ngón tay (đặt target_angle từ input)."""

    def update_direction(self, world):
        # target_angle đã được lớp giao diện cập nhật theo con trỏ.
        pass


class BotSnake(BaseSnake):
    """Bot: tự tìm mồi gần nhất và bẻ lái né va chạm (đa hình)."""

    # Các góc lệch để thử né (radian)
    _AVOID_OFFSETS = [0.0, 0.35, -0.35, 0.7, -0.7, 1.1, -1.1, 1.6, -1.6]

    def update_direction(self, world):
        hx, hy = self.head
        # 1) Hướng mong muốn: về phía mồi gần nhất
        food = world.nearest_food(hx, hy)
        if food is not None:
            desired = math.atan2(food.y - hy, food.x - hx)
        else:
            desired = self.angle

        # 2) Né: nhìn trước một đoạn, chọn góc thoáng gần hướng mong muốn nhất
        look = self.radius * 3.0 + 34.0
        best = desired
        for off in self._AVOID_OFFSETS:
            a = desired + off
            tx = hx + math.cos(a) * look
            ty = hy + math.sin(a) * look
            if not world.point_blocked(tx, ty, self):
                best = a
                break
        self.target_angle = best

        # 3) Thỉnh thoảng tăng tốc nếu đủ dài (để rượt/né)
        self.boosting = (self.length > 45 and random.random() < 0.015)
