# web/ — витрина ZAP.TUT (отдельный сервис)

Статичная витрина автозапчастей + тонкий FastAPI-прокси к Catalog API. Это
**отдельный Railway-сервис**, он не импортирует код бота и не трогает корневой
`railway.json`/`Dockerfile`. Браузер ходит только на свой домен (`/api/proxy/*`),
поэтому CORS не нужен, а лежащий/спящий каталог показывает офлайн-состояние.

## Локальный запуск

```bash
cd web
pip install -r requirements.txt
uvicorn server:app --reload --port 8080
# открой http://localhost:8080
```

## Переменные окружения

| Переменная | Зачем | Дефолт |
|---|---|---|
| `CATALOG_API_BASE` | база read-only Catalog API | `https://empathetic-renewal-production-8293.up.railway.app` |
| `SITE_BOT_USERNAME` | бот заказов для deep-link `?start=buy_<id>` (без `@`) | пусто → кнопка «Заказать» ведёт менеджеру |
| `CHANNEL_USERNAME` | канал | `@zap_tut` |
| `MANAGER_USERNAME` | менеджер для «Написать» (без `@`) | `Temurali_aliev` |

## Деплой в существующий Railway-проект (рядом с ботом)

Сайт живёт в этом же GitHub-репозитории в папке `web/`. В нужном проекте:

1. Открой проект **brave-consideration** → **New** → **GitHub Repo** → выбери
   этот репозиторий (`Timurali99/Timurali99-budget-bot`, ветка `feat/storefront-site`).
   Появится новый сервис.
2. Сервис → **Settings → Source → Root Directory** = `web`.
   Это изолирует сборку: Railway возьмёт `web/Dockerfile` и `web/railway.json`,
   а не корневой конфиг бота.
3. **Settings → Networking → Generate Domain** — получишь публичный URL сайта.
4. **Variables** — задай при необходимости `SITE_BOT_USERNAME` (юзернейм бота
   заказов). Остальное имеет рабочие дефолты.
5. Deploy. Проверка: `https://<домен>/health` → `{"status":"ok"}`.

> Ничего в сервисе бота менять не нужно — CORS больше не задействован, запросы к
> каталогу идут server-to-server из сервиса сайта.

## Что подтвердить по связке с ботом

Кнопка «Заказать» ведёт на `https://t.me/<bot>?start=buy_<product_id>`. В боте
deep-link `buy_` исторически ждёт `publication_id`, а каталог отдаёт `product_id`.
Если id-схемы различаются — нужен обработчик `?start=buy_<product_id>` на стороне
бота (или маппинг product→publication). До этого «Заказать» безопасно падает на
переписку с менеджером, когда `SITE_BOT_USERNAME` пуст.
