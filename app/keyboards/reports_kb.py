from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.common_kb import with_back_button
from app.models.expense import Expense


def period_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Сегодня", callback_data="rep:period:today")
    builder.button(text="🗓 7 дней", callback_data="rep:period:week")
    builder.button(text="📆 Месяц", callback_data="rep:period:month")
    builder.button(text="🔧 Свой период", callback_data="rep:period:custom")
    builder.adjust(2)
    with_back_button(builder, "⬅️ В меню", "nav:main")
    return builder.as_markup()


def report_result_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Последние траты", callback_data="rep:recent")
    builder.button(text="↩️ Отменить последнюю", callback_data="rep:undo_last")
    builder.adjust(1)
    with_back_button(builder, "⬅️ В меню", "nav:main")
    return builder.as_markup()


def recent_list_kb(expenses: list[Expense]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for expense in expenses:
        label = expense.note or f"{expense.category}"
        builder.row(
            InlineKeyboardButton(
                text=f"🗑 {label} — {expense.amount_base_minor // 100}₽",
                callback_data=f"rep:del:{expense.id}",
            )
        )
    with_back_button(builder, "⬅️ В меню", "nav:main")
    return builder.as_markup()
