# tos settings — lowercase, flat theme picker

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter
from theme import Colors, Fonts


PALETTES = {
    "red":    ("red",     (0x8B,0x00,0x00), (0xFF,0xD7,0x00), (0x5C,0x00,0x00)),
    "green":  ("green",   (0x00,0x22,0x00), (0x00,0xFF,0x00), (0x00,0x11,0x00)),
    "amber":  ("amber",   (0x11,0x0A,0x00), (0xFF,0xB0,0x00), (0x22,0x15,0x00)),
    "blue":   ("blue",    (0x00,0x00,0x44), (0x44,0x88,0xFF), (0x00,0x00,0x22)),
}


class Swatch(QWidget):
    def __init__(self, c, sz=24):
        super().__init__()
        self._c = c
        self.setFixedSize(sz, sz)

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), self._c)
        p.setPen(QColor(0, 0, 0))
        p.drawRect(0, 0, self.width()-1, self.height()-1)
        p.end()


class Settings(QWidget):
    changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cur = "red"
        self._build()

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0x5C, 0x00, 0x00))
        p.end()

    def _build(self):
        lo = QVBoxLayout(self)
        lo.setContentsMargins(10, 10, 10, 10)
        lo.setSpacing(6)

        t = QLabel("settings")
        t.setFont(Fonts.title())
        t.setStyleSheet("color: #FFD700; background: transparent; border-bottom: 1px solid #000;")
        lo.addWidget(t)
        lo.addSpacing(6)

        tl = QLabel("theme:")
        tl.setFont(Fonts.body())
        tl.setStyleSheet("color: #FFD700; background: transparent;")
        lo.addWidget(tl)

        self.nl = QLabel(PALETTES["red"][0])
        self.nl.setFont(Fonts.title())
        self.nl.setStyleSheet("color: #FFD700; background: transparent;")
        lo.addWidget(self.nl)

        lo.addSpacing(4)
        cl = QLabel("colors:")
        cl.setFont(Fonts.body())
        cl.setStyleSheet("color: #FFD700; background: transparent;")
        lo.addWidget(cl)

        self._sw = QWidget()
        self._sw.setStyleSheet("background: transparent;")
        self._slo = QHBoxLayout(self._sw)
        self._slo.setSpacing(4)
        self._rebuild()
        lo.addWidget(self._sw)

        lo.addSpacing(8)
        bl = QLabel("select:")
        bl.setFont(Fonts.body())
        bl.setStyleSheet("color: #FFD700; background: transparent;")
        lo.addWidget(bl)

        for k, (n, rb, ym, rd) in PALETTES.items():
            b = QPushButton("  " + n + "  ")
            b.setFont(Fonts.body())
            b.setFixedHeight(28)
            b.setStyleSheet(
                "QPushButton { background: #FFD700; color: #000; "
                "border: 1px solid #000; font-family: More Perfect DOS VGA; font-size: 12px; "
                "text-align: left; padding-left: 6px; }"
                "QPushButton:hover { background: #FFE44C; }")
            b.clicked.connect(lambda _, k=k: self._apply(k))
            lo.addWidget(b)

        lo.addStretch()
        f = QLabel("theme changes apply to new windows")
        f.setFont(Fonts.small())
        f.setStyleSheet("color: #CCAC00; background: transparent;")
        lo.addWidget(f)

    def _rebuild(self):
        while self._slo.count():
            it = self._slo.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        _, rb, ym, rd = PALETTES[self._cur]
        for c in [rb, ym, rd]:
            self._slo.addWidget(Swatch(QColor(*c), 24))
        self._slo.addStretch()

    def _apply(self, k):
        n, rb, ym, rd = PALETTES[k]
        self._cur = k
        self.nl.setText(n)
        self._rebuild()
        self.changed.emit(k)
        Colors.RED_BG = QColor(*rb)
        Colors.YELLOW_MAIN = QColor(*ym)
        Colors.RED_DARK = QColor(*rd)
        print(f"[settings] theme: {n}")
