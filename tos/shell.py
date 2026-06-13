# tos shell — start menu, desktop shortcuts, shutdown, all lowercase

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QDesktopWidget, QLabel, QFrame, QPushButton, QStackedWidget, QGridLayout, QMenu
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont

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
        p.fillRect(20, 4, 40, 40, QColor(0x5C, 0x00, 0x00))
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
        self.setFrameShape(QFrame.NoFrame)
        self._build(title, content)
        self.resize(Sizes