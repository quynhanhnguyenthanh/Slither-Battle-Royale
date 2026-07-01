# -*- coding: utf-8 -*-
"""
screens/result_screens.py

GameOverScreen (Thua) và GameWinScreen (Thắng).
Cả hai dùng chung một lớp cha ResultScreen -> tái sử dụng component,
chỉ khác tiêu đề và màu sắc (một dạng "khác biệt hoá" qua kế thừa).
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


class ResultScreen(Screen):
    TITLE = "KẾT THÚC"
    TITLE_COLOR = (1, 1, 1, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stats = {}
        box = BoxLayout(orientation="vertical", spacing=16, padding=40)

        self.lbl_title = Label(text=self.TITLE, font_size=42, bold=True,
                               color=self.TITLE_COLOR, size_hint=(1, 0.28))
        box.add_widget(self.lbl_title)

        self.lbl_stats = Label(text="", font_size=20, halign="center",
                               size_hint=(1, 0.42))
        self.lbl_stats.bind(size=lambda w, *a: setattr(w, "text_size", w.size))
        box.add_widget(self.lbl_stats)

        again = Button(text="CHƠI LẠI", font_size=22, bold=True,
                       size_hint=(1, 0.15), background_color=(0.2, 0.7, 0.35, 1))
        again.bind(on_release=self._again)
        box.add_widget(again)

        menu = Button(text="VỀ MENU", font_size=22, bold=True,
                      size_hint=(1, 0.15), background_color=(0.3, 0.55, 0.95, 1))
        menu.bind(on_release=self._menu)
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
