from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.common_kb import BTN_MENU, bottom_reply_kb, main_menu_kb

router = Router(name="start")

WELCOME_TEXT = (
    "👋 Привет! Я помогу учитывать расходы, следить за бюджетом, показывать "
    "актуальные курсы валют и крипты, свежие новости и отвечать на любые вопросы.\n\n"
    "💡 Просто напиши мне вопрос — и я отвечу. А для учёта трат жми кнопки ниже."
)

MENU_TEXT = "Главное меню — выбери, что хочешь сделать:"


async def _open_menu(message: Message, state: FSMContext, greet: bool = False) -> None:
    await state.clear()
    if greet:
        await message.answer(WELCOME_TEXT, reply_markup=bottom_reply_kb())
    await message.answer(MENU_TEXT, reply_markup=main_menu_kb())


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await _open_menu(message, state, greet=True)


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    await _open_menu(message, state)


@router.message(F.text == BTN_MENU)
async def btn_menu(message: Message, state: FSMContext) -> None:
    await _open_menu(message, state)


@router.callback_query(F.data == "nav:main")
async def nav_main(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(MENU_TEXT, reply_markup=main_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "ai:hint")
async def ai_hint(callback: CallbackQuery) -> None:
    await callback.answer(
        "Просто напиши свой вопрос сообщением — я отвечу 🤖", show_alert=True
    )
