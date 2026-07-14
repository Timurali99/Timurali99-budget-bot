from dataclasses import dataclass


@dataclass(frozen=True)
class Expense:
    id: int
    user_id: int
    category: str
    amount_minor: int
    currency: str
    amount_base_minor: int
    rate_used: float | None
    note: str | None
    created_at: str
