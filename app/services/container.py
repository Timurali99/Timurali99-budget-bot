from app.config import settings
from app.database.db import get_connection
from app.repositories.budget_repository import BudgetRepository
from app.repositories.expense_repository import ExpenseRepository
from app.services.budget_service import BudgetService
from app.services.expense_service import ExpenseService
from app.services.rates_service import rates_service


def get_expense_service() -> ExpenseService:
    return ExpenseService(
        ExpenseRepository(get_connection()), rates_service, settings.base_currency
    )


def get_budget_service() -> BudgetService:
    conn = get_connection()
    return BudgetService(BudgetRepository(conn), ExpenseRepository(conn))
