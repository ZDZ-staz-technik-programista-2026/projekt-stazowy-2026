from datetime import date, datetime, time

class InvalidTimeRangeError(ValueError):
    """ Raised when end_time <= start_time """

def calculate_hours(start_time : time, end_time : time) -> float:
    """
    Function that returns number of hours between start_time and end_time.
    - 09:00-17:00 -> 8.0
    - end_time <= start_time -> InvalidTimeRangeError
    """
    if end_time <= start_time:
        raise InvalidTimeRangeError(
            "End time must be greater than start time."
        )
    
    start_dt = datetime.combine(date.min, start_time)
    end_dt   = datetime.combine(date.min, end_time)
    time_delta = end_dt - start_dt

    return time_delta.total_seconds() / 3600