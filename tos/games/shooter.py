# tos shooter — move and shoot enemies, embedded Qt widget (no pygame)
import random

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QFont

RED  = QColor(0x8B, 0x00, 0x00)
RED2 = QColor(0x5C, 0x00, 0x00)
YEL  = QColor(0xFF, 0xD7, 0x00)
YEL2 = QColor(0xCC, 0xAC, 0x00)
BLK  = QColor(0x00, 0x00, 0x00)

W, H = 480, 400
FPS = 60
PW, PH = 30, 20


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
        self.px, self.py = W // 2, H - 50
        self.bullets = []   # [x, y]
        self.enemies = []   # [cx, cy, w, h]
        self.score = 0
        self.timer = 0
        self.cooldown = 0
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
        if Qt.Key_Space in k or Qt.Key_Up in k:
            if self.cooldown <= 0:
                self.bullets.append([self.px + PW // 2 - 2, self.py - 10])
                self.cooldown = 12
        self.px = max(PW // 2, min(W - PW // 2, self.px))
        if self.cooldown > 0:
            self.cooldown -= 1

        for b in self.bullets[:]:
            b[1] -= 6
            if b[1] < 0:
                self.bullets.remove(b)

        self.timer += 1
        if self.timer % 25 == 0:
            ex = random.randint(20, W - 20)
            self.enemies.append([ex, 0, 15, 15])

        for e2 in self.enemies[:]:
            e2[1] += 2
            if e2[1] > H:
                self.enemies.remove(e2)
            elif (abs(e2[0] - self.px) < e2[2] + PW // 2 and
                  abs(e2[1] - self.py) < e2[3] + PH // 2):
                self.over = True
                self.update()
                return

        for b in self.bullets[:]:
            for e2 in self.enemies[:]:
                if abs(b[0] - e2[0]) < e2[2] and abs(b[1] - e2[1]) < e2[3]:
                    self.bullets.remove(b)
                    self.enemies.remove(e2)
                    self.score += 1
                    break
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
        # enemies (centered)
        for cx, cy, ew, eh in self.enemies:
            r = QRect(cx - ew // 2, cy - eh // 2, ew, eh)
            p.fillRect(r, YEL2)
            p.setPen(BLK); p.setBrush(Qt.NoBrush)
            p.drawRect(r)
        # bullets
        for bx, by in self.bullets:
            p.fillRect(bx, by, 4, 8, YEL)
        # player (centered)
        pr = QRect(self.px - PW // 2, self.py - PH // 2, PW, PH)
        p.fillRect(pr, YEL)
        p.setPen(BLK); p.setBrush(Qt.NoBrush)
        p.drawRect(pr)
        # score + border
        p.setPen(YEL); p.setFont(_font(14))
        p.drawText(8, 8, 200, 20, Qt.AlignLeft | Qt.AlignTop, f"score: {self.score}")
        p.setPen(YEL); p.drawRect(0, 0, W - 1, H - 1)
        # game over
        if self.over:
            p.fillRect(self.rect(), QColor(0, 0, 0, 150))
            p.setPen(YEL)
            p.setFont(_font(22, True))
            p.drawText(QRect(0, 130, W, 30), Qt.AlignCenter, "game over")
            p.setFont(_font(36, True))
            p.drawText(QRect(0, 180, W, 40), Qt.AlignCenter, str(self.score))
            p.setFont(_font(14))
            p.drawText(QRect(0, 250, W, 20), Qt.AlignCenter, "space=again   esc=close")
        p.end()
