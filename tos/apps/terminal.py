# tos terminal — functional, with command parsing
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import QColor, QPalette, QTextCursor
from PyQt5.QtCore import Qt, pyqtSignal
from theme import Fonts


class Terminal(QPlainTextEdit):
    command_entered = pyqtSignal(str)  # emitted when user presses enter

    def __init__(self, parent=None):
        super().__init__(parent)
        pal = QPalette()
        pal.setColor(QPalette.Base, QColor(0, 0, 0))
        pal.setColor(QPalette.Text, QColor(255, 215, 0))
        self.setPalette(pal)
        self.setAutoFillBackground(True)
        self.setFont(Fonts.body())
        self.setStyleSheet("border: none;")
        self.setPlainText(
            "tos terminal v0.1\n"
            "===================\n"
            "type 'help' for commands.\n\n"
            "$ "
        )
        self._prompt_pos = len("tos terminal v0.1\n===================\ntype 'help' for commands.\n\n$ ")
        self.setReadOnly(False)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
            # get the current line
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
                return  # don't allow deleting the prompt
        super().keyPressEvent(e)

    def process_command(self, cmd):
        if not cmd:
            return
        if cmd == "help":
            self.appendPlainText("available commands:")
            self.appendPlainText("  help    - show this")
            self.appendPlainText("  clear   - clear screen")
            self.appendPlainText("  y & a   - ???")
        elif cmd == "clear":
            self.clear()
            self._prompt_pos = 0
        elif cmd == "y & a":
            self.appendPlainText("")
            self.command_entered.emit("y&a")
        else:
            self.appendPlainText(f"unknown command: {cmd}")
            self.appendPlainText("type 'help' for available commands")
