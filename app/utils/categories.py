from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    slug: str
    emoji: str
    label: str


CATEGORIES: tuple[Category, ...] = (
    Category("food", "🍔", "Еда"),
    Category("transport", "🚕", "Транспорт"),
    Category("home", "🏠", "Жильё"),
    Category("fun", "🎉", "Развлечения"),
    Category("health", "💊", "Здоровье"),
    Category("clothes", "👕", "Одежда"),
    Category("other", "📦", "Прочее"),
)

CATEGORY_BY_SLUG: dict[str, Category] = {c.slug: c for c in CATEGORIES}

OVERALL_BUDGET_SLUG = "__all__"


def category_label(slug: str) -> str:
    if slug == OVERALL_BUDGET_SLUG:
        return "💼 Общий"
    category = CATEGORY_BY_SLUG.get(slug)
    return f"{category.emoji} {category.label}" if category else slug
