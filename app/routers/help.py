from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.db import get_connection
from app.keyboards.common_kb import BTN_HELP
from app.repositories.budget_repository import BudgetRepository
from app.repositories.expense_repository import ExpenseRepository

router = Router(name="help")

HELP_TEXT = (
    "❓ <b>Помощь</b>\n\n"
    "• 💰 <b>Добавить трату</b> — выбери категорию и жми готовую покупку "
    "или введи свою сумму (можно в валюте: <code>20 USD</code>).\n"
    "• 📊 <b>Отчёты</b> — траты за сегодня / неделю / месяц / свой период.\n"
    "• 💼 <b>Бюджет</b> — месячные лимиты по категориям с прогресс-баром.\n"
    "• 💱 <b>Курсы</b> — живые курсы валют и крипты из интернета.\n"
    "• 📰 <b>Новости</b> — свежие заголовки из проверенного источника.\n"
    "• 🤖 <b>Вопрос AI</b> — просто напиши любой вопрос сообщением.\n\n"
    "Кнопки снизу всегда под рукой: Меню, Новости, Курсы, Помощь."
)


def _help_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑 Удалить все мои данные", callback_data="help:wipe")
    builder.button(text="⬅️ В меню", callback_data="nav:main")
    builder.adjust(1)
    return builder.as_markup()


def _confirm_wipe_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, удалить всё", callback_data="help:wipe:yes")
    builder.button(text="❌ Отмена", callback_data="help:menu")
    builder.adjust(1)
    return builder.as_markup()


@router.message(F.text == BTN_HELP)
async def help_from_button(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(HELP_TEXT, reply_markup=_help_kb())


@router.callback_query(F.data == "help:menu")
async def help_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(HELP_TEXT, reply_markup=_help_kb())
    await callback.answer()


@router.callback_query(F.data == "help:wipe")
async def help_wipe_confirm(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "⚠️ <b>Удалить ВСЕ твои данные?</b>\n\n"
        "Будут стёрты все траты и лимиты бюджета. Это действие необратимо.",
        reply_markup=_confirm_wipe_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "help:wipe:yes")
async def help_wipe_do(callback: CallbackQuery) -> None:
    conn = get_connection()
    user_id = callback.from_user.id
    expenses_deleted = await ExpenseRepository(conn).delete_all(user_id)
    await BudgetRepository(conn).delete_all(user_id)
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ В меню", callback_data="nav:main")
    await callback.message.edit_text(
        f"🗑 Готово. Удалено трат: {expenses_deleted}. Все лимиты сброшены.",
        reply_markup=builder.as_markup(),
    )
    await callback.answer("Данные удалены")
