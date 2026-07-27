from datetime import time
import pytest

from app.services import calculate_hours, InvalidTimeRangeError

def test_full_day_equals_8_hours():
    assert calculate_hours(time(9, 0), time(17, 0)) == 8.0

def test_end_time_before_start_time_is_rejected():
    with pytest.raises(InvalidTimeRangeError):
        calculate_hours(time(17,0), time(9,0))

def test_start_time_equals_end_time_is_rejected():
    with pytest.raises(InvalidTimeRangeError):
        calculate_hours(time(9,0), time(9,0))