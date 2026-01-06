from datetime import datetime, timezone

def get_previous_month(now: datetime | None = None) -> str:
    if now is None:
        now = datetime.now(timezone.utc)

    year, month = now.year, now.month
    if month == 1:
        return f"{year-1}-12"
    return f"{year}-{month-1:02d}"