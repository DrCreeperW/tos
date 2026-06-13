# tos launcher — real start menu panel (replaces broken QMenu version)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QScrollArea, QGridLayout, QMenu, QAction
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class Launcher(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.Popup)  # behaves like start menu popup
        self.setFixedSize(200, 300)

        self.setStyleSheet("""
            QWidget {
                background: #FFD700;
                border: 2px solid black;
                color: black;
                font-family: monospace;
                font-size: 12px;
            }

            QPushButton {
                background: transparent;
                border: none;
                text-align: left;
                padding: 6px;
            }

            QPushButton:hover {
                background: black;
                color: #FFD700;
            }
        """)

        self._sections = {}

    def add_section(self, name):
        if name not in self._sections:
            separator = QAction(None)
            separator.setSeparator(True)
            label = QAction(name)
            label.setFont(QFont("monospace", 8, QFont.Bold))
            label.setEnabled(False)
            self.addAction(separator)
            self.addAction(label)
            self._sections[name] = []

    def add_action(self, section, name, cb):
        if section not in self._sections:
            raise ValueError(f"Section '{section}' does not exist")
        action = QAction(name)
        action.triggered.connect(cb)
        self.addAction(action)
        self._sections[section].append(action)

    # ---------------- POPUP ----------------
    def popup(self, pos):
        self.move(pos)
        self.show()
        self.raise_()

    # optional compatibility (if your shell calls it)
    def refresh(self):
        self.update()
