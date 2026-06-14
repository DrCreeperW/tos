# tos tosp format — custom save format for TOS Paint (.tosp)
#
# Layout of a .tosp file:
#   bytes 0..3   : magic  b'TOSP'
#   byte  4      : version (1)
#   bytes 5..    : PNG-encoded image data (lossless, compact)
#
# The PNG payload is produced/consumed via QBuffer + QImage, so the format is
# both compact and rock-solid on any platform. The TOSP magic header makes it a
# genuine, recognisable TOS format rather than a plain PNG.

from PyQt5.QtCore import QBuffer, QByteArray
from PyQt5.QtGui import QImage

MAGIC = b"TOSP"
VERSION = 1


def encode(qimage):
    """Encode a QImage into .tosp bytes (magic + version + PNG payload)."""
    buf = QBuffer()
    buf.open(QBuffer.ReadWrite)
    qimage.save(buf, "PNG")
    png = bytes(buf.data())
    buf.close()
    return MAGIC + bytes([VERSION]) + png


def save(path, qimage):
    """Write a QImage to `path` as a .tosp file."""
    with open(path, "wb") as f:
        f.write(encode(qimage))


def decode(data):
    """Decode .tosp bytes into a QImage. Raises ValueError if not a tosp file."""
    if len(data) < len(MAGIC) + 1:
        raise ValueError("file too small to be a .tosp file")
    if data[:len(MAGIC)] != MAGIC:
        raise ValueError("not a .tosp file (bad magic header)")
    png = data[len(MAGIC) + 1:]   # skip magic + version byte
    img = QImage()
    if not img.loadFromData(QByteArray(png), "PNG"):
        raise ValueError("could not decode image data in .tosp file")
    return img


def load(path):
    """Read a .tosp file and return its QImage."""
    with open(path, "rb") as f:
        return decode(f.read())
