# tos launcher — real start menu panel (replaces broken QMenu version)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QScrollArea, QGridLayout
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
        self._games = {}

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

        # Apps section
        apps_title = QLabel("Apps")
        apps_title.setAlignment(Qt.AlignLeft)
        apps_title.setFont(QFont("monospace", 8, QFont.Bold))
        self.layout.addWidget(apps_title)

        self.apps_container = QGridLayout()
        self.apps_container.setSpacing(2)

        holder = QWidget()
        holder.setLayout(self.apps_container)

        scroll_apps = QScrollArea()
        scroll_apps.setWidgetResizable(True)
        scroll_apps.setWidget(holder)
        scroll_apps.setFrameShape(QFrame.NoFrame)

        self.layout.addWidget(scroll_apps)

        # Games section
        games_title = QLabel("Games")
        games_title.setAlignment(Qt.AlignLeft)
        games_title.setFont(QFont("monospace", 8, QFont.Bold))
        self.layout.addWidget(games_title)

        self.games_container = QGridLayout()
        self.games_container.setSpacing(2)

        holder_games = QWidget()
        holder_games.setLayout(self.games_container)

        scroll_games = QScrollArea()
        scroll_games.setWidgetResizable(True)
        scroll_games.setWidget(holder_games)
        scroll_games.setFrameShape(QFrame.NoFrame)

        self.layout.addWidget(scroll_games)

    # ---------------- ADD APP ----------------
    def add_app(self, name, cb):
        btn = QPushButton(name)
        btn.clicked.connect(cb)

        self.apps_container.addWidget(btn)
        self._apps[name] = btn

    # ---------------- REMOVE APP ----------------
    def remove_app(self, name):
        if name in self._apps:
            btn = self._apps.pop(name)
            btn.setParent(None)

    # ---------------- ADD GAME ----------------
    def add_game(self, name, cb):
        btn = QPushButton(name)
        btn.clicked.connect(cb)

        self.games_container.addWidget(btn)
        self._games[name] = btn

    # ---------------- REMOVE GAME ----------------
    def remove_game(self, name):
        if name in self._games:
            btn = self._games.pop(name)
            btn.setParent(None)

    # ---------------- POPUP ----------------
    def popup(self, pos):
        self.move(pos)
        self.show()
        self.raise_()

    # optional compatibility (if your shell calls it)
    def refresh(self):
        self.update()
