from PySide.QtGui import *
from PySide.QtCore import *

from functools import partial

from .. import clipboard


class Paste(QWidget):
    showPaste = Signal(list)
    hidePaste = Signal()

    def __init__(self, parent=None):
        super(Paste, self).__init__(parent)

        self.showPaste.connect(self.showAndPopulate)
        self.hidePaste.connect(self.hide)

        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.buttons = []

        self.buildUI()

    def buildUI(self):
        self.resize(500, 500)

        layout = QVBoxLayout()
        # layout.setSizeConstraint(QLayout.SetNoConstraint)

        self.setLayout(layout)

    def showAndPopulate(self, data):
        # for button in self.buttons:
        #     button.deleteLater()

        # self.buttons = []

        for each in data:
            text = each["text"] if not each["hasFile"] else each["text"][0]
            self.buttons.append(QPushButton(text, self))
            self.buttons[-1].setFocusPolicy(Qt.NoFocus)
            self.buttons[-1].clicked.connect(partial(clipboard.set, each))
            self.layout().insertWidget(0, self.buttons[-1])

            if len(self.buttons) > 2:
                w = self.buttons.pop(0)
                self.layout().removeWidget(w)
                w.deleteLater()

        # self.resize(100, 500)
        self.show()
