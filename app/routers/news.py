from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import settings
from app.keyboards.common_kb import BTN_NEWS
from app.services.news_service import NewsUnavailableError, news_service

router = Router(name="news")


def _news_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Обновить", callback_data="news:refresh")
    builder.button(text="⬅️ В меню", callback_data="nav:main")
    builder.adjust(1)
    return builder.as_markup()


async def _render_news() -> str:
    try:
        items = await news_service.latest(limit=6)
    except NewsUnavailableError:
        return "😔 Не удалось загрузить новости, попробуй позже."

    lines = [f"📰 <b>Свежие новости — {settings.news_source_name}</b>\n"]
    for i, item in enumerate(items, 1):
        lines.append(f'{i}. <a href="{item.link}">{item.title}</a>')
    lines.append("\n<i>Источник обновляется в реальном времени.</i>")
    return "\n".join(lines)


@router.message(F.text == BTN_NEWS)
async def news_from_button(message: Message, state: FSMContext) -> None:
    await state.clear()
    text = await _render_news()
    await message.answer(text, reply_markup=_news_kb(), disable_web_page_preview=True)


@router.callback_query(F.data == "news:menu")
async def news_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    text = await _render_news()
    await callback.message.edit_text(
        text, reply_markup=_news_kb(), disable_web_page_preview=True
    )
    await callback.answer()


@router.callback_query(F.data == "news:refresh")
async def news_refresh(callback: CallbackQuery) -> None:
    text = await _render_news()
    try:
        await callback.message.edit_text(
            text, reply_markup=_news_kb(), disable_web_page_preview=True
        )
    except Exception:
        # edit_text бросает, если текст не изменился — это нормально
        pass
    await callback.answer("Обновлено")
