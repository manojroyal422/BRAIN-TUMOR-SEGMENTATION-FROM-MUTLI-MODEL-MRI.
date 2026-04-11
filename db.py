import sqlite3

def get_db():
    return sqlite3.connect("brainai.db", check_same_thread=False)

db = get_db()

db.execute("""
CREATE TABLE IF NOT EXISTS users(
 id INTEGER PRIMARY KEY,
 name TEXT,
 email TEXT UNIQUE,
 password TEXT,
 role TEXT,
 approved INTEGER DEFAULT 0
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS messages(
 id INTEGER PRIMARY KEY,
 sender TEXT,
 receiver TEXT,
 msg TEXT
)
""")

db.commit()
