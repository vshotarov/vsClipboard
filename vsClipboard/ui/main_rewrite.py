from PySide.QtGui import *
from PySide.QtCore import *

from .. import config
from titleBar import TitleBar


class Main(QWidget):
    updatePreferences = Signal()

    def __init__(self, _config):
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
        self.setLayout(QVBoxLayout())

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

        bodyLayout.setColumnStretch(1,1)
        bodyLayout.setColumnStretch(0,10)

        bodyLayout.setContentsMargins(10, 10, 10, 10)

        # Add elements to main UI
        self.layout().addWidget(titleBar)
        self.layout().addLayout(bodyLayout)

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setAlignment(Qt.AlignTop)

        self.resize(350, self.minimumSizeHint().height())
