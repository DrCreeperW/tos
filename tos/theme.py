# tos theme — max contrast, flat, pixel, lowercase
# only colors: red (#8b0000), yellow (#ffd700), dark red (#5c0000), black, white

from PyQt5.QtGui import QColor, QFont


class Colors:
    RED_BG      = QColor(0x8B, 0x00, 0x00)
    RED_DARK    = QColor(0x5C, 0x00, 0x00)
    YELLOW_MAIN = QColor(0xFF, 0xD7, 0x00)
    YELLOW_DIM  = QColor(0xCC, 0xAC, 0x00)
    BLACK       = QColor(0x00, 0x00, 0x00)
    WHITE       = QColor(0xFF, 0xFF, 0xFF)

    @staticmethod
    def to_css(c):
        return c.name()

    @classmethod
    def bg_css(cls):
        return cls.RED_BG.name()

    @classmethod
    def dark_css(cls):
        return cls.RED_DARK.name()

    @classmethod
    def yellow_css(cls):
        return cls.YELLOW_MAIN.name()

    @classmethod
    def dim_css(cls):
        return cls.YELLOW_DIM.name()


class Fonts:
    DEFAULT_FONT = "More Perfect DOS VGA"

    @staticmethod
    def title():
        f = QFont(Fonts.DEFAULT_FONT)
        f.setPixelSize(14)
        f.setBold(True)
        return f

    @staticmethod
    def body():
        f = QFont(Fonts.DEFAULT_FONT)
        f.setPixelSize(12)
        return f

    @staticmethod
    def small():
        f = QFont(Fonts.DEFAULT_FONT)
        f.setPixelSize(10)
        return f

    @staticmethod
    def huge():
        f = QFont(Fonts.DEFAULT_FONT)
        f.setPixelSize(22)
        f.setBold(True)
        return f


class Sizes:
    TASKBAR_HEIGHT = 28
    LAUNCHER_WIDTH = 170
    MIN_WIN_WIDTH  = 300
    MIN_WIN_HEIGHT = 200
