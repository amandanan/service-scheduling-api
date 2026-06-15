"""Runtime-relative dates for tests.

Bookings go through availability checks that reject past slots, so tests must
target a date that is always in the future. Hard-coded calendar dates rot the
moment the real calendar catches up to them; these helpers compute the dates
fresh on every run instead.
"""

from datetime import date, timedelta

# default working hours are Mon-Fri 08:00-18:00, Sat 08:00-12:00, Sun closed,
# so the canonical test day must be a weekday a comfortable distance ahead.
_LEAD_DAYS = 30


def _from_now(days_ahead: int = _LEAD_DAYS) -> date:
    return date.today() + timedelta(days=days_ahead)


def future_weekday(days_ahead: int = _LEAD_DAYS) -> date:
    d = _from_now(days_ahead)
    while d.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        d += timedelta(days=1)
    return d


def future_sunday(days_ahead: int = _LEAD_DAYS) -> date:
    d = _from_now(days_ahead)
    while d.weekday() != 6:
        d += timedelta(days=1)
    return d


# a weekday (the establishment is open) and a Sunday (it is closed)
WEEKDAY = future_weekday()
WEEKDAY_STR = WEEKDAY.isoformat()
SUNDAY_STR = future_sunday().isoformat()


def at(hour: int, minute: int = 0) -> str:
    """ISO datetime string for the canonical weekday at the given time."""
    return f"{WEEKDAY_STR}T{hour:02d}:{minute:02d}:00"
