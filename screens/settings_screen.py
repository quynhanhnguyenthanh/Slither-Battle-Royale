# -*- coding: utf-8 -*-
"""
screens/settings_screen.py

Màn hình Cài đặt: chỉnh âm lượng và bật/tắt hiệu ứng âm thanh.
Ghi trực tiếp vào DataManager (đối tượng dùng chung toàn app).
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider


class SettingsScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        box = BoxLayout(orientation="vertical", spacing=18, padding=40)

        box.add_widget(Label(text="CÀI ĐẶT", font_size=34, bold=True,
                             size_hint=(1, 0.2)))

        box.add_widget(Label(text="Âm lượng", font_size=20, size_hint=(1, 0.1)))
        self.slider = Slider(min=0, max=1, value=0.7, step=0.05, size_hint=(1, 0.12))
        self.slider.bind(value=self._on_volume)
        box.add_widget(self.slider)

        self.btn_sfx = Button(text="", font_size=20, size_hint=(1, 0.15),
                              background_normal="")
        self.btn_sfx.bind(on_release=self._toggle_sfx)
        box.add_widget(self.btn_sfx)

        self.btn_music = Button(text="", font_size=20, size_hint=(1, 0.15),
                                background_normal="")
        self.btn_music.bind(on_release=self._toggle_music)
        box.add_widget(self.btn_music)

        back = Button(text="Quay lại", font_size=20, bold=True,
                      size_hint=(1, 0.15), background_normal="",
                      background_color=(0.3, 0.55, 0.95, 1))
        back.bind(on_release=self._back)
        box.add_widget(back)

        self.add_widget(box)

    def on_enter(self, *args):
        data = self.manager.app.data
        self.slider.value = data.get_volume()
        self._refresh_sfx_label()
        self._refresh_music_label()

    def _on_volume(self, slider, value):
        app = self.manager.app
        app.data.set_volume(value)
        app.audio.apply_volume()

    def _toggle_sfx(self, *a):
        app = self.manager.app
        app.data.toggle_sfx()
        app.audio.play_sfx("click")
        self._refresh_sfx_label()

    def _toggle_music(self, *a):
        app = self.manager.app
        app.data.toggle_music()
        app.audio.apply_music_setting()
        app.audio.play_sfx("click")
        self._refresh_music_label()

    def _refresh_sfx_label(self):
        on = self.manager.app.data.is_sfx_on()
        self.btn_sfx.text = "Hiệu ứng: %s" % ("BẬT" if on else "TẮT")
        self.btn_sfx.background_color = (0.2, 0.7, 0.3, 1) if on else (0.6, 0.3, 0.3, 1)

    def _refresh_music_label(self):
        on = self.manager.app.data.is_music_on()
        self.btn_music.text = "Nhạc nền: %s" % ("BẬT" if on else "TẮT")
        self.btn_music.background_color = (0.2, 0.7, 0.3, 1) if on else (0.6, 0.3, 0.3, 1)

    def _back(self, *a):
        self.manager.app.audio.play_sfx("click")
        self.manager.current = "menu"
