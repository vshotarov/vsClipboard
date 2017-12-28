import hotkey


from PySide.QtGui import *
from PySide.QtCore import *
import win32api
import win32con
import sys


def start():
    print "Started vsClipboard"

    def p():
        print "Pressed"

    def v():
        print "Pressed V"

    def r():
        print "Released"

    import threading

    t = threading.Thread(None, hotkey.listenForCopy, args=[p, r])
    t.start()

    t2 = threading.Thread(None, hotkey.listenForPaste, args=[v, r])
    t2.start()

    app = QApplication(sys.argv)
    w = QWidget()
    w.resize(300, 300)
    w.show()
    app.exec_()

    win32api.PostThreadMessage(t.ident, win32con.WM_QUIT, 0, 0)
    win32api.PostThreadMessage(t2.ident, win32con.WM_QUIT, 0, 0)
