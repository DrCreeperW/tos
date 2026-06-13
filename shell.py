import sys
import subprocess
import os

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QFrame, QPushButton, QStackedWidget, QGridLayout, QMenu, QHBoxLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPoint
from PyQt5.QtGui import QPainter, QColor

from theme import Colors, Fonts, Sizes
import cursor
from taskbar import Taskbar
from launcher import Launcher


# ---------------- SAFE CURSOR ----------------
def safe_cursor():
    try:
        return cursor.make_cursor()
    except:
        return None


# ---------------- DESKTOP ----------------
class DesktopBg(QWidget):
    def __init__(self):
        super().__init__()
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.grid.setSpacing(10)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), Colors.RED_BG)


# ---------------- SHORTCUT ----------------
class Shortcut(QWidget):
    clicked = pyqtSignal()

    def __init__(self, label):
        super().__init__()
        self.label = label
        self.setFixedSize(80, 68)

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(20, 4, 40, 40, QColor("#5C0000"))
        p.setPen(QColor("black"))
        p.drawRect(20, 4, 40, 40)
        p.setPen(QColor("#FFD700"))
        p.setFont(Fonts.body())
        p.drawText(self.rect(), Qt.AlignBottom | Qt.AlignHCenter, self.label)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit()


# ---------------- WINDOW ----------------
class AppWindow(QFrame):
    def __init__(self, title, content):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(Sizes.MIN_WIN_WIDTH, Sizes.MIN_WIN_HEIGHT)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        # TITLE BAR
        tb = QFrame()
        tb.setFixedHeight(22)
        tb.setStyleSheet("background:#FFD700; border:1px solid black;")

        h = QHBoxLayout(tb)
        h.setContentsMargins(6, 0, 6, 0)

        title_lbl = QLabel(title)
        title_lbl.setFont(Fonts.title())

        close_btn = QPushButton("x")
        close_btn.setFixedSize(18, 18)
        close_btn.setStyleSheet("background:#5C0000;color:#FFD700;")
        close_btn.clicked.connect(self.close)

        h.addWidget(title_lbl)
        h.addStretch()
        h.addWidget(close_btn)

        layout.addWidget(tb)
        layout.addWidget(content, 1)

        self._drag = None
        tb.mousePressEvent = self._press
        tb.mouseMoveEvent = self._move

    def _press(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = e.globalPos() - self.frameGeometry().topLeft()

    def _move(self, e):
        if self._drag and e.buttons() == Qt.LeftButton:
            self.move(e.globalPos() - self._drag)


# ---------------- SHELL ----------------
class TOSShell(QMainWindow):
    def __init__(self):
        super().__init__()

        QApplication.setAttribute(Qt.AA_DisableHighDpiScaling, True)

        self.setWindowTitle("tos")

        self.cursor = safe_cursor()
        if self.cursor:
            self.setCursor(self.cursor)

        self.windows = []
        self.logged = False
        self._built = False

        self.build_ui()
        self.showFullScreen()

        QTimer.singleShot(0, self.show_login)

    # ---------------- UI ----------------
    def build_ui(self):
        central = QWidget()
        central.setStyleSheet("background:#8B0000;")
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # LOGIN
        self.login_page = QWidget()
        login_layout = QVBoxLayout(self.login_page)

        self.login_placeholder = QLabel("loading login...")
        login_layout.addWidget(self.login_placeholder)

        self.stack.addWidget(self.login_page)

        # DESKTOP
        desktop = QWidget()
        dlayout = QVBoxLayout(desktop)
        dlayout.setContentsMargins(0, 0, 0, 0)

        self.taskbar = Taskbar(
            launcher_callback=self.open_menu,
            shutdown_callback=self.open_shutdown_menu
        )

        self.desk = DesktopBg()

        dlayout.addWidget(self.taskbar)
        dlayout.addWidget(self.desk, 1)

        self.stack.addWidget(desktop)

        self.launcher = Launcher(self)

    # ---------------- LOGIN ----------------
    def show_login(self):
        try:
            from apps.login import LoginScreen
            self.login_widget = LoginScreen(self.login_page)

            self.login_placeholder.hide()
            self.login_page.layout().addWidget(self.login_widget)

            self.login_widget.ok.connect(self.on_login_success)

        except Exception as e:
            self.login_placeholder.setText(f"login failed: {e}")

        self.stack.setCurrentIndex(0)

    def on_login_success(self, user):
        self.logged = True
        self.show_desktop()

    # ---------------- DESKTOP ----------------
    def show_desktop(self):
        self.stack.setCurrentIndex(1)
        QTimer.singleShot(50, self.build_shortcuts)

    def build_shortcuts(self):
        if self._built:
            return
        self._built = True

        items = [
            ("terminal", self.run_terminal),
            ("files", self.run_explorer),
            ("settings", self.run_settings),
            ("calc", self.run_calc),
            ("clock", self.run_clock),
            ("jumper", self.run_jumper),
            ("snake", self.run_snake),
            ("shooter", self.run_shooter),
        ]

        for i, (n, cb) in enumerate(items):
            sc = Shortcut(n)
            sc.clicked.connect(cb)
            self.desk.grid.addWidget(sc, i // 4, i % 4)

        # 🔥 FIX: ENSURE START MENU IS NOT EMPTY
        self._register_start_menu()

    # ---------------- START MENU FIX ----------------
    def _register_start_menu(self):
        self.launcher.add_app("terminal", self.run_terminal)
        self.launcher.add_app("files", self.run_explorer)
        self.launcher.add_app("settings", self.run_settings)
        self.launcher.add_app("calc", self.run_calc)
        self.launcher.add_app("clock", self.run_clock)

        # Dynamically add games
        game_folder = os.path.join(os.path.dirname(__file__), "games")
        if os.path.exists(game_folder):
            for filename in os.listdir(game_folder):
                if filename.endswith(".py"):
                    game_name = filename[:-3]
                    self.launcher.add_game(game_name, lambda n=game_name: self.run_game(n))

    # ---------------- MENU ----------------
    def open_menu(self):
        btn = getattr(self.taskbar, "menu_btn", None)
        if not btn:
            return

        pos = btn.mapToGlobal(btn.rect().bottomLeft())
        screen = QApplication.primaryScreen().geometry()

        x = max(10, min(pos.x(), screen.width() - 220))
        y = max(10, min(pos.y(), screen.height() - 320))

        self.launcher.setFixedSize(200, 300)
        self.launcher.popup(QPoint(x, y))

    # ---------------- SHUTDOWN ----------------
    def open_shutdown_menu(self):
        menu = QMenu(self)

        menu.setStyleSheet("""
            QMenu {
                background: #8B0000;
                color: #FFD700;
                border: 2px solid #000;
                font-family: monospace;
            }
            QMenu::item:selected {
                background: #FFD700;
                color: #000;
            }
        """)

        a1 = menu.addAction("logout")
        a2 = menu.addAction("shutdown")

        a1.triggered.connect(self.logout)
        a2.triggered.connect(self.shutdown)

        btn = getattr(self.taskbar, "_shut_btn", None)
        if btn:
            menu.exec_(btn.mapToGlobal(btn.rect().bottomLeft()))

    def logout(self):
        self.logged = False
        self._built = False
        self.stack.setCurrentIndex(0)
        QTimer.singleShot(0, self.show_login)

    def shutdown(self):
        QApplication.quit()

    # ---------------- WINDOWS ----------------
    def launch(self, title, widget):
        w = AppWindow(title, widget)
        w.setParent(self.desk)
        w.show()
        self.windows.append(w)

    # ---------------- GAME ----------------
    def run_game(self, name):
        path = os.path.join(os.path.dirname(__file__), "games", f"{name}.py")
        if os.path.exists(path):
            subprocess.Popen([sys.executable, path], cwd=os.path.dirname(path))

    # ---------------- APPS ----------------
    def run_terminal(self):
        from apps.terminal import Terminal

        term = Terminal()

        # 🔥 FIXED EASTER EGG (was broken indentation before)
        def egg(cmd):
            if cmd.strip().lower() == "y&a":
                lbl = QLabel("y & a", self.desk)
                lbl.setStyleSheet("color:#FFD700;")
                lbl.adjustSize()

                w = self.desk.width()
                h = self.desk.height()
                lbl.move(w - lbl.width() - 10, h - lbl.height() - 10)
                lbl.show()

        term.command_entered.connect(egg)
        self.launch("terminal", term)

    def run_explorer(self):
        from apps.file_explorer import FileExplorer
        self.launch("files", FileExplorer())

    def run_calc(self):
        from apps.calculator import Calculator
        self.launch("calc", Calculator())

    def run_clock(self):
        from apps.clock import Clock
        self.launch("clock", Clock())

    def run_settings(self):
        from apps.settings import Settings
        self.launch("settings", Settings())

    def run_jumper(self): self.run_game("jumper")
    def run_snake(self): self.run_game("snake")
    def run_pong(self): self.run_game("pong")
    def run_dodge(self): self.run_game("dodge")
    def run_click(self): self.run_game("click")
    def run_shooter(self): self.run_game("shooter")


# ---------------- MAIN ----------------
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    shell = TOSShell()
    shell.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
