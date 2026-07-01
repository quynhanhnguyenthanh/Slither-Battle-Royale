# -*- coding: utf-8 -*-
"""
config.py
Cấu hình trung tâm cho game "Slither Sinh Tồn" (Slither Battle Royale).
Tập trung mọi hằng số & bảng skin ở đây (Tính Module hóa).
"""

# ---------- Kích thước thế giới (lưới - grid) ----------
WORLD_W = 180
WORLD_H = 180
CELL = 28              # kích thước 1 ô (pixel) khi vẽ

# ---------- Nhịp game ----------
MOVE_INTERVAL = 1   # giây giữa 2 bước rắn (tốc độ)
FPS = 60

# ---------- Thiết lập màn chơi ----------
NUM_BOTS = 5
FOOD_COUNT = 40
START_LENGTH = 4

# ---------- Phần thưởng ----------
FOOD_SCORE = 1
FOOD_COIN = 1
LOOT_SCORE = 3
LOOT_COIN = 2
KILL_BONUS_COIN = 10

# ---------- Màu nền / lưới (RGBA 0..1) ----------
COLOR_BG = (0.05, 0.06, 0.09, 1)
COLOR_GRID = (1, 1, 1, 0.04)
COLOR_WALL = (0.90, 0.25, 0.35, 1)
COLOR_FOOD = (0.98, 0.85, 0.35, 1)
COLOR_LOOT = (1.0, 0.45, 0.55, 1)

# ---------- File giao diện (UI) trong assets/images/ui ----------
UI = {
    "backdrop": "backdrop.png",
    "vignette": "vignette.png",
    "title": "menu_title.png",
    "circle": "circle.png",
    "blur": "blur.png",
    "nav_home": "nav_home.png",
    "nav_skins": "nav_skins.png",
    "nav_heart": "nav_heart.png",
    "skin_owned": "skin_indicator.png",
    "skin_locked": "skin_indicator_locked.png",
    "card_gradient": "skin_card_gradient.png",
}

# ---------- Bảng skin (dùng sprite thật trong assets/images/skins) ----------
# body/head: tên file; eyes=True -> tự vẽ 2 con mắt (skin không có mặt sẵn).
# fallback: màu dự phòng nếu thiếu ảnh (game vẫn chạy).
SKINS = [
    {"id": "main", "name": "Cổ điển", "price": 0,
     "body": "snake_main.png", "head": None, "eyes": True,
     "fallback_head": (0.96, 0.95, 0.90, 1), "fallback_body": (0.85, 0.84, 0.80, 1)},

    {"id": "jelly", "name": "Thạch Lục", "price": 30,
     "body": "snake_jelly.png", "head": None, "eyes": True,
     "fallback_head": (0.30, 0.82, 0.45, 1), "fallback_body": (0.22, 0.68, 0.36, 1)},

    {"id": "jelly_blue", "name": "Thạch Lam", "price": 30,
     "body": "snake_jelly_blue.png", "head": None, "eyes": True,
     "fallback_head": (0.32, 0.52, 0.92, 1), "fallback_body": (0.24, 0.40, 0.78, 1)},

    {"id": "jelly_red", "name": "Thạch Đỏ", "price": 30,
     "body": "snake_jelly_red.png", "head": None, "eyes": True,
     "fallback_head": (0.92, 0.32, 0.42, 1), "fallback_body": (0.78, 0.24, 0.34, 1)},

    {"id": "outlined", "name": "Viền Nét", "price": 60,
     "body": "snake_outlined.png", "head": None, "eyes": True,
     "fallback_head": (0.98, 0.98, 0.98, 1), "fallback_body": (0.85, 0.85, 0.88, 1)},

    {"id": "black_ice", "name": "Băng Đen", "price": 80,
     "body": "snake_black_ice.png", "head": None, "eyes": True,
     "fallback_head": (0.12, 0.12, 0.16, 1), "fallback_body": (0.08, 0.08, 0.10, 1)},

    {"id": "stars", "name": "Ngàn Sao", "price": 100,
     "body": "snake_stars.png", "head": None, "eyes": True,
     "fallback_head": (0.45, 0.60, 0.95, 1), "fallback_body": (0.35, 0.48, 0.82, 1)},

    {"id": "canada", "name": "Canada", "price": 120,
     "body": "snake_canada.png", "head": None, "eyes": True,
     "fallback_head": (0.95, 0.50, 0.60, 1), "fallback_body": (0.82, 0.38, 0.48, 1)},

    {"id": "stare", "name": "Trố Mắt", "price": 150,
     "body": "snake_stare_body.png", "head": "snake_stare_head.png", "eyes": False,
     "fallback_head": (0.95, 0.90, 0.72, 1), "fallback_body": (0.90, 0.86, 0.66, 1)},

    {"id": "awesome", "name": "Ngầu", "price": 180,
     "body": "snake_awesome_body.png", "head": "snake_awesome_head.png", "eyes": False,
     "fallback_head": (0.98, 0.82, 0.25, 1), "fallback_body": (0.90, 0.74, 0.18, 1)},

    {"id": "vamp", "name": "Ma Cà Rồng", "price": 220,
     "body": "snake_vamp_body.png", "head": "snake_vamp_head.png", "eyes": False,
     "fallback_head": (0.88, 0.16, 0.22, 1), "fallback_body": (0.72, 0.12, 0.18, 1)},
]

# Các skin (body-only) dùng ngẫu nhiên cho bot
BOT_SKIN_POOL = ["jelly", "jelly_blue", "jelly_red", "black_ice",
                 "stars", "canada", "outlined", "vamp"]


def get_skin(skin_id):
    for s in SKINS:
        if s["id"] == skin_id:
            return s
    return SKINS[0]
