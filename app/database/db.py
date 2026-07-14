import os
from pathlib import Path

import aiosqlite

_connection: aiosqlite.Connection | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    amount_minor INTEGER NOT NULL,
    currency TEXT NOT NULL,
    amount_base_minor INTEGER NOT NULL,
    rate_used REAL,
    note TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_expenses_user_created
    ON expenses (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_expenses_user_category
    ON expenses (user_id, category);

CREATE TABLE IF NOT EXISTS budget_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    limit_minor INTEGER NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(user_id, category)
);
"""


async def init_db(db_path: str) -> aiosqlite.Connection:
    global _connection
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    _connection = await aiosqlite.connect(db_path)
    await _connection.execute("PRAGMA journal_mode=WAL")
    await _connection.execute("PRAGMA busy_timeout=5000")
    await _connection.executescript(SCHEMA)
    await _connection.commit()
    return _connection


def get_connection() -> aiosqlite.Connection:
    if _connection is None:
        raise RuntimeError("Database not initialized — call init_db() first")
    return _connection


async def close_db() -> None:
    global _connection
    if _connection is not None:
        await _connection.close()
        _connection = None
