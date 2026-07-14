from decimal import Decimal

import pytest

from app.repositories.expense_repository import ExpenseRepository
from app.services.expense_service import ExpenseService, InvalidAmountError, parse_amount_input


class StubRates:
    async def convert(self, amount: Decimal, from_ccy: str, to_ccy: str) -> Decimal:
        if from_ccy.upper() == "USD" and to_ccy.upper() == "RUB":
            return amount * Decimal(90)
        return amount


@pytest.fixture
def expense_service(db_conn):
    return ExpenseService(ExpenseRepository(db_conn), StubRates(), "RUB")


def test_parse_amount_input_default_currency():
    amount, currency = parse_amount_input("450", "RUB")
    assert amount == Decimal("450")
    assert currency == "RUB"


def test_parse_amount_input_explicit_currency():
    amount, currency = parse_amount_input("20 USD", "RUB")
    assert amount == Decimal("20")
    assert currency == "USD"


def test_parse_amount_input_rejects_garbage():
    with pytest.raises(InvalidAmountError):
        parse_amount_input("не число", "RUB")


async def test_log_quick_uses_catalog_price(expense_service):
    expense = await expense_service.log_quick(1, "coffee")
    assert expense.category == "food"
    assert expense.amount_base_minor == 25000
    assert expense.note == "Кофе"


async def test_log_custom_converts_foreign_currency(expense_service):
    expense = await expense_service.log_custom(1, "transport", "20 USD")
    assert expense.currency == "USD"
    assert expense.amount_base_minor == 20 * 90 * 100
    assert expense.rate_used == 90.0


async def test_log_custom_rejects_invalid_amount(expense_service):
    with pytest.raises(InvalidAmountError):
        await expense_service.log_custom(1, "food", "not a number")


async def test_report_aggregates_by_category(expense_service):
    await expense_service.log_quick(1, "coffee")
    await expense_service.log_quick(1, "taxi")
    report = await expense_service.report(1, "today")
    assert report.total_minor == 25000 + 35000
    assert report.by_category["food"] == 25000
    assert report.by_category["transport"] == 35000


async def test_undo_last_removes_most_recent(expense_service):
    await expense_service.log_quick(1, "coffee")
    taxi = await expense_service.log_quick(1, "taxi")
    undone = await expense_service.undo_last(1)
    assert undone.id == taxi.id
    recent = await expense_service.list_recent(1)
    assert len(recent) == 1
    assert recent[0].note == "Кофе"


async def test_expenses_are_scoped_per_user(expense_service):
    await expense_service.log_quick(1, "coffee")
    report_other_user = await expense_service.report(2, "today")
    assert report_other_user.total_minor == 0
