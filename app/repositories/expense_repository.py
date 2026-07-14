import aiosqlite

from app.models.expense import Expense


def _row_to_expense(row: aiosqlite.Row) -> Expense:
    return Expense(
        id=row["id"],
        user_id=row["user_id"],
        category=row["category"],
        amount_minor=row["amount_minor"],
        currency=row["currency"],
        amount_base_minor=row["amount_base_minor"],
        rate_used=row["rate_used"],
        note=row["note"],
        created_at=row["created_at"],
    )


class ExpenseRepository:
    def __init__(self, conn: aiosqlite.Connection):
        self._conn = conn

    async def insert(
        self,
        *,
        user_id: int,
        category: str,
        amount_minor: int,
        currency: str,
        amount_base_minor: int,
        rate_used: float | None,
        note: str | None,
        created_at: str,
    ) -> int:
        cursor = await self._conn.execute(
            """
            INSERT INTO expenses
                (user_id, category, amount_minor, currency, amount_base_minor,
                 rate_used, note, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                category,
                amount_minor,
                currency,
                amount_base_minor,
                rate_used,
                note,
                created_at,
            ),
        )
        await self._conn.commit()
        assert cursor.lastrowid is not None
        return cursor.lastrowid

    async def get_by_id(self, expense_id: int, user_id: int) -> Expense | None:
        self._conn.row_factory = aiosqlite.Row
        async with self._conn.execute(
            "SELECT * FROM expenses WHERE id = ? AND user_id = ?",
            (expense_id, user_id),
        ) as cursor:
            row = await cursor.fetchone()
        return _row_to_expense(row) if row else None

    async def delete(self, expense_id: int, user_id: int) -> bool:
        cursor = await self._conn.execute(
            "DELETE FROM expenses WHERE id = ? AND user_id = ?",
            (expense_id, user_id),
        )
        await self._conn.commit()
        return cursor.rowcount > 0

    async def get_last(self, user_id: int) -> Expense | None:
        self._conn.row_factory = aiosqlite.Row
        async with self._conn.execute(
            "SELECT * FROM expenses WHERE user_id = ? ORDER BY created_at DESC, id DESC LIMIT 1",
            (user_id,),
        ) as cursor:
            row = await cursor.fetchone()
        return _row_to_expense(row) if row else None

    async def list_recent(self, user_id: int, limit: int = 10) -> list[Expense]:
        self._conn.row_factory = aiosqlite.Row
        async with self._conn.execute(
            "SELECT * FROM expenses WHERE user_id = ? ORDER BY created_at DESC, id DESC LIMIT ?",
            (user_id, limit),
        ) as cursor:
            rows = await cursor.fetchall()
        return [_row_to_expense(row) for row in rows]

    async def sum_by_category(
        self, user_id: int, start_iso: str, end_iso: str
    ) -> dict[str, int]:
        async with self._conn.execute(
            """
            SELECT category, SUM(amount_base_minor) AS total
            FROM expenses
            WHERE user_id = ? AND created_at >= ? AND created_at < ?
            GROUP BY category
            """,
            (user_id, start_iso, end_iso),
        ) as cursor:
            rows = await cursor.fetchall()
        return {row[0]: row[1] for row in rows}

    async def sum_total(self, user_id: int, start_iso: str, end_iso: str) -> int:
        async with self._conn.execute(
            """
            SELECT COALESCE(SUM(amount_base_minor), 0)
            FROM expenses
            WHERE user_id = ? AND created_at >= ? AND created_at < ?
            """,
            (user_id, start_iso, end_iso),
        ) as cursor:
            row = await cursor.fetchone()
        return row[0] if row else 0

    async def sum_by_category_since(
        self, user_id: int, category: str | None, start_iso: str
    ) -> int:
        """Spent in a category (or overall if category is None) since start_iso, for budget progress."""
        if category is None:
            query = (
                "SELECT COALESCE(SUM(amount_base_minor), 0) FROM expenses "
                "WHERE user_id = ? AND created_at >= ?"
            )
            params = (user_id, start_iso)
        else:
            query = (
                "SELECT COALESCE(SUM(amount_base_minor), 0) FROM expenses "
                "WHERE user_id = ? AND category = ? AND created_at >= ?"
            )
            params = (user_id, category, start_iso)
        async with self._conn.execute(query, params) as cursor:
            row = await cursor.fetchone()
        return row[0] if row else 0
