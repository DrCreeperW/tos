# tos jumper — 2d platformer, embedded Qt widget (no pygame)
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
FPS = 60
PW, PH = 18, 18
GRAV = 0.5
JUMP = -9          # jump height ~76px
SPD = 5
GAP_MIN, GAP_MAX = 45, 65   # vertical distance between platforms
H_REACH = 90                 # max horizontal shift between consecutive platforms
# (full jump reach is ~180px; keeping shift <= 90 guarantees reachability
#  even with player reaction delay)


def _font(sz, bold=False):
    f = QFont("More Perfect DOS VGA")
    f.setPixelSize(sz)
    f.setBold(bold)
    return f


def _hit(a, p):
    """AABB overlap between player `a` (x,y,w,h) and platform dict `p`."""
    return (a.x < p['x'] + p['w'] and a.x + a.w > p['x'] and
            a.y < p['y'] + p['h'] and a.y + a.h > p['y'])


def _place_platform(prev_x_center):
    """Build one platform whose center is within H_REACH of prev_x_center.

    Guarantees every platform is horizontally reachable from the one below,
    so no layout is ever unplayable.
    """
    w = random.choice([70, 90, 110])
    shift = random.randint(-H_REACH, H_REACH)
    nc = prev_x_center + shift
    nc = max(w // 2, min(W - w // 2, nc))
    return {'x': nc - w // 2, 'w': w, 'h': 12}, nc


class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.w, self.h = PW, PH
        self.vx = self.vy = 0
        self.on = False
        self.score = 0

    def update(self, plats):
        self.vy += GRAV
        if self.vy > 12:
            self.vy = 12
        prev_y = self.y          # remember position before vertical move
        # horizontal
        self.x += self.vx
        for p in plats:
            if _hit(self, p):
                if self.vx > 0:
                    self.x = p['x'] - self.w
                elif self.vx < 0:
                    self.x = p['x'] + p['w']
        # vertical
        self.y += self.vy
        self.on = False
        # ONE-WAY platforms: only land on a platform when falling onto its top
        # (prev bottom was above the platform top). Lets the player jump up
        # through platforms instead of bonking their head.
        for p in plats:
            if _hit(self, p):
                if self.vy > 0:
                    prev_bottom = prev_y + self.h
                    if prev_bottom <= p['y'] + 2:
                        self.y = p['y'] - self.h
                        self.vy = 0
                        self.on = True

    def jump(self):
        if self.on:
            self.vy = JUMP

    def dead(self):
        return self.y > H + 50


def make_plats():
    plats = [{'x': 0, 'y': H - 20, 'w': W, 'h': 14}]
    prev_cx = W // 2
    prev_y = H - 20
    for _ in range(15):
        ny = prev_y - random.randint(GAP_MIN, GAP_MAX)
        if ny < 20:
            break
        pl, prev_cx = _place_platform(prev_cx)
        pl['y'] = ny
        plats.append(pl)
        prev_y = ny
    return plats


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
        self.plats = make_plats()
        self.p = Player(100, H - 80)
        self.over = False
        self.update()

    def _tick(self):
        if self.over:
            return
        k = self._keys
        self.p.vx = 0
        if Qt.Key_Left in k or Qt.Key_A in k:
            self.p.vx = -SPD
        if Qt.Key_Right in k or Qt.Key_D in k:
            self.p.vx = SPD
        if Qt.Key_Space in k or Qt.Key_Up in k or Qt.Key_W in k:
            self.p.jump()

        self.p.update(self.plats)
        if self.p.dead():
            self.over = True
            self.update()
            return

        # scroll up when climbing past the top third
        if self.p.y < H // 3 and self.p.vy < 0:
            scroll = -self.p.vy
            self.p.y += scroll
            self.p.score += int(scroll)   # score = total distance climbed
            for pl in self.plats:
                pl['y'] += scroll
            self.plats = [pl for pl in self.plats if pl['y'] < H + 20]
            # recycle platforms at the top, each within reach of the one below
            while True:
                topmost = min(self.plats, key=lambda p: p['y'])
                ny = topmost['y'] - random.randint(GAP_MIN, GAP_MAX)
                if ny < 20:
                    break
                prev_cx = topmost['x'] + topmost['w'] // 2
                pl, _ = _place_platform(prev_cx)
                pl['y'] = ny
                self.plats.append(pl)
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
        # grid
        p.setPen(RED2)
        for gx in range(0, W, 40):
            p.drawLine(gx, 0, gx, H)
        for gy in range(0, H, 40):
            p.drawLine(0, gy, W, gy)
        # platforms (platform y can drift to a float during scrolling, so
        # cast all coords to int — QPainter.fillRect needs ints)
        for pl in self.plats:
            x, y = int(pl['x']), int(pl['y'])
            w, h = int(pl['w']), int(pl['h'])
            p.fillRect(x, y, w, h, RED2)
            p.setPen(YEL2); p.drawLine(x, y, x + w - 1, y)
            p.setPen(BLK);  p.drawLine(x, y + h - 1, x + w - 1, y + h - 1)
            p.setPen(YEL2); p.drawLine(x, y, x, y + h - 1)
            p.setPen(BLK);  p.drawLine(x + w - 1, y, x + w - 1, y + h - 1)
        # player (x/y are floats from physics -> cast to int for drawing)
        px, py = int(self.p.x), int(self.p.y)
        p.fillRect(px + 2, py + 2, PW, PH, RED2)
        p.fillRect(px, py, PW, PH, YEL)
        p.setPen(BLK); p.setBrush(Qt.NoBrush)
        p.drawRect(px, py, PW - 1, PH - 1)
        # score + border
        p.setPen(YEL); p.setFont(_font(14))
        p.drawText(8, 8, 200, 20, Qt.AlignLeft | Qt.AlignTop, f"score: {self.p.score}")
        p.setPen(YEL); p.drawRect(0, 0, W - 1, H - 1)
        # game over
        if self.over:
            p.fillRect(self.rect(), QColor(0, 0, 0, 150))
            p.setPen(YEL)
            p.setFont(_font(22, True))
            p.drawText(QRect(0, 160, W, 30), Qt.AlignCenter, "game over")
            p.setFont(_font(36, True))
            p.drawText(QRect(0, 210, W, 40), Qt.AlignCenter, str(self.p.score))
            p.setFont(_font(14))
            p.drawText(QRect(0, 280, W, 20), Qt.AlignCenter, "space=again   esc=close")
        p.end()
