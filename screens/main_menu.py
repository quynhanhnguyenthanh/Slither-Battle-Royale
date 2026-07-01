# -*- coding: utf-8 -*-
"""
screens/main_menu.py

Màn hình chính (MainMenu).
Video nền + Logo + Menu.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.video import Video
from kivy.graphics import Color, Rectangle

import config
from utils import assets


class MainMenuScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = FloatLayout()

        # ==========================
        # VIDEO BACKGROUND
        # ==========================

        self.video = Video(
            source="assets/video/menu_background.mp4",
            state="play",
            options={"eos": "loop"},
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
        )

        self.video.allow_stretch = True
        self.video.keep_ratio = False

        root.add_widget(self.video)

        # ==========================
        # MENU
        # ==========================

        box = BoxLayout(
            orientation="vertical",
            spacing=14,
            padding=(36, 24),
            size_hint=(None, None),
            size=(320, 500),
            pos_hint={"center_x": 0.5, "center_y": 0.52},
        )

        title = assets.ui_path(config.UI["title"])

        if title:
            box.add_widget(Image(source=title, size_hint=(1, 0.34)))
        else:
            box.add_widget(
                Label(
                    text="SLITHER",
                    font_size=40,
                    bold=True,
                    size_hint=(1, 0.34),
                )
            )

        box.add_widget(
            Label(
                text="SINH TỒN",
                font_size=22,
                bold=True,
                size_hint=(1, 0.08),
            )
        )

        self.lbl_info = Label(
            text="",
            font_size=17,
            size_hint=(1, 0.1),
        )

        box.add_widget(self.lbl_info)

        box.add_widget(
            self._btn(
                "CHƠI NGAY",
                (0.20, 0.75, 0.35, 1),
                self._play,
            )
        )

        box.add_widget(
            self._btn(
                "CỬA HÀNG",
                (0.95, 0.72, 0.20, 1),
                self._shop,
            )
        )

        box.add_widget(
            self._btn(
                "CÀI ĐẶT",
                (0.30, 0.55, 0.95, 1),
                self._settings,
            )
        )

        box.add_widget(
            self._btn(
                "THOÁT",
                (0.75, 0.30, 0.30, 1),
                self._quit,
            )
        )

        root.add_widget(box)

        self.add_widget(root)

    def _resize_overlay(self, instance, value):
        self.overlay.pos = instance.pos
        self.overlay.size = instance.size

    def _btn(self, text, color, cb):
        b = Button(
            text=text,
            font_size=22,
            bold=True,
            size_hint=(1, 0.13),
            background_normal="",
            background_color=color,
        )
        b.bind(on_release=cb)
        return b

    def on_enter(self, *args):
        data = self.manager.app.data
        self.lbl_info.text = "Kỷ lục: %d      Coin: %d" % (
            data.get_best_score(),
            data.get_coins(),
        )

        self.video.state = "play"

    def on_leave(self, *args):
        self.video.state = "stop"

    def _play(self, *a):
        self.manager.app.audio.play_sfx("click")
        self.manager.current = "game"

    def _shop(self, *a):
        self.manager.app.audio.play_sfx("navigate")
        self.manager.current = "shop"

    def _settings(self, *a):
        self.manager.app.audio.play_sfx("navigate")
        self.manager.current = "settings"

    def _quit(self, *a):
        from kivy.app import App
        App.get_running_app().stop()
