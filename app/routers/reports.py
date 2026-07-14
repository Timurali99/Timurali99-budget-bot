import re
from datetime import date, datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config import settings
from app.fsm import ReportStates
from app.keyboards.common_kb import single_button_kb
from app.keyboards.reports_kb import period_kb, recent_list_kb, report_result_kb
from app.services.container import get_budget_service, get_expense_service
from app.services.expense_service import ExpenseReport
from app.utils.categories import OVERALL_BUDGET_SLUG, category_label
from app.utils.formatting import format_money, progress_bar

router = Router(name="reports")

CUSTOM_RANGE_RE = re.compile(
    r"^\s*(\d{2}\.\d{2}(?:\.\d{4})?)\s*-\s*(\d{2}\.\d{2}(?:\.\d{4})?)\s*$"
)


def _parse_date(raw: str) -> date:
    parts = raw.split(".")
    if len(parts) == 2:
        day, month = parts
        year = datetime.now().year
    else:
        day, month, year = parts
    return date(int(year), int(month), int(day))


def _format_report(report: ExpenseReport) -> str:
    if report.total_minor == 0:
        return f"📊 {report.period_label}: трат не было."
    lines = [f"📊 {report.period_label}", f"Итого: {format_money(report.total_minor, settings.base_currency)}", ""]
    for slug, amount in sorted(report.by_category.items(), key=lambda kv: -kv[1]):
        lines.append(f"{category_label(slug)}: {format_money(amount, settings.base_currency)}")
    return "\n".join(lines)


async def _report_with_budget(user_id: int, report: ExpenseReport) -> str:
    text = _format_report(report)
    budget_service = get_budget_service()
    progress = await budget_service.progress_for(user_id, OVERALL_BUDGET_SLUG)
    if progress is not None:
        bar = progress_bar(progress.spent_minor, progress.limit_minor)
        text += (
            f"\n\n💼 Общий бюджет за месяц: "
            f"{format_money(progress.spent_minor, settings.base_currency)} / "
            f"{format_money(progress.limit_minor, settings.base_currency)}\n{bar}"
        )
    return text


@router.callback_query(F.data == "rep:menu")
async def rep_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("За какой период показать отчёт?", reply_markup=period_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("rep:period:"))
async def rep_period(callback: CallbackQuery, state: FSMContext) -> None:
    period = callback.data.split(":", 2)[2]
    if period == "custom":
        await state.set_state(ReportStates.awaiting_range)
        await callback.message.edit_text(
            "Введи период в формате ДД.ММ-ДД.ММ (например: 01.07-14.07):",
            reply_markup=single_button_kb("❌ Отмена", "rep:menu"),
        )
        await callback.answer()
        return

    expense_service = get_expense_service()
    report = await expense_service.report(callback.from_user.id, period)
    text = await _report_with_budget(callback.from_user.id, report)
    await callback.message.edit_text(text, reply_markup=report_result_kb())
    await callback.answer()


@router.message(ReportStates.awaiting_range)
async def rep_custom_range(message: Message, state: FSMContext) -> None:
    match = CUSTOM_RANGE_RE.match(message.text or "")
    if not match:
        await message.answer(
            "Не понял период. Формат: ДД.ММ-ДД.ММ (например: 01.07-14.07)",
            reply_markup=single_button_kb("❌ Отмена", "rep:menu"),
        )
        return
    try:
        start = _parse_date(match.group(1))
        end = _parse_date(match.group(2))
    except ValueError:
        await message.answer(
            "Некорректная дата. Попробуй ещё раз, например: 01.07-14.07",
            reply_markup=single_button_kb("❌ Отмена", "rep:menu"),
        )
        return
    if start > end:
        start, end = end, start

    await state.clear()
    expense_service = get_expense_service()
    report = await expense_service.report(
        message.from_user.id, "custom", custom_start=start, custom_end=end
    )
    text = await _report_with_budget(message.from_user.id, report)
    await message.answer(text, reply_markup=report_result_kb())


@router.callback_query(F.data == "rep:recent")
async def rep_recent(callback: CallbackQuery) -> None:
    expense_service = get_expense_service()
    expenses = await expense_service.list_recent(callback.from_user.id, limit=10)
    if not expenses:
        await callback.answer("Пока нет ни одной траты", show_alert=True)
        return
    await callback.message.edit_text(
        "📋 Последние траты (нажми, чтобы удалить):", reply_markup=recent_list_kb(expenses)
    )
    await callback.answer()


@router.callback_query(F.data == "rep:undo_last")
async def rep_undo_last(callback: CallbackQuery) -> None:
    expense_service = get_expense_service()
    deleted = await expense_service.undo_last(callback.from_user.id)
    if deleted is None:
        await callback.answer("Нечего отменять", show_alert=True)
        return
    await callback.message.edit_text(
        f"↩️ Последняя трата отменена ({format_money(deleted.amount_base_minor, settings.base_currency)}).",
        reply_markup=report_result_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("rep:del:"))
async def rep_delete(callback: CallbackQuery) -> None:
    expense_id = int(callback.data.split(":", 2)[2])
    expense_service = get_expense_service()
    deleted = await expense_service.delete(callback.from_user.id, expense_id)
    if not deleted:
        await callback.answer("Уже удалено", show_alert=True)
        return
    expenses = await expense_service.list_recent(callback.from_user.id, limit=10)
    if not expenses:
        await callback.message.edit_text(
            "📋 Трат не осталось.", reply_markup=single_button_kb("⬅️ В меню", "nav:main")
        )
    else:
        await callback.message.edit_text(
            "📋 Последние траты (нажми, чтобы удалить):", reply_markup=recent_list_kb(expenses)
        )
    await callback.answer("Удалено")
