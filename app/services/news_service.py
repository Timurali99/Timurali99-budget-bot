import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class NewsItem:
    title: str
    link: str
    pub_date: str


class NewsUnavailableError(RuntimeError):
    pass


class NewsService:
    def __init__(self, rss_url: str, ttl_seconds: int = 300):
        self._rss_url = rss_url
        self._ttl_seconds = ttl_seconds
        self._cache: list[NewsItem] | None = None
        self._fetched_at: float = 0.0

    async def latest(self, limit: int = 6) -> list[NewsItem]:
        now = time.monotonic()
        if self._cache is not None and now - self._fetched_at < self._ttl_seconds:
            return self._cache[:limit]

        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                response = await client.get(
                    self._rss_url, headers={"User-Agent": "Mozilla/5.0 (budget-bot)"}
                )
            response.raise_for_status()
            root = ET.fromstring(response.content)
        except (httpx.HTTPError, ET.ParseError) as exc:
            raise NewsUnavailableError("Не удалось загрузить новости") from exc

        items: list[NewsItem] = []
        for item in root.iterfind(".//item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            pub_date = (item.findtext("pubDate") or "").strip()
            if title and link:
                items.append(NewsItem(title=title, link=link, pub_date=pub_date))
            if len(items) >= 20:
                break

        if not items:
            raise NewsUnavailableError("Источник не вернул новостей")

        self._cache = items
        self._fetched_at = now
        return items[:limit]


def build_news_service() -> NewsService:
    from app.config import settings

    return NewsService(settings.news_rss_url)


news_service = build_news_service()
