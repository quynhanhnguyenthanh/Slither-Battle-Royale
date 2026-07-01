# -*- coding: utf-8 -*-
"""
utils/data_manager.py

Lớp DataManager: quản lý dữ liệu lưu trữ của game trong file data.json.
Minh hoạ TÍNH ĐÓNG GÓI (Encapsulation):
  - Dữ liệu thật (_data) được giấu kín (quy ước "_" là private).
  - Bên ngoài chỉ tương tác qua các phương thức get/set an toàn.
"""

import os
import json


class DataManager:
    """Đọc/ghi tiến trình người chơi: best score, coin, skin, âm lượng."""

    DEFAULT_DATA = {
        "best_score": 0,
        "coins": 0,
        "owned_skins": ["main"],
        "current_skin": "main",
        "volume": 0.7,
        "sfx_on": True,
        "music_on": True,
    }

    def __init__(self, path="game_data.json"):
        self._path = path
        self._data = dict(self.DEFAULT_DATA)
        self.load()

    # ---------------- Đọc / Ghi file ----------------
    def load(self):
        """Nạp dữ liệu từ file. Nếu lỗi/thiếu -> dùng mặc định."""
        try:
            if os.path.exists(self._path):
                with open(self._path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                # Gộp để đảm bảo đủ khoá kể cả khi file cũ thiếu trường mới
                for key, value in self.DEFAULT_DATA.items():
                    self._data[key] = loaded.get(key, value)
        except (json.JSONDecodeError, OSError):
            self._data = dict(self.DEFAULT_DATA)
        return self._data

    def save(self):
        """Ghi dữ liệu hiện tại xuống file."""
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass  # Không làm sập game nếu ghi lỗi

    # ---------------- Truy cập có kiểm soát ----------------
    def get_best_score(self):
        return self._data["best_score"]

    def update_best_score(self, score):
        """Cập nhật best score nếu điểm mới cao hơn. Trả về True nếu phá kỷ lục."""
        if score > self._data["best_score"]:
            self._data["best_score"] = score
            self.save()
            return True
        return False

    def get_coins(self):
        return self._data["coins"]

    def add_coins(self, amount):
        self._data["coins"] += max(0, int(amount))
        self.save()

    def spend_coins(self, amount):
        """Trừ coin nếu đủ. Trả về True nếu thành công."""
        if self._data["coins"] >= amount:
            self._data["coins"] -= amount
            self.save()
            return True
        return False

    # ---------------- Skin ----------------
    def owns_skin(self, skin_id):
        return skin_id in self._data["owned_skins"]

    def buy_skin(self, skin_id, price):
        """Mua skin: kiểm tra coin, trừ tiền, thêm vào danh sách sở hữu."""
        if self.owns_skin(skin_id):
            return False
        if self.spend_coins(price):
            self._data["owned_skins"].append(skin_id)
            self.save()
            return True
        return False

    def get_current_skin(self):
        return self._data["current_skin"]

    def set_current_skin(self, skin_id):
        if self.owns_skin(skin_id):
            self._data["current_skin"] = skin_id
            self.save()
            return True
        return False

    # ---------------- Âm thanh ----------------
    def get_volume(self):
        return self._data["volume"]

    def set_volume(self, value):
        self._data["volume"] = max(0.0, min(1.0, float(value)))
        self.save()

    def is_sfx_on(self):
        return self._data["sfx_on"]

    def toggle_sfx(self):
        self._data["sfx_on"] = not self._data["sfx_on"]
        self.save()
        return self._data["sfx_on"]

    def is_music_on(self):
        return self._data.get("music_on", True)

    def toggle_music(self):
        self._data["music_on"] = not self.is_music_on()
        self.save()
        return self._data["music_on"]
