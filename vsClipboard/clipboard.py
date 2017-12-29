from ctypes import wintypes

import ctypes
import win32con
import win32clipboard

import time
import threading

import database

from PySide.QtCore import QThread


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
    if 8 in existingFormats or 2 in existingFormats or 17:
        return True
    return False


def isFile(existingFormats):
    if 15 in existingFormats:
        return True
    return False


def isText(existingFormats):
    if 11 in existingFormats or 13 in existingFormats:
        return True
    return False


def isHTML(existingFormats):
    if 49416 in existingFormats:
        return True
    return False


def getData():
    try:
        existing = getClipboardFormats()
    except:
        print "PASSING ERROR"
        pass

    hasText = isText(existing)
    hasFile = isFile(existing)
    hasImage = isImage(existing)
    hasHtml = isHTML(existing)

    if not hasText and not hasFile and not hasImage:
        return

    win32clipboard.OpenClipboard()

    text = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT) if hasText else None

    html = None
    if text and hasHtml:
        html = win32clipboard.GetClipboardData(49416)

    if hasFile:
        text = win32clipboard.GetClipboardData(15)

    if hasImage:
        pass

    win32clipboard.CloseClipboard()

    d = {
        "text": text,
        "html": html,
        # "hasFile" : hasFile or hasImage
        "hasFile": hasFile
    }

    return d


def monitorClipboard():
    t = QThread.currentThread()

    data = getData()
    while getattr(t, "do_run", True):
        print "Running"
        newData = getData()
        if newData and newData != data:
            print "Saving"
            save()
        data = newData
        time.sleep(.5)
    print "EXIT"


def save():
    data = getData()
    old = database.read()

    old = old[-1] if old else data

    if data:
        startTime = time.time()
        while data == old:
            if time.time() - startTime > 1:
                return
            time.sleep(.01)
            data = getData()
        database.write(data)
