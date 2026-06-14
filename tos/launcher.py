# tos launcher — proper start menu (Apps + Games sections)

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont


class Launcher(QWidget):
    def __init__(self, shell=None):
        super().__init__(shell)

        self.shell = shell
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFixedSize(260, 360)

        self.setStyleSheet("""
            QWidget {
                background: #FFD700;
                border: 2px solid #000;
            }
            QPushButton {
                background: #8B0000;
                color: #FFD700;
                border: 1px solid #000;
                padding: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background: #000;
                color: #FFD700;
            }
            QLabel {
                color: #000;
                font-weight: bold;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(6, 6, 6, 6)
        self.layout.setSpacing(8)

        # scroll area (prevents empty/overflow issues)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()
        self.vbox = QVBoxLayout(self.container)
        self.vbox.setAlignment(Qt.AlignTop)

        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)

        # storage
        self.apps = []
        self.games = []

        self._build_ui()

    # ---------------- UI BUILD ----------------
    def _build_ui(self):
        self.vbox.addWidget(self._section_label("APPS"))

        self.apps_container = QVBoxLayout()
        self.vbox.addLayout(self.apps_container)

        self.vbox.addWidget(self._section_label("GAMES"))

        self.games_container = QVBoxLayout()
        self.vbox.addLayout(self.games_container)

    def _section_label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("monospace", 10))
        return lbl

    # ---------------- API ----------------
    def add_app(self, name, cb):
        btn = QPushButton(name)
        btn.clicked.connect(cb)
        self.apps_container.addWidget(btn)

    def load_games(self, run_game_callback):
        game_dir = os.path.join(os.path.dirname(__file__), "games")

        if not os.path.exists(game_dir):
            return

        for file in os.listdir(game_dir):
            if file.endswith(".py"):
                name = file.replace(".py", "")

                btn = QPushButton(name)
                btn.clicked.connect(lambda _, n=name: run_game_callback(n))
                self.games_container.addWidget(btn)

    # ---------------- POPUP ----------------
    def popup(self, pos: QPoint):
        self.move(pos)
        self.show()