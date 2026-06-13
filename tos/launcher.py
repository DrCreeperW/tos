# tos launcher — flat menu, black on yellow

from PyQt5.QtWidgets import QMenu, QAction
from theme import Colors, Fonts


class Launcher(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "QMenu { background: #FFD700; color: #000; border: 2px solid #000; "
            "font-family: More Perfect DOS VGA; font-size: 12px; padding: 2px; }"
            "QMenu::item { padding: 3px 12px; margin: 1px 0; }"
            "QMenu::item:selected { background: #000; color: #FFD700; }"
            "QMenu::separator { height: 1px; background: #000; margin: 2px 4px; }")
        self.setFixedWidth(170)
        self._actions = {}

    def add_app(self, name, cb):
        a = QAction(name, self)
        a.triggered.connect(cb)
        self.addAction(a)
        self._actions[name] = a

    def remove_app(self, name):
        if name in self._actions:
            self.removeAction(self._actions.pop(name))
