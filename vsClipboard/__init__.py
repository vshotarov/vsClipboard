from ui import Main, Paste
import hotkey
import clipboard

from PySide.QtGui import *
from PySide.QtCore import *
from functools import partial
import win32api
import win32con
import win32gui
import sys
import time

def start():
    def pastePress():
        t = QThread.currentThread()
        getattr(t, "showPaste").emit(clipboard.getHistory())
        setattr(t, "foregroundWindow", win32gui.GetForegroundWindow())
        print "Paste Pressed"

    def pasteRelease():
        t = QThread.currentThread()
        getattr(t, "hidePaste").emit()
        win32gui.SetForegroundWindow(getattr(t, "foregroundWindow"))
        hotkey.sendPasteMessage()
        print "Paste Released"

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    main = Main()
    paste = Paste()
    # paste.show()
    main.show()

    clipboardMonitorThread = QThread()
    clipboardMonitorThread.run = clipboard.monitorClipboard
    clipboardMonitorThread.start()

    pasteThread = QThread()
    pasteThread.run = partial(hotkey.listenForPaste, pastePress, pasteRelease)
    pasteThread.showPaste = paste.showPaste
    pasteThread.hidePaste = paste.hidePaste
    pasteThread.start()

    app.exec_()

    clipboardMonitorThread.do_run = False
    win32api.PostThreadMessage(getattr(pasteThread, "threadId"), win32con.WM_QUIT, 0, 0)

    clipboardMonitorThread.wait()
    pasteThread.wait()

    sys.exit()


class MyWidget(QWidget):
    hideSignal = Signal()

    def __init__(self):
        super(MyWidget, self).__init__()

        self.hideSignal.connect(self.hide)


def startA():
    print "Started vsClipboard"

    # def p():
    #     print "Pressed"

    def v():
        # hotkey.sendPasteMessage()
        print "Pressed V"

    # def r():
    #     hotkey.sendCopyMessage()
    #     clipboard.save()
    #     print "Released"

    def rp():
        hotkey.sendPasteMessage()
        print "Released"

    # import threading

    # t = threading.Thread(None, hotkey.listenForCopy, args=[p, r])
    # t.start()

    app = QApplication(sys.argv)
    w = MyWidget()
    w.resize(300, 300)

    # t2 = threading.Thread(None, hotkey.listenForPaste, args=[v, rp])
    # t2.start()

    # t2 = threading.Thread(None, clipboard.monitorClipboard)
    # t2.start()
    t = QThread()
    from functools import partial
    # t.run = partial(hotkey.listenForPaste, v, rp)
    t.run = clipboard.monitorClipboard
    t.hide = w.hideSignal
    t.start()

    w.show()
    app.exec_()

    t.do_run = False
    t.wait(1000 * 3)

    # win32api.PostThreadMessage(t.ident, win32con.WM_QUIT, 0, 0)
    # win32api.PostThreadMessage(t2.ident, win32con.WM_QUIT, 0, 0)
