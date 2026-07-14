from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.common_kb import with_back_button
from app.utils.categories import CATEGORIES, OVERALL_BUDGET_SLUG


def budget_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Задать лимит", callback_data="bud:edit")
    builder.adjust(1)
    with_back_button(builder, "⬅️ В меню", "nav:main")
    return builder.as_markup()


def budget_category_picker_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💼 Общий лимит", callback_data=f"bud:set:{OVERALL_BUDGET_SLUG}")
    for category in CATEGORIES:
        builder.button(
            text=f"{category.emoji} {category.label}", callback_data=f"bud:set:{category.slug}"
        )
    builder.adjust(2)
    with_back_button(builder, "⬅️ Назад", "bud:menu")
    return builder.as_markup()
