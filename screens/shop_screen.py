from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle

import config
from utils import assets


class SkinCard(BoxLayout):
    """Một thẻ skin dạng dọc: sprite + tên/giá + nút."""

    def __init__(self, skin, screen, **kwargs):
        super().__init__(orientation="vertical", spacing=6, padding=8,
                         size_hint=(None, 1), width=160, **kwargs)
        self.skin = skin
        self.screen = screen

        with self.canvas.before:
            Color(0.12, 0.12, 0.16, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[12,])
        self.bind(pos=lambda i, v: self._update_bg(),
                  size=lambda i, v: self._update_bg())

        self.preview = Image(
            source=self._skin_image_path(),
            size_hint=(1, 0.45), allow_stretch=True, keep_ratio=True)
        self.add_widget(self.preview)

        self.info = Label(halign="center", valign="middle", font_size=17,
                          size_hint=(1, 0.25))
        self.info.bind(size=lambda w, *a: setattr(w, "text_size", w.size))
        self.add_widget(self.info)

        self.btn = Button(size_hint=(1, 0.3), font_size=18, bold=True,
                          background_normal="", background_color=(0, 0, 0, 0))
        self.btn.bind(on_release=self._on_press)
        with self.btn.canvas.before:
            self._btn_color = Color(0.95, 0.72, 0.2, 1)
            self._btn_rect = RoundedRectangle(pos=self.btn.pos, size=self.btn.size,
                                               radius=[10,])
        self.btn.bind(pos=lambda i, v, r=self._btn_rect: setattr(r, 'pos', v),
                      size=lambda i, v, r=self._btn_rect: setattr(r, 'size', v))
        self.add_widget(self.btn)

        self.refresh()

    def _update_bg(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.12, 0.12, 0.16, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[12,])

    def _skin_image_path(self):
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

        if current:
            self.btn.text = "Đang dùng"
            self._set_btn_color(0.5, 0.5, 0.55, 1)
        elif owned:
            self.btn.text = "Dùng"
            self._set_btn_color(0.2, 0.7, 0.35, 1)
        else:
            self.btn.text = "Mua"
            self._set_btn_color(0.95, 0.72, 0.2, 1)

    def _set_btn_color(self, r, g, b, a):
        self.btn.canvas.before.clear()
        with self.btn.canvas.before:
            Color(r, g, b, a)
            RoundedRectangle(pos=self.btn.pos, size=self.btn.size, radius=[10,])

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
        self.cards = []
        root = BoxLayout(orientation="vertical", spacing=10, padding=16)

        header = BoxLayout(size_hint=(1, None), height=56, spacing=10)
        header.add_widget(Label(text="CỬA HÀNG", font_size=32, bold=True,
                                ))
        self.lbl_coins = Label(text="Coin: 0", font_size=22, bold=True,
                               size_hint=(None, 1), width=160)
        header.add_widget(self.lbl_coins)
        root.add_widget(header)

        self.msg = Label(text="", font_size=18, size_hint=(1, None), height=24,
                         color=(1, 0.5, 0.5, 1))
        root.add_widget(self.msg)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=True,
                            do_scroll_y=False, bar_width=10)
        list_box = BoxLayout(orientation="horizontal", spacing=12,
                             size_hint=(None, 1), padding=(8, 6))
        list_box.bind(minimum_width=list_box.setter("width"))
        for skin in config.SKINS:
            card = SkinCard(skin, self)
            self.cards.append(card)
            list_box.add_widget(card)
        scroll.add_widget(list_box)
        root.add_widget(scroll)

        back = Button(text="Quay lại", font_size=22, bold=True,
                      size_hint=(1, None), height=56,
                      background_normal="", background_color=(0, 0, 0, 0))
        with back.canvas.before:
            Color(0.3, 0.55, 0.95, 1)
            r = RoundedRectangle(pos=back.pos, size=back.size, radius=[14,])
        back.bind(pos=lambda i, v, rect=r: setattr(rect, 'pos', v),
                  size=lambda i, v, rect=r: setattr(rect, 'size', v))
        back.bind(on_release=self._back)
        root.add_widget(back)

        self.add_widget(root)

    def on_enter(self, *args):
        self.msg.text = ""
        self.refresh_all()

    def refresh_all(self):
        self.lbl_coins.text = "Coin: %d" % self.manager.app.data.get_coins()
        for card in self.cards:
            card.refresh()

    def flash(self, text):
        self.msg.text = text

    def _back(self, *a):
        self.manager.app.audio.play_sfx("navigate")
        self.manager.current = "menu"
