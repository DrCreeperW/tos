# tos shell — start menu, desktop shortcuts, shutdown, all lowercase

import sys
import os
import importlib

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QFrame, QPushButton, QStackedWidget,
    QGridLayout, QMenu, QHBoxLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPoint, QEvent, QRect
from PyQt5.QtGui import QPainter, QColor, QPen

from theme import Colors, Fonts, Sizes
import cursor
from cursor import apply_cursors
from taskbar import Taskbar
from launcher import Launcher
from icons import draw_icon


# ---------------- SAFE CURSOR ----------------
def _cursor():
    """Cached custom cursor, built after QApplication exists.

    Never returns None — falls back to the standard arrow so no widget ever
    gets a NoneType cursor (the old crash/inconsistency source).
    """
    c = cursor.get_cursor()
    return c if c is not None else Qt.ArrowCursor


# ---------------- BOOT SCREEN ----------------
class BootScreen(QWidget):
    """Retro BIOS-style boot sequence shown before login.

    Reveals boot messages one line at a time, then a splash, then calls
    done_callback(). Any key press skips straight to the end.
    """
    done = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self._lines = [
            "tos bios v1.0",
            "(c) tos systems",
            "",
            "cpu:            [ ok ]",
            "memory:         640k   [ ok ]",
            "disk:           [ ok ]",
            "display:        vga    [ ok ]",
            "keyboard:       [ ok ]",
            "mouse:          [ ok ]",
            "",
            "loading tos kernel...",
            "loading drivers...",
            "loading desktop...",
            "",
            "welcome to tos",
        ]
        self._shown = 0
        self._finished = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._reveal)
        self._timer.start(120)   # ms per line

    def _reveal(self):
        if self._shown < len(self._lines):
            self._shown += 1
            self.update()
        else:
            self._timer.stop()
            QTimer.singleShot(800, self._finish)

    def _finish(self):
        if self._finished:
            return
        self._finished = True
        self.done.emit()

    def keyPressEvent(self, e):
        # skip the boot sequence
        if not self._finished:
            self._shown = len(self._lines)
            self._timer.stop()
            self.update()
            QTimer.singleShot(200, self._finish)

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0, 0, 0))
        p.setPen(QColor(0xFF, 0xD7, 0x00))
        p.setFont(Fonts.body())
        y = 40
        for i in range(self._shown):
            line = self._lines[i]
            if line == "welcome to tos":
                p.setFont(Fonts.huge())
                p.drawText(QRect(0, y - 10, self.width(), 50),
                           Qt.AlignCenter, line)
                p.setFont(Fonts.body())
                y += 50
            else:
                p.drawText(40, y, self.width() - 80, 20,
                           Qt.AlignLeft | Qt.AlignTop, line)
                y += 22
        # blinking cursor on the last revealed line while booting
        if not self._finished and self._shown < len(self._lines):
            p.drawText(40, y, 20, 20, Qt.AlignLeft | Qt.AlignTop, "_")
        p.end()


# ---------------- DESKTOP ----------------
class DesktopBg(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.grid.setSpacing(10)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), Colors.RED_BG)
        p.end()


# ---------------- SHORTCUT ----------------
class Shortcut(QWidget):
    clicked = pyqtSignal()

    def __init__(self, label, icon_name=None, parent=None):
        super().__init__(parent)
        self.label = label
        self.icon_name = icon_name or label
        self.setFixedSize(80, 68)
        self.setCursor(_cursor())

    def paintEvent(self, e):
        p = QPainter(self)
        # icon box background
        p.fillRect(20, 4, 40, 40, QColor(0x5C, 0x00, 0x00))
        # draw the pixel-art icon centered in the box
        draw_icon(self.icon_name, p, 20, 4)
        # black border around the box
        p.setPen(QColor("black"))
        p.setBrush(Qt.NoBrush)
        p.drawRect(20, 4, 40, 40)
        # label below
        p.setPen(QColor(0xFF, 0xD7, 0x00))
        p.setFont(Fonts.body())
        p.drawText(self.rect(), Qt.AlignBottom | Qt.AlignHCenter, self.label)
        p.end()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit()


# ---------------- WINDOW ----------------
class AppWindow(QFrame):
    """Embedded app window — a real child of the desktop, never a separate
    top-level window. Dragged via the title bar using parent-relative math.

    It sizes itself to whatever its content declares (games set a fixed size;
    plain apps fall back to the default window size), and provides:
      - ESC to close (caught from the content via an event filter)
      - click-to-raise / z-order (active window on top)
      - automatic timer cleanup on close
    """
    closed = pyqtSignal(object)

    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self._drag_start = None
        self._drag_origin = None
        self.content = content

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        # TITLE BAR
        tb = QFrame()
        tb.setFixedHeight(22)
        tb.setStyleSheet("background:#FFD700; border:1px solid black;")
        tb.setCursor(_cursor())

        h = QHBoxLayout(tb)
        h.setContentsMargins(6, 0, 6, 0)

        title_lbl = QLabel(title)
        title_lbl.setFont(Fonts.title())

        close_btn = QPushButton("x")
        close_btn.setFixedSize(18, 18)
        close_btn.setCursor(_cursor())
        close_btn.setStyleSheet("background:#5C0000;color:#FFD700;")
        close_btn.clicked.connect(self._do_close)

        h.addWidget(title_lbl)
        h.addStretch()
        h.addWidget(close_btn)

        layout.addWidget(tb)
        content.setParent(self)
        layout.addWidget(content, 1)

        # size to the content if it declares a fixed size, else default
        ms = content.minimumSize()
        cw = ms.width() if ms.width() > 0 else Sizes.MIN_WIN_WIDTH
        ch = ms.height() if ms.height() > 0 else Sizes.MIN_WIN_HEIGHT
        self.setFixedSize(cw + 4, ch + 22 + 4)

        # watch the content so ESC closes the window and clicks raise it
        content.installEventFilter(self)
        tb.mousePressEvent = self._press
        tb.mouseMoveEvent = self._move

    # ---- drag (parent-relative math so child windows never fly off) ----
    def _press(self, e):
        self.raise_()
        if e.button() == Qt.LeftButton:
            self._drag_start = e.globalPos()
            self._drag_origin = self.pos()

    def _move(self, e):
        if self._drag_start is not None and (e.buttons() & Qt.LeftButton):
            gp = e.globalPos()
            self.move(
                self._drag_origin.x() + (gp.x() - self._drag_start.x()),
                self._drag_origin.y() + (gp.y() - self._drag_start.y()),
            )

    # ---- event filter: ESC closes, any mouse press raises the window ----
    def eventFilter(self, obj, event):
        et = event.type()
        if et == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            self._do_close()
            return True
        if et == QEvent.MouseButtonPress:
            self.raise_()
        return super().eventFilter(obj, event)

    def showEvent(self, e):
        super().showEvent(e)
        # give the content keyboard focus as soon as the window appears
        if self.content is not None:
            self.content.setFocus()

    def paintEvent(self, e):
        super().paintEvent(e)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        p.setPen(QPen(QColor(0, 0, 0), 1))
        p.drawRect(0, 0, self.width() - 1, self.height() - 1)
        p.end()

    def _do_close(self):
        self.close()

    def closeEvent(self, e):
        # stop any game-loop timers living inside the window before teardown
        for t in self.findChildren(QTimer):
            t.stop()
        self.closed.emit(self)
        super().closeEvent(e)


# ---------------- SHELL ----------------
class TOSShell(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("tos")

        # build the custom cursor now that QApplication exists
        cursor.get_cursor()
        self.setCursor(_cursor())

        self.windows = []
        self.logged = False
        self._built = False
        self._menu_ready = False
        self._login_widget = None

        self.build_ui()
        self.show_desktop_screen()
        # start on the boot screen (page 0); it calls show_login() when done
        self.stack.setCurrentIndex(0)
        self._boot.setFocus()

    # ---------------- UI ----------------
    def show_desktop_screen(self):
        self.showFullScreen()
        self.raise_()
        self.activateWindow()

    def _on_boot_done(self):
        """Boot sequence finished -> show the login screen."""
        self.show_login()

    def build_ui(self):
        central = QWidget()
        central.setStyleSheet("background:#8B0000;")
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # PAGE 0: BOOT SCREEN
        self._boot = BootScreen()
        self._boot.done.connect(self._on_boot_done)
        self.stack.addWidget(self._boot)

        # PAGE 1: LOGIN
        self.login_page = QWidget()
        self.login_page.setStyleSheet("background:#8B0000;")
        login_layout = QVBoxLayout(self.login_page)
        login_layout.setContentsMargins(0, 0, 0, 0)

        self.login_placeholder = QLabel("loading login...")
        self.login_placeholder.setAlignment(Qt.AlignCenter)
        self.login_placeholder.setStyleSheet("color:#FFD700;")
        login_layout.addWidget(self.login_placeholder)

        self.stack.addWidget(self.login_page)

        # DESKTOP
        desktop = QWidget()
        desktop.setStyleSheet("background:#8B0000;")
        dlayout = QVBoxLayout(desktop)
        dlayout.setContentsMargins(0, 0, 0, 0)
        dlayout.setSpacing(0)

        self.taskbar = Taskbar(
            launcher_callback=self.open_menu,
            shutdown_callback=self.open_shutdown_menu
        )

        self.desk = DesktopBg()
        self.desk.setCursor(_cursor())

        dlayout.addWidget(self.taskbar)
        dlayout.addWidget(self.desk, 1)

        self.stack.addWidget(desktop)

        self.launcher = Launcher(self)

        # build shortcuts + start menu immediately so they always exist
        self.build_shortcuts()
        self.register_start_menu()

        # apply custom cursors to everything (no Windows cursors)
        apply_cursors(self)

    # ---------------- LOGIN ----------------
    def show_login(self):
        if self._login_widget is not None:
            self._login_widget.hide()
            self._login_widget.deleteLater()
            self._login_widget = None
        try:
            from apps.login import LoginScreen
            self._login_widget = LoginScreen(self.login_page)
            self.login_placeholder.hide()
            self.login_page.layout().addWidget(self._login_widget)
            self._login_widget.ok.connect(self.on_login_success)
        except Exception as e:
            self.login_placeholder.setText(f"login failed: {e}")
        apply_cursors(self._login_widget or self.login_page)
        self.stack.setCurrentIndex(1)

    def on_login_success(self, user):
        self.logged = True
        self.stack.setCurrentIndex(2)
        self.desk.updateGeometry()
        self.desk.update()

    # ---------------- SHORTCUTS ----------------
    def build_shortcuts(self):
        if self._built:
            return
        self._built = True

        items = [
            ("terminal", "terminal", self.run_terminal),
            ("files",    "files",    self.run_explorer),
            ("settings", "settings", self.run_settings),
            ("calc",     "calc",     self.run_calc),
            ("clock",    "clock",    self.run_clock),
            ("notepad",  "notepad",  self.run_notepad),
            ("paint",    "paint",    self.run_paint),
            ("snake",    "snake",    self.run_snake),
            ("jumper",   "jumper",   self.run_jumper),
        ]

        for i, (n, icon, cb) in enumerate(items):
            sc = Shortcut(n, icon_name=icon, parent=self.desk)
            sc.clicked.connect(cb)
            self.desk.grid.addWidget(sc, i // 4, i % 4)

    # ---------------- START MENU ----------------
    def register_start_menu(self):
        if self._menu_ready:
            return
        self._menu_ready = True

        if hasattr(self.launcher, "clear_apps"):
            self.launcher.clear_apps()
        if hasattr(self.launcher, "clear_games"):
            self.launcher.clear_games()

        # APPS only — games are auto-discovered by the launcher itself
        self.launcher.add_app("terminal", self.run_terminal)
        self.launcher.add_app("files", self.run_explorer)
        self.launcher.add_app("settings", self.run_settings)
        self.launcher.add_app("calc", self.run_calc)
        self.launcher.add_app("clock", self.run_clock)
        self.launcher.add_app("notepad", self.run_notepad)
        self.launcher.add_app("paint", self.run_paint)

        # GAMES — discovered dynamically from the games/ folder, once only
        if hasattr(self.launcher, "load_games"):
            self.launcher.load_games(self.run_game)

    # ---------------- MENU ----------------
    def open_menu(self):
        btn = getattr(self.taskbar, "menu_btn", None)
        if not btn:
            return
        pos = btn.mapToGlobal(btn.rect().bottomLeft())
        screen = QApplication.primaryScreen().geometry()
        lw = self.launcher.width()
        lh = self.launcher.height()
        x = max(4, min(pos.x(), screen.width() - lw - 4))
        y = max(4, min(pos.y(), screen.height() - lh - 4))
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
        for w in list(self.windows):
            if hasattr(w, "_btn"):
                self.taskbar.remove_app_btn(w._btn)
            w.deleteLater()
        self.windows.clear()
        self.logged = False
        self.show_login()

    def shutdown(self):
        QApplication.quit()

    # ---------------- WINDOW MANAGER ----------------
    def launch(self, title, widget):
        if not self.logged:
            return None
        w = AppWindow(title, widget, parent=self.desk)
        w.closed.connect(self._on_window_closed)
        w.show()
        w.raise_()
        # apply custom cursors to the new window + all its children
        apply_cursors(w)
        self.windows.append(w)
        # running-app button in the taskbar (clicked passes a bool -> bind it)
        b = self.taskbar.add_app_btn(
            title, lambda checked=False, w=w: self._focus(w))
        w._btn = b
        return w

    def _focus(self, w):
        if w in self.windows:
            w.raise_()
            # bring keyboard focus to the content (e.g. a running game)
            if getattr(w, "content", None) is not None:
                w.content.setFocus()
            else:
                w.setFocus()

    def _on_window_closed(self, w):
        if w in self.windows:
            self.windows.remove(w)
            if hasattr(w, "_btn"):
                self.taskbar.remove_app_btn(w._btn)

    # ---------------- GAMES (embedded) ----------------
    def run_game(self, name):
        """Launch a game as an embedded window inside the desktop.

        No subprocess, no pygame window — the game module is imported in
        process and its `Game` widget is hosted like any other app.
        """
        if not self.logged:
            return None
        try:
            mod = importlib.import_module(f"games.{name}")
        except Exception as ex:
            print(f"[tos] cannot load game '{name}': {ex}")
            return None
        game_cls = getattr(mod, "Game", None)
        if game_cls is None:
            print(f"[tos] game '{name}' has no Game class")
            return None
        self.launch(name, game_cls())

    # ---------------- APPS ----------------
    def run_terminal(self):
        from apps.terminal import Terminal
        term = Terminal()

        def on_command(cmd):
            c = cmd.strip().lower()
            if c == "y&a":
                lbl = QLabel("y & a", self.desk)
                lbl.setStyleSheet("color:#FFD700; background: transparent;")
                lbl.adjustSize()
                lbl.move(
                    self.desk.width() - lbl.width() - 10,
                    self.desk.height() - lbl.height() - 10
                )
                lbl.show()
                lbl.raise_()
            elif c in ("egg1", "egg2", "egg3", "egg4", "egg_ya"):
                self.run_game(c)

        term.command_entered.connect(on_command)
        self.launch("terminal", term)

    def run_explorer(self):
        from apps.file_explorer import FileExplorer
        ex = FileExplorer()
        # double-clicking a text or .tosp file opens the right app
        ex.open_file.connect(self._open_file)
        self.launch("files", ex)

    def _open_file(self, path):
        """Open a file from the explorer: .tosp -> paint, text -> notepad."""
        ext = os.path.splitext(path)[1].lower()
        title = os.path.basename(path)
        if ext == ".tosp":
            from apps.paint import Paint
            self.launch(title or "paint", Paint(path=path))
        else:
            from apps.notepad import Notepad
            self.launch(title or "notepad", Notepad(path=path))

    def run_calc(self):
        from apps.calculator import Calculator
        self.launch("calc", Calculator())

    def run_clock(self):
        from apps.clock import Clock
        self.launch("clock", Clock())

    def run_settings(self):
        from apps.settings import Settings
        s = Settings()
        s.changed.connect(self._apply_theme)
        self.launch("settings", s)

    def _apply_theme(self, name):
        """Propagate theme change to the whole shell — desktop, taskbar,
        launcher, and all open windows."""
        # desktop background + shell background repaint automatically via
        # Colors.RED_BG (DesktopBg reads it at paint time)
        self.desk.update()
        # central widget background
        self.centralWidget().setStyleSheet("background:" + Colors.bg_css() + ";")
        # taskbar + launcher rebuild stylesheets
        self.taskbar.refresh_theme()
        self.launcher.refresh_theme()
        # repaint all open windows so their QFrame borders update
        for w in self.windows:
            w.update()

    def run_notepad(self):
        from apps.notepad import Notepad
        self.launch("notepad", Notepad())

    def run_paint(self):
        from apps.paint import Paint
        self.launch("paint", Paint())

    def run_snake(self):  self.run_game("snake")
    def run_jumper(self): self.run_game("jumper")


# ---------------- MAIN ----------------
def _register_font():
    """Load the bundled retro font if present, so it is used everywhere."""
    try:
        from PyQt5.QtGui import QFontDatabase
        base = os.path.dirname(os.path.abspath(__file__))
        for cand in (os.path.join(base, "MorePerfectDOSVGA.ttf"),
                     os.path.join(base, "..", "MorePerfectDOSVGA.ttf")):
            if os.path.isfile(cand):
                QFontDatabase.addApplicationFont(os.path.abspath(cand))
                break
    except Exception:
        pass


def main():
    try:
        QApplication.setAttribute(Qt.AA_DisableHighDpiScaling, True)
    except Exception:
        pass
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    _register_font()
    shell = TOSShell()
    shell.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
