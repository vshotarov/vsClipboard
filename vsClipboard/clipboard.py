'''Clipboard getting and setting.

This module contains functions used for reading and polling the 
current clipboard data, as well as, for setting the current
clipboard to an entry from the history.

Attributes:
    u32: A shortened namespace for ctypes.windll.user32
'''
import ctypes
import win32clipboard

import time

import database

from PySide.QtCore import QThread


u32 = ctypes.windll.user32  # Make it easier to access the namespace


def getClipboardFormats():
    '''Returns a list containing the integer codes for the various formats currently
    in the clipboard

    Returns:
        list of formats currently in the clipboard
        list
    '''
    win32clipboard.OpenClipboard()

    available = []
    nextAvailable = win32clipboard.EnumClipboardFormats(0)
    while nextAvailable:
        available.append(nextAvailable)
        nextAvailable = win32clipboard.EnumClipboardFormats(nextAvailable)

    win32clipboard.CloseClipboard()

    return available


def isImage(existingFormats):
    '''Checks whether there is image data in the list of formats currently in the

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

    Args:
        existingFormats: list of the current formats in the clipboard

    Returns:
        True if text exists in the clipboard formats, else False
        bool
    '''
    if 11 in existingFormats or 13 in existingFormats:
        return True
    return False


def isHTML(existingFormats):
    '''Checks whether there is HTML data in the list of formats currently in the

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
    hasFile = isFile(existing)
    hasImage = isImage(existing)
    hasHtml = isHTML(existing)

    if not hasText and not hasFile and not hasImage:
        return {}

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
    '''Polls the clipboard for changes and saves them to the history.

    The while loop exits once the "do_run" attribute of the current thread
    is set to False from the main thread.
    '''
    t = QThread.currentThread()

    data = getData()
    while getattr(t, "do_run", True):
        newData = getData()
        if newData and newData != data:
            save()
        data = newData
        time.sleep(.5)


def save():
    '''Saves the current clipboard data to history.
    
    The data is retrieved using getData() and is then appended
    to the existing clipboard history.
    '''
    data = getData()
    old = database.read()

    old = old[-1] if old else data

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
    win32clipboard.OpenClipboard()

    win32clipboard.EmptyClipboard()

    win32clipboard.SetClipboardData(win32clipboard.CF_TEXT, data["text"])

    win32clipboard.CloseClipboard()


def getHistory():
    '''Returns the list containing the existing clipboard history.
    
    The list contains dictionaries in the format specified in the getData function.
    
    Returns:
        A list of dict elements containing entries in the clipboard history
        list
    '''
    return database.read()
