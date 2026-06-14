# tos pong — 1 player vs wall, embedded Qt widget (no pygame)
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QFont

RED  = QColor(0x8B, 0x00, 0x00)
RED2 = QColor(0x5C, 0x00, 0x00)
YEL  = QColor(0xFF, 0xD7, 0x00)
YEL2 = QColor(0xCC, 0xAC, 0x00)
BLK  = QColor(0x00, 0x00, 0x00)

W, H = 480, 360
FPS = 60
PAD_W, PAD_H = 8, 50
BALL_S = 8


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
        self.px = 20
        self.py = H // 2 - PAD_H // 2
        self.bx, self.by = W // 2, H // 2
        self.bdx, self.bdy = 4, 3
        self.score = 0
        self.over = False
        self.update()

    def _tick(self):
        if self.over:
            return
        k = self._keys
        if Qt.Key_Up in k or Qt.Key_W in k:
            self.py -= 5
        if Qt.Key_Down in k or Qt.Key_S in k:
            self.py += 5
        self.py = max(0, min(H - PAD_H, self.py))

        self.bx += self.bdx
        self.by += self.bdy
        if self.by <= 0 or self.by >= H - BALL_S:
            self.bdy = -self.bdy
        if self.bx <= 0:
            self.over = True
            self.update()
            return
        if self.bx >= W:
            self.bdx = -self.bdx
            self.score += 1
        # paddle collision
        if self.bx <= self.px + PAD_W and self.by + BALL_S > self.py and self.by < self.py + PAD_H:
            self.bdx = -self.bdx
            self.bx = self.px + PAD_W
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
        # center dashed line
        p.setPen(RED2)
        for y in range(0, H, 20):
            p.drawLine(W // 2, y, W // 2, y + 10)
        # paddle
        p.fillRect(self.px, self.py, PAD_W, PAD_H, YEL)
        p.setPen(BLK); p.setBrush(Qt.NoBrush)
        p.drawRect(self.px, self.py, PAD_W - 1, PAD_H - 1)
        # ball
        p.fillRect(self.bx, self.by, BALL_S, BALL_S, YEL)
        p.setPen(BLK)
        p.drawRect(self.bx, self.by, BALL_S - 1, BALL_S - 1)
        # score + border
        p.setPen(YEL); p.setFont(_font(14))
        p.drawText(QRect(0, 4, W, 20), Qt.AlignCenter, f"score: {self.score}")
        p.setPen(YEL); p.drawRect(0, 0, W - 1, H - 1)
        # game over
        if self.over:
            p.fillRect(self.rect(), QColor(0, 0, 0, 150))
            p.setPen(YEL)
            p.setFont(_font(22, True))
            p.drawText(QRect(0, 100, W, 30), Qt.AlignCenter, "game over")
            p.setFont(_font(36, True))
            p.drawText(QRect(0, 150, W, 40), Qt.AlignCenter, str(self.score))
            p.setFont(_font(14))
            p.drawText(QRect(0, 220, W, 20), Qt.AlignCenter, "space=again   esc=close")
        p.end()
