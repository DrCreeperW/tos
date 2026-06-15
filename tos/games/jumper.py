# tos jumper — climbing platformer with menu (1P or 2P), embedded Qt widget
#
# Menu:     click a button or press 1/2 to choose mode
# Player 1 (yellow): Arrow keys — Left/Right to move, Up to jump
# Player 2 (amber):  WASD    — A/D to move, W to jump
# Single player: fall = game over.   Multiplayer: either falls = other wins.

import random

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont

RED  = QColor(0x8B, 0x00, 0x00)
RED2 = QColor(0x5C, 0x00, 0x00)
YEL  = QColor(0xFF, 0xD7, 0x00)   # player 1
AMB  = QColor(0xCC, 0xAC, 0x00)   # player 2 (amber)
AMB2 = QColor(0x88, 0x70, 0x00)   # player 2 shadow
BLK  = QColor(0x00, 0x00, 0x00)

W, H = 480, 480
FPS = 60
PW, PH = 18, 18
GRAV = 0.5
JUMP = -9
SPD = 5
GAP_MIN, GAP_MAX = 45, 65
H_REACH = 90

# menu button rectangles (centered)
BTN_W, BTN_H = 180, 40
BTN1 = QRect(W // 2 - BTN_W // 2, 220, BTN_W, BTN_H)
BTN2 = QRect(W // 2 - BTN_W // 2, 280, BTN_W, BTN_H)


def _font(sz, bold=False):
    f = QFont("More Perfect DOS VGA")
    f.setPixelSize(sz)
    f.setBold(bold)
    return f


def _hit(a, p):
    return (a.x < p['x'] + p['w'] and a.x + a.w > p['x'] and
            a.y < p['y'] + p['h'] and a.y + a.h > p['y'])


def _place_platform(prev_x_center):
    w = random.choice([70, 90, 110])
    shift = random.randint(-H_REACH, H_REACH)
    nc = prev_x_center + shift
    nc = max(w // 2, min(W - w // 2, nc))
    return {'x': nc - w // 2, 'w': w, 'h': 12}, nc


class Player:
    def __init__(self, x, y, color, shadow_color):
        self.x, self.y = x, y
        self.w, self.h = PW, PH
        self.vx = self.vy = 0
        self.on = False
        self.score = 0
        self.alive = True
        self.color = color
        self.shadow_color = shadow_color

    def update(self, plats):
        if not self.alive:
            self.vy += GRAV
            if self.vy > 12:
                self.vy = 12
            self.y += self.vy
            return
        self.vy += GRAV
        if self.vy > 12:
            self.vy = 12
        prev_y = self.y
        # horizontal
        self.x += self.vx
        for p in plats:
            if _hit(self, p):
                if self.vx > 0:
                    self.x = p['x'] - self.w
                elif self.vx < 0:
                    self.x = p['x'] + p['w']
        # vertical (one-way platforms)
        self.y += self.vy
        self.on = False
        for p in plats:
            if _hit(self, p):
                if self.vy > 0:
                    prev_bottom = prev_y + self.h
                    if prev_bottom <= p['y'] + 2:
                        self.y = p['y'] - self.h
                        self.vy = 0
                        self.on = True

    def jump(self):
        if self.alive and self.on:
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
        self._mode = "menu"          # "menu" or "playing"
        self._num_players = 1        # 1 or 2
        self.plats = make_plats()
        self.p1 = None
        self.p2 = None
        self.over = False
        self._hover = None           # which menu button is hovered
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000 // FPS)

    # ----------------------------------------------------------- game setup
    def _start_game(self, num_players):
        self._num_players = num_players
        self.plats = make_plats()
        # p1 (arrows) on the RIGHT, p2 (WASD) on the LEFT — matches keyboard
        self.p1 = Player(W - 100 - PW, H - 80, YEL, RED2)
        self.p2 = Player(100, H - 80, AMB, AMB2) if num_players == 2 else None
        self.over = False
        self._mode = "playing"
        self._keys.clear()
        self.setMouseTracking(False)
        self.update()

    def _back_to_menu(self):
        self._mode = "menu"
        self.over = False
        self._keys.clear()
        self.update()

    # ----------------------------------------------------------- game loop
    def _tick(self):
        if self._mode != "playing" or self.over:
            return
        k = self._keys

        # ---- Player 1: arrows (Left/Right/Up) ----
        self.p1.vx = 0
        if Qt.Key_Left in k:
            self.p1.vx = -SPD
        if Qt.Key_Right in k:
            self.p1.vx = SPD
        if Qt.Key_Up in k:
            self.p1.jump()

        # ---- Player 2: WASD (only in 2-player) ----
        if self.p2 is not None:
            self.p2.vx = 0
            if Qt.Key_A in k:
                self.p2.vx = -SPD
            if Qt.Key_D in k:
                self.p2.vx = SPD
            if Qt.Key_W in k:
                self.p2.jump()

        # ---- physics ----
        self.p1.update(self.plats)
        if self.p2 is not None:
            self.p2.update(self.plats)

        # ---- death checks ----
        if self.p1.dead():
            self.p1.alive = False
        if self.p2 is not None and self.p2.dead():
            self.p2.alive = False

        # single player: p1 falls = game over
        if self._num_players == 1:
            if not self.p1.alive:
                self.over = True
                self.update()
                return
        else:
            # multiplayer: either falls = game over
            if not self.p1.alive or not self.p2.alive:
                self.over = True
                self.update()
                return

        # ---- scrolling: based on the higher player (lower y) ----
        if self.p2 is not None:
            higher = self.p1 if self.p1.y <= self.p2.y else self.p2
        else:
            higher = self.p1
        if higher.y < H // 3 and higher.vy < 0:
            scroll = -higher.vy
            self.p1.y += scroll
            self.p1.score += int(scroll)
            if self.p2 is not None:
                self.p2.y += scroll
                self.p2.score += int(scroll)
            for pl in self.plats:
                pl['y'] += scroll
            self.plats = [pl for pl in self.plats if pl['y'] < H + 20]
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

    # ----------------------------------------------------------- input
    def keyPressEvent(self, e):
        # menu: 1 = single, 2 = multiplayer
        if self._mode == "menu":
            if e.key() == Qt.Key_1:
                self._start_game(1)
            elif e.key() == Qt.Key_2:
                self._start_game(2)
            return
        # playing
        self._keys.add(e.key())
        if self.over:
            if e.key() == Qt.Key_Space:
                self._start_game(self._num_players)   # replay same mode
            elif e.key() == Qt.Key_M:
                self._back_to_menu()

    def keyReleaseEvent(self, e):
        if e.isAutoRepeat():
            return
        self._keys.discard(e.key())

    def mousePressEvent(self, e):
        if self._mode != "menu":
            return
        pos = e.pos()
        if BTN1.contains(pos):
            self._start_game(1)
        elif BTN2.contains(pos):
            self._start_game(2)

    def mouseMoveEvent(self, e):
        if self._mode != "menu":
            return
        pos = e.pos()
        new_hover = None
        if BTN1.contains(pos):
            new_hover = 1
        elif BTN2.contains(pos):
            new_hover = 2
        if new_hover != self._hover:
            self._hover = new_hover
            self.update()

    # ----------------------------------------------------------- drawing
    def _draw_player(self, p, painter):
        px, py = int(p.x), int(p.y)
        painter.fillRect(px + 2, py + 2, PW, PH, p.shadow_color)
        painter.fillRect(px, py, PW, PH, p.color)
        painter.setPen(BLK); painter.setBrush(Qt.NoBrush)
        painter.drawRect(px, py, PW - 1, PH - 1)

    def _draw_menu(self, p):
        p.fillRect(self.rect(), RED)
        # grid
        p.setPen(RED2)
        for gx in range(0, W, 40):
            p.drawLine(gx, 0, gx, H)
        for gy in range(0, H, 40):
            p.drawLine(0, gy, W, gy)
        # title
        p.setPen(YEL)
        p.setFont(_font(36, True))
        p.drawText(QRect(0, 80, W, 50), Qt.AlignCenter, "jumper")
        p.setFont(_font(12))
        p.setPen(AMB)
        p.drawText(QRect(0, 150, W, 20), Qt.AlignCenter, "choose a mode")
        # buttons
        self._draw_button(p, BTN1, "1 player", self._hover == 1)
        self._draw_button(p, BTN2, "2 player", self._hover == 2)
        # hint
        p.setPen(AMB)
        p.setFont(_font(11))
        p.drawText(QRect(0, 360, W, 40), Qt.AlignCenter,
                   "click or press 1 / 2\nesc=close")

    def _draw_button(self, p, rect, label, hovered):
        bg = YEL if hovered else RED2
        fg = BLK if hovered else YEL
        p.fillRect(rect, bg)
        p.setPen(BLK); p.setBrush(Qt.NoBrush)
        p.drawRect(rect)
        p.setPen(fg)
        p.setFont(_font(16, True))
        p.drawText(rect, Qt.AlignCenter, label)

    def _draw_game(self, p):
        p.fillRect(self.rect(), RED)
        # grid
        p.setPen(RED2)
        for gx in range(0, W, 40):
            p.drawLine(gx, 0, gx, H)
        for gy in range(0, H, 40):
            p.drawLine(0, gy, W, gy)
        # platforms
        for pl in self.plats:
            x, y = int(pl['x']), int(pl['y'])
            w, h = int(pl['w']), int(pl['h'])
            p.fillRect(x, y, w, h, RED2)
            p.setPen(YEL);  p.drawLine(x, y, x + w - 1, y)
            p.setPen(BLK);  p.drawLine(x, y + h - 1, x + w - 1, y + h - 1)
            p.setPen(YEL);  p.drawLine(x, y, x, y + h - 1)
            p.setPen(BLK);  p.drawLine(x + w - 1, y, x + w - 1, y + h - 1)
        # players
        if self.p1 is not None:
            self._draw_player(self.p1, p)
        if self.p2 is not None:
            self._draw_player(self.p2, p)
        # scores — p1 on the right (matches arrows), p2 on the left (matches WASD)
        if self.p2 is not None:
            p.setPen(AMB); p.setFont(_font(14))
            p.drawText(8, 8, 120, 20, Qt.AlignLeft | Qt.AlignTop,
                       f"p2: {self.p2.score}")
        p.setPen(YEL); p.setFont(_font(14))
        p.drawText(W - 120, 8, 112, 20, Qt.AlignRight | Qt.AlignTop,
                   f"p1: {self.p1.score}" if self.p1 else "")
        # border
        p.setPen(YEL); p.drawRect(0, 0, W - 1, H - 1)

    def paintEvent(self, e):
        p = QPainter(self)
        if self._mode == "menu":
            self._draw_menu(p)
            p.end()
            return
        self._draw_game(p)
        # game over overlay
        if self.over:
            if self._num_players == 1:
                msg = "game over"
                detail = f"score: {self.p1.score}"
            else:
                if not self.p1.alive and not self.p2.alive:
                    msg = "both fell!"
                elif not self.p1.alive:
                    msg = "p2 wins!"
                else:
                    msg = "p1 wins!"
                detail = f"p1: {self.p1.score}   p2: {self.p2.score}"
            p.fillRect(self.rect(), QColor(0, 0, 0, 150))
            p.setPen(YEL)
            p.setFont(_font(22, True))
            p.drawText(QRect(0, 150, W, 30), Qt.AlignCenter, msg)
            p.setFont(_font(14))
            p.drawText(QRect(0, 200, W, 20), Qt.AlignCenter, detail)
            p.setFont(_font(14))
            p.drawText(QRect(0, 280, W, 20), Qt.AlignCenter,
                       "space=again   m=menu   esc=close")
        p.end()
