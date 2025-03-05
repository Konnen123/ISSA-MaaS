import sqlite3

conn = None

def get_connection():
    global conn
    if conn is None:
        conn = sqlite3.connect('identifier.sqlite', check_same_thread=False)

    return conn
