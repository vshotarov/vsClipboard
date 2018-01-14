import json
from PySide.QtCore import QThread

_config = {
    "history_length" : 10,
    "hold_before_showing" : .15
}

def parse():
    try:
        with open("config.json", "r") as f:
            config = json.loads(f.read())
    except:
        config = _config
    return config

def get(key=None):
    t = QThread.currentThread()
    if not key:
        return getattr(t, "config")
    else:
        return getattr(t, "config")[key]

def update(new):
    try:
        with open("config.json", "w") as f:
            f.write(json.dumps(new, sort_keys=1, indent=4))
    except:
        print "Could not save new configuration to the config file."
