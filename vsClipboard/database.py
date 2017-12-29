import json
import cPickle


def read():
    # with open(r"D:/Programming/Python/vsClipboard/db.json", "r") as f:
    #     return json.loads(f.read())

    try:
        data = cPickle.load(open(r"D:/Programming/Python/vsClipboard/db.pickle", "rb"))
    except EOFError:
        data = []
    return data


def write(data):
    old = read()
    old.append(data)
    f = open(r"D:/Programming/Python/vsClipboard/db.pickle", "wb")
    cPickle.dump(old, f)
