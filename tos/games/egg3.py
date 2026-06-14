# egg3: beep machine — embedded Qt widget (no pygame)
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QFont

W, H = 400, 200
NOTES = ["beep", "boop", "bip", "bop", "baap"]


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
        self.i = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(250)   # ~4 fps like the original

    def _tick(self):
        self.i += 1
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0x5C, 0x00, 0x00))
        p.setPen(QColor(0xFF, 0xD7, 0x00))
        p.setFont(_font(14))
        p.drawText(QRect(0, 80, W, 20), Qt.AlignCenter, NOTES[self.i % len(NOTES)])
        p.end()
