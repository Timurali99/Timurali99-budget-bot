from aiogram.fsm.state import State, StatesGroup


class ExpenseStates(StatesGroup):
    awaiting_amount = State()


class BudgetStates(StatesGroup):
    awaiting_limit = State()


class ReportStates(StatesGroup):
    awaiting_range = State()


class ConverterStates(StatesGroup):
    awaiting_amount = State()
