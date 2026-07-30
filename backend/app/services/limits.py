"""
Pure domain functions for enforcing worked-hours and scheduling rules:
daily/weekly hour limits and overlap detection between entries.

These functions raise domain-specific exceptions instead of returning
HTTP responses directly. The API layer (see app/main.py) catches these
exceptions and translates them into the appropriate HTTP status code
and error body, keeping business rules independent of the web framework.
"""
from datetime import time

class ScheduleOverlapError(ValueError):
    """Raised when two time ranges for the same student overlap."""

    def __init__(self, message: str, conflicting_entry_id: int | None = None, conflicting_range: str | None = None):
        super().__init__(message)
        self.conflicting_entry_id = conflicting_entry_id
        self.conflicting_range = conflicting_range


class DailyLimitExceededError(ValueError):
    """Raised when requested hours would exceed the daily limit."""

    def __init__(self, message: str, daily_limit: float, current_daily_hours: float, requested_hours: float):
        super().__init__(message)
        self.daily_limit = daily_limit
        self.current_daily_hours = current_daily_hours
        self.requested_hours = requested_hours


class WeeklyLimitExceededError(ValueError):
    """Raised when requested hours would exceed the weekly limit."""

    def __init__(self, message: str, weekly_limit: float, current_weekly_hours: float, requested_hours: float):
        super().__init__(message)
        self.weekly_limit = weekly_limit
        self.current_weekly_hours = current_weekly_hours
        self.requested_hours = requested_hours


def check_overlap(start_a: time, end_a: time, start_b: time, end_b: time, conflicting_entry_id: int) -> None:
    """
    Raise ScheduleOverlapError if two time ranges overlap.

    Ranges that share an exact boundary (e.g. 09:00-12:00 and 12:00-16:00)
    are NOT considered overlapping - this is intentional, since a student
    can log consecutive blocks of work back to back.

    Args:
        start_a, end_a: time range of the entry being validated.
        start_b, end_b: time range of an existing, already-stored entry.
        conflicting_entry_id: id of the existing entry, used for the error message.
    """
    if start_a < end_b and end_a > start_b:
        raise ScheduleOverlapError(
            f"Time entry allocation overlaps with an existing registered block (ID: {conflicting_entry_id}).",
            conflicting_entry_id=conflicting_entry_id,
            conflicting_range=f"{start_b.strftime('%H:%M')}-{end_b.strftime('%H:%M')}",
        )


def check_daily_limit(current_daily_hours: float, requested_hours: float, daily_limit: float) -> None:
    """
    Raise DailyLimitExceededError if adding requested_hours to
    current_daily_hours (hours already logged that day) would exceed
    the student's daily_hours_limit.
    """
    if current_daily_hours + requested_hours > daily_limit:
        raise DailyLimitExceededError(
            "The requested log block exceeds your daily hourly cap configuration limit.",
            daily_limit=daily_limit,
            current_daily_hours=current_daily_hours,
            requested_hours=requested_hours,
        )


def check_weekly_limit(current_weekly_hours: float, requested_hours: float, weekly_limit: float = 40.0) -> None:
    """
    Raise WeeklyLimitExceededError if adding requested_hours to
    current_weekly_hours (hours already logged Monday-Sunday) would
    exceed the weekly_limit (defaults to the 40h contractual cap).
    """
    if current_weekly_hours + requested_hours > weekly_limit:
        raise WeeklyLimitExceededError(
            "The requested log block breaches the global 40-hour running weekly quota boundary.",
            weekly_limit=weekly_limit,
            current_weekly_hours=current_weekly_hours,
            requested_hours=requested_hours,
        )