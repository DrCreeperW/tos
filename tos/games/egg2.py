# egg2: fake loading — embedded Qt widget (no pygame)
import random

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QFont

W, H = 400, 200


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
        self.pct = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(60)

    def _tick(self):
        if self.pct < 100 and random.random() < 0.7:
            self.pct += 1
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0x5C, 0x00, 0x00))
        p.setPen(QColor(0xFF, 0xD7, 0x00))
        p.setFont(_font(14))
        p.drawText(QRect(0, 70, W, 20), Qt.AlignCenter, f"loading... {self.pct}%")
        # progress bar
        p.fillRect(100, 110, self.pct * 2, 10, QColor(0xFF, 0xD7, 0x00))
        p.setPen(QColor(0, 0, 0)); p.setBrush(Qt.NoBrush)
        p.drawRect(100, 110, 200, 10)
        p.end()
