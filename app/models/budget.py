from dataclasses import dataclass


@dataclass(frozen=True)
class BudgetLimit:
    id: int
    user_id: int
    category: str
    limit_minor: int
    updated_at: str
