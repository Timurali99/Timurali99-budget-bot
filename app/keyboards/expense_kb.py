from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.common_kb import with_back_button
from app.services.catalog_seed import CatalogItem, items_for_category
from app.utils.categories import CATEGORIES


def categories_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for category in CATEGORIES:
        builder.button(
            text=f"{category.emoji} {category.label}", callback_data=f"exp:cat:{category.slug}"
        )
    builder.adjust(2)
    with_back_button(builder, "⬅️ В меню", "nav:main")
    return builder.as_markup()


def quick_add_kb(category_slug: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    items: list[CatalogItem] = items_for_category(category_slug)
    for item in items:
        price_major = item.price_minor // 100
        builder.button(
            text=f"{item.emoji} {item.label} — {price_major}₽",
            callback_data=f"exp:q:{item.id}",
        )
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(
            text="✏️ Другая сумма", callback_data=f"exp:custom:{category_slug}"
        )
    )
    with_back_button(builder, "⬅️ К категориям", "exp:new")
    return builder.as_markup()


def confirm_kb(expense_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="↩️ Отменить", callback_data=f"exp:undo:{expense_id}")
    builder.button(text="➕ Ещё трата", callback_data="exp:new")
    builder.adjust(1)
    with_back_button(builder, "⬅️ В меню", "nav:main")
    return builder.as_markup()
