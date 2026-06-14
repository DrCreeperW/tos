# egg ya — cryptic "y & a" message, embedded Qt widget (no pygame)
import random

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QFont

W, H = 400, 300


def _font(sz, bold=False):
    f = QFont("More Perfect DOS VGA")
    f.setPixelSize(sz)
    f.setBold(bold)
    return f


class Game(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(W, H)
        self.setFocusPolicy(Qt.StrongFocus)
        self.t = 0
        self._dots = []   # list of (x, y, QColor)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(100)   # ~10 fps like the original

    def _tick(self):
        self.t += 1
        self._dots = []
        for _ in range(20):
            dx = random.randint(0, W)
            dy = random.randint(0, H)
            c = QColor(0xFF, 0xD7, 0x00) if random.random() > 0.5 else QColor(0xCC, 0xAC, 0x00)
            self._dots.append((dx, dy, c))
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0x5C, 0x00, 0x00))
        # flicker text
        if self.t % 15 < 12:
            p.setPen(QColor(0xFF, 0xD7, 0x00))
            p.setFont(_font(48, True))
            p.drawText(QRect(0, 96, W, 48), Qt.AlignCenter, "y & a")
        # random dots
        for dx, dy, c in self._dots:
            p.setPen(c)
            p.drawPoint(dx, dy)
        p.setPen(QColor(0xCC, 0xAC, 0x00))
        p.setFont(_font(14))
        p.drawText(QRect(0, 230, W, 20), Qt.AlignCenter, "press esc to close")
        p.end()
