from database.db import create_connection

def reset_daily_search_count():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE daily_search_count SET count = 0;")
    conn.commit()

    conn.close()

if __name__ == "__main__":
    reset_daily_search_count()
