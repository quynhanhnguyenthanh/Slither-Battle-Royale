# -*- coding: utf-8 -*-
"""Gói thực thể trong game: rắn và vật phẩm."""
from .snake import BaseSnake, PlayerSnake, BotSnake, UP, DOWN, LEFT, RIGHT
from .collectibles import Food, Loot

__all__ = [
    "BaseSnake", "PlayerSnake", "BotSnake",
    "Food", "Loot",
    "UP", "DOWN", "LEFT", "RIGHT",
]
