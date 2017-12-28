from ctypes import wintypes

import ctypes
import win32con
import win32clipboard

import database


u32 = ctypes.windll.user32


def getClipboardFormats():
    win32clipboard.OpenClipboard()

    available = []
    nextAvailable = win32clipboard.EnumClipboardFormats(0)
    while nextAvailable:
        available.append(nextAvailable)
        nextAvailable = win32clipboard.EnumClipboardFormats(nextAvailable)

    win32clipboard.CloseClipboard()

    return available


def isImage(existingFormats):
    if not existingFormats:
        existingFormats = getClipboardFormats()

    if 8 in existingFormats or 2 in existingFormats or 17:
        return True
    return False


def isFile(existingFormats):
    if not existingFormats:
        existingFormats = getClipboardFormats()

    if 15 in existingFormats:
        return True
    return False
