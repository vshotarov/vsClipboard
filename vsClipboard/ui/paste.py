from PySide.QtGui import *
from PySide.QtCore import *

from functools import partial

from .. import clipboard


class Paste(QWidget):
    '''This is the ui to display and select clipboard history
    items.

    The visibility of this widget is triggered by holding the "ctrl + v" hotkey 
    for longer than the value specified in the config for "hold_before_showing".

    The mouse wheel can be used to scroll through the list and select different
    entries.

    Once the "ctrl+v" hotkey is released, the widget is hidden and the currently
    selected item is pasted.

    Attributes:
        showPaste: a custom signal which triggers the visibility of the widget.
        hidePaste: a custom signal which hides the widget
    '''
    showPaste = Signal(list)
    hidePaste = Signal()

    def __init__(self, _config=None):
        '''Constructs the widget.

        We set the needed flags and attributes and we build the
        actual UI. 

        Additionally, we store the passed in parsed _config, so we can use the
        correct length when displaying the history.

        Args:
            _config: Preferences as a dictionary.
        '''
        super(Paste, self).__init__()

        # Connect custom signals
        self.showPaste.connect(self.showAndPopulate)
        self.hidePaste.connect(self.hide)

        # Set flags and attributes
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # States and storage
        self.buttons = []
        self.wheelScrolled = False
        self.active = None
        self.previousData = []

        # Build the ui elements
        self.buildUI()

        # Handle preferences
        self.initConfig(_config)

        # Apply stylesheet
        with open("vsClipboard/ui/styles.css", "r") as f:
            self.setStyleSheet(f.read())

    def focusNextPrevChild(self, down):
        '''This event is called when pressing the Up and Down arrow keys.
        
        I reimplement it in order to support using up and down arrow keys
        for navigating the selection.
        
        Args:
            down: Usually this argument is called next as it specifies whether 
            to go forward or backward, but in my case it's clearer to call it
            down.
        
        Returns:
            bool
        '''
        if down:
            self.selectNext()
        else:
            self.selectPrevious()
        
        # return super(Paste, self).focusNextPrevChild(*args)
        return True

    def buildUI(self):
        '''Creates and prepares the layout for displaying the clipboard
        history.'''
        screen = QCoreApplication.instance().desktop().availableGeometry()
        self.move(screen.x() + screen.width() - 400, screen.y())
        self.setFixedSize(400, screen.height())

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

    def showAndPopulate(self, data):
        '''Receives the clipboard history, displays it and shows the widget.

        This function grabs the latest :preferences["history_length"] elements
        from the clipboard history and displays them. If there hasn't been a
        change then this function shows the widget and returns early.

        Args:
            data: The clipboard history
        '''
        # Grab the latest chunk of the history
        data = data[-self.historyLength:] if len(data) >= self.historyLength \
            else data
        data = list(reversed(data))

        # Check if we even need to rebuild the list
        if data == self.previousData:
            self.show()
            self.activateWindow()
            return

        # If there has been a change in the clipboard history then release the
        # currently active item and store the new data
        self.active = None
        self.previousData = data

        self.deselect()

        # Clean the list
        for each in self.buttons:
            self.layout().removeWidget(each)
            each.deleteLater()

        self.buttons = []

        # Build the new list
        for each in data:
            # As nothing else but text is currently supported, we need to check
            # the data type in order to pick the correct portion to display
            text = each["unicode"] if each["unicode"] else each["text"]
            if each["hasFile"]:
                text = text[0]

            # Clean up the text to be displayed nicely in the ui
            # - strip out leading and multiple spaces
            # - clamp the length to a 100 characters
            # - limit the new lines to 2
            text = text.strip().lstrip()
            text = text[:100] + "..." if len(text) > 100 else text
            text = "\n".join(text.split("\n")[:2]) + "..." \
                if len(text.split("\n")) > 2 else text

            # Add new button and connect it to the self.buttonClicked function
            # to handle it
            self.buttons.append(QPushButton(text, self))
            self.buttons[-1].setSizePolicy(
                QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
            self.buttons[-1].clicked.connect(
                partial(self.buttonClicked, each, self.buttons[-1]))
            self.layout().addWidget(self.buttons[-1])

        # Since there has been a change in the clipboard history we need to
        # select the latest clipboard item and clean up the wheelScrolled state
        self.wheelScrolled = False
        self.select(self.buttons[0])
        self.show()
        self.activateWindow()

    def deselect(self):
        '''Deselects the currently active item.

        All this means is we remove the "selected" objectName and force a 
        recalculation of the styleSheet so the change is reflected.
        '''
        if self.active:
            self.active.setObjectName("")
            self.active.setStyleSheet("")

    def select(self, button):
        '''Apply the selected colour to the passed in button

        We apply the "selected" objectName, which acts as a CSS class and 
        force a recalculation of the styleSheet.

        Args:
            button: The button to be "selected"
        '''
        self.active = button
        self.active.setObjectName("selected")
        self.active.setStyleSheet("")

    def buttonClicked(self, data, button):
        '''Applies the "selected" state to the specified button and sets the
        clipboard to the data, so it can be pasted.

        Args:
            data: The data coming from the clipboard history database
            button: The button widget
        '''
        self.deselect()
        self.select(button)

        clipboard.set(data)

    def initConfig(self, config):
        '''Stores the history_length preference, so it can be reflected in the
        widget.

        Args:
            config: The preferences as a dictionary
        '''
        self.historyLength = config["history_length"]

    def selectNext(self):
        '''Selects the next entry in the clipboard history.'''
        currentButtonIndex = self.buttons.index(self.active)

        self.deselect()
        self.select(self.buttons[(currentButtonIndex + 1) % len(self.buttons)])

    def selectPrevious(self):
        '''Selects the previous entry in the clipboard history.'''
        currentButtonIndex = self.buttons.index(self.active)

        self.deselect()
        self.select(self.buttons[(currentButtonIndex - 1) % len(self.buttons)])

    def wheelEvent(self, e):
        '''Override of the default wheel event, so we can cycle through the
        clipboard history with a wheel scroll.

        Args:
            e: the event
        '''
        if e.delta() < 0:
            self.selectNext()
        else:
            self.selectPrevious()

        # Store the fact that we have scrolled so we can pick the correct
        # item on exiting
        self.wheelScrolled = True

        return super(Paste, self).wheelEvent(e)

    def hideEvent(self, e):
        '''Ovrride the default hide event, so we can handle applying the data
        from the currently active element if it was specified by a wheel scroll.

        Args:
            e: the event
        '''
        if self.wheelScrolled:
            self.active.clicked.emit()

        return super(Paste, self).hideEvent(e)
