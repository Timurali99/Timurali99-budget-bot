import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from app.models.expense import Expense
from app.repositories.expense_repository import ExpenseRepository
from app.services.catalog_seed import CATALOG_BY_ID
from app.services.rates_service import RatesService
from app.utils.formatting import decimal_to_minor

AMOUNT_RE = re.compile(r"^\s*(\d+(?:[.,]\d{1,2})?)\s*([A-Za-z]{2,5})?\s*$")


class InvalidAmountError(ValueError):
    pass


@dataclass(frozen=True)
class ExpenseReport:
    period_label: str
    total_minor: int
    by_category: dict[str, int]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_amount_input(text: str, default_currency: str) -> tuple[Decimal, str]:
    match = AMOUNT_RE.match(text)
    if not match:
        raise InvalidAmountError(
            "Не понял сумму. Введи число, например: 450 или 20 USD"
        )
    raw_amount, raw_currency = match.groups()
    amount = Decimal(raw_amount.replace(",", "."))
    if amount <= 0:
        raise InvalidAmountError("Сумма должна быть больше нуля")
    currency = raw_currency.upper() if raw_currency else default_currency
    return amount, currency


def _period_bounds(
    period: str, custom_start: date | None = None, custom_end: date | None = None
) -> tuple[str, str, str]:
    now = datetime.now(timezone.utc)
    today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_midnight = today_midnight + timedelta(days=1)

    if period == "today":
        return today_midnight.isoformat(), tomorrow_midnight.isoformat(), "Сегодня"
    if period == "week":
        start = today_midnight - timedelta(days=6)
        return start.isoformat(), tomorrow_midnight.isoformat(), "Последние 7 дней"
    if period == "month":
        start = today_midnight.replace(day=1)
        return start.isoformat(), tomorrow_midnight.isoformat(), "Текущий месяц"
    if period == "custom":
        if custom_start is None or custom_end is None:
            raise InvalidAmountError("Не указан период")
        start_dt = datetime(
            custom_start.year, custom_start.month, custom_start.day, tzinfo=timezone.utc
        )
        end_dt = datetime(
            custom_end.year, custom_end.month, custom_end.day, tzinfo=timezone.utc
        ) + timedelta(days=1)
        label = f"{custom_start:%d.%m.%Y} — {custom_end:%d.%m.%Y}"
        return start_dt.isoformat(), end_dt.isoformat(), label
    raise ValueError(f"Unknown period: {period}")


class ExpenseService:
    def __init__(
        self,
        expense_repo: ExpenseRepository,
        rates: RatesService,
        base_currency: str,
    ):
        self._repo = expense_repo
        self._rates = rates
        self._base_currency = base_currency

    async def log_quick(self, user_id: int, item_id: str) -> Expense:
        item = CATALOG_BY_ID.get(item_id)
        if item is None:
            raise InvalidAmountError("Такой позиции больше нет в каталоге")
        expense_id = await self._repo.insert(
            user_id=user_id,
            category=item.category,
            amount_minor=item.price_minor,
            currency=self._base_currency,
            amount_base_minor=item.price_minor,
            rate_used=None,
            note=item.label,
            created_at=_now_iso(),
        )
        expense = await self._repo.get_by_id(expense_id, user_id)
        assert expense is not None
        return expense

    async def log_custom(self, user_id: int, category: str, raw_text: str) -> Expense:
        amount, currency = parse_amount_input(raw_text, self._base_currency)
        amount_minor = decimal_to_minor(amount)

        if currency == self._base_currency:
            amount_base_minor = amount_minor
            rate_used = None
        else:
            converted = await self._rates.convert(amount, currency, self._base_currency)
            amount_base_minor = decimal_to_minor(converted)
            rate_used = float(converted / amount)

        expense_id = await self._repo.insert(
            user_id=user_id,
            category=category,
            amount_minor=amount_minor,
            currency=currency,
            amount_base_minor=amount_base_minor,
            rate_used=rate_used,
            note=None,
            created_at=_now_iso(),
        )
        expense = await self._repo.get_by_id(expense_id, user_id)
        assert expense is not None
        return expense

    async def undo_last(self, user_id: int) -> Expense | None:
        last = await self._repo.get_last(user_id)
        if last is None:
            return None
        deleted = await self._repo.delete(last.id, user_id)
        return last if deleted else None

    async def delete(self, user_id: int, expense_id: int) -> bool:
        return await self._repo.delete(expense_id, user_id)

    async def list_recent(self, user_id: int, limit: int = 10) -> list[Expense]:
        return await self._repo.list_recent(user_id, limit)

    async def report(
        self,
        user_id: int,
        period: str,
        custom_start: date | None = None,
        custom_end: date | None = None,
    ) -> ExpenseReport:
        start_iso, end_iso, label = _period_bounds(period, custom_start, custom_end)
        by_category = await self._repo.sum_by_category(user_id, start_iso, end_iso)
        total = sum(by_category.values())
        return ExpenseReport(period_label=label, total_minor=total, by_category=by_category)
