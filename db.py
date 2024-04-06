from bottle import run, route, template, get, request, install
import sqlite3
from bottle_sqlite import SQLitePlugin
import inspect

# install(SQLitePlugin(dbfile='items.db'))
db = sqlite3.connect(
    "cafe_db.db",
    isolation_level=None,
)

cur = db.cursor()
# フィールド作成用SQL文
# sql = """
#     CREATE TABLE takeout_order (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         name TEXT,
#         quantity TEXT,
#         reservation_code TEXT
#     )
# """
#adminは管理者権限の有無
#
# cur.execute(sql)
# db.commit()
# db.close()

# db = sqlite3.connect(
#     "items.db",
#     isolation_level=None,
# )

# cur = db.cursor()
sql = """ INSERT INTO staff (staff_name, staff_ID, pass_word, admin) VALUES
('千代勝正', 'staff_chiyo', 'dei_katsumasa', 1)
"""
# # sql = """ DELETE FROM items WHERE id = 10; """
# sql = """DROP TABLE user"""

# sql = """ALTER TABLE user ADD registered_datetime DATETIME"""
# #
db.execute(sql)
db.commit()
db.close()