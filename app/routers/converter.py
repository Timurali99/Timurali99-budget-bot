import re
from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.fsm import ConverterStates
from app.keyboards.common_kb import single_button_kb
from app.keyboards.converter_kb import pair_result_kb, pairs_kb
from app.services.rates_service import RateUnavailableError, rates_service

router = Router(name="converter")

CUSTOM_PAIR_RE = re.compile(r"^\s*(\d+(?:[.,]\d+)?)\s+([A-Za-z]{2,5})\s+([A-Za-z]{2,5})\s*$")
PLAIN_AMOUNT_RE = re.compile(r"^\s*(\d+(?:[.,]\d+)?)\s*$")


async def _convert_and_format(amount: Decimal, from_ccy: str, to_ccy: str) -> str:
    result = await rates_service.convert(amount, from_ccy, to_ccy)
    return (
        f"💱 {amount.normalize()} {from_ccy.upper()} = "
        f"{result.quantize(Decimal('0.01'))} {to_ccy.upper()}"
    )


@router.callback_query(F.data == "rate:menu")
async def rate_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "Выбери пару или введи свою — курс всегда берётся живьём из интернета:",
        reply_markup=pairs_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("rate:pair:"))
async def rate_pair(callback: CallbackQuery) -> None:
    pair = callback.data.split(":", 2)[2]
    from_ccy, to_ccy = pair.split("_")
    try:
        text = await _convert_and_format(Decimal(1), from_ccy, to_ccy)
    except RateUnavailableError:
        await callback.answer("Не удалось получить курс, попробуй позже", show_alert=True)
        return
    await callback.message.edit_text(text, reply_markup=pair_result_kb(pair))
    await callback.answer()


@router.callback_query(F.data.startswith("rate:amount:"))
async def rate_amount_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    pair = callback.data.split(":", 2)[2]
    from_ccy, _ = pair.split("_")
    await state.set_state(ConverterStates.awaiting_amount)
    await state.update_data(pair=pair)
    await callback.message.edit_text(
        f"Введи сумму в {from_ccy.upper()}:",
        reply_markup=single_button_kb("❌ Отмена", "rate:menu"),
    )
    await callback.answer()


@router.callback_query(F.data == "rate:custom")
async def rate_custom_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ConverterStates.awaiting_amount)
    await state.update_data(pair=None)
    await callback.message.edit_text(
        "Введи сумму и валюты, например: 100 usd rub",
        reply_markup=single_button_kb("❌ Отмена", "rate:menu"),
    )
    await callback.answer()


@router.message(ConverterStates.awaiting_amount)
async def rate_amount_input(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    pair = data.get("pair")
    raw_text = message.text or ""

    if pair:
        from_ccy, to_ccy = pair.split("_")
        match = PLAIN_AMOUNT_RE.match(raw_text)
        if not match:
            await message.answer(
                "Не понял сумму. Введи число, например: 100",
                reply_markup=single_button_kb("❌ Отмена", "rate:menu"),
            )
            return
        amount_str = match.group(1)
    else:
        match = CUSTOM_PAIR_RE.match(raw_text)
        if not match:
            await message.answer(
                "Не понял. Формат: сумма из в, например: 100 usd rub",
                reply_markup=single_button_kb("❌ Отмена", "rate:menu"),
            )
            return
        amount_str, from_ccy, to_ccy = match.groups()

    try:
        amount = Decimal(amount_str.replace(",", "."))
        if amount <= 0:
            raise InvalidOperation
    except InvalidOperation:
        await message.answer(
            "Сумма должна быть положительным числом.",
            reply_markup=single_button_kb("❌ Отмена", "rate:menu"),
        )
        return

    try:
        text = await _convert_and_format(amount, from_ccy, to_ccy)
    except RateUnavailableError:
        await message.answer(
            "Не удалось получить курс для этой валюты, попробуй позже.",
            reply_markup=single_button_kb("⬅️ К парам", "rate:menu"),
        )
        return

    await state.clear()
    pair_for_kb = f"{from_ccy.lower()}_{to_ccy.lower()}"
    await message.answer(text, reply_markup=pair_result_kb(pair_for_kb))
