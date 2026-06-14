# tos login — fullscreen, lowercase, max contrast

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPalette, QColor
from theme import Fonts

USERS = {"user": "tos", "admin": "admin", "guest": ""}


class LoginScreen(QWidget):
    ok = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        lo = QVBoxLayout(self)
        lo.setAlignment(Qt.AlignCenter)

        logo = QLabel("tos")
        logo.setFont(Fonts.huge())
        logo.setStyleSheet("color: #FFD700; background: transparent;")
        logo.setAlignment(Qt.AlignCenter)
        lo.addWidget(logo)

        sub = QLabel("terminal operating system")
        sub.setFont(Fonts.small())
        sub.setStyleSheet("color: #FFD700; background: transparent;")
        sub.setAlignment(Qt.AlignCenter)
        lo.addSpacing(4)
        lo.addWidget(sub)
        lo.addSpacing(20)

        # form box
        box = QWidget()
        box.setFixedWidth(280)
        box.setStyleSheet("background: #5C0000; border: 2px solid #000;")
        fl = QVBoxLayout(box)
        fl.setContentsMargins(16, 16, 16, 16)
        fl.setSpacing(6)

        ul = QLabel("username:")
        ul.setFont(Fonts.body())
        ul.setStyleSheet("color: #FFD700; background: transparent;")
        fl.addWidget(ul)

        self.u = QLineEdit()
        self.u.setFont(Fonts.body())
        self.u.setStyleSheet(
            "QLineEdit { background: #000; color: #FFD700; "
            "border: 1px solid #FFD700; padding: 3px 6px; font-family: More Perfect DOS VGA; font-size: 12px; }")
        self.u.setPlaceholderText("user")
        fl.addWidget(self.u)

        pl = QLabel("password:")
        pl.setFont(Fonts.body())
        pl.setStyleSheet("color: #FFD700; background: transparent;")
        fl.addWidget(pl)

        self.p = QLineEdit()
        self.p.setFont(Fonts.body())
        self.p.setEchoMode(QLineEdit.Password)
        self.p.setStyleSheet(self.u.styleSheet())
        self.p.setPlaceholderText("tos")
        fl.addWidget(self.p)

        fl.addSpacing(8)

        btn = QPushButton("  login  ")
        btn.setFont(Fonts.title())
        btn.setFixedHeight(28)
        btn.setStyleSheet(
            "QPushButton { background: #FFD700; color: #000; "
            "border: 1px solid #000; font-weight: bold; font-family: More Perfect DOS VGA; }"
            "QPushButton:hover { background: #FFE44C; }")
        btn.clicked.connect(self._go)
        fl.addWidget(btn)

        self.err = QLabel("")
        self.err.setFont(Fonts.body())
        self.err.setStyleSheet("color: #FF4444; background: transparent;")
        self.err.setAlignment(Qt.AlignCenter)
        fl.addWidget(self.err)

        lo.addWidget(box, alignment=Qt.AlignCenter)
        lo.addSpacing(20)

        f = QLabel("press enter to login")
        f.setFont(Fonts.small())
        f.setStyleSheet("color: #CCAC00; background: transparent;")
        f.setAlignment(Qt.AlignCenter)
        lo.addWidget(f)

        self.p.returnPressed.connect(self._go)
        self.u.returnPressed.connect(lambda: self.p.setFocus())

    def _go(self):
        u = self.u.text().strip().lower()
        pw = self.p.text()
        if not u:
            self._error("enter a username")
            return
        if u in USERS and pw == USERS[u]:
            self.err.setText("")
            self.ok.emit(u)
            return
        self._error("invalid credentials")
        self.p.clear()
        self.p.setFocus()

    def _error(self, m):
        self.err.setText("  " + m + "  ")
        QTimer.singleShot(3000, lambda: self.err.setText(""))

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.u.clear()
            self.p.clear()
            self.err.setText("")
            self.u.setFocus()
        super().keyPressEvent(e)
