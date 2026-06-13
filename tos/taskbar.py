# tos taskbar — start button, running apps, clock, shutdown menu

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFrame, QMenu
from PyQt5.QtCore import Qt, QTimer, QTime
from theme import Fonts


class Taskbar(QFrame):
    def __init__(self, launcher_callback=None, shutdown_callback=None, parent=None):
        super().__init__(parent)
        self._lc = launcher_callback
        self._sc = shutdown_callback
        self.app_buttons = []
        self._setup()
        self._tick()

    def _setup(self):
        self.setFixedHeight(28)
        self.setStyleSheet("background: #FFD700;")
        lo = QHBoxLayout(self)
        lo.setContentsMargins(4, 1, 4, 1)
        lo.setSpacing(2)

        # start button
        self.menu_btn = QPushButton(" start ")
        self.menu_btn.setFixedHeight(22)
        self.menu_btn.setStyleSheet(
            "QPushButton { background: #5C0000; color: #FFD700; border: 1px solid #000; "
            "font-family: More Perfect DOS VGA; font-size: 12px; font-weight: bold; }"
            "QPushButton:hover { background: #8B0000; }")
        if self._lc:
            self.menu_btn.clicked.connect(self._lc)
        lo.addWidget(self.menu_btn)

        # running app buttons
        self._apps = QWidget()
        self._alo = QHBoxLayout(self._apps)
        self._alo.setContentsMargins(0, 0, 0, 0)
        self._alo.setSpacing(2)
        self._alo.addStretch()
        lo.addWidget(self._apps, stretch=1)

        # clock
        self.clock = QPushButton("--:--")
        self.clock.setFixedHeight(22)
        self.clock.setStyleSheet(
            "QPushButton { background: #5C0000; color: #FFD700; border: 1px solid #000; "
            "font-family: More Perfect DOS VGA; font-size: 12px; font-weight: bold; padding: 0 8px; }"
            "QPushButton:hover { background: #8B0000; }")
        lo.addWidget(self.clock)

        # shutdown menu attached to clock right-click OR a dedicated button
        self._shut_btn = QPushButton(" > ")
        self._shut_btn.setFixedWidth(22)
        self._shut_btn.setFixedHeight(22)
        self._shut_btn.setStyleSheet(
            "QPushButton { background: #5C0000; color: #FFD700; border: 1px solid #000; "
            "font-family: More Perfect DOS VGA; font-size: 10px; font-weight: bold; }"
            "QPushButton:hover { background: #8B0000; }")
        if self._sc:
            self._shut_btn.clicked.connect(self._sc)
        lo.addWidget(self._shut_btn)

    def _tick(self):
        self._tm = QTimer(self)
        self._tm.timeout.connect(lambda: self.clock.setText(QTime.currentTime().toString("HH:mm")))
        self._tm.start(1000)
        self.clock.setText(QTime.currentTime().toString("HH:mm"))

    def add_app_btn(self, title, cb):
        b = QPushButton(title)
        b.setFixedHeight(22)
        b.setStyleSheet(
            "QPushButton { background: #FFD700; color: #000; border: 1px solid #000; "
            "font-family: More Perfect DOS VGA; font-size: 11px; font-weight: bold; }"
            "QPushButton:hover { background: #000; color: #FFD700; }")
        b.clicked.connect(cb)
        self._alo.insertWidget(self._alo.count() - 1, b)
        self.app_buttons.append(b)
        return b

    def remove_app_btn(self, b):
        if b in self.app_buttons:
            self.app_buttons.remove(b)
            self._alo.removeWidget(b)
            b.deleteLater()
