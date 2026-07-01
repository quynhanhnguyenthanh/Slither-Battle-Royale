# -*- coding: utf-8 -*-
"""
screens/shop_screen.py

Cửa hàng skin. Xem trước bằng SPRITE THẬT, trạng thái nút:
Mua (Buy) / Dùng (Use) / Đang dùng (Using).
Icon trạng thái: skin_indicator (đã sở hữu) / skin_indicator_locked (khoá).
Đọc/ghi qua đối tượng DataManager. Tái sử dụng component SkinRow.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget

import config
from utils import assets


class SkinRow(BoxLayout):
    """Một hàng skin: sprite xem trước + tên/giá + icon trạng thái + nút."""

    def __init__(self, skin, screen, **kwargs):
        super().__init__(orientation="horizontal", spacing=10, padding=6,
                         size_hint=(1, None), height=88, **kwargs)
        self.skin = skin
        self.screen = screen

        self.preview = Image(
            source=self._skin_image_path(),
            size_hint=(None, 1), width=76, allow_stretch=True, keep_ratio=True)
        self.add_widget(self.preview)

        self.info = Label(halign="left", valign="middle", font_size=18)
        self.info.bind(size=lambda w, *a: setattr(w, "text_size", w.size))
        self.add_widget(self.info)

        self.indicator = Image(size_hint=(None, 1), width=44,
                               allow_stretch=True, keep_ratio=True)
        self.add_widget(self.indicator)

        self.btn = Button(size_hint=(None, 1), width=112, bold=True,
                          background_normal="")
        self.btn.bind(on_release=self._on_press)
        self.add_widget(self.btn)

        self.refresh()

    def _skin_image_path(self):
        # Ưu tiên ảnh đầu (có mặt), nếu không thì ảnh thân
        import os
        from utils.assets import SKIN_DIR
        name = self.skin.get("head") or self.skin["body"]
        p = os.path.join(SKIN_DIR, name)
        return p if os.path.exists(p) else ""

    def refresh(self):
        if self.screen.manager is None:
            return
        data = self.screen.manager.app.data
        self.info.text = "%s\nGiá: %d coin" % (self.skin["name"], self.skin["price"])
        owned = data.owns_skin(self.skin["id"])
        current = data.get_current_skin() == self.skin["id"]

        self.indicator.source = assets.ui_path(
            config.UI["skin_owned"] if owned else config.UI["skin_locked"])

        if current:
            self.btn.text = "Đang dùng"
            self.btn.background_color = (0.5, 0.5, 0.55, 1)
        elif owned:
            self.btn.text = "Dùng"
            self.btn.background_color = (0.2, 0.7, 0.35, 1)
        else:
            self.btn.text = "Mua"
            self.btn.background_color = (0.95, 0.72, 0.2, 1)

    def _on_press(self, *a):
        app = self.screen.manager.app
        data = app.data
        sid, price = self.skin["id"], self.skin["price"]

        if data.get_current_skin() == sid:
            return
        if data.owns_skin(sid):
            data.set_current_skin(sid)
            app.audio.play_sfx("click")
        else:
            if not data.buy_skin(sid, price):
                app.audio.play_sfx("die")
                self.screen.flash("Không đủ coin!")
                return
            data.set_current_skin(sid)
            app.audio.play_sfx("eat")
        self.screen.refresh_all()


class ShopScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rows = []
        root = BoxLayout(orientation="vertical", spacing=8, padding=16)

        header = BoxLayout(size_hint=(1, None), height=50, spacing=10)
        header.add_widget(Label(text="CỬA HÀNG", font_size=30, bold=True))
        self.lbl_coins = Label(text="Coin: 0", font_size=20, bold=True,
                               size_hint=(None, 1), width=150)
        header.add_widget(self.lbl_coins)
        root.add_widget(header)

        self.msg = Label(text="", font_size=16, size_hint=(1, None), height=22,
                         color=(1, 0.5, 0.5, 1))
        root.add_widget(self.msg)

        # Danh sách cuộn được
        scroll = ScrollView(size_hint=(1, 1))
        list_box = BoxLayout(orientation="vertical", spacing=6,
                             size_hint=(1, None), padding=(0, 2))
        list_box.bind(minimum_height=list_box.setter("height"))
        for skin in config.SKINS:
            row = SkinRow(skin, self)
            self.rows.append(row)
            list_box.add_widget(row)
        scroll.add_widget(list_box)
        root.add_widget(scroll)

        back = Button(text="Quay lại", font_size=20, bold=True,
                      size_hint=(1, None), height=52, background_normal="",
                      background_color=(0.3, 0.55, 0.95, 1))
        back.bind(on_release=self._back)
        root.add_widget(back)

        self.add_widget(root)

    def on_enter(self, *args):
        self.msg.text = ""
        self.refresh_all()

    def refresh_all(self):
        self.lbl_coins.text = "Coin: %d" % self.manager.app.data.get_coins()
        for row in self.rows:
            row.refresh()

    def flash(self, text):
        self.msg.text = text

    def _back(self, *a):
        self.manager.app.audio.play_sfx("navigate")
        self.manager.current = "menu"

