from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💰 Добавить трату", callback_data="exp:new")
    builder.button(text="📊 Отчёты", callback_data="rep:menu")
    builder.button(text="💼 Бюджет", callback_data="bud:menu")
    builder.button(text="💱 Курсы / Конвертер", callback_data="rate:menu")
    builder.adjust(1)
    return builder.as_markup()


def back_to_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ В меню", callback_data="nav:main")
    return builder.as_markup()


def with_back_button(
    builder: InlineKeyboardBuilder, text: str, callback_data: str
) -> InlineKeyboardBuilder:
    builder.row(InlineKeyboardButton(text=text, callback_data=callback_data))
    return builder


def single_button_kb(text: str, callback_data: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data=callback_data)
    return builder.as_markup()
