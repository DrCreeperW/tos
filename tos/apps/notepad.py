# tos notepad — simple text editor

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel)
from PyQt5.QtCore import Qt

from theme import Fonts
from dialogs import save_dialog, open_dialog, basename


BTN = (
    "QPushButton { background: #5C0000; color: #FFD700; border: 1px solid #000; "
    "font-family: More Perfect DOS VGA; font-size: 12px; font-weight: bold; padding: 2px 8px; }"
    "QPushButton:hover { background: #8B0000; }")

EDIT = (
    "QTextEdit { background: #000; color: #FFD700; border: 1px solid #000; "
    "font-family: More Perfect DOS VGA; font-size: 12px; }")

TEXT_FILTERS = "text files (*.txt *.md *.py *.json *.csv *.log *.ini *.cfg);;all files (*)"


class Notepad(QWidget):
    def __init__(self, path=None, parent=None):
        super().__init__(parent)
        self._path = None
        self._build()
        if path:
            self._load(path)

    def _build(self):
        self.setFixedSize(460, 320)

        lo = QVBoxLayout(self)
        lo.setContentsMargins(6, 6, 6, 6)
        lo.setSpacing(4)

        self._text_edit = QTextEdit()
        self._text_edit.setFont(Fonts.body())
        self._text_edit.setStyleSheet(EDIT)
        lo.addWidget(self._text_edit, stretch=1)

        button_lo = QHBoxLayout()
        button_lo.setContentsMargins(0, 0, 0, 0)
        button_lo.setSpacing(4)

        self._status = QLabel("untitled")
        self._status.setFont(Fonts.small())
        self._status.setStyleSheet("color: #CCAC00; background: transparent;")
        button_lo.addWidget(self._status)
        button_lo.addStretch()

        open_btn = QPushButton("open")
        open_btn.setStyleSheet(BTN)
        open_btn.clicked.connect(self._open_dialog)
        button_lo.addWidget(open_btn)

        save_btn = QPushButton("save")
        save_btn.setStyleSheet(BTN)
        save_btn.clicked.connect(self._save)
        button_lo.addWidget(save_btn)

        lo.addLayout(button_lo)

    # ---------------- file ops ----------------
    def _load(self, path):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                self._text_edit.setPlainText(f.read())
            self._path = path
            self._status.setText(basename(path))
        except Exception as ex:
            self._status.setText("error: %s" % ex)

    def _open_dialog(self):
        path = open_dialog(self, "open", TEXT_FILTERS)
        if path:
            self._load(path)

    def _save(self):
        # save back to the current file if there is one; else ask for a name
        path = self._path
        if not path:
            path = save_dialog(self, "save", "untitled.txt", "text files (*.txt);;all files (*)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._text_edit.toPlainText())
            self._path = path
            self._status.setText(basename(path))
        except Exception as ex:
            self._status.setText("error: %s" % ex)
