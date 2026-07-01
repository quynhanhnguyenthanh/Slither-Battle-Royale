# -*- coding: utf-8 -*-
"""
entities/collectibles.py

Vật phẩm trên bản đồ (toạ độ thực, liên tục):
  - Food: hạt mồi thường.
  - Loot: hạt lớn rơi ra từ xác rắn chết (kế thừa Food).
"""

import config


class Food:
    def __init__(self, x, y, score=config.FOOD_SCORE, coin=config.FOOD_COIN,
                 color=config.COLOR_FOOD, radius=config.FOOD_RADIUS,
                 grow=config.GROW_PER_FOOD):
        self.x = float(x)
        self.y = float(y)
        self.score = score
        self.coin = coin
        self.color = color
        self.radius = radius
        self.grow = grow

    @property
    def pos(self):
        return (self.x, self.y)


class Loot(Food):
    """Mồi lớn từ xác rắn: giá trị cao hơn, to hơn."""

    def __init__(self, x, y):
        super().__init__(
            x, y,
            score=config.LOOT_SCORE,
            coin=config.LOOT_COIN,
            color=config.COLOR_LOOT,
            radius=config.LOOT_RADIUS,
            grow=config.GROW_PER_LOOT,
        )
