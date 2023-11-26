import sqlite3
from sqlite3 import Connection


def create_connection() -> Connection:
    conn = sqlite3.connect("database/database.db")
    return conn

def init_db():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            search_time TIMESTAMP NOT NULL,
            item_name TEXT NOT NULL,
            amazon_com_price REAL,
            amazon_co_uk_price REAL,
            amazon_de_price REAL,
            amazon_ca_price REAL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_search_count (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL UNIQUE,
            count INTEGER NOT NULL
        );
    """)

    conn.commit()
    conn.close()

def add_search_history(query: str, search_time: str, item_name: str, prices: dict = None):
    conn = create_connection()
    cursor = conn.cursor()

    if prices is None:
        cursor.execute("""
            INSERT INTO search_history (query, search_time, item_name)
            VALUES (?, ?, ?);
        """, (query, search_time, item_name))
    else:
        cursor.execute("""
            INSERT INTO search_history (query, search_time, item_name, amazon_com_price, amazon_co_uk_price, amazon_de_price, amazon_ca_price)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (query, search_time, item_name, prices["amazon_com"], prices["amazon_co_uk"], prices["amazon_de"], prices["amazon_ca"]))

    conn.commit()
    conn.close()

def update_last_search_prices(prices: list):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM search_history ORDER BY id DESC LIMIT 1;")
    last_search_id = cursor.fetchone()[0]

    cursor.execute("""
        UPDATE search_history
        SET amazon_com_price = ?,
            amazon_co_uk_price = ?,
            amazon_de_price = ?,
            amazon_ca_price = ?
        WHERE id = ?;
    """, (*prices, last_search_id))

    conn.commit()
    conn.close()

def get_search_history():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM search_history;")
    search_history = cursor.fetchall()

    conn.close()

    return search_history

def get_daily_search_count(date: str):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT count FROM daily_search_count WHERE date = ?;", (date,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else 0

def increment_daily_search_count(date: str):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT count FROM daily_search_count WHERE date = ?;", (date,))
    result = cursor.fetchone()

    if result:
        cursor.execute("UPDATE daily_search_count SET count = ? WHERE date = ?;", (result[0] + 1, date))
    else:
        cursor.execute("INSERT INTO daily_search_count (date, count) VALUES (?, 1);", (date,))

    conn.commit()
    conn.close()

def clear_search_history():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM search_history;")

    conn.commit()
    conn.close()




if __name__ == "__main__":
    init_db()
    