from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from app.repositories.budget_repository import BudgetRepository
from app.repositories.expense_repository import ExpenseRepository
from app.utils.categories import OVERALL_BUDGET_SLUG
from app.utils.formatting import decimal_to_minor


@dataclass(frozen=True)
class BudgetProgress:
    category: str
    spent_minor: int
    limit_minor: int


def _month_start_iso() -> str:
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()


class BudgetService:
    def __init__(self, budget_repo: BudgetRepository, expense_repo: ExpenseRepository):
        self._budget_repo = budget_repo
        self._expense_repo = expense_repo

    async def set_limit(self, user_id: int, category: str, amount: Decimal) -> None:
        limit_minor = decimal_to_minor(amount)
        await self._budget_repo.upsert_limit(
            user_id, category, limit_minor, datetime.now(timezone.utc).isoformat()
        )

    async def progress_for(self, user_id: int, category: str) -> BudgetProgress | None:
        limit = await self._budget_repo.get_limit(user_id, category)
        if limit is None:
            return None
        month_start = _month_start_iso()
        db_category = None if category == OVERALL_BUDGET_SLUG else category
        spent = await self._expense_repo.sum_by_category_since(user_id, db_category, month_start)
        return BudgetProgress(category=category, spent_minor=spent, limit_minor=limit.limit_minor)

    async def list_progress(self, user_id: int) -> list[BudgetProgress]:
        limits = await self._budget_repo.list_limits(user_id)
        month_start = _month_start_iso()
        result = []
        for limit in limits:
            db_category = None if limit.category == OVERALL_BUDGET_SLUG else limit.category
            spent = await self._expense_repo.sum_by_category_since(
                user_id, db_category, month_start
            )
            result.append(
                BudgetProgress(
                    category=limit.category, spent_minor=spent, limit_minor=limit.limit_minor
                )
            )
        return result
