'''This file contains the entry point of the application.

All the modules are tied into the UI in the start function.

We are spawning 2 threads

- one to monitor the clipboard
- one to listen for paste events and handle them

Additionally, a functionality of saving and reloading the
preferences while running is set up.

Once the application exits, we make sure the threads are
terminated fully.
'''
from ui import Main, Paste
import hotkey
import clipboard
import config

from PySide.QtGui import *
from PySide.QtCore import *
from functools import partial
import win32api
import win32con
import win32gui
import sys


def start():
    '''Creates and runs the application

    This function initializes a QApplication instance, sets up
    the threads needed for it to operate and runs them untill
    an application exit is registered, when all the processes
    are terminated.
    '''
    parsedConfig = config.parse()

    # Create the application
    app = QApplication(sys.argv)

    # App settings
    app.setQuitOnLastWindowClosed(False)

    # Create all pieces of the UI
    mainUI = Main(parsedConfig)
    pasteUI = Paste(parsedConfig)

    QApplication.instance().installEventFilter(pasteUI)

    mainUI.show()

    ######################
    # Register the custom clipboard format used for recognizing
    # internal clipboard changes
    clipboard.registerCustomClipboardFormat()

    ######################
    # Defining the functions that are being ran on pressing
    # and releasing the hotkey combination

    def pastePress():
        t = QThread.currentThread()
        getattr(t, "showPaste").emit(clipboard.getHistory())
        setattr(t, "foregroundWindow", win32gui.GetForegroundWindow())

    def pasteRelease():
        t = QThread.currentThread()
        getattr(t, "hidePaste").emit()
        win32gui.SetForegroundWindow(getattr(t, "foregroundWindow"))
        hotkey.sendPasteMessage()

    ######################
    # Create the two threads we need:
    #   1 - Monitoring thread
    #       Polls the clipboard for changes
    #   2 - Paste thread
    #       Listens for the Ctrl + V hotkey and handles the
    #       paste mechanism.
    clipboardMonitorThread = QThread()
    clipboardMonitorThread.run = clipboard.monitorClipboard
    clipboardMonitorThread.config = parsedConfig
    clipboardMonitorThread.start()

    pasteThread = QThread()
    pasteThread.run = partial(hotkey.listenForPaste, pastePress, pasteRelease)
    pasteThread.showPaste = pasteUI.showPaste
    pasteThread.hidePaste = pasteUI.hidePaste
    pasteThread.config = parsedConfig
    pasteThread.start()

    #######################
    # Handle updating the preferences in all threads, so
    # changes can be reflected on pressing the "Save"
    # (preferences) button

    def updateConfig():
        parsedConfig = config.parse()
        pasteUI.initConfig(parsedConfig)
        clipboardMonitorThread.config = parsedConfig
        pasteThread.config = parsedConfig

    # Connect the update function to the update signal
    mainUI.updatePreferences.connect(updateConfig)

    #########################
    # Run the app
    app.exec_()

    # Once we exit we need to take care of the threads
    #
    # Set do_run to false as it's being checked against
    # in the while loop, so it causes it to break
    clipboardMonitorThread.do_run = False

    # Send the WM_QUIT message to the paste thread which
    # is being listened for in the while loop and it's
    # causing it to break
    win32api.PostThreadMessage(getattr(pasteThread, "threadId"), win32con.WM_QUIT, 0, 0)

    # Join the threads in the main one to make sure they
    # are completely terminated
    clipboardMonitorThread.wait()
    pasteThread.wait()

    # Exit
    sys.exit()
