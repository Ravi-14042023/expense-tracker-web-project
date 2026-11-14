import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "expenses.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE,
            icon TEXT NOT NULL DEFAULT '📦',
            is_archived INTEGER NOT NULL DEFAULT 0
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL CHECK (amount > 0),
            category_id INTEGER,
            expense_date TEXT NOT NULL,
            notes TEXT DEFAULT '',
            is_deleted INTEGER NOT NULL DEFAULT 0,
            deleted_at TEXT,
            FOREIGN KEY (category_id) REFERENCES categories(id)
                ON DELETE SET NULL
        )
    """)

    category_count = connection.execute("SELECT COUNT(*) FROM categories").fetchone()[0]

    if category_count == 0:
        default_categories = [
            ("Food & Snacks", "🍔"),
            ("Transport", "🛺"),
            ("Education", "📚"),
            ("Shopping", "🛍️"),
            ("Bills", "💡"),
            ("Health", "💊"),
            ("Other", "📦"),
        ]

        connection.executemany(
            "INSERT INTO categories (name, icon) VALUES (?, ?)",
            default_categories,
        )

    connection.commit()
    connection.close()
