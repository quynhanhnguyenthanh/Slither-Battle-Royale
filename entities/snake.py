# -*- coding: utf-8 -*-
"""

Cây kế thừa của các loài rắn — điểm nhấn OOP của đồ án:

        BaseSnake  (lớp cha: toạ độ, tốc độ, thân, move(), die())
        /        \\
  PlayerSnake     BotSnake
 (điều khiển       (AI tự động
  bằng touch)       hướng về mồi)

- TÍNH KẾ THỪA (Inheritance): Player & Bot dùng lại toàn bộ logic của BaseSnake.
- TÍNH ĐA HÌNH (Polymorphism): mỗi lớp con GHI ĐÈ phương thức update_direction()
  để tự quyết định hướng đi theo cách riêng, nhưng GameScreen gọi chung một tên.
"""

import random

# 4 hướng đi cơ bản (dx, dy)
UP = (0, 1)
DOWN = (0, -1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]


class BaseSnake:
    """Lớp cha chứa toàn bộ hành vi chung của một con rắn trên lưới."""

    def __init__(self, x, y, direction=RIGHT, length=4,
                 skin_id="main",
                 head_color=(1, 1, 1, 1), body_color=(0.7, 0.7, 0.7, 1),
                 name="snake"):
        self.direction = direction
        self.skin_id = skin_id           # id skin để lớp vẽ tra texture
        self.head_color = head_color     # màu dự phòng nếu thiếu ảnh
        self.body_color = body_color
        self.name = name
        self.alive = True
        self.score = 0
        self._pending_growth = 0  # số đốt cần mọc thêm

        # Thân rắn: danh sách toạ độ ô, phần tử [0] là ĐẦU.
        dx, dy = direction
        self.body = [(x - dx * i, y - dy * i) for i in range(length)]

    # ---------------- Thuộc tính tiện ích ----------------
    @property
    def head(self):
        return self.body[0]

    @property
    def length(self):
        return len(self.body)

    def occupies(self, cell, ignore_head=False):
        """Kiểm tra ô 'cell' có nằm trong thân rắn không."""
        segments = self.body[1:] if ignore_head else self.body
        return cell in segments

    # ---------------- Hành vi cốt lõi ----------------
    def update_direction(self, world):
        """
        Quyết định hướng đi cho bước kế tiếp.
        Lớp cha giữ nguyên hướng; các lớp con SẼ GHI ĐÈ (đa hình).
        """
        pass

    def move(self):
        """
        Tiến 1 bước: chèn đầu mới theo hướng hiện tại.
        Nếu đang cần mọc thì giữ đuôi, ngược lại bỏ đuôi (giữ nguyên độ dài).
        """
        hx, hy = self.head
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)
        self.body.insert(0, new_head)

        if self._pending_growth > 0:
            self._pending_growth -= 1
        else:
            self.body.pop()
        return new_head

    def grow(self, amount=1):
        self._pending_growth += amount

    def die(self):
        self.alive = False

    def try_reverse(self, new_dir):
        """Không cho rắn quay đầu 180 độ (đâm vào chính cổ)."""
        if self.length > 1:
            cur_dx, cur_dy = self.direction
            if (new_dir[0] == -cur_dx and new_dir[1] == -cur_dy):
                return False
        self.direction = new_dir
        return True


class PlayerSnake(BaseSnake):
    """
    Rắn của người chơi — điều khiển bằng touch/phím.
    GHI ĐÈ update_direction(): áp dụng hướng mà người chơi vừa yêu cầu.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._requested_dir = self.direction

    def set_input_direction(self, new_dir):
        """Được gọi từ input (touch/phím) — chỉ lưu yêu cầu, chưa áp dụng ngay."""
        if new_dir in DIRECTIONS:
            self._requested_dir = new_dir

    def update_direction(self, world):
        # Đa hình: người chơi tự chọn hướng, chỉ đổi nếu hợp lệ.
        self.try_reverse(self._requested_dir)


class BotSnake(BaseSnake):
    """
    Rắn máy — AI tự động.
    GHI ĐÈ update_direction(): tìm mồi gần nhất, đi về phía đó,
    đồng thời né va chạm (tường / thân rắn) ngay trước mặt.
    """

    def update_direction(self, world):
        target = self._nearest_food(world)
        candidates = self._safe_directions(world)

        if not candidates:
            # Không còn hướng an toàn -> đi bừa (sẽ chết), miễn không quay đầu.
            candidates = [d for d in DIRECTIONS
                          if not self._is_reverse(d)] or DIRECTIONS

        if target is not None:
            hx, hy = self.head
            tx, ty = target
            # Chọn hướng an toàn giúp giảm khoảng cách tới mồi nhiều nhất.
            candidates.sort(key=lambda d: abs((hx + d[0]) - tx) + abs((hy + d[1]) - ty))
            # Thỉnh thoảng đi ngẫu nhiên cho tự nhiên (10%).
            if random.random() < 0.10:
                random.shuffle(candidates)

        self.direction = candidates[0]

    # ---------------- Trợ giúp AI ----------------
    def _is_reverse(self, d):
        return self.length > 1 and d[0] == -self.direction[0] and d[1] == -self.direction[1]

    def _safe_directions(self, world):
        """Các hướng mà ô kế tiếp không phải tường/thân rắn và không quay đầu."""
        hx, hy = self.head
        safe = []
        for d in DIRECTIONS:
            if self._is_reverse(d):
                continue
            nxt = (hx + d[0], hy + d[1])
            if not world.cell_blocked(nxt, ignore_snake=self):
                safe.append(d)
        return safe

    def _nearest_food(self, world):
        if not world.foods:
            return None
        hx, hy = self.head
        nearest = min(world.foods,
                      key=lambda f: abs(f.x - hx) + abs(f.y - hy))
        return (nearest.x, nearest.y)

