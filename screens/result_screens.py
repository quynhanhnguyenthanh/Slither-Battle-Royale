from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle

import config


def _rounded_btn(text, font_size, bg_color, cb, **kw):
    b = Button(text=text, font_size=font_size, bold=True,
               background_normal="", background_color=(0, 0, 0, 0), **kw)
    with b.canvas.before:
        Color(*bg_color)
        rect = RoundedRectangle(pos=b.pos, size=b.size, radius=[14,])
    b.bind(pos=lambda i, v, r=rect: setattr(r, 'pos', v),
           size=lambda i, v, r=rect: setattr(r, 'size', v))
    b.bind(on_release=cb)
    return b


class ResultScreen(Screen):
    TITLE = "KẾT THÚC"
    TITLE_COLOR = (1, 1, 1, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stats = {}
        box = BoxLayout(orientation="vertical", spacing=20, padding=30)

        self.lbl_title = Label(text=self.TITLE, font_size=50, bold=True,
                               color=self.TITLE_COLOR, size_hint=(1, 0.26))
        box.add_widget(self.lbl_title)

        self.lbl_stats = Label(text="", font_size=26, halign="center", size_hint=(1, 0.44))
        self.lbl_stats.bind(size=lambda w, *a: setattr(w, "text_size", w.size))
        box.add_widget(self.lbl_stats)

        again = _rounded_btn("CHƠI LẠI", 28, (0.2, 0.7, 0.35, 1),
                             self._again, size_hint=(1, 0.17))
        box.add_widget(again)

        menu = _rounded_btn("VỀ MENU", 28, (0.3, 0.55, 0.95, 1),
                            self._menu, size_hint=(1, 0.17))
        box.add_widget(menu)

        self.add_widget(box)

    def set_stats(self, stats):
        self.stats = stats

    def on_enter(self, *args):
        s = self.stats
        mins = int(s.get("time", 0)) // 60
        secs = int(s.get("time", 0)) % 60
        best_tag = "  (KỶ LỤC MỚI!)" if s.get("new_best") else ""
        self.lbl_stats.text = (
            "Điểm: %d%s\n"
            "Kỷ lục: %d\n"
            "Thời gian sống: %02d:%02d\n"
            "Bot đã hạ: %d / %d\n"
            "Coin nhận được: +%d"
        ) % (
            s.get("score", 0), best_tag,
            s.get("best_score", 0),
            mins, secs,
            s.get("bots_killed", 0), s.get("total_bots", 0),
            s.get("coins_earned", 0),
        )

    def _again(self, *a):
        self.manager.app.audio.play_sfx("click")
        self.manager.current = "game"

    def _menu(self, *a):
        self.manager.app.audio.play_sfx("click")
        self.manager.current = "menu"


class GameOverScreen(ResultScreen):
    TITLE = "GAME OVER"
    TITLE_COLOR = (0.95, 0.35, 0.35, 1)


class GameWinScreen(ResultScreen):
    TITLE = "CHIẾN THẮNG!"
    TITLE_COLOR = (0.35, 0.95, 0.45, 1)
