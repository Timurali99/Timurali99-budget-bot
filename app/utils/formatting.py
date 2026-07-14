from decimal import ROUND_HALF_UP, Decimal


def minor_to_decimal(amount_minor: int) -> Decimal:
    return (Decimal(amount_minor) / 100).quantize(Decimal("0.01"))


def decimal_to_minor(amount: Decimal) -> int:
    return int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def format_money(amount_minor: int, currency: str) -> str:
    value = minor_to_decimal(amount_minor)
    return f"{value:,.2f} {currency}".replace(",", " ")


def progress_bar(spent_minor: int, limit_minor: int, width: int = 10) -> str:
    if limit_minor <= 0:
        return ""
    ratio = min(spent_minor / limit_minor, 1.0)
    filled = round(ratio * width)
    bar = "🟩" * filled + "⬜" * (width - filled)
    percent = round(ratio * 100)
    warning = " ⚠️" if spent_minor > limit_minor else ""
    return f"{bar} {percent}%{warning}"
