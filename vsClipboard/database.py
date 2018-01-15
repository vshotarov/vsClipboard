import cPickle
import sqlite3

from PySide.QtCore import QThread


def _createTable(connection):
    '''Creates the entries table in the database

    Creates a table called entries with the following
    fields

    - id - INTEGER PRIMARY KEY
    - data - BLOB

    Args:
        connection: The connection to the database
    '''
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE entries(id INTEGER PRIMARY KEY, data BLOB)")
    connection.commit()


def _initConnection():
    '''Connects to the database

    Also creates the entries table if it does not already
    exist.

    Returns:
        Database connection
        sqlite3.Connection
    '''
    connection = sqlite3.connect("clipboard_database")

    if not connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall():
        _createTable(connection)

    return connection


def _getConnection():
    '''Gets or creates a database connection and returns it

    The connection is stored on the thread so we don't have to
    create and close it every time we need to use the database,
    as that happens multiple times a second.

    Returns:
        Database connection
        sqlite3.Connection
    '''
    t = QThread.currentThread()
    if not hasattr(t, "dbConnection"):
        setattr(t, "dbConnection", _initConnection())
    return getattr(t, "dbConnection")


def read():
    '''Reads the database and returns all entries as list

    Returns:
        A list of clipboard history entries
        list
    '''
    connection = _getConnection()

    cursor = connection.cursor()
    cursor.execute("SELECT data from entries")

    data = [cPickle.loads(str(row[0])) for row in cursor.fetchall()]

    return data


def write(data):
    '''Writes the passed in data to the database

    Args:
        data: A dictionary representing a clipboard history
        entry
    '''
    connection = _getConnection()

    pickledData = cPickle.dumps(data, cPickle.HIGHEST_PROTOCOL)

    cursor = connection.cursor()

    cursor.execute("INSERT INTO entries(data) VALUES (?)", [sqlite3.Binary(pickledData)])

    connection.commit()
