# egg1: why are you here — embedded Qt widget (no pygame)
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
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

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0x5C, 0x00, 0x00))
        p.setPen(QColor(0xFF, 0xD7, 0x00))
        p.setFont(_font(14))
        p.drawText(self.rect(), Qt.AlignCenter, "why are you here?")
        p.end()
