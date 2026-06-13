# tos cursor — simple monochrome arrow, no outline

from PyQt5.QtGui import QCursor, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt


def make_cursor():
    size = 16
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, False)

    shape = [
        "X#             ",
        "XX#            ",
        "X X#           ",
        "X  X#          ",
        "X   X#         ",
        "X    X#        ",
        "X     X#       ",
        "X      X#      ",
        "X   XXXX#      ",
        "X  X    X#     ",
        "X X      X#    ",
        "XX        X#   ",
        "X          X#  ",
    ]

    yel = QColor(0xFF, 0xD7, 0x00)
    blk = QColor(0x00, 0x00, 0x00)

    for y, row in enumerate(shape):
        for x in range(len(row)):
            ch = row[x]
            if ch == 'X':
                p.setPen(yel)
                p.drawPoint(x, y)
            elif ch == '#':
                p.setPen(blk)
                p.drawPoint(x, y)
    p.end()
    return QCursor(pm, hotX=0, hotY=0)


TOS_CURSOR = None
