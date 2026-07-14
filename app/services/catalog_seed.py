from dataclasses import dataclass


@dataclass(frozen=True)
class CatalogItem:
    id: str
    category: str
    emoji: str
    label: str
    price_minor: int  # in BASE_CURRENCY, minor units (e.g. kopecks)


def _minor(major_amount: int) -> int:
    return major_amount * 100


CATALOG: tuple[CatalogItem, ...] = (
    CatalogItem("coffee", "food", "☕", "Кофе", _minor(250)),
    CatalogItem("lunch", "food", "🍽", "Обед", _minor(450)),
    CatalogItem("groceries", "food", "🛒", "Продукты", _minor(800)),
    CatalogItem("snack", "food", "🍪", "Перекус", _minor(150)),
    CatalogItem("taxi", "transport", "🚕", "Такси", _minor(350)),
    CatalogItem("metro", "transport", "🚇", "Метро", _minor(60)),
    CatalogItem("fuel", "transport", "⛽", "Бензин", _minor(2000)),
    CatalogItem("parking", "transport", "🅿️", "Парковка", _minor(150)),
    CatalogItem("rent", "home", "🏠", "Аренда", _minor(20000)),
    CatalogItem("utilities", "home", "💡", "Коммуналка", _minor(3500)),
    CatalogItem("internet", "home", "🌐", "Интернет", _minor(600)),
    CatalogItem("cinema", "fun", "🎬", "Кино", _minor(400)),
    CatalogItem("bar", "fun", "🍻", "Бар", _minor(1200)),
    CatalogItem("games", "fun", "🎮", "Игры", _minor(500)),
    CatalogItem("pharmacy", "health", "💊", "Аптека", _minor(500)),
    CatalogItem("doctor", "health", "🩺", "Врач", _minor(2000)),
    CatalogItem("gym", "health", "🏋️", "Спортзал", _minor(1500)),
    CatalogItem("clothes_item", "clothes", "👕", "Одежда", _minor(2500)),
    CatalogItem("shoes", "clothes", "👟", "Обувь", _minor(3500)),
    CatalogItem("gift", "other", "🎁", "Подарок", _minor(1000)),
    CatalogItem("other_item", "other", "📦", "Прочее", _minor(300)),
)

CATALOG_BY_ID: dict[str, CatalogItem] = {item.id: item for item in CATALOG}


def items_for_category(category: str) -> list[CatalogItem]:
    return [item for item in CATALOG if item.category == category]
