from PySide.QtGui import *
from PySide.QtCore import *

from functools import partial

from .. import clipboard


ACTIVE_COLOUR = "rgba(135, 23, 23, 255)"
HOVER_COLOUR = "rgba(112,78,223, 255)"


class Button(QPushButton):
    def __init__(self, text, parent):
        super(Button, self).__init__(text, parent)

    def enterEvent(self, e):
        pass

class Paste(QWidget):
    showPaste = Signal(list)
    hidePaste = Signal()

    def __init__(self, parent=None):
        super(Paste, self).__init__(parent)

        self.showPaste.connect(self.showAndPopulate)
        self.hidePaste.connect(self.hide)

        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        # self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.buttons = []
        self.active = None
        self.previousData = []

        self.buildUI()

        self.itemHeight = self.height() * .1

        self.setStyleSheet("""
QPushButton:hover{background-color:%s}
QPushButton{background-color:#444; border: 0; border-bottom: 1px solid black;}""" % HOVER_COLOUR);

    def buildUI(self):
        screen = QCoreApplication.instance().desktop().availableGeometry()
        self.move(screen.x() + screen.width() - 400, screen.y())
        self.setFixedSize(400, screen.height())

        layout = QVBoxLayout()
        layout.setSpacing(0)

        self.setLayout(layout)

    def showAndPopulate(self, data):
        data = list(reversed(data[-10:])) if len(data) >= 10 else data

        if data == self.previousData:
            self.show()
            return

        self.active = None
        self.previousData = data

        self.deselect()

        for each in reversed(self.buttons):
            self.layout().removeWidget(each)
            each.deleteLater()

        self.buttons = []

        for each in data:
            text = each["text"] if not each["hasFile"] else each["text"][0]
            text = text.strip().lstrip()
            text = text[:100] + "..." if len(text) > 100 else text
            text = "\n".join(text.split("\n")[:2]) + "..." if len(text.split("\n")) > 2 else text

            self.buttons.append(Button(text, self))
            self.buttons[-1].setFocusPolicy(Qt.NoFocus)
            self.buttons[-1].setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
            self.buttons[-1].clicked.connect(partial(self.buttonClicked, each, self.buttons[-1]))
            self.layout().addWidget(self.buttons[-1])

        self.select(self.buttons[0])
        self.show()

    def deselect(self):
        if self.active:
            self.active.setStyleSheet("")

    def select(self, button):
        self.active = button
        self.active.setStyleSheet("background-color:%s" % ACTIVE_COLOUR)

    def buttonClicked(self, data, button):
        self.deselect()
        self.select(button)

        clipboard.set(data)

