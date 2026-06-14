# tos dialogs — TOS-styled file dialog (NOT the native OS file picker)
#
# A custom in-TOS file browser for save/open operations. It browses the real
# filesystem but is styled like the rest of TOS — no Windows Explorer / native
# QFileDialog ever appears.

import os
import re

from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
from theme import Fonts
from cursor import apply_cursors


# ---- styling ----
BG      = "#5C0000"
ACCENT  = "#FFD700"
ACCENT2 = "#8B0000"
DIM     = "#CCAC00"

BTN = (
    "QPushButton { background: #5C0000; color: #FFD700; border: 1px solid #000; "
    "font-family: 'More Perfect DOS VGA'; font-size: 12px; font-weight: bold; padding: 3px 10px; }"
    "QPushButton:hover { background: #8B0000; }")

BTN_GO = (
    "QPushButton { background: #FFD700; color: #000; border: 1px solid #000; "
    "font-family: 'More Perfect DOS VGA'; font-size: 12px; font-weight: bold; padding: 3px 10px; }"
    "QPushButton:hover { background: #FFE44C; }")

EDIT = (
    "QLineEdit { background: #000; color: #FFD700; border: 1px solid #FFD700; "
    "font-family: 'More Perfect DOS VGA'; font-size: 12px; padding: 2px 4px; }")

LIST = (
    "QListWidget { background: #000; color: #FFD700; border: 1px solid #000; "
    "font-family: 'More Perfect DOS VGA'; font-size: 12px; outline: none; }"
    "QListWidget::item { padding: 2px 6px; }"
    "QListWidget::item:selected { background: #FFD700; color: #000; }")


# ---- helpers ----
def _parse_exts(filters):
    """Extract extensions from a filter string like 'text (*.txt *.md);;all (*)'.

    Returns None if any group is 'all files' (show everything), otherwise a
    set of extensions.
    """
    exts = set()
    for part in filters.split(";;"):
        found = re.findall(r'\*\.(\w+)', part)
        if not found:
            return None         # "all files (*)" present -> show everything
        exts.update(found)
    return exts


def _matches(name, exts, is_dir):
    if is_dir:
        return True
    if exts is None or not exts:          # all files
        return True
    return os.path.splitext(name)[1].lstrip('.').lower() in exts


class TOSFileDialog(QDialog):
    """In-TOS file browser dialog. mode = 'open' or 'save'."""

    def __init__(self, parent=None, title="open", mode="open",
                 filters="all files (*)", default_name=""):
        super().__init__(parent)
        self._mode = mode
        self._path = os.path.expanduser("~")
        self._exts = _parse_exts(filters)
        self._default_ext = next(iter(self._exts), None) if self._exts else None
        self._chosen = None
        self._build(title, default_name)
        self._refresh()

    def chosen_path(self):
        return self._chosen

    # -------------------------------------------------------------- build
    def _build(self, title, default_name):
        self.setWindowTitle(title)
        self.setFixedSize(420, 400)
        self.setStyleSheet(f"background: {BG};")

        lo = QVBoxLayout(self)
        lo.setContentsMargins(10, 10, 10, 10)
        lo.setSpacing(6)

        # title
        tl = QLabel(title)
        tl.setFont(Fonts.title())
        tl.setStyleSheet(f"color: {ACCENT}; border: none;")
        lo.addWidget(tl)

        # nav bar
        nav = QHBoxLayout()
        nav.setSpacing(4)
        up = QPushButton(" ^ ")
        up.setFixedWidth(32)
        up.setStyleSheet(BTN)
        up.clicked.connect(self._go_up)
        nav.addWidget(up)

        self._path_lbl = QLabel("")
        self._path_lbl.setFont(Fonts.body())
        self._path_lbl.setStyleSheet(f"color: {ACCENT}; border: none; padding: 0 4px;")
        nav.addWidget(self._path_lbl, 1)
        lo.addLayout(nav)

        # file list
        self._list = QListWidget()
        self._list.setStyleSheet(LIST)
        self._list.setFont(Fonts.body())
        self._list.itemDoubleClicked.connect(self._on_double)
        self._list.itemClicked.connect(self._on_click)
        lo.addWidget(self._list, 1)

        # filename entry (save mode only)
        if self._mode == "save":
            fl = QHBoxLayout()
            fl.setSpacing(4)
            nl = QLabel("file:")
            nl.setFont(Fonts.body())
            nl.setStyleSheet(f"color: {ACCENT}; border: none;")
            fl.addWidget(nl)
            self._name_edit = QLineEdit(default_name)
            self._name_edit.setStyleSheet(EDIT)
            self._name_edit.returnPressed.connect(self._confirm)
            fl.addWidget(self._name_edit, 1)
            lo.addLayout(fl)

        # buttons
        bl = QHBoxLayout()
        bl.addStretch()

        cancel = QPushButton("cancel")
        cancel.setStyleSheet(BTN)
        cancel.clicked.connect(self.reject)
        bl.addWidget(cancel)

        action_text = "save" if self._mode == "save" else "open"
        action = QPushButton(action_text)
        action.setStyleSheet(BTN_GO)
        action.clicked.connect(self._confirm)
        bl.addWidget(action)
        lo.addLayout(bl)

        # apply custom cursors (no Windows cursors)
        apply_cursors(self)

    # ----------------------------------------------------------- browsing
    def _refresh(self):
        self._path_lbl.setText("  " + self._path)
        self._list.clear()
        try:
            entries = sorted(
                os.listdir(self._path),
                key=lambda x: (not os.path.isdir(os.path.join(self._path, x)),
                               x.lower()))
        except OSError:
            return
        for n in entries:
            if n.startswith("."):
                continue
            fp = os.path.join(self._path, n)
            is_dir = os.path.isdir(fp)
            if not _matches(n, self._exts, is_dir):
                continue
            label = ("[dir]  " if is_dir else "       ") + n
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, (fp, is_dir))
            item.setForeground(
                QBrush(QColor(255, 215, 0) if is_dir else QColor(255, 228, 76)))
            self._list.addItem(item)

    def _on_click(self, item):
        fp, is_dir = item.data(Qt.UserRole)
        if not is_dir and self._mode == "save":
            self._name_edit.setText(os.path.basename(fp))

    def _on_double(self, item):
        fp, is_dir = item.data(Qt.UserRole)
        if is_dir:
            self._path = fp
            self._refresh()
        else:
            self._chosen = fp
            self.accept()

    def _go_up(self):
        p = os.path.dirname(self._path)
        if p and p != self._path:
            self._path = p
            self._refresh()

    def _confirm(self):
        if self._mode == "save":
            name = self._name_edit.text().strip()
            if not name:
                return
            # auto-append extension if missing
            if self._default_ext and os.path.splitext(name)[1] == "":
                name += "." + self._default_ext
            self._chosen = os.path.join(self._path, name)
        else:
            item = self._list.currentItem()
            if item:
                fp, is_dir = item.data(Qt.UserRole)
                if not is_dir:
                    self._chosen = fp
        if self._chosen:
            self.accept()


# ---- public API (same signature as before) ----
def save_dialog(parent, title="save", default_name="", filters="all files (*)"):
    """Open the TOS save dialog. Returns the chosen path or None."""
    d = TOSFileDialog(parent, title=title, mode="save",
                      filters=filters, default_name=default_name)
    if d.exec_() == QDialog.Accepted:
        return d.chosen_path()
    return None


def open_dialog(parent, title="open", filters="all files (*)"):
    """Open the TOS open dialog. Returns the chosen path or None."""
    d = TOSFileDialog(parent, title=title, mode="open", filters=filters)
    if d.exec_() == QDialog.Accepted:
        return d.chosen_path()
    return None


def basename(path):
    """Filename without directory, or 'untitled' if empty."""
    return os.path.basename(path) if path else "untitled"
