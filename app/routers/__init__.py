from aiogram import Router

from app.routers import budgets, converter, expenses, reports, start


def get_routers() -> list[Router]:
    return [
        start.router,
        expenses.router,
        budgets.router,
        reports.router,
        converter.router,
    ]
