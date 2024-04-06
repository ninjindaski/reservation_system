from bottle import run, route, template, get, request, install
import sqlite3
from bottle_sqlite import SQLitePlugin
import inspect

db = sqlite3.connect(
    "cafe_db.db",
    isolation_level=None,
)

cur = db.cursor()


sql = """
    CREATE TABLE reservations(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    duration INTEGER,　
    customer_name INTEGER,
    remarks TEXT,
    reservation_code TEXT,　
    promotion_discount_rate INTEGER,　
    promotion_remarks TEXT,
    is_arrived INTEGER,
    is_event INTEGER,
    number_of_customer INTEGER,
    date DATETIME,
    time INTEGER,
    order_complete_time DATETIME,
    email TEXT
    )
"""

db.execute(sql)
db.commit()
db.close()
