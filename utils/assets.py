# -*- coding: utf-8 -*-
"""
utils/assets.py

Nạp và cache texture (ảnh) để vẽ lên canvas, đồng thời cung cấp đường dẫn
ảnh UI cho các widget. Dùng resource_find() để tương thích khi đóng gói APK.

Thiết kế "chống lỗi": thiếu ảnh -> trả về None, phần vẽ sẽ tự dùng màu dự phòng.
"""

import os
from kivy.core.image import Image as CoreImage
from kivy.resources import resource_add_path, resource_find

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMG_DIR = os.path.join(ASSETS_DIR, "images")
SKIN_DIR = os.path.join(IMG_DIR, "skins")
UI_DIR = os.path.join(IMG_DIR, "ui")

# Đăng ký để resource_find() tìm được cả khi chạy trong APK
for _p in (ASSETS_DIR, IMG_DIR, SKIN_DIR, UI_DIR):
    if os.path.isdir(_p):
        resource_add_path(_p)

_tex_cache = {}


def _resolve(subdir, filename):
    path = os.path.join(IMG_DIR, subdir, filename)
    if os.path.exists(path):
        return path
    return resource_find(filename)


def _texture(subdir, filename):
    key = subdir + "/" + filename
    if key in _tex_cache:
        return _tex_cache[key]
    tex = None
    path = _resolve(subdir, filename)
    if path:
        try:
            tex = CoreImage(path).texture
        except Exception:
            tex = None
    _tex_cache[key] = tex
    return tex


# ---------- Texture cho rắn ----------
def skin_body_texture(skin):
    return _texture("skins", skin["body"])


def skin_head_texture(skin):
    filename = skin.get("head") or skin["body"]
    return _texture("skins", filename)


def eye_textures():
    return (_texture("skins", "snake_eye_left.png"),
            _texture("skins", "snake_eye_right.png"))


def circle_texture():
    return _texture("ui", "circle.png")


# ---------- Đường dẫn ảnh UI (cho widget Image / background) ----------
def ui_path(filename):
    path = os.path.join(UI_DIR, filename)
    if os.path.exists(path):
        return path
    return resource_find(filename) or ""
