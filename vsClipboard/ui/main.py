from PySide.QtGui import *
from PySide.QtCore import *


class Main(QWidget):
    def __init__(self):
        super(Main, self).__init__()

        self.buildUI()

    def buildUI(self):
        self.resize(300, 300)

        l = QLabel("This is the main window", self)

    def closeEvent(self, e):
        QApplication.instance().quit()
