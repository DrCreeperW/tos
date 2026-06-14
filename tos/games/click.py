# tos click — click targets before they disappear, embedded Qt widget (no pygame)
import random

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QFont, QCursor


RED  = QColor(0x8B, 0x00, 0x00)
YEL  = QColor(0xFF, 0xD7, 0x00)
YEL2 = QColor(0xCC, 0xAC, 0x00)
BLK  = QColor(0x00, 0x00, 0x00)

W, H = 480, 400
FPS = 60


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
        self.setCursor(Qt.CrossCursor)
        self._reset()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000 // FPS)

    def _reset(self):
        self.targets = []   # [x, y, size, ttl]
        self.score = 0
        self.lives = 3
        self.timer = 0
        self.over = False
        self.update()

    def _tick(self):
        if self.over:
            return
        self.timer += 1
        if self.timer % 30 == 0 and len(self.targets) < 5:
            sz = random.randint(16, 32)
            self.targets.append([random.randint(sz, W - sz),
                                 random.randint(sz, H - sz), sz, 60])
        for t in self.targets[:]:
            t[3] -= 1
            if t[3] <= 0:
                self.targets.remove(t)
                self.lives -= 1
                if self.lives <= 0:
                    self.over = True
                    self.update()
                    return
        self.update()

    def mousePressEvent(self, e):
        if self.over:
            return
        if e.button() == Qt.LeftButton:
            mx, my = e.pos().x(), e.pos().y()
            hit = False
            for t in self.targets[:]:
                tx, ty, ts, _ = t
                if abs(mx - tx) < ts and abs(my - ty) < ts:
                    self.targets.remove(t)
                    self.score += 1
                    hit = True
                    break
            if not hit:
                self.lives -= 1
                if self.lives <= 0:
                    self.over = True
                    self.update()
            else:
                self.update()

    def keyPressEvent(self, e):
        if self.over and e.key() == Qt.Key_Space:
            self._reset()

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), RED)
        for tx, ty, ts, tt in self.targets:
            fade = 60 - tt
            if fade < 30:
                c = QColor(max(0, 200 - fade * 2), max(0, 180 - fade), 0)
            else:
                c = YEL2
            r = QRect(tx - ts // 2, ty - ts // 2, ts, ts)
            p.fillRect(r, c)
            p.setPen(BLK); p.setBrush(Qt.NoBrush)
            p.drawRect(r)
        p.setPen(YEL); p.setFont(_font(14))
        p.drawText(8, 8, 240, 20, Qt.AlignLeft | Qt.AlignTop,
                   f"score: {self.score}  lives: {self.lives}")
        p.setPen(YEL); p.drawRect(0, 0, W - 1, H - 1)
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
