# tos terminal — functional, with command parsing
import os
import time
import random

from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import QColor, QPalette, QTextCursor
from PyQt5.QtCore import Qt, pyqtSignal
from theme import Fonts

TOS_VERSION = "v0.3"
FORTUNES = [
    "the early bird gets the worm, but the second mouse gets the cheese.",
    "a closed mouth gathers no feet.",
    "if at first you don't succeed, skydiving is not for you.",
    "the journey of a thousand miles begins with a single pixel.",
    "to err is human, to really foul things up requires a computer.",
    "there is no place like 127.0.0.1.",
    "the best way to predict the future is to invent it. or wait.",
    "you can't cross the sea merely by staring at the water.",
    "a yam a day keeps the doctor away.",
    "press any key to continue. any other key to quit.",
]


class Terminal(QPlainTextEdit):
    command_entered = pyqtSignal(str)  # emitted for egg-triggering commands

    def __init__(self, parent=None):
        super().__init__(parent)
        pal = QPalette()
        pal.setColor(QPalette.Base, QColor(0, 0, 0))
        pal.setColor(QPalette.Text, QColor(255, 215, 0))
        self.setPalette(pal)
        self.setAutoFillBackground(True)
        self.setFont(Fonts.body())
        self.setStyleSheet("border: none;")
        self._user = "user"
        self.setPlainText(
            "tos terminal " + TOS_VERSION + "\n"
            "===================\n"
            "type 'help' for commands.\n\n"
            "$ "
        )
        self._prompt_pos = len(self.toPlainText())
        self.setReadOnly(False)

    def _print(self, *lines):
        for ln in lines:
            self.appendPlainText(ln)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.End)
            line_start = cursor.block().position()
            full_text = self.toPlainText()
            cmd = full_text[line_start:].strip()
            if cmd.startswith("$ "):
                cmd = cmd[2:].strip()
            self.appendPlainText("")
            self.process_command(cmd)
            self._prompt_pos = len(self.toPlainText())
            self.appendPlainText("$ ")
            return
        elif e.key() == Qt.Key_Backspace:
            cursor = self.textCursor()
            if cursor.position() <= self._prompt_pos:
                return
        super().keyPressEvent(e)

    def process_command(self, cmd):
        if not cmd:
            return
        parts = cmd.split()
        name = parts[0].lower()
        args = parts[1:]

        # ---- basic commands ----
        if name == "help":
            self._print(
                "available commands:",
                "  help          - show this",
                "  clear         - clear screen",
                "  echo <text>   - print text back",
                "  date          - show date and time",
                "  whoami        - show current user",
                "  pwd           - print working directory",
                "  ls            - list files in home",
                "  about         - about tos",
                "  ver           - tos version",
                "  games         - list available games",
                "  fortune       - random wisdom",
                "  matrix        - enter the matrix",
                "  reboot        - restart tos (fake)",
                "  y & a         - ???",
                "",
                "  ...and a few secrets. explore!",
            )
        elif name == "clear":
            self.clear()
            self._prompt_pos = 0
        elif name == "echo":
            self._print(" ".join(args) if args else "")
        elif name == "date":
            self._print(time.strftime("%Y-%m-%d %H:%M:%S"))
        elif name == "whoami":
            self._print(self._user)
        elif name == "pwd":
            self._print(os.path.expanduser("~"))
        elif name == "ls":
            home = os.path.expanduser("~")
            try:
                entries = sorted(os.listdir(home))
                shown = [e for e in entries if not e.startswith(".")][:20]
                if shown:
                    self._print(*shown)
                else:
                    self._print("(empty)")
            except Exception:
                self._print("(error reading directory)")
        elif name == "about":
            self._print(
                "tos - terminal operating system",
                "a toy desktop os built with python + qt",
                "version " + TOS_VERSION,
                "all lowercase. all retro. all red.",
            )
        elif name in ("ver", "version"):
            self._print("tos " + TOS_VERSION)
        elif name == "games":
            self._print(
                "available games:",
                "  snake   jumper   pong   dodge",
                "  click   shooter",
                "",
                "  open them from the start menu.",
            )
        elif name == "fortune":
            self._print(random.choice(FORTUNES))
        elif name == "matrix":
            self._print("wake up, " + self._user + "...")
            for _ in range(8):
                row = "  " + " ".join(
                    random.choice("01010110100101110100") for _ in range(40))
                self._print(row)
            self._print("the matrix has you. follow the yellow cursor.")
        elif name == "reboot":
            self._print("rebooting tos...")
            self._print("[ ok ] stopping services")
            self._print("[ ok ] unmounting filesystems")
            self._print("[ ok ] see you soon")
            self._print("(just kidding. this is a toy os.)")

        # ---- egg triggers (emit signal so shell can launch the egg) ----
        elif name == "y" and "&" in cmd and "a" in cmd:
            self._print("")
            self.command_entered.emit("y&a")
        elif name == "why":
            self._print("why not?")
            self.command_entered.emit("egg1")
        elif name == "sudo":
            self._print("nice try. loading sudo anyway...")
            self.command_entered.emit("egg2")
        elif name == "beep":
            self._print("initiating beep sequence...")
            self.command_entered.emit("egg3")
        elif name == "42":
            self._print("the answer to life, the universe, and everything.")
            self.command_entered.emit("egg4")

        else:
            self._print(
                "unknown command: " + cmd,
                "type 'help' for available commands",
            )
