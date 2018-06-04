'''This module manages the config (preferences)

The configuration of the application is saved in a file called
config.json in the same directory where the application is
running.

If the file does not exist, the defaults stored in the _config
dictionary.

Attributes:
    _config: Default configuration
'''
import json
from PySide.QtCore import QThread

import ctypes 
# Letting windows know that this is an application
# on it's own, instead of just pythonw.exe
# source - https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7
myappid = u'vsClipboard.v_0_1' 
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

_config = {
    "history_length": 10,
    "hold_before_showing": .15,
    "poll_clipboard_interval": .5
}


def parse():
    '''Reads, parses and returns the config file.

    Returns:
        A dictionary representing the config file
        dict
    '''
    try:
        with open("config.json", "r") as f:
            config = json.loads(f.read())
    except:
        config = _config
    return config


def get(key=None):
    '''Returns either the full config or a single key.

    This function always returns the most up to date config
    stored on the thread object.

    Args:
        key: The key we are interested in (default: {None})

    Returns:
        Either the value of the key specified or if no key is
        specified the full config dict is returned.
        dict
    '''
    t = QThread.currentThread()
    if not key:
        return getattr(t, "config")
    else:
        return getattr(t, "config")[key]


def save(new):
    '''Saves the passed in dictionary as the new config file.

    Args:
        new: A dictionary containing updated configuration

    Raises:
        IOError: Error if it is not possible to write the
        config.json file.
    '''
    try:
        with open("config.json", "w") as f:
            f.write(json.dumps(new, sort_keys=1, indent=4))
    except:
        raise IOError("Could not save new configuration to the config file.")
