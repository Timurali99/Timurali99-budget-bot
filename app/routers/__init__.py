from aiogram import Router

from app.routers import (
    assistant,
    budgets,
    converter,
    expenses,
    help,
    news,
    reports,
    start,
)


def get_routers() -> list[Router]:
    return [
        start.router,
        expenses.router,
        budgets.router,
        reports.router,
        converter.router,
        news.router,
        help.router,
        # assistant — catch-all для свободного текста, всегда ПОСЛЕДНИЙ
        assistant.router,
    ]
