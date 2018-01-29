from PySide.QtGui import *
from PySide.QtCore import *


class TitleBar(QWidget):
    '''A custom title bar for the main widget.

    Just wanted something a bit more in line with the look of
    the "Paste" widget than the default windows title bar.
    '''

    def __init__(self):
        '''Constructs the title bar.
        '''
        super(TitleBar, self).__init__()

        # Allowing styling of the background via stylesheets
        self.setAttribute(Qt.WA_StyledBackground)

        self.buildUI()

    def buildUI(self):
        '''Creates the UI elements.
        '''
        self.setLayout(QHBoxLayout())

        windowTitle = QLabel("vsClipboard")
        self.minimizeButton = QPushButton("-")
        self.closeButton = QPushButton("x")

        self.layout().addWidget(windowTitle)
        self.layout().addStretch(1)
        self.layout().addWidget(self.minimizeButton)
        self.layout().addWidget(self.closeButton)
