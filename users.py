import sqlite3

DB_PATH = 'bible_plan.db'

def add_user_id(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
        conn.commit()

def get_all_user_ids():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        rows = c.execute('SELECT user_id FROM users').fetchall()
        return [row[0] for row in rows] 