from datetime import date

def get_previous_month() -> str:
    today = date.today()
    year, month = today.year, today.month
    if month == 1:
        return f"{year-1}-12"
    return f"{year}-{month-1:02d}"