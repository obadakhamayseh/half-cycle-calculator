import math
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Rectangle

BG_COLOR      = (0.07, 0.07, 0.12, 1)
CARD_COLOR    = (0.12, 0.12, 0.20, 1)
ACCENT        = (0.18, 0.52, 0.95, 1)
ACCENT2       = (0.10, 0.75, 0.60, 1)
TEXT_COLOR    = (0.95, 0.95, 0.95, 1)
SUBTEXT_COLOR = (0.60, 0.63, 0.70, 1)
RESULT_ODD    = (0.14, 0.14, 0.22, 1)
RESULT_EVEN   = (0.11, 0.11, 0.18, 1)

Window.clearcolor = BG_COLOR


class RoundedCard(BoxLayout):
    def __init__(self, bg_color=CARD_COLOR, radius=16, **kw):
        super().__init__(**kw)
        self._bg = bg_color
        self._r  = radius
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self._r])


class ResultRow(BoxLayout):
    def __init__(self, index, value, mode, **kw):
        super().__init__(orientation="horizontal",
                         size_hint_y=None, height=dp(44), **kw)
        bg = RESULT_ODD if index % 2 == 0 else RESULT_EVEN
        with self.canvas.before:
            Color(*bg)
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        accent = ACCENT if mode == "HIGH" else ACCENT2

        bar = BoxLayout(size_hint_x=None, width=dp(4))
        with bar.canvas:
            Color(*accent)
            self._bar_rect = Rectangle(pos=bar.pos, size=bar.size)
        bar.bind(pos=self._upd_bar, size=self._upd_bar)
        self._bar      = bar
        self._bar_clr  = accent

        lbl_n = Label(text=f"[{index}]",
                      size_hint_x=None, width=dp(50),
                      color=(*accent[:3], 0.8),
                      font_size=dp(13), bold=True, halign="center")
        lbl_v = Label(text=f"{value:.3f}",
                      color=TEXT_COLOR,
                      font_size=dp(15), bold=True, halign="left")

        self.add_widget(bar)
        self.add_widget(lbl_n)
        self.add_widget(lbl_v)

    def _upd_bar(self, w, *_):
        w.canvas.clear()
        with w.canvas:
            Color(*self._bar_clr)
            Rectangle(pos=w.pos, size=w.size)

    def _upd(self, *_):
        self._rect.pos  = self.pos
        self._rect.size = self.size


class HalfCycleLayout(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical",
                         padding=dp(16), spacing=dp(12), **kw)
        self._build()

    def _build(self):
        # ── العنوان ──
        title_card = RoundedCard(orientation="vertical",
                                 padding=dp(14), spacing=dp(4),
                                 size_hint_y=None, height=dp(70))
        title_card.add_widget(Label(text="Half Cycle Calculator",
                                    font_size=dp(20), bold=True,
                                    color=TEXT_COLOR))
        title_card.add_widget(Label(text="Gann Square of 9  •  180°",
                                    font_size=dp(12),
                                    color=(*ACCENT[:3], 0.8)))
        self.add_widget(title_card)

        # ── بطاقة المدخلات ──
        input_card = RoundedCard(orientation="vertical",
                                 padding=dp(14), spacing=dp(10),
                                 size_hint_y=None, height=dp(220))

        # HIGH / LOW
        mode_row = GridLayout(cols=2, spacing=dp(8),
                              size_hint_y=None, height=dp(46))
        self.btn_high = ToggleButton(
            text="▲  HIGH", group="mode", state="down",
            background_normal="", background_down="",
            background_color=ACCENT,
            color=TEXT_COLOR, bold=True, font_size=dp(14))
        self.btn_low = ToggleButton(
            text="▼  LOW", group="mode",
            background_normal="", background_down="",
            background_color=(0.15, 0.18, 0.28, 1),
            color=SUBTEXT_COLOR, bold=True, font_size=dp(14))
        self.btn_high.bind(on_press=lambda x: self._set_mode("HIGH"))
        self.btn_low.bind(on_press=lambda x: self._set_mode("LOW"))
        mode_row.add_widget(self.btn_high)
        mode_row.add_widget(self.btn_low)
        input_card.add_widget(mode_row)

        # Swing & Factor
        fields = GridLayout(cols=2, spacing=dp(10),
                            size_hint_y=None, height=dp(90))
        for lbl, hint, attr in [
                ("Swing  (السعر)",    "مثال: 690", "inp_swing"),
                ("Factor  (المعامل)", "مثال: 2",   "inp_factor")]:
            col = BoxLayout(orientation="vertical", spacing=dp(4))
            col.add_widget(Label(text=lbl, color=SUBTEXT_COLOR,
                                 font_size=dp(12),
                                 size_hint_y=None, height=dp(22),
                                 halign="left"))
            ti = TextInput(hint_text=hint, multiline=False,
                           input_filter="float",
                           background_color=(0.08, 0.08, 0.16, 1),
                           foreground_color=TEXT_COLOR,
                           hint_text_color=SUBTEXT_COLOR,
                           cursor_color=ACCENT,
                           font_size=dp(15),
                           padding=[dp(10), dp(10)])
            setattr(self, attr, ti)
            col.add_widget(ti)
            fields.add_widget(col)
        input_card.add_widget(fields)

        # عدد النتائج + زر الحساب
        bottom_row = GridLayout(cols=2, spacing=dp(10),
                                size_hint_y=None, height=dp(50))
        results_col = BoxLayout(orientation="vertical", spacing=dp(2))
        results_col.add_widget(Label(text="عدد النتائج",
                                     color=SUBTEXT_COLOR, font_size=dp(12),
                                     size_hint_y=None, height=dp(20)))
        self.spinner = Spinner(
            values=[str(i) for i in range(1, 51)],
            text="1",
            background_normal="", background_color=(0.08, 0.08, 0.16, 1),
            color=TEXT_COLOR, font_size=dp(14))
        results_col.add_widget(self.spinner)
        bottom_row.add_widget(results_col)

        self.calc_btn = Button(
            text="⚡  احسب",
            background_normal="", background_color=ACCENT,
            color=TEXT_COLOR, bold=True, font_size=dp(15))
        self.calc_btn.bind(on_press=self.calculate)
        bottom_row.add_widget(self.calc_btn)
        input_card.add_widget(bottom_row)
        self.add_widget(input_card)

        # ── شريط المعلومات ──
        self.info_lbl = Label(
            text="أدخل القيم ثم اضغط احسب",
            color=SUBTEXT_COLOR, font_size=dp(11),
            size_hint_y=None, height=dp(22))
        self.add_widget(self.info_lbl)

        # ── قائمة النتائج ──
        results_card = RoundedCard(orientation="vertical", padding=0, spacing=0)
        self.results_box = BoxLayout(orientation="vertical",
                                     size_hint_y=None, spacing=0)
        self.results_box.bind(minimum_height=self.results_box.setter("height"))
        sv = ScrollView(do_scroll_x=False)
        sv.add_widget(self.results_box)
        results_card.add_widget(sv)
        self.add_widget(results_card)

    def _set_mode(self, mode):
        if mode == "HIGH":
            self.btn_high.background_color = ACCENT
            self.btn_high.color = TEXT_COLOR
            self.btn_low.background_color  = (0.15, 0.18, 0.28, 1)
            self.btn_low.color = SUBTEXT_COLOR
        else:
            self.btn_low.background_color  = ACCENT2
            self.btn_low.color  = TEXT_COLOR
            self.btn_high.background_color = (0.15, 0.18, 0.28, 1)
            self.btn_high.color = SUBTEXT_COLOR

    def calculate(self, *_):
        self.results_box.clear_widgets()

        try:
            swing = float(self.inp_swing.text)
            assert swing > 0
        except:
            self.info_lbl.text  = "⚠  Swing يجب أن يكون رقماً موجباً"
            self.info_lbl.color = (0.95, 0.35, 0.35, 1)
            return

        try:
            factor = float(self.inp_factor.text)
            assert factor > 0
        except:
            self.info_lbl.text  = "⚠  Factor يجب أن يكون رقماً موجباً"
            self.info_lbl.color = (0.95, 0.35, 0.35, 1)
            return

        n          = int(self.spinner.text)
        mode       = "HIGH" if self.btn_high.state == "down" else "LOW"
        sqrt_swing = math.sqrt(swing)

        # ══════════════════════════════════════
        #  نصف دورة 180°
        #  HIGH  →  ( √Swing  −  Factor × i ) ²
        #  LOW   →  ( √Swing  +  Factor × i ) ²
        # ══════════════════════════════════════
        for i in range(1, n + 1):
            val    = (sqrt_swing - factor * i) if mode == "HIGH" \
                     else (sqrt_swing + factor * i)
            result = val ** 2 if val > 0 else 0.0
            self.results_box.add_widget(ResultRow(i, result, mode))

        formula = (f"(√{swing} − {factor}×n)²" if mode == "HIGH"
                   else f"(√{swing} + {factor}×n)²")
        self.info_lbl.text  = (f"✔  {n} نتيجة  |  {formula}"
                               f"  |  √Swing={sqrt_swing:.3f}")
        self.info_lbl.color = (*ACCENT2[:3], 1)


class HalfCycleApp(App):
    def build(self):
        self.title = "Half Cycle Calculator"
        return HalfCycleLayout()


if __name__ == "__main__":
    HalfCycleApp().run()
