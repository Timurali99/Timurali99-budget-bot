from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.common_kb import with_back_button
from app.services.rates_service import POPULAR_PAIRS


def pairs_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for from_ccy, to_ccy in POPULAR_PAIRS:
        builder.button(
            text=f"{from_ccy.upper()} → {to_ccy.upper()}",
            callback_data=f"rate:pair:{from_ccy}_{to_ccy}",
        )
    builder.button(text="🔧 Своя пара", callback_data="rate:custom")
    builder.adjust(2)
    with_back_button(builder, "⬅️ В меню", "nav:main")
    return builder.as_markup()


def pair_result_kb(pair: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Своя сумма", callback_data=f"rate:amount:{pair}")
    builder.adjust(1)
    with_back_button(builder, "⬅️ К парам", "rate:menu")
    return builder.as_markup()
