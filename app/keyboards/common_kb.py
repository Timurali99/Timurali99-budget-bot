from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Тексты нижних постоянных кнопок. Вынесены в константы, чтобы роутеры ловили их
# по точному совпадению, а AI-ассистент (catch-all) их не перехватывал.
BTN_MENU = "📋 Меню"
BTN_NEWS = "📰 Новости"
BTN_RATES = "💱 Курсы"
BTN_HELP = "❓ Помощь"
BOTTOM_BUTTON_TEXTS = {BTN_MENU, BTN_NEWS, BTN_RATES, BTN_HELP}


def bottom_reply_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_MENU), KeyboardButton(text=BTN_NEWS)],
            [KeyboardButton(text=BTN_RATES), KeyboardButton(text=BTN_HELP)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Напиши трату, вопрос или жми кнопки…",
    )


def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💰 Добавить трату", callback_data="exp:new")
    builder.button(text="📊 Отчёты", callback_data="rep:menu")
    builder.button(text="💼 Бюджет", callback_data="bud:menu")
    builder.button(text="💱 Курсы / Конвертер", callback_data="rate:menu")
    builder.button(text="📰 Новости", callback_data="news:menu")
    builder.button(text="🤖 Задать вопрос AI", callback_data="ai:hint")
    builder.button(text="❓ Помощь", callback_data="help:menu")
    builder.adjust(1, 2, 2, 1)
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
