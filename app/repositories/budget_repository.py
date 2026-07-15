import aiosqlite

from app.models.budget import BudgetLimit


def _row_to_budget(row: aiosqlite.Row) -> BudgetLimit:
    return BudgetLimit(
        id=row["id"],
        user_id=row["user_id"],
        category=row["category"],
        limit_minor=row["limit_minor"],
        updated_at=row["updated_at"],
    )


class BudgetRepository:
    def __init__(self, conn: aiosqlite.Connection):
        self._conn = conn

    async def list_limits(self, user_id: int) -> list[BudgetLimit]:
        self._conn.row_factory = aiosqlite.Row
        async with self._conn.execute(
            "SELECT * FROM budget_limits WHERE user_id = ?", (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
        return [_row_to_budget(row) for row in rows]

    async def get_limit(self, user_id: int, category: str) -> BudgetLimit | None:
        self._conn.row_factory = aiosqlite.Row
        async with self._conn.execute(
            "SELECT * FROM budget_limits WHERE user_id = ? AND category = ?",
            (user_id, category),
        ) as cursor:
            row = await cursor.fetchone()
        return _row_to_budget(row) if row else None

    async def delete_all(self, user_id: int) -> int:
        cursor = await self._conn.execute(
            "DELETE FROM budget_limits WHERE user_id = ?", (user_id,)
        )
        await self._conn.commit()
        return cursor.rowcount

    async def upsert_limit(
        self, user_id: int, category: str, limit_minor: int, updated_at: str
    ) -> None:
        await self._conn.execute(
            """
            INSERT INTO budget_limits (user_id, category, limit_minor, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, category)
            DO UPDATE SET limit_minor = excluded.limit_minor, updated_at = excluded.updated_at
            """,
            (user_id, category, limit_minor, updated_at),
        )
        await self._conn.commit()
