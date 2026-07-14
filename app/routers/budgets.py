from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config import settings
from app.fsm import BudgetStates
from app.keyboards.budget_kb import budget_category_picker_kb, budget_menu_kb
from app.keyboards.common_kb import single_button_kb
from app.services.container import get_budget_service
from app.utils.categories import category_label
from app.utils.formatting import format_money, progress_bar

router = Router(name="budgets")


async def _budget_overview_text(user_id: int) -> str:
    budget_service = get_budget_service()
    entries = await budget_service.list_progress(user_id)
    if not entries:
        return "💼 Лимиты бюджета ещё не заданы.\n\nНажми «✏️ Задать лимит», чтобы настроить."
    lines = ["💼 Бюджет на текущий месяц:\n"]
    for entry in entries:
        bar = progress_bar(entry.spent_minor, entry.limit_minor)
        lines.append(
            f"{category_label(entry.category)}: "
            f"{format_money(entry.spent_minor, settings.base_currency)} / "
            f"{format_money(entry.limit_minor, settings.base_currency)}\n{bar}"
        )
    return "\n\n".join(lines)


@router.callback_query(F.data == "bud:menu")
async def bud_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    text = await _budget_overview_text(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=budget_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "bud:edit")
async def bud_edit(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Для какой категории задать месячный лимит?",
        reply_markup=budget_category_picker_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("bud:set:"))
async def bud_set_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    slug = callback.data.split(":", 2)[2]
    await state.set_state(BudgetStates.awaiting_limit)
    await state.update_data(category=slug)
    await callback.message.edit_text(
        f"Введи месячный лимит для «{category_label(slug)}» в {settings.base_currency} "
        f"(например: 15000):",
        reply_markup=single_button_kb("❌ Отмена", "bud:menu"),
    )
    await callback.answer()


@router.message(BudgetStates.awaiting_limit)
async def bud_set_amount(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    category = data.get("category")
    raw = (message.text or "").strip().replace(",", ".")
    try:
        amount = Decimal(raw)
        if amount <= 0:
            raise InvalidOperation
    except InvalidOperation:
        await message.answer(
            "Не понял сумму. Введи положительное число, например: 15000",
            reply_markup=single_button_kb("❌ Отмена", "bud:menu"),
        )
        return

    budget_service = get_budget_service()
    await budget_service.set_limit(message.from_user.id, category, amount)
    await state.clear()
    text = await _budget_overview_text(message.from_user.id)
    await message.answer(f"✅ Лимит сохранён.\n\n{text}", reply_markup=budget_menu_kb())
