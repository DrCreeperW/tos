# tos dodge — avoid falling blocks, embedded Qt widget (no pygame)
import random

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QFont

RED  = QColor(0x8B, 0x00, 0x00)
YEL  = QColor(0xFF, 0xD7, 0x00)
YEL2 = QColor(0xCC, 0xAC, 0x00)
BLK  = QColor(0x00, 0x00, 0x00)

W, H = 400, 500
FPS = 60
PW = 30
PH = 20


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
        self._keys = set()
        self._reset()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000 // FPS)

    def _reset(self):
        self.px = W // 2 - PW // 2
        self.py = H - 50
        self.blocks = []
        self.score = 0
        self.timer = 0
        self.over = False
        self.update()

    def _tick(self):
        if self.over:
            return
        k = self._keys
        if Qt.Key_Left in k or Qt.Key_A in k:
            self.px -= 5
        if Qt.Key_Right in k or Qt.Key_D in k:
            self.px += 5
        self.px = max(0, min(W - PW, self.px))

        self.timer += 1
        if self.timer % 20 == 0:
            bw = random.randint(15, 40)
            bx = random.randint(0, W - bw)
            self.blocks.append([bx, 0, bw, 15])

        for b in self.blocks[:]:
            b[1] += 3 + self.score // 10
            if b[1] > H:
                self.blocks.remove(b)
                self.score += 1
            elif (self.px < b[0] + b[2] and self.px + PW > b[0] and
                  self.py < b[1] + b[3] and self.py + PH > b[1]):
                self.over = True
                self.update()
                return
        self.update()

    def keyPressEvent(self, e):
        self._keys.add(e.key())
        if self.over and e.key() == Qt.Key_Space:
            self._reset()

    def keyReleaseEvent(self, e):
        if e.isAutoRepeat():
            return
        self._keys.discard(e.key())

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), RED)
        # blocks
        for b in self.blocks:
            r = QRect(b[0], b[1], b[2], b[3])
            p.fillRect(r, YEL2)
            p.setPen(BLK); p.setBrush(Qt.NoBrush)
            p.drawRect(r)
        # player
        p.fillRect(self.px, self.py, PW, PH, YEL)
        p.setPen(BLK)
        p.drawRect(self.px, self.py, PW - 1, PH - 1)
        # score + border
        p.setPen(YEL); p.setFont(_font(14))
        p.drawText(8, 8, 200, 20, Qt.AlignLeft | Qt.AlignTop, f"score: {self.score}")
        p.setPen(YEL); p.drawRect(0, 0, W - 1, H - 1)
        # game over
        if self.over:
            p.fillRect(self.rect(), QColor(0, 0, 0, 150))
            p.setPen(YEL)
            p.setFont(_font(22, True))
            p.drawText(QRect(0, 160, W, 30), Qt.AlignCenter, "game over")
            p.setFont(_font(36, True))
            p.drawText(QRect(0, 210, W, 40), Qt.AlignCenter, str(self.score))
            p.setFont(_font(14))
            p.drawText(QRect(0, 280, W, 20), Qt.AlignCenter, "space=again   esc=close")
        p.end()
