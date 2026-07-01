# -*- coding: utf-8 -*-
"""
utils/audio.py

AudioManager: nạp & phát hiệu ứng âm thanh (.ogg trong assets/sounds).
Ánh xạ sự kiện game -> file âm thanh thực có trong repo.
Chống lỗi: thiếu file nào thì bỏ qua file đó, game vẫn chạy.
"""

import os
from kivy.core.audio import SoundLoader
from kivy.resources import resource_find

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUND_DIR = os.path.join(BASE_DIR, "assets", "sounds")


class AudioManager:
    # Ánh xạ tên sự kiện trong game -> file .ogg thực tế
    SFX_FILES = {
        "eat": "alert_money.ogg",     # ăn mồi / nhận coin
        "die": "error_2.ogg",         # rắn chết
        "win": "start_game.ogg",      # chiến thắng
        "click": "button_up.ogg",     # bấm nút
        "navigate": "navigate.ogg",   # chuyển màn hình
        "kill": "whoosh.ogg",         # hạ được bot
    }

    def __init__(self, data_manager):
        self.data = data_manager
        self._sfx = {}
        self._load_all()

    def _path(self, filename):
        p = os.path.join(SOUND_DIR, filename)
        return p if os.path.exists(p) else (resource_find(filename) or "")

    def _load_all(self):
        for name, filename in self.SFX_FILES.items():
            path = self._path(filename)
            self._sfx[name] = SoundLoader.load(path) if path else None

    def play_sfx(self, name):
        if not self.data.is_sfx_on():
            return
        sound = self._sfx.get(name)
        if sound:
            sound.volume = self.data.get_volume()
            sound.stop()
            sound.play()

    # Giữ API tương thích với phần còn lại (không có nhạc nền trong bộ assets)
    def play_music(self):
        pass

    def stop_music(self):
        pass

    def apply_volume(self):
        pass
