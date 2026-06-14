# tos snake — classic snake game, embedded Qt widget (no pygame)
import random

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QFont

RED  = QColor(0x8B, 0x00, 0x00)
RED2 = QColor(0x5C, 0x00, 0x00)
YEL  = QColor(0xFF, 0xD7, 0x00)
YEL2 = QColor(0xCC, 0xAC, 0x00)
BLK  = QColor(0x00, 0x00, 0x00)

W, H = 480, 480
CELL = 16
COLS = W // CELL
ROWS = H // CELL
FPS = 8


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
        self._reset()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000 // FPS)

    def _reset(self):
        self.snake = [(COLS // 2, ROWS // 2)]
        self.dx, self.dy = 1, 0
        self.food = self._rand_cell()
        self.score = 0
        self.over = False
        self.update()

    def _rand_cell(self):
        return (random.randrange(COLS), random.randrange(ROWS))

    def _tick(self):
        if self.over:
            return
        hx, hy = self.snake[0]
        nx, ny = hx + self.dx, hy + self.dy
        if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS or (nx, ny) in self.snake:
            self.over = True
            self.update()
            return
        self.snake.insert(0, (nx, ny))
        if (nx, ny) == self.food:
            self.score += 1
            self.food = self._rand_cell()
        else:
            self.snake.pop()
        self.update()

    def keyPressEvent(self, e):
        k = e.key()
        if self.over:
            if k == Qt.Key_Space:
                self._reset()
            return
        if k in (Qt.Key_Left, Qt.Key_A) and self.dx != 1:
            self.dx, self.dy = -1, 0
        elif k in (Qt.Key_Right, Qt.Key_D) and self.dx != -1:
            self.dx, self.dy = 1, 0
        elif k in (Qt.Key_Up, Qt.Key_W) and self.dy != 1:
            self.dx, self.dy = 0, -1
        elif k in (Qt.Key_Down, Qt.Key_S) and self.dy != -1:
            self.dx, self.dy = 0, 1

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), RED)
        # grid
        p.setPen(RED2)
        for gx in range(0, W, CELL):
            p.drawLine(gx, 0, gx, H)
        for gy in range(0, H, CELL):
            p.drawLine(0, gy, W, gy)
        # snake
        for x, y in self.snake:
            r = QRect(x * CELL + 1, y * CELL + 1, CELL - 2, CELL - 2)
            p.fillRect(r, YEL)
            p.setPen(BLK)
            p.drawRect(r)
        # food
        fx, fy = self.food
        p.fillRect(QRect(fx * CELL + 2, fy * CELL + 2, CELL - 4, CELL - 4), YEL2)
        # score + border
        p.setPen(YEL)
        p.setFont(_font(14))
        p.drawText(8, 8, 200, 20, Qt.AlignLeft | Qt.AlignTop, f"score: {self.score}")
        p.setPen(YEL)
        p.setBrush(Qt.NoBrush)
        p.drawRect(0, 0, W - 1, H - 1)
        # game over
        if self.over:
            p.fillRect(self.rect(), QColor(0, 0, 0, 150))
            p.setPen(YEL)
            p.setFont(_font(22, True))
            p.drawText(QRect(0, 150, W, 30), Qt.AlignCenter, "game over")
            p.setFont(_font(36, True))
            p.drawText(QRect(0, 200, W, 40), Qt.AlignCenter, str(self.score))
            p.setFont(_font(14))
            p.drawText(QRect(0, 280, W, 20), Qt.AlignCenter, "space=again   esc=close")
        p.end()
