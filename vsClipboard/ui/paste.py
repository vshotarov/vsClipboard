from PySide.QtGui import *
from PySide.QtCore import *


class Paste(QWidget):
    showPaste = Signal()
    hidePaste = Signal()

    def __init__(self, parent=None):
        super(Paste, self).__init__(parent)

        self.showPaste.connect(self.show)
        self.hidePaste.connect(self.hide)

        self.buildUI()

    def buildUI(self):
        self.resize(100, 500)

        l = QLabel("hui", self)
