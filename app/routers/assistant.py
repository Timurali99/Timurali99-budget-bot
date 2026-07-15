import logging

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import StateFilter
from aiogram.types import Message

from app.keyboards.common_kb import BOTTOM_BUTTON_TEXTS
from app.services.ai_service import AIUnavailableError, ai_service

logger = logging.getLogger(__name__)

router = Router(name="assistant")


# Ловит любой свободный текст, когда пользователь не в FSM-сценарии и это не
# нижняя кнопка/команда. Регистрируется ПОСЛЕДНИМ, поэтому не мешает остальным.
@router.message(
    StateFilter(None),
    F.text,
    ~F.text.startswith("/"),
    ~F.text.in_(BOTTOM_BUTTON_TEXTS),
)
async def ask_ai(message: Message) -> None:
    if not ai_service.enabled:
        await message.answer(
            "🤖 AI-ассистент пока не подключён. Добавь переменную "
            "<code>OPENROUTER_API_KEY</code> (бесплатный ключ на openrouter.ai/keys), "
            "и я смогу отвечать на вопросы."
        )
        return

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    try:
        answer = await ai_service.ask(message.text)
    except AIUnavailableError:
        await message.answer("🤖 Не смог получить ответ. Попробуй переформулировать.")
        return
    except Exception:
        logger.exception("AI request failed")
        await message.answer("😔 Сервис ИИ временно недоступен, попробуй позже.")
        return

    await message.answer(answer, disable_web_page_preview=True)
