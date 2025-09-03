import sqlite3

DB_FILE = "data/news_app.db"

def initialize_db():
    """Initialize the database and create the hashtag_logs table."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hashtag_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def add_tags(tags):
    """Add a list of tags to the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        for tag in tags:
            cursor.execute("INSERT INTO hashtag_logs (tag) VALUES (?)", (tag,))
        conn.commit()

def get_tag_frequency(limit=10):
    """Get the frequency of each tag."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tag, COUNT(*) as frequency
            FROM hashtag_logs
            GROUP BY tag
            ORDER BY frequency DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()

def clear_hashtag_logs():
    """Clear all records from the hashtag_logs table."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hashtag_logs")
        conn.commit()
    return "해시태그 기록이 모두 삭제되었습니다."

# Initialize the database when the module is loaded
initialize_db()