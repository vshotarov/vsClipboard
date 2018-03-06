'''Managing the intialization, monitoring and cleanup of the Ctrl + V hotkey.

This module interacts with the hotkey functionalities of Windows, to provide
us with a way to non-destructively register a callback to be fired whenever
Ctrl + V is pressed and held for more than a threshold (.15 seconds in this
case).

Attributes:
    u32: A shortened namespace for ctypes.windll.user32
    V_KEY_CODE: The virtual key code for the "V" key specified in
    https://msdn.microsoft.com/en-us/library/windows/desktop/dd375731(v=vs.85).aspx
'''
from ctypes import wintypes
from PySide.QtCore import *
import logging

import ctypes
import win32con
import win32api

import threading
import time

import config

u32 = ctypes.windll.user32  # Make it easier to access the namespace

V_KEY_CODE = ord("V")  # The key code for the "V" key that needs to be passed to win functions


def _hold(funcPress, funcRelease):
    '''This function is triggered on pressing the paste hotkey and waits for a release.

    Whenever the user pesses the paste key combination, this function gets the current
    state of the "V" key in order to detect whether the key was just tapped or is
    being held down.

    If it is just being tapped, then we wait for a release and just trigger the normal
    paste functionality, before exiting.

    If it is being held pressed down for more than .15 seconds, then the funcPress
    callable is executed, followed by a while loop waiting for the key to be released.
    Once it is released the funcRelease callable is executed.

    Args:
        funcPress: a callable to execute once the user is held the key down for more than .15 seconds
        funcRelease: a callable to execute once the user has released the key after initially having
        held it down for more than .15 seconds
    '''
    keyCode = V_KEY_CODE

    vState = u32.GetKeyState(keyCode)
    ctrlState = u32.GetKeyState(win32con.VK_CONTROL)
    vPressed = (vState >> 8) & 1
    ctrlPressed = (ctrlState >> 8) & 1

    if not (vPressed and ctrlPressed):
        # Getting around a bug where the hotkey is triggered by releasing a key which has 
        # been pressed together with the Ctrl + V combination.
        #
        # Example - If I press Ctrl + A + V it triggers the Ctl + V hotkey. But if at any
        # point I release A, it triggers it again, which means that after releasing the 
        # Ctrl + V hotkey, the _hold function will be called again. 
        return

    released = True
    startTime = time.time()

    while u32.GetKeyState(keyCode) == vState and u32.GetKeyState(win32con.VK_CONTROL) == ctrlState:
        if time.time() - startTime > config.get("hold_before_showing"):
            released = False
            break
        # time.sleep(.01)

    if released:
        sendPasteMessage()
        return

    funcPress()

    while u32.GetKeyState(keyCode) == vState and u32.GetKeyState(win32con.VK_CONTROL) == ctrlState:
        time.sleep(.01)

    funcRelease()


def _registerHotkey():
    '''Registers the Ctrl + V hotkey combination.

    The hotkey is triggered again only after the previous press has been released.
    That is specified by the 0x4000 flag.

    The hotkey is initialized with ID set to 1, so it can be unregistered later on, by
    passing the same id.

    Raises:
        RuntimeError: If for any reason the hotkey cannot be initialized raises an error.
    '''
    if not u32.RegisterHotKey(None, 1, win32con.MOD_CONTROL | 0x4000, V_KEY_CODE):
        raise RuntimeError("Could not register hotkey for Ctl + V, 1 " + str(V_KEY_CODE))


def _unregisterHotkey():
    '''Unregisters the Ctrl + V hotkey.
    '''
    u32.UnregisterHotKey(None, 1)


def _pressKey(keys):
    '''Simulates a key release followed by key press for the passed in keys.

    The reason for releasing before pressing is to make sure that our press
    triggers the internal paste hotkey.

    Args:
        keys: A list of keys to press.
    '''
    ctrlState = (u32.GetKeyState(win32con.VK_CONTROL) >> 8) & 1
    for code in keys:
        win32api.keybd_event(code, 0, 0, 0)
    for code in keys:
        win32api.keybd_event(code, 0, win32con.KEYEVENTF_KEYUP, 0)
    if ctrlState:
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)


def sendPasteMessage():
    '''Simulates a Ctrl + V key press without triggering our custom hotkey.

    This function unregisters the hotkey we have previously registered,
    simulates the Ctrl + V key press combination and after that registers
    our custom hotkey once more.

    The unregister and register limbo is needed to bypass our own callback
    as otherwise we are falling into an infinite loop.
    '''
    _unregisterHotkey()
    _pressKey([win32con.VK_CONTROL, V_KEY_CODE])
    _registerHotkey()


def listenForPaste(funcPress, funcRelease):
    '''Registers the Ctrl + V hotkey and monitors it untill the thread receives
    a WM_QUIT message from the main thread.

    This is the entry point of the monitoring system for the Ctrl + V combination.

    It registers the hotkey and sends the current thread's ID to the main thread,
    so we can send a QUIT message from the main to this one when we want to exit.

    On exit we are checking whether we have a database connection stored on the
    thread and if we do, we close it.

    Args:
        funcPress: A callable to be executed when the hotkey is pressed for more than .15 seconds
        funcRelease: A callable to be executed when the hotkey is released after being triggered
    '''
    _registerHotkey()

    t = QThread.currentThread()
    t.threadId = threading.currentThread().ident

    try:
        msg = wintypes.MSG()
        while u32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == win32con.WM_HOTKEY:
                _hold(funcPress, funcRelease)
                continue
            if msg.message == win32con.WM_QUIT:
                break
            u32.TranslateMessage(ctypes.byref(msg))
            u32.DispatchMessageA(ctypes.byref(msg))
    finally:
        u32.UnregisterHotKey(None, 1)
        logging.info("Unregistered the Ctrl + V hotkey")

        if hasattr(t, "dbConnection"):
            getattr(t, "dbConnection").close()
            logging.info("Closed dbConnection in paste thread")
