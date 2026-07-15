from decimal import Decimal

import pytest

from app.repositories.budget_repository import BudgetRepository
from app.repositories.expense_repository import ExpenseRepository
from app.services.expense_service import ExpenseService
from app.services.news_service import NewsItem, NewsService


class StubRates:
    async def convert(self, amount: Decimal, from_ccy: str, to_ccy: str) -> Decimal:
        return amount


@pytest.fixture
def expense_service(db_conn):
    return ExpenseService(ExpenseRepository(db_conn), StubRates(), "RUB")


async def test_delete_all_wipes_only_that_user(db_conn, expense_service):
    await expense_service.log_quick(1, "coffee")
    await expense_service.log_quick(1, "lunch")
    await expense_service.log_quick(2, "coffee")
    budget_repo = BudgetRepository(db_conn)
    await budget_repo.upsert_limit(1, "food", 100000, "2026-07-15T00:00:00+00:00")

    deleted = await ExpenseRepository(db_conn).delete_all(1)
    await budget_repo.delete_all(1)

    assert deleted == 2
    assert await ExpenseRepository(db_conn).list_recent(1) == []
    assert await budget_repo.list_limits(1) == []
    # другой пользователь не затронут
    assert len(await ExpenseRepository(db_conn).list_recent(2)) == 1


SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <title>Test feed</title>
  <item><title>Первая новость</title><link>https://example.com/1</link>
    <pubDate>Wed, 15 Jul 2026 10:00:00 +0300</pubDate></item>
  <item><title>Вторая новость</title><link>https://example.com/2</link></item>
</channel></rss>"""


async def test_news_parses_rss(monkeypatch):
    service = NewsService("https://example.com/rss")

    class FakeResponse:
        content = SAMPLE_RSS.encode("utf-8")

        def raise_for_status(self):
            pass

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr("app.services.news_service.httpx.AsyncClient", FakeClient)

    items = await service.latest(limit=5)
    assert items[0] == NewsItem(
        title="Первая новость",
        link="https://example.com/1",
        pub_date="Wed, 15 Jul 2026 10:00:00 +0300",
    )
    assert len(items) == 2
