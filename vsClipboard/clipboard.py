'''Clipboard getting and setting.

This module contains functions used for reading and polling the 
current clipboard data, as well as, for setting the current
clipboard to an entry from the history.

Attributes:
    u32: A shortened namespace for ctypes.windll.user32
'''
import ctypes
import win32clipboard
import pywintypes
import logging

import time

import database
import config

from PySide.QtCore import QThread


u32 = ctypes.windll.user32  # Make it easier to access the namespace


def registerCustomClipboardFormat():
    '''Registers a custom clipbord format to detect internal clipboard
    changes.

    We need to be able to detec whether a clipboard change is due to our 
    own functions or an outside source, in order to make sure that pasting
    does not add entries to the clipboard history.

    Returns:
        The id of the custom format
        int

    Raises:
        RuntimeError: Raises an error if for any reason we can't register
        a clipboard format.
    '''
    customFormatID = win32clipboard.RegisterClipboardFormat("vsClipboardPaste")
    if customFormatID == 0:
        raise RuntimeError("Could not register custom clipboard format")
    return customFormatID


def getClipboardFormats():
    '''Returns a list containing the integer codes for the various formats currently
    in the clipboard

    Returns:
        list of formats currently in the clipboard
        list
    '''
    openClipboard()

    available = []
    nextAvailable = win32clipboard.EnumClipboardFormats(0)
    while nextAvailable:
        available.append(nextAvailable)
        nextAvailable = win32clipboard.EnumClipboardFormats(nextAvailable)

    win32clipboard.CloseClipboard()

    return available


def isInternal():
    '''Checks whether the current clipboard data is set from withing the application.

    Using the custom clipboard format we have registered, we detect whether the change
    of the clipboard is due to internal reasons, in which case it is being skipped in
    the monitorClipboard function.

    Returns:
        True if the clipboard change is internal, False otherwise
        bool
    '''
    t = QThread.currentThread()

    if not hasattr(t, "customClipboardFormatID"):
        t.customClipboardFormatID = registerCustomClipboardFormat()

    if getattr(t, "customClipboardFormatID") in getClipboardFormats():
        return True
    return False


def isImage(existingFormats):
    '''Checks whether there is image data in the list of formats currently in the
    clipboard.

    Args:
        existingFormats: list of the current formats in the clipboard

    Returns:
        True if an image exists in the clipboard formats, else False
        bool
    '''
    if 8 in existingFormats or 2 in existingFormats or 17:
        return True
    return False


def isFile(existingFormats):
    '''Checks whether there is file data in the list of formats currently in the
    clipboard.

    Args:
        existingFormats: list of the current formats in the clipboard

    Returns:
        True if a file exists in the clipboard formats, else False
        bool
    '''
    if 15 in existingFormats:
        return True
    return False


def isText(existingFormats):
    '''Checks whether there is text data in the list of formats currently in the
    clipboard.

    Args:
        existingFormats: list of the current formats in the clipboard

    Returns:
        True if text exists in the clipboard formats, else False
        bool
    '''
    if 1 in existingFormats:
        return True
    return False


def isUnicode(existingFormats):
    '''Checks whether there is unicode data in the list of formats currently in the
    clipboard.

    Args:
        existingFormats: list of the current formats in the clipboard

    Returns:
        True if unicode exists in the clipboard formats, else False
        bool
    '''
    if 13 in existingFormats:
        return True
    return False


def isHTML(existingFormats):
    '''Checks whether there is HTML data in the list of formats currently in the
    clipboard.

    Args:
        existingFormats: list of the current formats in the clipboard

    Returns:
        True if HTML exists in the clipboard formats, else False
        bool
    '''
    if 49416 in existingFormats:
        return True
    return False


def getData():
    '''Retrieves the data from the clipboard and returns it as a dictionary.

    The dictionary that is returned is of the form
    {
        "text" : the text data,
        "html" : the html data,
        "unicode" : the unicode data,
        "hasFile" : a boolean value of whether the text contained is a path to a file
    }

    In the future the "hasFile" key will also be true if there is an image on the clipboard,
    as the way images are going to be handled is that they are going to be saved to a file
    whenever they are detected in the clipboard. An additional "hasImage" key will be added,
    so the paste function knows how to handle it.

    Returns:
        A dictionary containing the current clipboard data in the above specified format.
        If no recognizable data is found - text, file, html, image (images are not currently supported)
        an empty dictionary is returned.
        dict
    '''
    existing = getClipboardFormats()

    hasText = isText(existing)
    hasUnicode = isUnicode(existing)
    hasFile = isFile(existing)
    hasImage = isImage(existing)
    hasHtml = isHTML(existing)

    if not hasUnicode and not hasText and not hasFile and not hasHtml:  # Once image support is addes hasImage needs to be added here
        return {}

    openClipboard()

    text = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT) if hasText else None
    _unicode = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT) if hasUnicode else None

    html = None
    if hasHtml:
        html = win32clipboard.GetClipboardData(49416)

    if hasFile:
        text = win32clipboard.GetClipboardData(15)

    if hasImage:
        pass

    win32clipboard.CloseClipboard()

    d = {
        "text": text,
        "html": html,
        "unicode": _unicode,
        # "hasFile" : hasFile or hasImage
        "hasFile": hasFile
    }

    return d


def monitorClipboard():
    '''Polls the clipboard for changes and saves them to the history.

    The while loop exits once the "do_run" attribute of the current thread
    is set to False from the main thread.

    On exit we are checking whether we have a database connection stored on the
    thread and if we do, we close it.
    '''
    t = QThread.currentThread()

    history = getHistory()
    data = history[-1] if history else {}
    while getattr(t, "do_run", True):
        newData = getData()
        if newData and newData != data and not isInternal():
            save()
        data = newData
        time.sleep(config.get("poll_clipboard_interval"))

    if hasattr(t, "dbConnection"):
        getattr(t, "dbConnection").close()
        logging.info("Closed dbConnection in clipboard thread")


def save():
    '''Saves the current clipboard data to history.

    The data is retrieved using getData() and is then appended
    to the existing clipboard history.
    '''
    data = getData()
    old = getHistory()

    old = old[-1] if old else {}

    if data:
        startTime = time.time()

        # If the data that needs to be saved is exactly the same
        # as the latest data in the history, give it 1 second
        # to make sure changes have been reflected and if
        # there is still no change return

        # Otherwise carry on saving the data, as
        # it can be assumed that it is different
        # than the latest one in the history
        while data == old:
            if time.time() - startTime > 1:
                logging.error("Failed to save")
                return
            time.sleep(.01)
            data = getData()
        database.write(data)


def set(data):
    '''Sets the clipboard to the passed in data from the history.

    Currently, only the text data is supported, so if a file has been copied
    only the path to it would be set to clipboard.

    Once image support is added, similar to the file case, only a path to
    the saved image file would be set to the clipboard.

    In the future, I might find I prefer pasting actual files and images,
    instead of just paths, in which case, all I need to do is check
    if there is a file or image stored, read that and put it
    on the clipboard.

    Args:
        data: The data received from the clipboard history in the
        same format as in the getData function
    '''
    t = QThread.currentThread()

    if not hasattr(t, "customClipboardFormatID"):
        t.customClipboardFormatID = registerCustomClipboardFormat()

    openClipboard()

    win32clipboard.EmptyClipboard()

    # Setting the actual clipboard data
    if data["unicode"]:
        win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, data["unicode"])

    if data["text"]:
        win32clipboard.SetClipboardData(win32clipboard.CF_TEXT,
                                        data["text"] if isinstance(data["text"], basestring) else str(data["text"][0]))

    if data["html"]:
        win32clipboard.SetClipboardData(49416, data["html"])

    # Setting custom clipboard format to identify that it's an internal change
    win32clipboard.SetClipboardData(getattr(t, "customClipboardFormatID"), "1")

    win32clipboard.CloseClipboard()


def getHistory():
    '''Returns the list containing the existing clipboard history.

    The list contains dictionaries in the format specified in the getData function.

    Returns:
        A list of dict elements containing entries in the clipboard history
        list
    '''
    return database.read()


def openClipboard():
    '''Opens the windows clipboard.

    The win32clipboard.OpenClipboard() function needs to be wrapped in a try
    and except loop as it is possible that the clipboard is currently in
    operation when we try to access it, which would error with access denied.
    '''
    try:
        win32clipboard.OpenClipboard()
        return
    except pywintypes.error:
        startTime = time.time()
        while (time.time() - startTime) < 2:
            try:
                win32clipboard.OpenClipboard()
                return
            except pywintypes.error:
                logging.debug("Could not open clipboard. Trying again...")
                time.sleep(.05)
        logging.error("Failed opening clipboard.")
