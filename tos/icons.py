# tos icons — pixel-art icons for desktop shortcuts
#
# Each icon is drawn with QPainter in the TOS retro style (yellow + black
# on dark red). No external image files — everything is generated in code.
#
# Use:  from icons import draw_icon
#       draw_icon(name, painter, x, y)  # draws a 40x40 icon

from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRect

# palette
YEL = QColor(0xFF, 0xD7, 0x00)
YEL2 = QColor(0xCC, 0xAC, 0x00)
BLK = QColor(0x00, 0x00, 0x00)
DRK = QColor(0x3A, 0x00, 0x00)

ICON_SIZE = 40


def _px(painter, x, y, w, h, color):
    """Draw a filled pixel block."""
    painter.fillRect(x, y, w, h, color)


# ---- individual icon drawers ----
# Each draws into a 40x40 area at (ox, oy). Scaled by CELL=4 so a 10x10 grid.

def _terminal(p, ox, oy):
    # > prompt + cursor block
    c = 4
    p.setPen(QPen(YEL, 2))
    p.drawLine(ox + c*1, oy + c*2, ox + c*4, oy + c*5)
    p.drawLine(ox + c*1, oy + c*8, ox + c*4, oy + c*5)
    _px(p, ox + c*6, oy + c*7, c*2, c*2, YEL)

def _files(p, ox, oy):
    # folder shape
    c = 4
    _px(p, ox + c*1, oy + c*2, c*4, c*1, YEL)
    _px(p, ox + c*1, oy + c*3, c*1, c*1, YEL)
    _px(p, ox + c*4, oy + c*3, c*1, c*1, YEL)
    _px(p, ox + c*1, oy + c*3, c*8, c*6, YEL)
    _px(p, ox + c*2, oy + c*4, c*6, c*4, DRK)
    # underline
    p.setPen(QPen(BLK, 1))
    p.drawRect(ox + c*1, oy + c*2, c*8-1, c*7-1)

def _settings(p, ox, oy):
    # gear = circle with notches + center hole
    cx, cy, r = ox + 20, oy + 20, 12
    p.setPen(QPen(YEL, 3))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(cx - r, cy - r, r * 2, r * 2)
    # notches
    for ang in range(0, 360, 45):
        import math
        rx = cx + math.cos(math.radians(ang)) * (r - 2)
        ry = cy + math.sin(math.radians(ang)) * (r - 2)
        ex = cx + math.cos(math.radians(ang)) * (r + 4)
        ey = cy + math.sin(math.radians(ang)) * (r + 4)
        p.drawLine(int(rx), int(ry), int(ex), int(ey))
    # center hole
    p.setBrush(DRK)
    p.setPen(QPen(BLK, 1))
    p.drawEllipse(cx - 3, cy - 3, 6, 6)

def _calc(p, ox, oy):
    # calculator grid
    c = 4
    for row in range(3):
        for col in range(3):
            _px(p, ox + c + col * (c*2 + 1), oy + c + row * (c*2 + 1),
                c*2, c*2, YEL)
    # = bar at bottom
    _px(p, ox + c, oy + c + 3 * (c*2 + 1), c*7, c*2, YEL2)

def _clock(p, ox, oy):
    cx, cy = ox + 20, oy + 20
    p.setPen(QPen(YEL, 3))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(cx - 13, cy - 13, 26, 26)
    # hands
    p.drawLine(cx, cy, cx, cy - 8)
    p.drawLine(cx, cy, cx + 6, cy + 2)

def _notepad(p, ox, oy):
    # document with lines
    c = 4
    p.setPen(QPen(YEL, 1))
    p.setBrush(DRK)
    p.drawRect(ox + c, oy + c, c*8, c*9)
    p.setPen(QPen(YEL, 2))
    p.drawLine(ox + c*2, oy + c*3, ox + c*7, oy + c*3)
    p.drawLine(ox + c*2, oy + c*5, ox + c*7, oy + c*5)
    p.drawLine(ox + c*2, oy + c*7, ox + c*5, oy + c*7)

def _paint(p, ox, oy):
    # brush + palette
    c = 4
    # palette blob
    p.setPen(QPen(BLK, 1))
    p.setBrush(YEL)
    p.drawEllipse(ox + c*2, oy + c*4, c*5, c*4)
    # brush handle (diagonal)
    p.setPen(QPen(YEL2, 3))
    p.drawLine(ox + c*6, oy + c*2, ox + c*9, oy + c*1)
    # brush tip
    p.setPen(QPen(BLK, 1))
    p.setBrush(YEL)
    p.drawEllipse(ox + c*6 - 2, oy + c*2 - 2, 5, 5)

def _snake(p, ox, oy):
    # S-shaped snake body + head
    c = 4
    _px(p, ox + c*1, oy + c*2, c*2, c*2, YEL)
    _px(p, ox + c*3, oy + c*2, c*2, c*2, YEL)
    _px(p, ox + c*5, oy + c*2, c*2, c*2, YEL)
    _px(p, ox + c*5, oy + c*4, c*2, c*2, YEL)
    _px(p, ox + c*5, oy + c*6, c*2, c*2, YEL)
    _px(p, ox + c*3, oy + c*6, c*2, c*2, YEL)
    # head (bigger)
    _px(p, ox + c*1, oy + c*6, c*2, c*2, YEL2)
    # eye
    _px(p, ox + c*1, oy + c*6, 2, 2, BLK)

def _jumper(p, ox, oy):
    # little guy jumping on a platform
    c = 4
    # platform
    _px(p, ox + c*2, oy + c*8, c*6, c*1, YEL)
    # body
    _px(p, ox + c*4, oy + c*3, c*2, c*3, YEL)
    # legs spread (jumping)
    p.setPen(QPen(YEL, 2))
    p.drawLine(ox + c*4, oy + c*6, ox + c*2, oy + c*7)
    p.drawLine(ox + c*6, oy + c*6, ox + c*8, oy + c*7)
    # arms up
    p.drawLine(ox + c*4, oy + c*3, ox + c*2, oy + c*2)
    p.drawLine(ox + c*6, oy + c*3, ox + c*8, oy + c*2)

def _generic(p, ox, oy):
    # fallback: question mark in a box
    c = 4
    p.setPen(QPen(YEL, 1))
    p.setBrush(DRK)
    p.drawRect(ox + c, oy + c, c*8, c*8)
    p.setPen(QPen(YEL, 2))
    # question mark shape
    p.drawLine(ox + c*3, oy + c*3, ox + c*5, oy + c*3)
    p.drawLine(ox + c*5, oy + c*3, ox + c*5, oy + c*5)
    p.drawLine(ox + c*5, oy + c*5, ox + c*4, oy + c*6)
    _px(p, ox + c*4, oy + c*8, 2, 2, YEL)


# ---- registry ----
_ICONS = {
    "terminal": _terminal,
    "files":    _files,
    "settings": _settings,
    "calc":     _calc,
    "clock":    _clock,
    "notepad":  _notepad,
    "paint":    _paint,
    "snake":    _snake,
    "jumper":   _jumper,
    # games
    "pong":     _clock,     # reuse clock-like circle
    "dodge":    _generic,
    "click":    _generic,
    "shooter":  _generic,
}


def draw_icon(name, painter, x, y):
    """Draw the icon for `name` at (x, y) into a 40x40 area.

    Falls back to a generic question-mark box if the name is unknown.
    """
    fn = _ICONS.get(name, _generic)
    fn(painter, x, y)


def has_icon(name):
    return name in _ICONS
