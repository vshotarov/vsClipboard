import cPickle
import sqlite3

from PySide.QtCore import QThread

def _createTable(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE entries(id INTEGER PRIMARY KEY, data BLOB)")
    connection.commit()


def _initConnection():
    connection = sqlite3.connect("D:/Programming/Python/vsClipboard_DB")

    if not connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall():
        _createTable(connection)

    return connection


# def _getConnection():
# 	t = QThread.currentThread()
# 	if not hasattr(t, "dbConnection"):
# 		setattr(t, "dbConnection", _initConnection())
# 	return getattr(t, "dbConnection")


def read():
    connection = _initConnection()

    cursor = connection.cursor()
    cursor.execute("SELECT data from entries")

    data = [cPickle.loads(str(row[0])) for row in cursor.fetchall()]

    connection.close()

    return data

    # try:
    #     data = cPickle.load(open(r"D:/Programming/Python/vsClipboard/db.pickle", "rb"))
    # except EOFError:
    #     data = []
    # return data


def write(data):
    connection = _initConnection()

    pickledData = cPickle.dumps(data, cPickle.HIGHEST_PROTOCOL)

    cursor = connection.cursor()

    cursor.execute("INSERT INTO entries(data) VALUES (?)", [sqlite3.Binary(pickledData)])

    connection.commit()
    connection.close()

    # old = read()
    # old.append(data)
    # f = open(r"D:/Programming/Python/vsClipboard/db.pickle", "wb")
    # cPickle.dump(old, f)
