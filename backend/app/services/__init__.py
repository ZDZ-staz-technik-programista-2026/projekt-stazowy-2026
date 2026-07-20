from app.services.time_calculations import calculate_hours, InvalidTimeRangeError

# To import calculate_hours from this package, use: 'from app.services import calculate_hours'
# calculate_hours(start_time: time, end_time: time) -> float   # raises InvalidTimeRangeError on end <= start