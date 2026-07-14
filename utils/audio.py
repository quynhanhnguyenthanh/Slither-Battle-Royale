# -*- coding: utf-8 -*-
"""
utils/audio.py

AudioManager: hiệu ứng âm thanh (.ogg).
Ánh xạ sự kiện game -> file thực trong assets/sounds. Thiếu file thì bỏ qua.
"""

import os
from kivy.core.audio import SoundLoader
from kivy.resources import resource_find

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUND_DIR = os.path.join(BASE_DIR, "assets", "sounds")


class AudioManager:
    SFX_FILES = {
        "eat": "alert_money.ogg",
        "die": "error_2.ogg",
        "win": "start_game.ogg",
        "click": "button_up.ogg",
        "navigate": "navigate.ogg",
        "kill": "whoosh.ogg",
        "boost_on": "boost_start.ogg",
        "boost_off": "boost_stop.ogg",
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
