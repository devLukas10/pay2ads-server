import sqlite3
import json
db_conexions = sqlite3.connect('./pay2ads.db', 1000)
db = db_conexions.cursor()

# create users table
db.execute("""
    CREATE TABLE IF NOT EXISTS users 
    (
        id INTEGER PRIMARY_KEY AUTO_INCREMENT, 
        username TEXT, email TEXT, reference_link TEXT, my_reference_link TEXT,
        balance TEXT, reference_bonus TEXT, clicks TEXT,
        reference_count TEXT, password TEXT, created_at TEXT
    )
""")
db.execute("""
    CREATE TABLE IF NOT EXISTS users_marketing 
    (
        id TEXT, username TEXT, link TEXT, posted_at TEXT
    )
""")
db.execute("""
    CREATE TABLE IF NOT EXISTS users_payment_forms 
    (
        id TEXT, username TEXT, back_name TEXT, iban TEXT, number TEXT, valor TEXT, created_at TEXT
    )
""")

class DBModuls:
    # create find All methodes
    def findAll (self, query):
        db.execute(f"SELECT * FROM {query}")
        result = db.fetchall()
        column = [desc[0] for desc in db.description]
        converts_to_json = [dict(zip(column, row)) for row in result]
        return converts_to_json
