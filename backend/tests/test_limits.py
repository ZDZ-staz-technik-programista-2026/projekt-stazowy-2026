import pytest
from datetime import time

from app.services import(
    check_overlap,
    check_daily_limit,
    check_weekly_limit,
    ScheduleOverlapError,
    DailyLimitExceededError,
    WeeklyLimitExceededError,
)

# --- Overlap ---
def test_overlapping_entries_are_rejected():
    with pytest.raises(ScheduleOverlapError):
        check_overlap(start_a=time(9,0), end_a=time(12, 0), start_b=time(11, 0), end_b=time(14, 0), conflicting_entry_id=1)

def test_adjacent_entries_are_accepted():
    check_overlap(start_a=time(9,0), end_a=time(12, 0), start_b=time(12, 0), end_b=time(16, 0), conflicting_entry_id=1)

def test_identical_entries_are_rejected():
    with pytest.raises(ScheduleOverlapError):
        check_overlap(start_a=time(9, 0), end_a=time(12, 0), start_b=time(9, 0), end_b=time(12, 0), conflicting_entry_id=1)

def test_non_overlapping_entries_are_accepted():
    check_overlap(start_a=time(9, 0), end_a=time(10, 0), start_b=time(14, 0), end_b=time(16, 0), conflicting_entry_id=1)

# --- Daily Limit ---
def test_entry_above_daily_limit_is_rejected():
    with pytest.raises(DailyLimitExceededError):
        check_daily_limit(current_daily_hours=3, requested_hours=6, daily_limit=8)

def test_entry_within_daily_limit_is_accepted():
    check_daily_limit(current_daily_hours=4, requested_hours=4, daily_limit=8)

def test_entry_exactly_at_daily_limit_is_accepted():
    check_daily_limit(current_daily_hours=0, requested_hours=8, daily_limit=8)

# --- Weekly Limit ---
def test_entry_above_weekly_limit_is_rejected():
    with pytest.raises(WeeklyLimitExceededError):
        check_weekly_limit(current_weekly_hours=35, requested_hours=8, weekly_limit=40)

def test_entry_within_weekly_limit_is_accepted():
    check_weekly_limit(current_weekly_hours=30, requested_hours=8, weekly_limit=40)

def test_entry_exactly_at_weekly_limit_is_accepted():
    check_weekly_limit(current_weekly_hours=32, requested_hours=8, weekly_limit=40)