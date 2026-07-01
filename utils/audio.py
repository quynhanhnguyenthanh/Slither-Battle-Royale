# -*- coding: utf-8 -*-
"""
utils/audio.py

AudioManager: hiệu ứng âm thanh (.ogg) + nhạc nền (nếu có file).
Ánh xạ sự kiện game -> file thực trong assets/sounds. Thiếu file thì bỏ qua.

Nhạc nền: bộ assets gốc KHÔNG kèm file nhạc nền. Nếu bạn thêm
assets/sounds/bgm.ogg (hoặc music.ogg), game sẽ tự phát lặp và có thể
bật/tắt trong màn Cài đặt.
"""

import os
from kivy.core.audio import SoundLoader
from kivy.resources import resource_find

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUND_DIR = os.path.join(BASE_DIR, "assets", "sounds")


class AudioManager:
    SFX_FILES = {
        "eat": "alert_money.ogg",     # ăn mồi / nhận coin
        "die": "error_2.ogg",         # rắn chết
        "win": "start_game.ogg",      # chiến thắng
        "click": "button_up.ogg",     # bấm nút
        "navigate": "navigate.ogg",   # chuyển màn hình
        "kill": "whoosh.ogg",         # hạ được bot
        "boost_on": "boost_start.ogg",  # bắt đầu tăng tốc
        "boost_off": "boost_stop.ogg",  # ngừng tăng tốc
    }
    MUSIC_CANDIDATES = ["bgm.ogg", "music.ogg", "background.ogg"]

    def __init__(self, data_manager):
        self.data = data_manager
        self._sfx = {}
        self._music = None
        self._load_all()

    def _path(self, filename):
        p = os.path.join(SOUND_DIR, filename)
        return p if os.path.exists(p) else (resource_find(filename) or "")

    def _load_all(self):
        for name, filename in self.SFX_FILES.items():
            path = self._path(filename)
            self._sfx[name] = SoundLoader.load(path) if path else None
        for cand in self.MUSIC_CANDIDATES:
            path = self._path(cand)
            if path:
                self._music = SoundLoader.load(path)
                if self._music:
                    self._music.loop = True
                    break

    # ---------------- Hiệu ứng ----------------
    def play_sfx(self, name):
        if not self.data.is_sfx_on():
            return
        sound = self._sfx.get(name)
        if sound:
            sound.volume = self.data.get_volume()
            sound.stop()
            sound.play()

    # ---------------- Nhạc nền ----------------
    def play_music(self):
        if self._music and self.data.is_music_on():
            self._music.volume = self.data.get_volume() * 0.6
            if self._music.state != "play":
                self._music.play()

    def stop_music(self):
        if self._music and self._music.state == "play":
            self._music.stop()

    def apply_music_setting(self):
        if self.data.is_music_on():
            self.play_music()
        else:
            self.stop_music()

    def apply_volume(self):
        if self._music:
            self._music.volume = self.data.get_volume() * 0.6
