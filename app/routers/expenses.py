from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config import settings
from app.fsm import ExpenseStates
from app.keyboards.common_kb import single_button_kb
from app.keyboards.expense_kb import categories_kb, confirm_kb, quick_add_kb
from app.services.budget_service import BudgetService
from app.services.container import get_budget_service, get_expense_service
from app.services.expense_service import InvalidAmountError
from app.utils.categories import CATEGORY_BY_SLUG, OVERALL_BUDGET_SLUG, category_label
from app.utils.formatting import format_money, progress_bar

router = Router(name="expenses")


async def _confirmation_text(user_id: int, category: str, amount_base_minor: int, note: str | None) -> str:
    budget_service: BudgetService = get_budget_service()
    label = category_label(category)
    what = f"{label}"
    if note:
        what += f" — {note}"
    text = f"✅ Записано: {what}\n💵 {format_money(amount_base_minor, settings.base_currency)}"

    for slug in (category, OVERALL_BUDGET_SLUG):
        progress = await budget_service.progress_for(user_id, slug)
        if progress is not None:
            bar = progress_bar(progress.spent_minor, progress.limit_minor)
            scope = "по категории" if slug == category else "общий"
            text += (
                f"\n\n📊 Бюджет ({scope}): "
                f"{format_money(progress.spent_minor, settings.base_currency)} / "
                f"{format_money(progress.limit_minor, settings.base_currency)}\n{bar}"
            )
    return text


@router.callback_query(F.data == "exp:new")
async def exp_new(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("Выбери категорию траты:", reply_markup=categories_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("exp:cat:"))
async def exp_category(callback: CallbackQuery) -> None:
    slug = callback.data.split(":")[2]
    category = CATEGORY_BY_SLUG.get(slug)
    if category is None:
        await callback.answer("Неизвестная категория", show_alert=True)
        return
    await callback.message.edit_text(
        f"{category.emoji} {category.label} — выбери покупку или введи свою сумму:",
        reply_markup=quick_add_kb(slug),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("exp:q:"))
async def exp_quick(callback: CallbackQuery) -> None:
    item_id = callback.data.split(":", 2)[2]
    expense_service = get_expense_service()
    try:
        expense = await expense_service.log_quick(callback.from_user.id, item_id)
    except InvalidAmountError as exc:
        await callback.answer(str(exc), show_alert=True)
        return
    text = await _confirmation_text(
        callback.from_user.id, expense.category, expense.amount_base_minor, expense.note
    )
    await callback.message.edit_text(text, reply_markup=confirm_kb(expense.id))
    await callback.answer()


@router.callback_query(F.data.startswith("exp:custom:"))
async def exp_custom_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    slug = callback.data.split(":", 2)[2]
    await state.set_state(ExpenseStates.awaiting_amount)
    await state.update_data(category=slug)
    await callback.message.edit_text(
        "Введи сумму (например: 450 или 20 USD):",
        reply_markup=single_button_kb("❌ Отмена", "exp:new"),
    )
    await callback.answer()


@router.message(ExpenseStates.awaiting_amount)
async def exp_custom_amount(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    category = data.get("category")
    expense_service = get_expense_service()
    try:
        expense = await expense_service.log_custom(message.from_user.id, category, message.text or "")
    except InvalidAmountError as exc:
        await message.answer(str(exc), reply_markup=single_button_kb("❌ Отмена", "exp:new"))
        return
    await state.clear()
    text = await _confirmation_text(
        message.from_user.id, expense.category, expense.amount_base_minor, expense.note
    )
    await message.answer(text, reply_markup=confirm_kb(expense.id))


@router.callback_query(F.data.startswith("exp:undo:"))
async def exp_undo(callback: CallbackQuery) -> None:
    expense_id = int(callback.data.split(":", 2)[2])
    expense_service = get_expense_service()
    deleted = await expense_service.delete(callback.from_user.id, expense_id)
    if deleted:
        await callback.message.edit_text(
            "↩️ Трата отменена.", reply_markup=single_button_kb("⬅️ В меню", "nav:main")
        )
    else:
        await callback.answer("Уже отменено или не найдено", show_alert=True)
        return
    await callback.answer()
