# tos calc — simple retro calculator, all lowercase
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt
from theme import Fonts


class Calculator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._expr = ""
        self._build()

    def _build(self):
        lo = QVBoxLayout(self)
        lo.setContentsMargins(6, 6, 6, 6)
        lo.setSpacing(4)

        self._disp = QLineEdit("0")
        self._disp.setFont(Fonts.title())
        self._disp.setAlignment(Qt.AlignRight)
        self._disp.setReadOnly(True)
        self._disp.setStyleSheet(
            "QLineEdit { background: #000; color: #FFD700; border: 1px solid #000; "
            "font-family: More Perfect DOS VGA; font-size: 16px; padding: 4px 8px; }")
        lo.addWidget(self._disp)

        grid = QGridLayout()
        grid.setSpacing(2)
        style = (
            "QPushButton { background: #5C0000; color: #FFD700; border: 1px solid #000; "
            "font-family: More Perfect DOS VGA; font-size: 14px; font-weight: bold; }"
            "QPushButton:hover { background: #8B0000; }")
        for txt, r, c in [
            ('7',0,0),('8',0,1),('9',0,2),('/',0,3),
            ('4',1,0),('5',1,1),('6',1,2),('*',1,3),
            ('1',2,0),('2',2,1),('3',2,2),('-',2,3),
            ('0',3,0),('.',3,1),('=',3,2),('+',3,3),
        ]:
            b = QPushButton(txt)
            b.setFixedSize(44, 36)
            b.setFont(Fonts.title())
            b.setStyleSheet(style)
            b.clicked.connect(lambda _, t=txt: self._press(t))
            grid.addWidget(b, r, c)

        cb = QPushButton("c")
        cb.setFixedSize(44, 28)
        cb.setFont(Fonts.title())
        cb.setStyleSheet(style)
        cb.clicked.connect(self._clear)
        grid.addWidget(cb, 4, 0, 1, 4)

        lo.addLayout(grid)

    def _press(self, t):
        if t == '=':
            self._eval()
        else:
            self._expr += t
            self._disp.setText(self._expr)

    def _eval(self):
        try:
            r = eval(self._expr)
            self._disp.setText(str(r))
            self._expr = str(r)
        except:
            self._disp.setText("err")
            self._expr = ""

    def _clear(self):
        self._expr = ""
        self._disp.setText("0")
