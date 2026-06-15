# tos pong — player vs AI, embedded Qt widget (no pygame)
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
AI_SPEED = 4           # slightly slower than ball so the AI is beatable
WIN_SCORE = 7


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
        # player paddle (left)
        self.px = 20
        self.py = H // 2 - PAD_H // 2
        # AI paddle (right)
        self.ax = W - 20 - PAD_W
        self.ay = H // 2 - PAD_H // 2
        # ball
        self.bx, self.by = W // 2, H // 2
        self.bdx, self.bdy = 4, 3
        # scores
        self.pscore = 0
        self.ascore = 0
        self.over = False
        self.update()

    def _reset_ball(self, towards_player=False):
        """Centre the ball, send it toward the loser of the last point."""
        self.bx, self.by = W // 2, H // 2
        self.bdy = 3 if self.by % 2 == 0 else -3
        self.bdx = -4 if towards_player else 4

    def _tick(self):
        if self.over:
            return
        k = self._keys

        # ---- player paddle (Up/Down) ----
        if Qt.Key_Up in k:
            self.py -= 5
        if Qt.Key_Down in k:
            self.py += 5
        self.py = max(0, min(H - PAD_H, self.py))

        # ---- AI paddle: track the ball, but capped at AI_SPEED ----
        paddle_center = self.ay + PAD_H // 2
        if self.bdx > 0:   # only chase when ball is coming toward AI
            if self.by < paddle_center - 5:
                self.ay -= AI_SPEED
            elif self.by > paddle_center + 5:
                self.ay += AI_SPEED
        self.ay = max(0, min(H - PAD_H, self.ay))

        # ---- ball movement ----
        self.bx += self.bdx
        self.by += self.bdy
        if self.by <= 0 or self.by >= H - BALL_S:
            self.bdy = -self.bdy

        # player scores (ball passes AI)
        if self.bx >= W:
            self.pscore += 1
            if self.pscore >= WIN_SCORE:
                self.over = True
                self.update()
                return
            self._reset_ball(towards_player=True)
            return

        # AI scores (ball passes player)
        if self.bx <= 0:
            self.ascore += 1
            if self.ascore >= WIN_SCORE:
                self.over = True
                self.update()
                return
            self._reset_ball(towards_player=False)
            return

        # ---- paddle collisions ----
        # player paddle (left)
        if (self.bx <= self.px + PAD_W and self.bx + BALL_S >= self.px and
                self.by + BALL_S > self.py and self.by < self.py + PAD_H):
            self.bdx = abs(self.bdx)
            self.bx = self.px + PAD_W
        # AI paddle (right)
        if (self.bx + BALL_S >= self.ax and self.bx <= self.ax + PAD_W and
                self.by + BALL_S > self.ay and self.by < self.ay + PAD_H):
            self.bdx = -abs(self.bdx)
            self.bx = self.ax - BALL_S

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
        # player paddle (left, yellow)
        p.fillRect(self.px, self.py, PAD_W, PAD_H, YEL)
        p.setPen(BLK); p.setBrush(Qt.NoBrush)
        p.drawRect(self.px, self.py, PAD_W - 1, PAD_H - 1)
        # AI paddle (right, amber/dim)
        p.fillRect(self.ax, self.ay, PAD_W, PAD_H, YEL2)
        p.drawRect(self.ax, self.ay, PAD_W - 1, PAD_H - 1)
        # ball
        p.fillRect(self.bx, self.by, BALL_S, BALL_S, YEL)
        p.drawRect(self.bx, self.by, BALL_S - 1, BALL_S - 1)
        # scores
        p.setPen(YEL); p.setFont(_font(18, True))
        p.drawText(QRect(0, 4, W // 2, 30), Qt.AlignCenter, str(self.pscore))
        p.drawText(QRect(W // 2, 4, W // 2, 30), Qt.AlignCenter, str(self.ascore))
        p.setPen(YEL2); p.setFont(_font(10))
        p.drawText(QRect(0, 4, W // 2, 14), Qt.AlignLeft, "you")
        p.drawText(QRect(W // 2, 4, W // 2, 14), Qt.AlignRight, "ai")
        # border
        p.setPen(YEL); p.drawRect(0, 0, W - 1, H - 1)
        # game over
        if self.over:
            p.fillRect(self.rect(), QColor(0, 0, 0, 150))
            p.setPen(YEL)
            won = self.pscore >= WIN_SCORE
            p.setFont(_font(22, True))
            p.drawText(QRect(0, 110, W, 30), Qt.AlignCenter,
                       "you win!" if won else "ai wins!")
            p.setFont(_font(36, True))
            p.drawText(QRect(0, 160, W, 40), Qt.AlignCenter,
                       f"{self.pscore} - {self.ascore}")
            p.setFont(_font(14))
            p.drawText(QRect(0, 230, W, 20), Qt.AlignCenter,
                       "space=again   esc=close")
        p.end()
