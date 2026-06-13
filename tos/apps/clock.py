# tos clock — digital & analog toggle
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QPainter, QColor, QFont
from theme import Fonts


class Clock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._mode = "digital"  # "digital" or "analog"
        self._build()

    def _build(self):
        lo = QVBoxLayout(self)
        lo.setContentsMargins(8, 8, 8, 8)

        self._display = QLabel("00:00:00")
        self._display.setFont(Fonts.huge())
        self._display.setAlignment(Qt.AlignCenter)
        self._display.setStyleSheet("color: #FFD700; background: transparent;")
        lo.addWidget(self._display, stretch=1)

        toggle = QPushButton("  switch  ")
        toggle.setFont(Fonts.body())
        toggle.setFixedHeight(28)
        toggle.setStyleSheet(
            "QPushButton { background: #FFD700; color: #000; border: 1px solid #000; "
            "font-family: More Perfect DOS VGA; font-size: 12px; font-weight: bold; }")
        toggle.clicked.connect(self._toggle)
        lo.addWidget(toggle)

        self._tm = QTimer(self)
        self._tm.timeout.connect(self._tick)
        self._tm.start(1000)
        self._tick()

    def _tick(self):
        now = QTime.currentTime()
        if self._mode == "digital":
            self._display.setText(now.toString("HH:mm:ss"))
            self._display.setFont(Fonts.huge())
        else:
            self._display.setText("")
        self.update()

    def _toggle(self):
        self._mode = "analog" if self._mode == "digital" else "digital"
        self._tick()

    def paintEvent(self, e):
        super().paintEvent(e)
        if self._mode == "analog":
            p = QPainter(self)
            p.setRenderHint(QPainter.Antialiasing, True)
            cx, cy = self.width() // 2, self.height() // 2 - 10
            r = min(cx, cy) - 10
            r = max(r, 50)

            # face
            p.setPen(QColor(0, 0, 0))
            p.setBrush(QColor(0x5C, 0x00, 0x00))
            p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

            # tick marks
            now = QTime.currentTime()
            h = now.hour() % 12
            m = now.minute()
            s = now.second()

            # hour hand
            ha = (h + m / 60) * 30 - 90
            import math
            hx = cx + math.cos(math.radians(ha)) * r * 0.5
            hy = cy + math.sin(math.radians(ha)) * r * 0.5
            p.setPen(QColor(0xFF, 0xD7, 0x00))
            p.drawLine(cx, cy, int(hx), int(hy))

            # minute hand
            ma = m * 6 - 90
            mx = cx + math.cos(math.radians(ma)) * r * 0.7
            my = cy + math.sin(math.radians(ma)) * r * 0.7
            p.setPen(QColor(0xFF, 0xD7, 0x00))
            p.drawLine(cx, cy, int(mx), int(my))

            # second hand
            sa = s * 6 - 90
            sx = cx + math.cos(math.radians(sa)) * r * 0.8
            sy = cy + math.sin(math.radians(sa)) * r * 0.8
            p.setPen(QColor(0xCC, 0xAC, 0x00))
            p.drawLine(cx, cy, int(sx), int(sy))

            p.end()
