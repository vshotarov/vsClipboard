from PySide.QtGui import *
from PySide.QtCore import *


class Main(QWidget):
    def __init__(self):
        super(Main, self).__init__()

        self.buildUI()

    def buildUI(self):
        self.resize(300, 300)

        self.trayIcon = QSystemTrayIcon(QIcon("icon.png"), self)
        self.trayIcon.setToolTip("vsClipboard\nMonitoring clipboard")
        self.trayIcon.activated.connect(self.trayIconActivated)

        trayContextMenu = QMenu()
        actionShow = trayContextMenu.addAction("Show window")
        actionExit = trayContextMenu.addAction("Exit")
        actionShow.triggered.connect(self._show)
        actionExit.triggered.connect(self.close)
        self.trayIcon.setContextMenu(trayContextMenu)

        self.trayIcon.show()

        QLineEdit(self)

    def closeEvent(self, e):
        QApplication.instance().quit()

    def changeEvent(self, e):
        if e.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                e.ignore()
                QTimer.singleShot(100, self.hide)
                return

        super(Main, self).changeEvent(e)

    def trayIconActivated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show()

    def _show(self):
        if not self.isVisible():
            self.activateWindow()
            QTimer.singleShot(100, self.showNormal)
        else:
            self.showMinimized()