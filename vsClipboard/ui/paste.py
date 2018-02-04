from PySide.QtGui import *
from PySide.QtCore import *

from functools import partial

from .. import clipboard


ACTIVE_COLOUR = "#2980b9"
HOVER_COLOUR = "rgba(112,78,223, 255)"


class Button(QPushButton):
    def __init__(self, text, parent):
        super(Button, self).__init__(text, parent)

    def enterEvent(self, e):
        pass


class Paste(QWidget):
    showPaste = Signal(list)
    hidePaste = Signal()

    def __init__(self, parsedConfig=None):
        super(Paste, self).__init__()

        self.showPaste.connect(self.showAndPopulate)
        self.hidePaste.connect(self.hide)

        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        # self.setAttribute(Qt.WA_TranslucentBackground)

        self.buttons = []
        self.wheelScrolled = False
        self.active = None
        self.previousData = []

        self.buildUI()

        self.initConfig(parsedConfig)

        self.itemHeight = self.height() * .1

        with open("vsClipboard/ui/styles.css", "r") as f:
            self.setStyleSheet(f.read())

    def buildUI(self):
        screen = QCoreApplication.instance().desktop().availableGeometry()
        self.move(screen.x() + screen.width() - 400, screen.y())
        self.setFixedSize(400, screen.height())

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        self.setLayout(layout)

    def eventFilter(self, obj, event):
        # print obj, event

        return super(Paste, self).eventFilter(obj, event)

    def showAndPopulate(self, data):
        data = data[-self.historyLength:] if len(data) >= self.historyLength else data
        data = list(reversed(data))

        if data == self.previousData:
            self.show()
            self.activateWindow()
            return

        self.active = None
        self.previousData = data

        self.deselect()

        for each in reversed(self.buttons):
            self.layout().removeWidget(each)
            each.deleteLater()

        self.buttons = []

        for each in data:
            if each["hasFile"]:
                text = each["text"][0]
            elif each["unicode"]:
                text = each["unicode"]
            else:
                text = each["text"]
            text = text.strip().lstrip()
            text = text[:100] + "..." if len(text) > 100 else text
            text = "\n".join(text.split("\n")[:2]) + "..." if len(text.split("\n")) > 2 else text

            self.buttons.append(Button(text, self))
            # self.buttons[-1].setFocusPolicy(Qt.NoFocus)
            self.buttons[-1].setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
            self.buttons[-1].clicked.connect(partial(self.buttonClicked, each, self.buttons[-1]))
            self.layout().addWidget(self.buttons[-1])

        self.wheelScrolled = False
        self.select(self.buttons[0])
        self.show()
        self.activateWindow()

    def deselect(self):
        if self.active:
            self.active.setStyleSheet("")

    def select(self, button):
        self.active = button
        self.active.setStyleSheet("background-color:%s; margin:0; padding-left:10px; padding-right:10px;" % ACTIVE_COLOUR)

    def buttonClicked(self, data, button):
        self.deselect()
        self.select(button)

        clipboard.set(data)

    def initConfig(self, config):
        self.config = config
        self.historyLength = self.config["history_length"]

    def wheelEvent(self, e):
        currentButtonIndex = self.buttons.index(self.active)

        toSelectIndex = currentButtonIndex + 1 if e.delta() < 0 else currentButtonIndex - 1

        self.deselect()
        self.select(self.buttons[toSelectIndex % len(self.buttons)])

        self.wheelScrolled = True

        return super(Paste, self).wheelEvent(e)

    def hideEvent(self, e):
        if self.wheelScrolled:
            self.active.clicked.emit()

        return super(Paste, self).hideEvent(e)
