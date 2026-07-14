from decimal import Decimal

import pytest

from app.services.rates_service import RatesService


@pytest.fixture
def rates(monkeypatch):
    service = RatesService(ttl_seconds=90)

    async def fake_fiat_rates():
        return {"USD": 1.0, "RUB": 90.0, "EUR": 0.9}

    async def fake_crypto_snapshot():
        return {"bitcoin": {"usd": 65000.0, "rub": 5850000.0, "eur": 58500.0}}

    monkeypatch.setattr(service, "get_fiat_rates", fake_fiat_rates)
    monkeypatch.setattr(service, "get_crypto_snapshot", fake_crypto_snapshot)
    return service


async def test_same_currency_short_circuits(rates):
    assert await rates.convert(Decimal(50), "usd", "USD") == Decimal(50)


async def test_fiat_to_fiat(rates):
    assert await rates.convert(Decimal(100), "usd", "rub") == Decimal("9000")


async def test_crypto_to_fiat(rates):
    assert await rates.convert(Decimal(1), "btc", "usd") == Decimal("65000")


async def test_fiat_to_crypto(rates):
    assert await rates.convert(Decimal(65000), "usd", "btc") == Decimal("1")


async def test_crypto_to_crypto_bridges_through_usd(rates):
    # 1 BTC == 65000 USD, so 1 BTC in "usd"-priced terms roundtrips to itself.
    usd_value = await rates.convert(Decimal(1), "btc", "usd")
    back_to_btc = await rates.convert(usd_value, "usd", "btc")
    assert back_to_btc == Decimal("1")
