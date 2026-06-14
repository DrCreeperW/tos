# tos file explorer — lowercase, flat retro

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QLabel, QPushButton, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QBrush
from theme import Fonts


# extensions that open in notepad when double-clicked
TEXT_EXTS = {
    ".txt", ".md", ".py", ".json", ".csv", ".log", ".ini", ".cfg",
    ".sh", ".bat", ".xml", ".html", ".css", ".js", ".yaml", ".yml",
}


def _is_text(fp):
    return os.path.splitext(fp)[1].lower() in TEXT_EXTS


def _size(b):
    if b < 1024: return f"{b} b"
    if b < 1024*1024: return f"{b//1024} kb"
    return f"{b//(1024*1024)} mb"


class FileExplorer(QWidget):
    # emitted with a file path when a text file is double-clicked
    open_file = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._path = os.path.expanduser("~")
        self._build()
        self._open(self._path)

    def _build(self):
        lo = QVBoxLayout(self)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(1)

        nav = QWidget()
        nav.setStyleSheet("background: #5C0000;")
        nl = QHBoxLayout(nav)
        nl.setContentsMargins(4, 3, 4, 3)

        self.up = QPushButton(" ^ ")
        self.up.setFixedWidth(30)
        self.up.setFont(Fonts.body())
        self.up.setStyleSheet(
            "QPushButton { background: #FFD700; color: #000; "
            "border: 1px solid #000; font-family: More Perfect DOS VGA; font-size: 12px; }")
        self.up.clicked.connect(self._go_up)
        nl.addWidget(self.up)

        self.pl = QLabel("")
        self.pl.setFont(Fonts.body())
        self.pl.setStyleSheet("color: #FFD700; background: transparent; padding: 2px 6px;")
        nl.addWidget(self.pl, stretch=1)

        lo.addWidget(nav)

        self.tree = QTreeWidget()
        self.tree.setFont(Fonts.body())
        self.tree.setHeaderLabels(["name", "size", "type"])
        self.tree.setColumnCount(3)
        self.tree.setColumnWidth(0, 260)
        self.tree.setColumnWidth(1, 60)
        self.tree.setColumnWidth(2, 50)
        self.tree.setStyleSheet(
            "QTreeWidget { background: #5C0000; color: #FFD700; border: 1px solid #000; "
            "font-family: More Perfect DOS VGA; font-size: 12px; outline: none; }"
            "QTreeWidget::item { padding: 2px 4px; border: none; }"
            "QTreeWidget::item:selected { background: #FFD700; color: #000; }"
            "QHeaderView::section { background: #8B0000; color: #FFD700; "
            "border: 1px solid #000; font-family: More Perfect DOS VGA; font-size: 12px; "
            "font-weight: bold; padding: 2px 6px; }")
        self.tree.setRootIsDecorated(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree.itemDoubleClicked.connect(self._on_item)
        lo.addWidget(self.tree, stretch=1)

    def _open(self, path):
        self._path = os.path.abspath(path)
        self.pl.setText("  " + self._path)
        self.tree.clear()

        try:
            items = sorted(os.listdir(self._path),
                          key=lambda x: (not os.path.isdir(os.path.join(self._path, x)), x.lower()))
        except:
            it = QTreeWidgetItem(self.tree, ["[error]", "", ""])
            it.setForeground(0, QBrush(QColor(255, 68, 68)))
            return

        if self._path != "/":
            it = QTreeWidgetItem(self.tree, ["..", "", "dir"])
            it.setData(0, Qt.UserRole, os.path.dirname(self._path))
            it.setForeground(0, QBrush(QColor(255, 215, 0)))

        for n in items:
            fp = os.path.join(self._path, n)
            if n.startswith("."):
                continue
            try:
                s = os.stat(fp)
                sz = _size(s.st_size)
                ty = "dir" if os.path.isdir(fp) else "file"
            except:
                sz = "?"; ty = "?"
            it = QTreeWidgetItem(self.tree, [n, sz, ty])
            it.setData(0, Qt.UserRole, fp)
            it.setForeground(0, QBrush(QColor(255, 215, 0) if ty == "dir" else QColor(255, 228, 76)))

    def _on_item(self, it, col):
        fp = it.data(0, Qt.UserRole)
        if not fp:
            return
        if os.path.isdir(fp):
            self._open(fp)
        elif _is_text(fp) or os.path.splitext(fp)[1].lower() == ".tosp":
            # open text files in notepad / tosp files in paint (shell decides)
            self.open_file.emit(fp)

    def _go_up(self):
        p = os.path.dirname(self._path)
        if p and p != self._path:
            self._open(p)
