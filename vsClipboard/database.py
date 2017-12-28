import json


def read():
    with open(r"D:/Programming/Python/vsClipboard/db.json", "r") as f:
        return json.loads(f.read())


def write(data):
    with open(r"D:/Programming/Python/vsClipboard/db.json", "w") as f:
        f.write(json.dumps(data, sort_keys=1, indent=4))
