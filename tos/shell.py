# tos shell — start menu, desktop shortcuts, shutdown, all lowercase

import sys
import subprocess
import os

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
        self.resize(Sizes.MIN_WIN_WIDTH, Sizes.MIN_WIN_HEIGHT)

    def _build(self, title, content):
        lo = QVBoxLayout(self)
        lo.setContentsMargins(2, 2, 2, 2)
        lo.setSpacing(0)

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
        cx.setStyleSheet(
            "QPushButton { background: #5C0000; color: #FFD700; "
            "border: 1px solid #000; font-weight: bold; font-size: 9px; padding: 0; }"
        )
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

        # login page
        self._login_page = QWidget()
        self._login_lo = QVBoxLayout(self._login_page)
        self.stack.addWidget(self._login_page)

        # desktop page
        dp = QWidget()
        dl = QVBoxLayout(dp)
        dl.setContentsMargins(0, 0, 0, 0)

        self.taskbar = Taskbar(
            launcher_callback=self._toggle_menu,
            shutdown_callback=self._show_shutdown_menu
        )
        dl.addWidget(self.taskbar)

        self.desk = DesktopBg()
        dl.addWidget(self.desk, stretch=1)

        self.stack.addWidget(dp)

        self.launcher = Launcher(self)
        self._register_apps()

        QTimer.singleShot(300, self._build_shortcuts)

    def _build_shortcuts(self):
        items = [
            ("terminal", self._run_terminal),
            ("files", self._run_explorer),
            ("settings", self._run_settings),
            ("calc", self._run_calc),
            ("clock", self._run_clock),
            ("jumper", self._run_jumper),
            ("snake", self._run_snake),
            ("shooter", self._run_shooter),
        ]

        for i, (name, cb) in enumerate(items):
            sc = Shortcut(name)
            sc.clicked.connect(cb)
            self.desk.grid.addWidget(sc, i // 4, i % 4)

    def _register_apps(self):
        for name, cb in [
            ("terminal", self._run_terminal),
            ("file explorer", self._run_explorer),
            ("calculator", self._run_calc),
            ("clock", self._run_clock),
            ("settings", self._run_settings),
        ]:
            self.launcher.add_app(name, cb)

        self.launcher.addSeparator()
        self.launcher.add_app("logout", self._logout)
        self.launcher.add_app("shutdown", self._shutdown)

    def _toggle_menu(self):
        self.launcher.popup(
            self.taskbar.menu_btn.mapToGlobal(
                self.taskbar.menu_btn.rect().bottomLeft()
            )
        )

    def _show_shutdown_menu(self):
        m = QMenu(self)
        a1 = m.addAction("logout")
        a1.triggered.connect(self._logout)
        a2 = m.addAction("shutdown")
        a2.triggered.connect(self._shutdown)
        m.exec_(self.taskbar._shut_btn.mapToGlobal(self.taskbar._shut_btn.rect().bottomLeft()))

    def _fullscreen(self):
        s = QDesktopWidget().screenGeometry(0)
        self.setGeometry(s)
        self.showFullScreen()

    def _show_login(self):
        from apps.login import LoginScreen
        self._login = LoginScreen(self._login_page)
        self._login_lo.addWidget(self._login)
        self._login.ok.connect(self._on_login)
        self.stack.setCurrentIndex(0)

    def _on_login(self, user):
        self._logged = True
        self.stack.setCurrentIndex(1)
        self.taskbar.show()

    def _logout(self):
        for w in self._windows:
            w.close()
        self._windows.clear()
        self._logged = False
        self.taskbar.hide()
        self._show_login()

    def _shutdown(self):
        QApplication.quit()

    def launch(self, title, widget):
        if not self._logged:
            return

        w = AppWindow(title, widget)
        w.closed.connect(self._on_close)

        self._windows.append(w)
        w.setParent(self.desk)
        w.show()
        w.raise_()

        self.taskbar.add_app_btn(title, lambda: w.raise_())

    def _on_close(self, w):
        if w in self._windows:
            self._windows.remove(w)

    # ================= FIXED GAME LAUNCHER =================
    def _run_game(self, name):
        import os
        import sys
        import subprocess

        p = os.path.join(os.path.dirname(__file__), "games", name + ".py")
        subprocess.Popen([sys.executable, p])

    def _run_terminal(self):
        from apps.terminal import Terminal
        self.launch("terminal", Terminal())

    def _run_explorer(self):
        from apps.file_explorer import FileExplorer
        self.launch("files", FileExplorer())

    def _run_calc(self):
        from apps.calculator import Calculator
        self.launch("calc", Calculator())

    def _run_clock(self):
        from apps.clock import Clock
        self.launch("clock", Clock())

    def _run_settings(self):
        from apps.settings import Settings
        self.launch("settings", Settings())

    def _run_jumper(self): self._run_game("jumper")
    def _run_snake(self): self._run_game("snake")
    def _run_shooter(self): self._run_game("shooter")


def main():
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication

    QApplication.setAttribute(Qt.AA_DisableHighDpiScaling, True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    shell = TOSShell()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()