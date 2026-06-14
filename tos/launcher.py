# tos launcher — fixed Apps/Games menu, no duplicates

import os

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont
from cursor import apply_cursors
from theme import Colors


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
                border: none;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)

        self.container = QWidget()
        self.scroll.setWidget(self.container)

        root.addWidget(self.scroll)

        self.vbox = QVBoxLayout(self.container)
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.setSpacing(6)

        # APPS SECTION
        self.apps_label = QLabel("APPS")
        self.apps_label.setFont(QFont("Courier New", 10, QFont.Bold))
        self.vbox.addWidget(self.apps_label)

        self.apps_container = QVBoxLayout()
        self.vbox.addLayout(self.apps_container)

        # GAMES SECTION
        self.games_label = QLabel("GAMES")
        self.games_label.setFont(QFont("Courier New", 10, QFont.Bold))
        self.vbox.addWidget(self.games_label)

        self.games_container = QVBoxLayout()
        self.vbox.addLayout(self.games_container)

        self.refresh_theme()

    # ---------------- THEME ----------------
    def refresh_theme(self):
        """Re-apply stylesheet using the current theme colors."""
        self.setStyleSheet("""
            QWidget {
                background: """ + Colors.yellow_css() + """;
                border: 2px solid #000;
            }
            QPushButton {
                background: """ + Colors.bg_css() + """;
                color: """ + Colors.yellow_css() + """;
                border: 1px solid #000;
                padding: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background: #000;
                color: """ + Colors.yellow_css() + """;
            }
            QLabel {
                color: #000;
                font-weight: bold;
                border: none;
            }
        """)

    # ---------------- INTERNAL ----------------
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    # ---------------- APPS ----------------
    def clear_apps(self):
        self._clear_layout(self.apps_container)

    def add_app(self, name, callback):
        btn = QPushButton(name)
        btn.clicked.connect(callback)
        btn.clicked.connect(self.hide)
        self.apps_container.addWidget(btn)
        apply_cursors(btn)

    # ---------------- GAMES ----------------
    def clear_games(self):
        self._clear_layout(self.games_container)

    def load_games(self, run_game_callback):
        self.clear_games()

        game_dir = os.path.join(os.path.dirname(__file__), "games")
        if not os.path.isdir(game_dir):
            return

        files = sorted(os.listdir(game_dir))

        for filename in files:
            if not filename.endswith(".py"):
                continue
            if filename.startswith("_"):
                continue

            name = filename[:-3]

            btn = QPushButton(name)
            btn.clicked.connect(lambda checked=False, n=name: run_game_callback(n))
            btn.clicked.connect(self.hide)

            self.games_container.addWidget(btn)
            apply_cursors(btn)

    # ---------------- POPUP ----------------
    def popup(self, pos: QPoint):
        self.move(pos)
        self.show()
        self.raise_()
        self.activateWindow()