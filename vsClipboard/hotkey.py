from ctypes import wintypes

import ctypes
import win32con
import win32api

import time

u32 = ctypes.windll.user32

C_KEY_CODE = ord("C")
V_KEY_CODE = ord("V")


def _hold(keyCode, funcPress, funcRelease):
    funcPress()
    state = u32.GetKeyState(keyCode)
    while u32.GetKeyState(keyCode) == state:
        time.sleep(.01)
    funcRelease()


def registerHotkey(ident, keyCode):
    if not u32.RegisterHotKey(None, ident, win32con.MOD_CONTROL | 0x4000, keyCode):
        raise RuntimeError("Could not register hotkey " + str(ident) + " " + str(keyCode))


def unregisterHotkey(ident):
    u32.UnregisterHotKey(None, ident)


def _listen(keyCode, ident, funcPress, funcRelease):
    registerHotkey(ident, keyCode)

    try:
        msg = wintypes.MSG()
        while u32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == win32con.WM_HOTKEY:
                _hold(keyCode, funcPress, funcRelease)
                continue
            u32.TranslateMessage(ctypes.byref(msg))
            u32.DispatchMessageA(ctypes.byref(msg))
    finally:
        u32.UnregisterHotKey(None, ident)


def listenForCopy(funcPress, funcRelease):
    _listen(C_KEY_CODE, 0, funcPress, funcRelease)


def listenForPaste(funcPress, funcRelease):
    _listen(V_KEY_CODE, 1, funcPress, funcRelease)


def sendCopyMessage():
    unregisterHotkey(0)
    _pressKey([win32con.MOD_CONTROL, C_KEY_CODE])
    registerHotkey(0, C_KEY_CODE)


def sendPasteMessage():
    unregisterHotkey(1)
    _pressKey([win32con.MOD_CONTROL, V_KEY_CODE])
    registerHotkey(1, V_KEY_CODE)


def _pressKey(keys):
    for code in keys:
        win32api.keybd_event(code, 0, 0, 0)
    for code in keys:
        win32api.keybd_event(code, 0, win32con.KEYEVENTF_KEYUP, 0)
