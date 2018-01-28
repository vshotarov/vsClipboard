from PySide.QtGui import *
from PySide.QtCore import *


class TitleBar(QWidget):
    def __init__(self):
        super(TitleBar, self).__init__()

        self.setAttribute(Qt.WA_StyledBackground)

        self.buildUI()

    def buildUI(self):
        self.setLayout(QHBoxLayout())

        windowTitle = QLabel("vsClipboard")
        minimizeButton = QPushButton("-")
        closeButton = QPushButton("x")

        self.layout().addWidget(windowTitle)
        self.layout().addStretch(1)
        self.layout().addWidget(minimizeButton)
        self.layout().addWidget(closeButton)

        # self.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
