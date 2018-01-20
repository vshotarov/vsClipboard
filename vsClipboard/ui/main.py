from PySide.QtGui import *
from PySide.QtCore import *

from .. import config

class Main(QWidget):
    updatePreferences = Signal()

    def __init__(self, _config):
        super(Main, self).__init__()

        self.config = _config

        self.buildUI()

    def buildUI(self):
        self.resize(300, 300)

        self.setLayout(QVBoxLayout())

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

        t = QLineEdit(self)

        self.historyLengthSpinBox = QSpinBox(self)
        self.historyLengthSpinBox.setMinimum(1)
        self.historyLengthSpinBox.setMaximum(50)
        self.historyLengthSpinBox.setValue(self.config["history_length"])

        self.holdBeforeShowSpinBox = QDoubleSpinBox(self)
        self.holdBeforeShowSpinBox.setMinimum(.01)
        self.holdBeforeShowSpinBox.setMaximum(5)
        self.holdBeforeShowSpinBox.setValue(self.config["hold_before_showing"])

        self.pollIntervalSpinBox = QDoubleSpinBox(self)
        self.pollIntervalSpinBox.setMinimum(.01)
        self.pollIntervalSpinBox.setMaximum(5)
        self.pollIntervalSpinBox.setValue(self.config["poll_clipboard_interval"])

        self.savePreferencesButton = QPushButton("Save preferences", self)
        self.savePreferencesButton.clicked.connect(self.savePreferences)

        self.layout().addWidget(t)
        self.layout().addWidget(self.historyLengthSpinBox)
        self.layout().addWidget(self.holdBeforeShowSpinBox)
        self.layout().addWidget(self.pollIntervalSpinBox)
        self.layout().addWidget(self.savePreferencesButton)

        with open("vsClipboard/ui/styles.css", "r") as f:
            self.setStyleSheet(f.read())

    def savePreferences(self):
        d = {}
        d["history_length"] = self.historyLengthSpinBox.value()
        d["hold_before_showing"] = self.holdBeforeShowSpinBox.value()
        d["poll_clipboard_interval"] = self.pollIntervalSpinBox.value()
        config.save(d)
        self.updatePreferences.emit()

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