# egg4: nope — embedded Qt widget (no pygame)
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect
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

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0x8B, 0x00, 0x00))
        p.setPen(QColor(0xFF, 0xD7, 0x00))
        p.setFont(_font(48, True))
        p.drawText(QRect(0, 50, W, 60), Qt.AlignCenter, "nope")
        p.setPen(QColor(0xCC, 0xAC, 0x00))
        p.setFont(_font(14))
        p.drawText(QRect(0, 140, W, 20), Qt.AlignCenter, "press esc to close")
        p.end()
