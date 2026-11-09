import os
import sqlite3

DB_PATH = os.environ.get("BOOKS_DB", "books.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    author      TEXT NOT NULL,
    rented      INTEGER NOT NULL DEFAULT 0,
    rental_date TEXT,
    return_date TEXT
);
"""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the tables and seed an initial book if the table is empty."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 0:
            conn.execute(
                "INSERT INTO books (title, author) VALUES (?, ?)",
                ("The Poppy War", "R. F. Kuang"),
            )


def _to_dict(row):
    d = dict(row)
    d["rented"] = bool(d["rented"])
    return d


def list_books(available_only=False):
    query = "SELECT * FROM books"
    if available_only:
        query += " WHERE rented = 0"
    with get_connection() as conn:
        return [_to_dict(r) for r in conn.execute(query)]


def get_book(book_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    return _to_dict(row) if row else None


def add_book(title, author):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO books (title, author) VALUES (?, ?)", (title, author)
        )
        return cur.lastrowid


def set_rental(book_id, rented, rental_date=None, return_date=None):
    with get_connection() as conn:
        conn.execute(
            "UPDATE books SET rented = ?, rental_date = ?, return_date = ? WHERE id = ?",
            (int(rented), rental_date, return_date, book_id),
        )
