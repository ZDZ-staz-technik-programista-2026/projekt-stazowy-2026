from app.services.time_calculations import calculate_hours, InvalidTimeRangeError
# To import calculate_hours from this package, use: 'from app.services import calculate_hours'
# calculate_hours(start_time: time, end_time: time) -> float   # raises InvalidTimeRangeError on end <= start

from app.services.status_transitions import validate_transition, InvalidStatusTransitionError
# To import validate_transition from this package, use: 'from app.services import validate_transition'
# validate_transition(current_status: str, new_status: str, role: str) -> None   # raises InvalidStatusTransitionError on disallowed transition