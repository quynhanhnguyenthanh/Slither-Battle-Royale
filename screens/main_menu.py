# -*- coding: utf-8 -*-
"""
screens/main_menu.py

Màn hình chính (MainMenu). Kế thừa Screen của Kivy.
Dùng ảnh UI thật: backdrop (nền), menu_title (logo), vignette (viền tối).
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle

import config
from utils import assets


class MainMenuScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = FloatLayout()

        # Nền backdrop (kéo giãn full màn hình)
        backdrop = assets.ui_path(config.UI["backdrop"])
        with root.canvas.before:
            Color(*config.COLOR_BG)
            self._bg_rect = Rectangle(pos=(0, 0), size=(1, 1))
            if backdrop:
                from kivy.core.image import Image as CoreImage
                Color(1, 1, 1, 0.55)
                self._bg_tex = CoreImage(backdrop).texture
                self._bg_img = Rectangle(texture=self._bg_tex, pos=(0, 0), size=(1, 1))
            else:
                self._bg_img = None
        self.bind(size=self._resize, pos=self._resize)

        # Cụm nội dung giữa màn hình
        box = BoxLayout(orientation="vertical", spacing=14, padding=(36, 24),
                        size_hint=(None, None), size=(320, 500),
                        pos_hint={"center_x": 0.5, "center_y": 0.52})

        title = assets.ui_path(config.UI["title"])
        if title:
            box.add_widget(Image(source=title, size_hint=(1, 0.34)))
        else:
            box.add_widget(Label(text="SLITHER", font_size=40, bold=True,
                                 size_hint=(1, 0.34)))

        box.add_widget(Label(text="SINH TỒN", font_size=22, bold=True,
                             size_hint=(1, 0.08)))

        self.lbl_info = Label(text="", font_size=17, size_hint=(1, 0.1))
        box.add_widget(self.lbl_info)

        box.add_widget(self._btn("CHƠI NGAY", (0.20, 0.75, 0.35, 1), self._play))
        box.add_widget(self._btn("CỬA HÀNG", (0.95, 0.72, 0.20, 1), self._shop))
        box.add_widget(self._btn("CÀI ĐẶT", (0.30, 0.55, 0.95, 1), self._settings))
        box.add_widget(self._btn("THOÁT", (0.75, 0.30, 0.30, 1), self._quit))
        root.add_widget(box)

        # Vignette phủ trên
        vig = assets.ui_path(config.UI["vignette"])
        if vig:
            root.add_widget(Image(source=vig, allow_stretch=True,
                                  keep_ratio=False, size_hint=(1, 1)))

        self.add_widget(root)

    def _resize(self, *a):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        if self._bg_img is not None:
            self._bg_img.pos = self.pos
            self._bg_img.size = self.size

    def _btn(self, text, color, cb):
        b = Button(text=text, font_size=22, bold=True, size_hint=(1, 0.13),
                   background_normal="", background_color=color)
        b.bind(on_release=cb)
        return b

    def on_enter(self, *args):
        data = self.manager.app.data
        self.lbl_info.text = "Kỷ lục: %d      Coin: %d" % (
            data.get_best_score(), data.get_coins())

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

