# tos cursor — custom pixel-art cursors (no Windows cursors anywhere)
#
# Three cursor types, all retro pixel-art matching the TOS theme:
#   arrow  - default pointer (yellow arrow, black outline)  [scale 1 - compact]
#   text   - I-beam for text entry fields                    [scale 2 - big]
#   pointer- hand for clickable items (buttons, links)       [scale 2 - big]

from PyQt5.QtGui import QCursor, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, QRect

# --- palette ---
YEL = QColor(0xFF, 0xD7, 0x00)
BLK = QColor(0x00, 0x00, 0x00)


def _build(shape, hot_x=0, hot_y=0, scale=1):
    """Build a QCursor from an ASCII shape. 'X' = yellow, '#' = black.

    Each ASCII cell is drawn as a scale x scale block.
    hot_x / hot_y are in ASCII-cell units.
    """
    height = len(shape)
    width = max(len(row) for row in shape)
    pm = QPixmap(width * scale, height * scale)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, False)
    for y, row in enumerate(shape):
        for x in range(len(row)):
            ch = row[x]
            if ch == 'X':
                p.fillRect(QRect(x * scale, y * scale, scale, scale), YEL)
            elif ch == '#':
                p.fillRect(QRect(x * scale, y * scale, scale, scale), BLK)
    p.end()
    return QCursor(pm, hotX=hot_x * scale, hotY=hot_y * scale)


# --- cursor shapes ---

ARROW_SHAPE = [
    "X#",
    "XX#",
    "X X#",
    "X  X#",
    "X   X#",
    "X    X#",
    "X     X#",
    "X      X#",
    "X   XXXX#",
    "X  X    X#",
    "X X      X#",
    "XX        X#",
    "X          X#",
]

# I-beam: horizontal serifs top & bottom, vertical stem
TEXT_SHAPE = [
    "X#X",
    " X#",
    " X#",
    " X#",
    " X#",
    " X#",
    " X#",
    " X#",
    " X#",
    "X#X",
]

# Pointing hand: finger pointing up, fingertip at top
POINTER_SHAPE = [
    "  X# ",
    "  XX#",
    "  XXX#",
    "  X XX#",
    "  X  X#",
    "  X  X#",
    "  X  X#",
    "  X  X#",
    "  XXXXX#",
]

# --- cached singletons (built lazily after QApplication exists) ---
_ARROW = None
_TEXT = None
_POINTER = None


def get_cursor():
    """Default arrow cursor. Builds lazily, cached. Never raises.

    Kept at scale 1 (compact) so the default pointer stays unobtrusive.
    """
    global _ARROW
    if _ARROW is None:
        try:
            _ARROW = _build(ARROW_SHAPE, 0, 0, scale=1)
        except Exception:
            _ARROW = None
    return _ARROW


def get_text_cursor():
    """Text/I-beam cursor for text-entry fields. Builds lazily, cached.

    Drawn at scale 2 so it's clearly visible over text fields.
    """
    global _TEXT
    if _TEXT is None:
        try:
            _TEXT = _build(TEXT_SHAPE, 1, 4, scale=2)
        except Exception:
            _TEXT = None
    return _TEXT


def get_pointer_cursor():
    """Pointing-hand cursor for clickable items. Builds lazily, cached.

    Drawn at scale 2 so it's clearly visible over buttons.
    """
    global _POINTER
    if _POINTER is None:
        try:
            _POINTER = _build(POINTER_SHAPE, 2, 0, scale=2)
        except Exception:
            _POINTER = None
    return _POINTER


def apply_cursors(widget):
    """Recursively set the correct custom cursor on widget and ALL children.

    Call this after a widget tree is fully built:
      - QLineEdit / QTextEdit / QPlainTextEdit  -> text cursor
      - QPushButton                              -> pointer cursor
      - everything else                          -> arrow cursor

    This ensures NO Windows system cursor ever appears.
    """
    from PyQt5.QtWidgets import (
        QWidget, QLineEdit, QTextEdit, QPlainTextEdit, QPushButton)

    arrow = get_cursor()
    text = get_text_cursor()
    pointer = get_pointer_cursor()

    # the widget itself
    widget.setCursor(arrow if arrow is not None else Qt.ArrowCursor)

    for child in widget.findChildren(QWidget):
        if isinstance(child, (QLineEdit, QTextEdit, QPlainTextEdit)):
            child.setCursor(text if text is not None else Qt.IBeamCursor)
        elif isinstance(child, QPushButton):
            child.setCursor(pointer if pointer is not None else Qt.PointingHandCursor)
        else:
            child.setCursor(arrow if arrow is not None else Qt.ArrowCursor)


# Backwards compatibility: old code called cursor.get_cursor() / make_cursor()
def make_cursor():
    return _build(ARROW_SHAPE, 0, 0, scale=1)


TOS_CURSOR = None
