
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "output_1000" / "books.db"

with sqlite3.connect(DB_FILE) as conn:

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM books")
    total = cursor.fetchone()[0]

    print("Total books in SQLite:", total)

    cursor.execute("""
        SELECT Title, Price, Status, Rating
        FROM books
        LIMIT 5
    """)

    print("\nFirst 5 books:")
    for row in cursor.fetchall():
        print(row)

    cursor.execute("""
        SELECT COUNT(*)
        FROM books
        WHERE Rating = 5
    """)

    five_star = cursor.fetchone()[0]

    print("\n5-star books:", five_star)

    assert total == 1000, "Expected 1000 books"
    print("\nPASS: SQLite contains 1000 books")
