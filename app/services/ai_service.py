import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = (
    "Ты — дружелюбный помощник внутри Telegram-бота для учёта личных расходов, "
    "бюджета и курсов валют. Отвечай на русском, кратко и по делу. Если вопрос "
    "про деньги, бюджет или финансы — дай практичный совет. На любые другие "
    "вопросы тоже отвечай нормально."
)


class AIUnavailableError(RuntimeError):
    pass


class AIService:
    def __init__(self, api_key: str, model: str):
        self._api_key = api_key
        self._model = model

    @property
    def enabled(self) -> bool:
        return bool(self._api_key)

    async def ask(self, question: str) -> str:
        if not self.enabled:
            raise AIUnavailableError("AI не настроен")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as exc:
            raise AIUnavailableError(f"Неожиданный ответ модели: {data}") from exc


def build_ai_service() -> AIService:
    from app.config import settings

    return AIService(settings.openrouter_api_key, settings.ai_model)


ai_service = build_ai_service()
