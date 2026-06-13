# tos notepad — simple text editor

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QFileDialog, QHBoxLayout
from PyQt5.QtCore import Qt
from theme import Fonts


class Notepad(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        lo = QVBoxLayout(self)
        lo.setContentsMargins(6, 6, 6, 6)
        lo.setSpacing(4)

        self._text_edit = QTextEdit()
        self._text_edit.setFont(Fonts.body())
        lo.addWidget(self._text_edit, stretch=1)

        button_lo = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save_file)
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self._open_file)
        button_lo.addWidget(open_btn)
        button_lo.addWidget(save_btn)
        lo.addLayout(button_lo)

    def _save_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self._text_edit.toPlainText())

    def _open_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            with open(file_path, 'r') as f:
                self._text_edit.setPlainText(f.read())
