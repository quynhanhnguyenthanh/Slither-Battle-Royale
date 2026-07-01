# -*- coding: utf-8 -*-
"""
main.py — Điểm khởi chạy game "Slither Sinh Tồn" (Slither Battle Royale).

Cấu hình ScreenManager và tạo các đối tượng dùng chung (DataManager, AudioManager).
Dữ liệu lưu trong game_data.json tại thư mục dữ liệu người dùng (an toàn cho Android).

Chạy trên máy tính:  python main.py
Đóng gói Android:    buildozer -v android debug
"""

import os

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from utils import DataManager, AudioManager
from screens import (
    MainMenuScreen, SettingsScreen, ShopScreen,
    GameScreen, GameOverScreen, GameWinScreen,
)

# Kích thước cửa sổ khi chạy thử trên PC (tỉ lệ dọc như điện thoại)
Window.size = (420, 740)


class GameManager(ScreenManager):
    """ScreenManager có tham chiếu App để mọi màn hình dùng chung dữ liệu."""

    def __init__(self, app, **kwargs):
        super().__init__(transition=FadeTransition(duration=0.2), **kwargs)
        self.app = app
        self.add_widget(MainMenuScreen(name="menu"))
        self.add_widget(GameScreen(name="game"))
        self.add_widget(ShopScreen(name="shop"))
        self.add_widget(SettingsScreen(name="settings"))
        self.add_widget(GameOverScreen(name="game_over"))
        self.add_widget(GameWinScreen(name="game_win"))
        self.current = "menu"


class SlitherApp(App):
    title = "Slither Sinh Ton"

    def build(self):
        # File lưu: user_data_dir để ghi được trên mọi nền tảng (kể cả Android)
        data_path = os.path.join(self.user_data_dir, "game_data.json")
        self.data = DataManager(data_path)
        self.audio = AudioManager(self.data)
        return GameManager(self)

    def on_stop(self):
        self.data.save()


if __name__ == "__main__":
    SlitherApp().run()

