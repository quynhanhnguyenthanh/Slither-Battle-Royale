from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.graphics import Color, RoundedRectangle

import config


def _rounded_btn(bg_color=(0.3, 0.55, 0.95, 1), **kw):
    b = Button(background_normal="", background_color=(0, 0, 0, 0), **kw)
    with b.canvas.before:
        Color(*bg_color)
        rect = RoundedRectangle(pos=b.pos, size=b.size, radius=[14,])
    b.bind(pos=lambda i, v, r=rect: setattr(r, 'pos', v),
           size=lambda i, v, r=rect: setattr(r, 'size', v))
    return b


class SettingsScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        box = BoxLayout(orientation="vertical", spacing=18, padding=40)

        box.add_widget(Label(text="CÀI ĐẶT", font_size=36, bold=True,
                             size_hint=(1, 0.2)))

        box.add_widget(Label(text="Âm lượng", font_size=22,
                             size_hint=(1, 0.1)))
        self.slider = Slider(min=0, max=1, value=0.7, step=0.05,
                             size_hint=(1, 0.12))
        self.slider.bind(value=self._on_volume)
        box.add_widget(self.slider)

        self.btn_sfx = _rounded_btn((0.2, 0.7, 0.3, 1),
                                    text="", font_size=22,
                                    size_hint=(1, 0.15))
        self.btn_sfx.bind(on_release=self._toggle_sfx)
        box.add_widget(self.btn_sfx)

        self.btn_music = _rounded_btn((0.2, 0.7, 0.3, 1),
                                      text="", font_size=22,
                                      size_hint=(1, 0.15))
        self.btn_music.bind(on_release=self._toggle_music)
        box.add_widget(self.btn_music)

        back = _rounded_btn((0.3, 0.55, 0.95, 1),
                            text="Quay lại", font_size=22,
                            size_hint=(1, 0.15))
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
        self.btn_sfx.canvas.before.clear()
        with self.btn_sfx.canvas.before:
            Color(*(0.2, 0.7, 0.3, 1) if on else (0.6, 0.3, 0.3, 1))
            RoundedRectangle(pos=self.btn_sfx.pos, size=self.btn_sfx.size, radius=[14,])

    def _refresh_music_label(self):
        on = self.manager.app.data.is_music_on()
        self.btn_music.text = "Nhạc nền: %s" % ("BẬT" if on else "TẮT")
        self.btn_music.canvas.before.clear()
        with self.btn_music.canvas.before:
            Color(*(0.2, 0.7, 0.3, 1) if on else (0.6, 0.3, 0.3, 1))
            RoundedRectangle(pos=self.btn_music.pos, size=self.btn_music.size, radius=[14,])

    def _back(self, *a):
        self.manager.app.audio.play_sfx("click")
        self.manager.current = "menu"
