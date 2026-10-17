import sqlite3

conn = sqlite3.connect("lobby_events.sqlite")
cur = conn.cursor()

cur.execute("SELECT type, name, sql FROM sqlite_master")
for row in cur.fetchall():
    print(row)
