# tos launcher — real start menu panel (replaces broken QMenu version)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class Launcher(QWidget):
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

        self._apps = {}

        self._build_ui()

    # ---------------- UI ----------------
    def _build_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(2)

        title = QLabel("START")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("monospace", 10, QFont.Bold))
        self.layout.addWidget(title)

        self.container = QVBoxLayout()
        self.container.setSpacing(2)

        holder = QWidget()
        holder.setLayout(self.container)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(holder)
        scroll.setFrameShape(QFrame.NoFrame)

        self.layout.addWidget(scroll)

    # ---------------- ADD APP ----------------
    def add_app(self, name, cb):
        btn = QPushButton(name)
        btn.clicked.connect(cb)

        self.container.addWidget(btn)
        self._apps[name] = btn

    # ---------------- REMOVE APP ----------------
    def remove_app(self, name):
        if name in self._apps:
            btn = self._apps.pop(name)
            btn.setParent(None)

    # ---------------- POPUP ----------------
    def popup(self, pos):
        self.move(pos)
        self.show()
        self.raise_()

    # optional compatibility (if your shell calls it)
    def refresh(self):
        self.update()