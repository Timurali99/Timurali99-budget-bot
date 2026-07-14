# budget-bot

Telegram-бот учёта расходов и бюджета: логирование трат кнопками (с быстрым
каталогом типовых покупок внутри каждой категории), отчёты по периодам, месячные
лимиты бюджета с прогресс-баром и конвертер валют/крипты на живых курсах
(open.er-api.com + CoinGecko, без ключей и без хардкода).

## Стек

Python 3.12+, aiogram 3.x, aiosqlite (SQLite), httpx. Без Postgres/Alembic/Redis —
для одного файла SQLite это лишнее.

## Локальный запуск

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # вписать BOT_TOKEN из BotFather
python -m app.main
```

## Тесты

```bash
pytest -q
```

Тесты сервисного слоя гоняются на реальном temp-SQLite (не моках БД); у
`rates_service` в тестах подменены только сетевые методы — сам расчёт конвертации
не замокан.

## Деплой на Railway

1. Подключить репозиторий в Railway (New Project → Deploy from GitHub repo).
2. В Variables задать `BOT_TOKEN` (и опционально `BASE_CURRENCY`).
3. **Обязательно** подключить persistent volume (Settings → Volumes), примонтировать
   например на `/data`, и задать `DB_PATH=/data/bot.db` в Variables — иначе база
   обнуляется при каждом редеплое (файловая система контейнера эфемерна).
4. Railway использует `deploy.startCommand` из `railway.json`, а не `CMD` из
   `Dockerfile` — при изменении команды запуска держи оба файла синхронными вручную.
