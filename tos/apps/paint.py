# tos paint — simple drawing app, flat retro

import os

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QImage

from theme import Fonts
import tosformat
from dialogs import save_dialog, open_dialog, basename

from PyQt5.QtCore import QTimer


# drawing palette (TOS colors)
PALETTE = [
    QColor(0xFF, 0xD7, 0x00),   # yellow
    QColor(0xCC, 0xAC, 0x00),   # amber
    QColor(0x8B, 0x00, 0x00),   # red
    QColor(0x5C, 0x00, 0x00),   # dark red
    QColor(0x00, 0x00, 0x00),   # black
    QColor(0xFF, 0xFF, 0xFF),   # white
]
CANVAS_BG = QColor(0x00, 0x00, 0x00)   # black canvas

BRUSHES = [1, 3, 6, 10]

TOSP_FILTERS = "tos paintings (*.tosp);;all files (*)"

TOOL_BTN = (
    "QPushButton { background: #5C0000; color: #FFD700; border: 1px solid #000; "
    "font-family: More Perfect DOS VGA; font-size: 12px; font-weight: bold; padding: 0 6px; }"
    "QPushButton:hover { background: #8B0000; }")
TOOL_BTN_ON = (
    "QPushButton { background: #FFD700; color: #000; border: 1px solid #000; "
    "font-family: More Perfect DOS VGA; font-size: 12px; font-weight: bold; padding: 0 6px; }")


class Canvas(QWidget):
    """Drawing surface backed by a QImage so strokes persist across repaints."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._img = None
        self._last = None
        self.color = PALETTE[0]
        self.brush_size = 3
        self.eraser = False
        self.setMinimumSize(460, 330)

    def resizeEvent(self, e):
        # (re)create the backing image sized to the widget; preserve content
        old = self._img
        self._img = QImage(self.size(), QImage.Format_RGB32)
        self._img.fill(CANVAS_BG)
        if old is not None and not old.isNull():
            QPainter(self._img).drawImage(0, 0, old)
        self.update()

    def _pen(self):
        col = CANVAS_BG if self.eraser else self.color
        return QPen(col, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

    def _stroke_to(self, pos):
        if self._img is None:
            return
        qp = QPainter(self._img)
        qp.setPen(self._pen())
        if self._last is None:
            qp.drawPoint(pos)
        else:
            qp.drawLine(self._last, pos)
        qp.end()
        self._last = pos
        self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._last = None
            self._stroke_to(e.pos())

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            self._stroke_to(e.pos())

    def mouseReleaseEvent(self, e):
        self._last = None

    def clear(self):
        if self._img is not None:
            self._img.fill(CANVAS_BG)
            self.update()

    def load_image(self, img):
        """Replace the canvas with a loaded QImage (scaled to fit)."""
        self._img = QImage(self.size(), QImage.Format_RGB32)
        self._img.fill(CANVAS_BG)
        if img is not None and not img.isNull():
            p = QPainter(self._img)
            p.drawImage(0, 0, img.scaled(self.size()))
            p.end()
        self.update()

    def image(self):
        """Return the current backing QImage (or None)."""
        return self._img

    def pixel(self, x, y):
        """Test helper: the color of one backing pixel (invalid if no image)."""
        if self._img is None or self._img.isNull():
            return None
        return QColor(self._img.pixel(x, y))

    def paintEvent(self, e):
        qp = QPainter(self)
        if self._img is not None and not self._img.isNull():
            qp.drawImage(0, 0, self._img)
        qp.end()


class Paint(QWidget):
    def __init__(self, path=None, parent=None):
        super().__init__(parent)
        self.setFixedSize(460, 360)
        self._cur_color = PALETTE[0]
        self._cur_size = 3
        self._cur_eraser = False
        self._path = None          # current .tosp file path (if saved)
        self._pending_path = path   # file to load after canvas is ready
        self._build()
        if path:
            # canvas image is created in resizeEvent, so defer until shown
            QTimer.singleShot(0, self._load_pending)

    def _load_pending(self):
        """Load the painting from _pending_path once the canvas exists."""
        if self._pending_path:
            try:
                img = tosformat.load(self._pending_path)
                self.canvas.load_image(img)
                self._path = self._pending_path
            except Exception as ex:
                print("[tos paint] open error:", ex)
            self._pending_path = None

    def _build(self):
        lo = QVBoxLayout(self)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)

        # toolbar
        bar = QWidget()
        bar.setFixedHeight(30)
        bar.setStyleSheet("background: #5C0000;")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(4, 2, 4, 2)
        bl.setSpacing(4)

        # color swatches
        self.color_btns = []
        for c in PALETTE:
            b = QPushButton()
            b.setFixedSize(20, 20)
            b.clicked.connect(lambda _, c=c: self._pick_color(c))
            bl.addWidget(b)
            self.color_btns.append((b, c))

        bl.addWidget(self._vsep())

        # brush sizes
        self.size_btns = []
        for sz in BRUSHES:
            b = QPushButton(str(sz))
            b.setFixedHeight(20)
            b.setMinimumWidth(24)
            b.setFont(Fonts.body())
            b.clicked.connect(lambda _, s=sz: self._pick_size(s))
            bl.addWidget(b)
            self.size_btns.append((b, sz))

        bl.addWidget(self._vsep())

        self.eraser_btn = QPushButton("eraser")
        self.eraser_btn.setFixedHeight(20)
        self.eraser_btn.setFont(Fonts.small())
        self.eraser_btn.clicked.connect(self._toggle_eraser)
        bl.addWidget(self.eraser_btn)

        clr = QPushButton("clear")
        clr.setFixedHeight(20)
        clr.setFont(Fonts.small())
        clr.setStyleSheet(TOOL_BTN)
        clr.clicked.connect(self._clear)
        bl.addWidget(clr)

        bl.addWidget(self._vsep())

        opn = QPushButton("open")
        opn.setFixedHeight(20)
        opn.setFont(Fonts.small())
        opn.setStyleSheet(TOOL_BTN)
        opn.clicked.connect(self._open)
        bl.addWidget(opn)

        sav = QPushButton("save")
        sav.setFixedHeight(20)
        sav.setFont(Fonts.small())
        sav.setStyleSheet(TOOL_BTN)
        sav.clicked.connect(self._save)
        bl.addWidget(sav)

        bl.addStretch()
        lo.addWidget(bar)

        self.canvas = Canvas()
        lo.addWidget(self.canvas, 1)

        self._refresh()

    @staticmethod
    def _vsep():
        s = QWidget()
        s.setFixedWidth(2)
        s.setStyleSheet("background: #FFD700;")
        return s

    # ---- selection handlers ----
    def _pick_color(self, c):
        self._cur_color = c
        self._cur_eraser = False
        self.canvas.color = c
        self.canvas.eraser = False
        self._refresh()

    def _pick_size(self, s):
        self._cur_size = s
        self.canvas.brush_size = s
        self._refresh()

    def _toggle_eraser(self):
        self._cur_eraser = not self._cur_eraser
        self.canvas.eraser = self._cur_eraser
        self._refresh()

    def _clear(self):
        self.canvas.clear()

    # ---- save / open (.tosp) ----
    def _save(self):
        img = self.canvas.image()
        if img is None or img.isNull():
            return
        # save back to the current file if there is one; else ask for a name
        path = self._path
        if not path:
            path = save_dialog(self, "save painting", "untitled.tosp", TOSP_FILTERS)
        if not path:
            return
        try:
            tosformat.save(path, img)
            self._path = path
        except Exception as ex:
            print("[tos paint] save error:", ex)

    def _open(self):
        path = open_dialog(self, "open painting", TOSP_FILTERS)
        if not path:
            return
        try:
            img = tosformat.load(path)
            self.canvas.load_image(img)
            self._path = path
        except Exception as ex:
            print("[tos paint] open error:", ex)

    # ---- refresh button styles to show current selection ----
    def _refresh(self):
        for b, c in self.color_btns:
            on = (c == self._cur_color and not self._cur_eraser)
            ring = "#FFD700" if on else "#000"
            w = 2 if on else 1
            b.setStyleSheet(
                f"QPushButton {{ background: {c.name()}; border: {w}px solid {ring}; }}")
        for b, sz in self.size_btns:
            b.setStyleSheet(TOOL_BTN_ON if sz == self._cur_size else TOOL_BTN)
        self.eraser_btn.setStyleSheet(TOOL_BTN_ON if self._cur_eraser else TOOL_BTN)
