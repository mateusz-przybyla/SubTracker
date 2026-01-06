from datetime import datetime, timezone

from api.utils import date_helpers

def test_get_previous_month_normal_case():
    dt = datetime(2026, 8, 15, tzinfo=timezone.utc)

    result = date_helpers.get_previous_month(dt)

    assert result == "2026-07"

def test_get_previous_month_january():
    dt = datetime(2026, 1, 10, tzinfo=timezone.utc)

    result = date_helpers.get_previous_month(dt)

    assert result == "2025-12"

def test_get_previous_month_february():
    dt = datetime(2026, 2, 1, tzinfo=timezone.utc)

    result = date_helpers.get_previous_month(dt)

    assert result == "2026-01"

def test_get_previous_month_zero_padding():
    dt = datetime(2026, 10, 1, tzinfo=timezone.utc)

    result = date_helpers.get_previous_month(dt)

    assert result == "2026-09"