# -*- coding: utf-8 -*-
"""
entities/collectibles.py

Vật phẩm thu thập trên bản đồ:
  - Food : mồi thường, xuất hiện ngẫu nhiên.
  - Loot : mồi lớn RỚT RA từ xác con rắn chết (kế thừa Food).

Minh hoạ KHỞI TẠO ĐỐI TƯỢNG và KẾ THỪA ở quy mô nhỏ.
Được vẽ bằng sprite ui/circle.png (tô màu theo thuộc tính color).
"""

import config


class Food:
    """Mồi thường: cho điểm và coin khi bị ăn."""

    def __init__(self, x, y, score=config.FOOD_SCORE, coin=config.FOOD_COIN,
                 color=config.COLOR_FOOD, radius_ratio=0.34):
        self.x = x
        self.y = y
        self.score = score
        self.coin = coin
        self.color = color
        self.radius_ratio = radius_ratio  # bán kính vẽ so với ô

    @property
    def pos(self):
        return (self.x, self.y)


class Loot(Food):
    """Mồi loot: to hơn, giá trị cao hơn, rơi ra từ thân rắn đã chết."""

    def __init__(self, x, y):
        super().__init__(
            x, y,
            score=config.LOOT_SCORE,
            coin=config.LOOT_COIN,
            color=config.COLOR_LOOT,
            radius_ratio=0.46,
        )
