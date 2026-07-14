import aiosqlite
import pytest_asyncio

from app.database.db import SCHEMA


@pytest_asyncio.fixture
async def db_conn(tmp_path):
    path = tmp_path / "test.db"
    conn = await aiosqlite.connect(str(path))
    await conn.executescript(SCHEMA)
    await conn.commit()
    yield conn
    await conn.close()
