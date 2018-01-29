from PySide.QtGui import *
from PySide.QtCore import *

from .. import config
from titleBar import TitleBar


class Main(QWidget):
    '''This is the main window of the program.
    
    The window is mainly used for changing the preferences, but
    also for terminating the application.
    
    Attributes:
        updatePreferences: A custom signal responsible for letting
        the other parts of the program know about changes in the
        preferences.
    '''
    updatePreferences = Signal()

    def __init__(self, _config):
        '''Constructs the widget.
        
        We set the needed flags and attributes and we build the
        actual UI, using the passed in _config as the default
        values of the preferences.
        
        Args:
            _config: Preferences as a dictionary.
        '''
        super(Main, self).__init__()

        self.config = _config

        # UI setup
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground)

        # Build UI elements
        self.buildUI()

        # Load stylesheet
        with open("vsClipboard/ui/styles.css", "r") as f:
            self.setStyleSheet(f.read())

    def buildUI(self):
        '''Creates the UI elements and arranges them in proper layouts.
        '''
        self.setLayout(QVBoxLayout())

        # Building the UI elements and arranging them
        # in the respective layouts

        # Custom title bar
        titleBar = TitleBar()

        # Body
        bodyLayout = QGridLayout()
        # Preferences
        # Length of history to show
        historyLengthLabel = QLabel("History length")

        historyLengthField = QSpinBox()
        historyLengthField.setMinimum(1)
        historyLengthField.setMaximum(50)
        historyLengthField.setValue(self.config["history_length"])

        # Time (in seconds) to wait before showing the clipboard history
        # when Ctrl + V is pressed
        holdTimeLabel = QLabel("Hold before showing (sec)")

        holdTimeField = QDoubleSpinBox()
        holdTimeField.setMinimum(.01)
        holdTimeField.setMaximum(5)
        holdTimeField.setValue(self.config["hold_before_showing"])

        # Interval (in seconds) to poll the clipboard for changes
        clipboardPollIntervalLabel = QLabel("Clipboard poll interval (sec)")

        clipboardPollIntervalField = QDoubleSpinBox()
        clipboardPollIntervalField.setMinimum(.01)
        clipboardPollIntervalField.setMaximum(5)
        clipboardPollIntervalField.setValue(self.config["poll_clipboard_interval"])

        # Save preferences button
        savePreferencesButton = QPushButton("Save preferences")

        # Add preference elements to body layout
        bodyLayout.addWidget(historyLengthLabel, 1, 0)
        bodyLayout.addWidget(historyLengthField, 1, 1)

        bodyLayout.addWidget(holdTimeLabel, 2, 0)
        bodyLayout.addWidget(holdTimeField, 2, 1)

        bodyLayout.addWidget(clipboardPollIntervalLabel, 3, 0)
        bodyLayout.addWidget(clipboardPollIntervalField, 3, 1)

        bodyLayout.addWidget(savePreferencesButton, 4, 0, 1, 2)

        bodyLayout.setColumnStretch(1, 1)
        bodyLayout.setColumnStretch(0, 10)

        bodyLayout.setContentsMargins(10, 10, 10, 10)

        # Add elements to main UI
        self.layout().addWidget(titleBar)
        self.layout().addLayout(bodyLayout)

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setAlignment(Qt.AlignTop)

        self.resize(350, self.minimumSizeHint().height())

        # Create the system tray icon
        trayIcon = QSystemTrayIcon(QIcon("icon.png"), parent=self)
        trayIcon.setToolTip("vsClipboard\nMonitoring clipboard")
        trayIcon.show()

        trayContextMenu = QMenu()
        actionShow = trayContextMenu.addAction("Preferences")
        actionExit = trayContextMenu.addAction("Exit")
        trayIcon.setContextMenu(trayContextMenu)

        # Connecting signals and slots
        # Window related
        titleBar.minimizeButton.clicked.connect(self.showMinimized)
        titleBar.closeButton.clicked.connect(self.close)

        # Tray icon
        trayIcon.activated.connect(self.trayIconActivated)
        actionShow.triggered.connect(self._show)
        actionExit.triggered.connect(self.close)

        # Preferences
        savePreferencesButton.clicked.connect(self.savePreferences)

        # Store fields for access across the class
        self.historyLengthField = historyLengthField
        self.holdTimeField = holdTimeField
        self.clipboardPollIntervalField = clipboardPollIntervalField

    def trayIconActivated(self, reason):
        '''Handles activating the window from the system tray.

        Args:
            reason: How was the icon triggered
        '''
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show()

    def savePreferences(self):
        '''Saves the current preferences to the config file.

        After the preferences are saved the updatePreferences signal is
        emitted, which triggers an update on all other parts of the program

        - the Paste widget
        - the clipboard monitoring thread
        - the hotkey thread
        '''
        newSettings = {}
        newSettings["history_length"] = self.historyLengthField.value()
        newSettings["hold_before_showing"] = self.holdTimeField.value()
        newSettings["poll_clipboard_interval"] = self.clipboardPollIntervalField.value()

        config.save(newSettings)

        self.updatePreferences.emit()

    def _show(self):
        '''Handles toggling visibility of the widget.

        If the window is currently visible this function minimizes it.

        If it is currently hidden, then it activates the window and shows
        the widget.
        '''
        if not self.isVisible():
            self.activateWindow()
            QTimer.singleShot(100, self.showNormal)
        else:
            self.showMinimized()

    def changeEvent(self, e):
        '''Handles minimizing.

        Since we are minimizing to the system tray, we need to hide the widget
        when minimize is requested.

        Args:
            e: The change event
        '''
        if e.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                e.ignore()
                QTimer.singleShot(100, self.hide)
                return

        super(Main, self).changeEvent(e)

    def closeEvent(self, e):
        '''Exits the application.

        Since the QApplication instance is set to not close on last window
        closed, we need to make sure it is closed as we close this main window.

        Args:
            e: The close event
        '''
        QApplication.instance().quit()
