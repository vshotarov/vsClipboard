from ctypes import wintypes

import ctypes
import win32con

import time

u32 = ctypes.windll.user32

C_KEY_CODE = ord("C")
V_KEY_CODE = ord("V")


def _hold(keyCode, funcPress, funcRelease):
    state = u32.GetKeyState(keyCode)
    funcPress()
    while u32.GetKeyState(keyCode) == state:
        time.sleep(.01)
    funcRelease()


def _listen(keyCode, ident, funcPress, funcRelease):
    if not u32.RegisterHotKey(None, ident, win32con.MOD_CONTROL | 0x4000, keyCode):
        raise RuntimeError("Could not register hotkey " + str(ident) + " " + str(keyCode))

    try:
        msg = wintypes.MSG()
        while u32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == win32con.WM_HOTKEY:
                _hold(keyCode, funcPress, funcRelease)
            u32.TranslateMessage(ctypes.byref(msg))
            u32.DispatchMessageA(ctypes.byref(msg))
    finally:
        u32.UnregisterHotKey(None, ident)


def listenForCopy(funcPress, funcRelease):
    _listen(C_KEY_CODE, 0, funcPress, funcRelease)


def listenForPaste(funcPress, funcRelease):
    _listen(V_KEY_CODE, 1, funcPress, funcRelease)
