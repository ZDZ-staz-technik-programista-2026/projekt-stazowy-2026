from datetime import time


class ScheduleOverlapError(ValueError):
    """Raised when two time ranges for the same student overlap."""

    def __init__(self, message: str, conflicting_entry_id: int | None = None):
        super().__init__(message)
        self.conflicting_entry_id = conflicting_entry_id


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
    Raises ScheduleOverlapError if two time ranges overlap.
    Adjacent ranges (e.g. 09:00-12:00 and 12:00-16:00) are NOT overlapping.
    """
    if start_a < end_b and end_a > start_b:
        raise ScheduleOverlapError(
            f"Time entry allocation overlaps with an existing registered block (ID: {conflicting_entry_id}).",
            conflicting_entry_id=conflicting_entry_id,
        )


def check_daily_limit(current_daily_hours: float, requested_hours: float, daily_limit: float) -> None:
    if current_daily_hours + requested_hours > daily_limit:
        raise DailyLimitExceededError(
            "The requested log block exceeds your daily hourly cap configuration limit.",
            daily_limit=daily_limit,
            current_daily_hours=current_daily_hours,
            requested_hours=requested_hours,
        )


def check_weekly_limit(current_weekly_hours: float, requested_hours: float, weekly_limit: float = 40.0) -> None:
    if current_weekly_hours + requested_hours > weekly_limit:
        raise WeeklyLimitExceededError(
            "The requested log block breaches the global 40-hour running weekly quota boundary.",
            weekly_limit=weekly_limit,
            current_weekly_hours=current_weekly_hours,
            requested_hours=requested_hours,
        )