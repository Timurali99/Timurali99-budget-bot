import time
from decimal import Decimal

import httpx

FIAT_ANCHOR_URL = "https://open.er-api.com/v6/latest/USD"
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"

CRYPTO_IDS: dict[str, str] = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "usdt": "tether",
    "usdc": "usd-coin",
}
VS_CURRENCIES: tuple[str, ...] = ("usd", "rub", "eur")

POPULAR_PAIRS: tuple[tuple[str, str], ...] = (
    ("usd", "rub"),
    ("eur", "rub"),
    ("usdt", "rub"),
    ("btc", "usd"),
    ("eth", "usd"),
)


class RateUnavailableError(RuntimeError):
    pass


class RatesService:
    def __init__(self, ttl_seconds: int = 90):
        self._ttl_seconds = ttl_seconds
        self._fiat_rates: dict[str, float] | None = None
        self._fiat_fetched_at: float = 0.0
        self._crypto_snapshot: dict[str, dict[str, float]] | None = None
        self._crypto_fetched_at: float = 0.0

    async def get_fiat_rates(self) -> dict[str, float]:
        now = time.monotonic()
        if self._fiat_rates is not None and now - self._fiat_fetched_at < self._ttl_seconds:
            return self._fiat_rates

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(FIAT_ANCHOR_URL)
        response.raise_for_status()
        data = response.json()
        if data.get("result") != "success":
            raise RateUnavailableError(f"Fiat rate API returned an error: {data}")

        self._fiat_rates = data["rates"]
        self._fiat_fetched_at = now
        return self._fiat_rates

    async def get_crypto_snapshot(self) -> dict[str, dict[str, float]]:
        now = time.monotonic()
        if (
            self._crypto_snapshot is not None
            and now - self._crypto_fetched_at < self._ttl_seconds
        ):
            return self._crypto_snapshot

        params = {
            "ids": ",".join(CRYPTO_IDS.values()),
            "vs_currencies": ",".join(VS_CURRENCIES),
        }
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(COINGECKO_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise RateUnavailableError("Crypto rate API returned no data")

        self._crypto_snapshot = data
        self._crypto_fetched_at = now
        return self._crypto_snapshot

    @staticmethod
    def is_crypto(symbol: str) -> bool:
        return symbol.lower() in CRYPTO_IDS

    async def _to_usd(self, amount: Decimal, symbol: str) -> Decimal:
        symbol_lower = symbol.lower()
        if self.is_crypto(symbol_lower):
            snapshot = await self.get_crypto_snapshot()
            coin_id = CRYPTO_IDS[symbol_lower]
            price_usd = snapshot.get(coin_id, {}).get("usd")
            if price_usd is None:
                raise RateUnavailableError(f"No USD price available for {symbol}")
            return amount * Decimal(str(price_usd))

        rates = await self.get_fiat_rates()
        code = symbol.upper()
        rate = rates.get(code)
        if rate is None:
            raise RateUnavailableError(f"Unknown fiat currency: {symbol}")
        return amount / Decimal(str(rate))

    async def _from_usd(self, amount_usd: Decimal, symbol: str) -> Decimal:
        symbol_lower = symbol.lower()
        if self.is_crypto(symbol_lower):
            snapshot = await self.get_crypto_snapshot()
            coin_id = CRYPTO_IDS[symbol_lower]
            price_usd = snapshot.get(coin_id, {}).get("usd")
            if price_usd is None:
                raise RateUnavailableError(f"No USD price available for {symbol}")
            return amount_usd / Decimal(str(price_usd))

        rates = await self.get_fiat_rates()
        code = symbol.upper()
        rate = rates.get(code)
        if rate is None:
            raise RateUnavailableError(f"Unknown fiat currency: {symbol}")
        return amount_usd * Decimal(str(rate))

    async def get_rate(self, from_ccy: str, to_ccy: str) -> Decimal:
        """1 unit of from_ccy expressed in to_ccy, via a live USD bridge."""
        return await self.convert(Decimal(1), from_ccy, to_ccy)

    async def convert(self, amount: Decimal, from_ccy: str, to_ccy: str) -> Decimal:
        if from_ccy.lower() == to_ccy.lower():
            return amount
        amount_usd = await self._to_usd(amount, from_ccy)
        return await self._from_usd(amount_usd, to_ccy)


rates_service = RatesService()
