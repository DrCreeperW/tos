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
        p