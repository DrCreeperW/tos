# tos shell — start menu, desktop shortcuts, shutdown, all lowercase

import sys
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QDesktopWidget, QLabel, QFrame, QPushButton, QStackedWidget, QGridLayout, QMenu
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QFont

from theme import Colors, Fonts, Sizes
import cursor
from taskbar import Taskbar
from launcher import Launcher


class DesktopBg(QWidget):
    """red desktop background, holds shortcuts"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.grid.setSpacing(8)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), Colors.RED_BG)
        p.end()


class Shortcut(QWidget):
    clicked = pyqtSignal()

    def __init__(self, label, parent=None):
        super().__init__(parent)
        self._l = label
        self.setFixedSize(80, 68)
        self.setCursor(cursor.TOS_CURSOR)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        p.fillRect(20, 4, 40, 40, QColor(0x5C, 0, 0))
        p.setPen(QColor(0, 0, 0))
        p.drawRect(20, 4, 40, 40)
        p.setPen(QColor(0xFF, 0xD7, 0x00))
        p.setFont(Fonts.body())
        p.drawText(0, 46, 80, 20, Qt.AlignCenter, self._l)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit()


class AppWindow(QFrame):
    closed = pyqtSignal(object)

    def __init__(self, title, content, app_id=None):
        super().__init__()
        self.app_id = app_id or title
        self.setWindowFlags(Qt.FramelessWindowHint)
        self._build(title, content)
        self.resize(Sizes.MIN_WIN_WIDTH, Sizes.MIN_WIN_HEIGHT)

    def _build(self, title, content):
        lo = QVBoxLayout(self)
        lo.setContentsMargins(2, 2, 2, 2)
        tb = QFrame()
        tb.setFixedHeight(20)
        tb.setStyleSheet("background: #FFD700; border-bottom: 1px solid #000;")
        def tb_press(e):
            if e.button() == Qt.LeftButton:
                self._drag = e.globalPos() - self.frameGeometry().topLeft()
                e.accept()
        def tb_move(e):
            if e.buttons() == Qt.LeftButton and hasattr(self, '_drag'):
                self.move(e.globalPos() - self._drag)
                e.accept()
        tb.mousePressEvent = tb_press
        tb.mouseMoveEvent = tb_move
        tlo = QHBoxLayout(tb)
        tlo.setContentsMargins(4, 0, 2, 0)
        lbl = QLabel(title)
        lbl.setFont(Fonts.title())
        lbl.setStyleSheet("color: #000; background: transparent;")
        tlo.addWidget(lbl, stretch=1)
        cx = QPushButton("x")
        cx.setFixedSize(16, 16)
        cx.setFont(Fonts.body())
        cx.setStyleSheet("QPushButton { background: #5C0000; color: #FFD700; border: 1px solid #000; font-weight: bold; font-size: 9px; padding: 0; }")
        cx.clicked.connect(self._close)
        tlo.addWidget(cx)
        lo.addWidget(tb)
        self.content = content
        lo.addWidget(self.content, stretch=1)

    def paintEvent(self, e):
        super().paintEvent(e)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        p.setPen(QPen(QColor(0, 0, 0), 1))
        p.drawRect(0, 0, self.width() - 1, self.height() - 1)
        p.end()

    def _close(self):
        self.closed.emit(self)
        self.close()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = e.globalPos() - self.frameGeometry().topLeft()
            e.accept()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton and hasattr(self, '_drag'):
            self.move(e.globalPos() - self._drag)
            e.accept()


class TOSShell(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("tos")
        cursor.TOS_CURSOR = cursor.make_cursor()
        self.setCursor(cursor.TOS_CURSOR)
        self._windows = []
        self._wcount = 0
        self._logged = False
        self._label = ""
        self._build()
        self._fullscreen()
        self._show_login()

    def _build(self):
        central = QWidget()
        central.setStyleSheet("background: #8B0000;")
        self.setCentralWidget(central)
        ml = QVBoxLayout(central)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(0)

        self.stack = QStackedWidget()
        ml.addWidget(self.stack, stretch=1)

        # page 0: login
        self._login_page = QWidget()
        self._login_page.setAutoFillBackground(True)
        lp = self._login_page.palette()
        lp.setColor(self._login_page.backgroundRole(), QColor(0x8B, 0x00, 0x00))
        self._login_page.setPalette(lp)
        self._login_lo = QVBoxLayout(self._login_page)
        self._login_lo.setContentsMargins(0, 0, 0, 0)
        self.stack.addWidget(self._login_page)

        # page 1: desktop
        dp = QWidget()
        dl = QVBoxLayout(dp)
        dl.setContentsMargins(0, 0, 0, 0)
        dl.setSpacing(0)

        self.taskbar = Taskbar(launcher_callback=self._toggle_menu, shutdown_callback=self._show_shutdown_menu)
        dl.addWidget(self.taskbar)

        self.desk = DesktopBg()
        dl.addWidget(self.desk, stretch=1)

        self.stack.addWidget(dp)
        self.launcher = Launcher(self)
        self._register_apps()
        QTimer.singleShot(3