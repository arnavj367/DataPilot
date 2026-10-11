
"""Local persistent memory for DataPilot using SQLite."""

import sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "datapilot_memory.db"


def get_connection():
    """Open a connection to the local memory database."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_memory():
    """Create the memory table if it does not exist."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def save_memory(content, category="general"):
    """Save a memory permanently until the user deletes it."""
    content = content.strip()
    category = category.strip() or "general"

    if not content:
        raise ValueError("Memory cannot be empty.")

    initialize_memory()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO memories (category, content, created_at)
            VALUES (?, ?, ?)
            """,
            (
                category,
                content,
                datetime.now(timezone.utc).isoformat(),
            ),
        )


def get_memories(limit=50):
    """Return the most recently saved memories."""
    initialize_memory()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, category, content, created_at
            FROM memories
            ORDER BY id DESC
            LIMIT ?
            """,
            (max(1, min(int(limit), 500)),),
        ).fetchall()

    return [dict(row) for row in rows]


def delete_memory(memory_id):
    """Delete one memory by its ID."""
    initialize_memory()

    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM memories WHERE id = ?",
            (int(memory_id),),
        )
        return cursor.rowcount > 0


def clear_memories():
    """Delete all saved memories."""
    initialize_memory()

    with get_connection() as connection:
        connection.execute("DELETE FROM memories")


initialize_memory()
