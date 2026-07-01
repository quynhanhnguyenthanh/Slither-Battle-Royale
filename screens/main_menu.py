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
from kivy.graphics import Color, Rectangle, RoundedRectangle

import config
from utils import assets

import av
from kivy.clock import Clock
from kivy.graphics.texture import Texture


class VideoBackground:

    def __init__(self, path, target_size=(420, 740), fps=15):
        self._container = av.open(path)
        self._stream = self._container.streams.video[0]
        self._fps = fps
        self._target_w, self._target_h = target_size

        self.texture = Texture.create(
            size=(self._target_w, self._target_h), colorfmt="rgb")

        self._playing = False
        self._clock_event = None
        self._generator = None
        self.seek(0)

    def seek(self, pts):
        self._container.seek(pts)
        self._generator = self._container.decode(video=0)

    def start(self):
        if self._playing:
            return
        self._playing = True
        self._clock_event = Clock.schedule_interval(self._tick, 1.0 / self._fps)

    def stop(self):
        self._playing = False
        if self._clock_event:
            self._clock_event.cancel()
            self._clock_event = None

    def close(self):
        self.stop()
        self._container.close()

    def _tick(self, dt):
        try:
            frame = next(self._generator)
        except StopIteration:
            self.seek(0)
            try:
                frame = next(self._generator)
            except StopIteration:
                return

        if frame.width != self._target_w or frame.height != self._target_h:
            frame = frame.reformat(self._target_w, self._target_h)

        img = frame.to_ndarray(format="rgb24")
        self.texture.blit_buffer(
            img.tobytes(), colorfmt="rgb", bufferfmt="ubyte")


class MainMenuScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = FloatLayout()

        # Nền video
        self._video_bg = None
        try:
            self._video_bg = VideoBackground("assets/video/menu_background.mp4")
            with root.canvas.before:
                Color(*config.COLOR_BG)
                self._bg_rect = Rectangle(pos=(0, 0), size=(1, 1))
                Color(1, 1, 1, 1)
                self._bg_img = Rectangle(
                    texture=self._video_bg.texture, pos=(0, 0), size=(1, 1))
            self.bind(size=self._resize, pos=self._resize)
        except Exception:
            self._video_bg = None

        # MENU
        box = BoxLayout(
            orientation="vertical",
            spacing=18,
            padding=(36, 20),
            size_hint=(None, None),
            size=(360, 540),
            pos_hint={"center_x": 0.5, "center_y": 0.52},
        )

        title = assets.ui_path(config.UI["title"])

        if title:
            box.add_widget(Image(source=title, size_hint=(1, 0.34)))
        else:
            box.add_widget(
                Label(
                    text="SLITHER",
                    font_size=48,
                    bold=True,
                    size_hint=(1, 0.34),
                )
            )

        box.add_widget(
            Label(
                text="SINH TỒN",
                font_size=30,
                bold=True,
                size_hint=(1, 0.08),
            )
        )

        self.lbl_info = Label(
            text="",
            font_size=22,
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

    def _resize(self, *a):
        if not self._video_bg:
            return
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._bg_img.pos = self.pos
        self._bg_img.size = self.size

    def _btn(self, text, color, cb):
        b = Button(
            text=text,
            font_size=28,
            bold=True,
            size_hint=(1, 0.15),
            background_normal="",
            background_color=(0, 0, 0, 0),
        )
        with b.canvas.before:
            Color(*color)
            rect = RoundedRectangle(pos=b.pos, size=b.size, radius=[14,])
        b.bind(pos=lambda i, v, r=rect: setattr(r, 'pos', v),
               size=lambda i, v, r=rect: setattr(r, 'size', v))
        b.bind(on_release=cb)
        return b

    def on_enter(self, *args):
        data = self.manager.app.data
        self.lbl_info.text = "Kỷ lục: %d      Coin: %d" % (
            data.get_best_score(),
            data.get_coins(),
        )
        if self._video_bg:
            self._video_bg.start()

    def on_leave(self, *args):
        if self._video_bg:
            self._video_bg.stop()

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
