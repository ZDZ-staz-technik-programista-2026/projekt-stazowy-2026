"""
Business-rule validation used by the entry creation (POST) and edit
(PATCH) endpoints.
 
Two different styles are used here on purpose:
 
- validate_time_range / validate_future_date / validate_description /
  validate_entry_status_for_patch return either None (valid) or a
  ready-made JSONResponse (invalid). These predate the domain-exception
  refactor and are kept as-is, since they don't need db access to decide
  the outcome.
- check_schedule_overlap / check_hours_limit call the pure domain
  functions in app.services.limits (check_overlap, check_daily_limit,
  check_weekly_limit), which raise domain exceptions instead of
  returning a response. Those exceptions are caught by the global
  handlers in app.main, keeping the HTTP-shape decisions in one place.
"""

from datetime import date, time, datetime, timedelta

from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.models import Entry, User
from app.services.time_calculations import (
    calculate_hours,
    InvalidTimeRangeError
)

from app.services import check_overlap, check_daily_limit, check_weekly_limit


def validate_time_range(start_time, end_time):
    """
    Return the calculated hours for (start_time, end_time), or a ready
    JSONResponse (400 INVALID_TIME_RANGE) if end_time <= start_time.
    """
    try:
        return calculate_hours(start_time, end_time)
    except InvalidTimeRangeError:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "error": "BAD_REQUEST",
                "message": "Validation failed: 'end_time' cannot occur before or equal to 'start_time'.",
                "code": "INVALID_TIME_RANGE",
                "details": {
                    "start_time": str(start_time),
                    "end_time": str(end_time)
                }
            }
        )


def validate_future_date(entry_date: date):
    """Return a 400 FUTURE_DATE_FORBIDDEN JSONResponse if entry_date is after today, else None."""
    if entry_date > date.today():
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "error": "BAD_REQUEST",
                "message": "Cannot log entry information against calendar dates extending in front of the present time scope.",
                "code": "FUTURE_DATE_FORBIDDEN",
                "details": {
                    "input_date": str(entry_date)
                }
            }
        )
    return None


def validate_description(description: str):
    """Return a 400 EMPTY_DESCRIPTION JSONResponse if description is empty/whitespace-only, else None."""
    if not description or not description.strip():
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "error": "BAD_REQUEST",
                "message": "Description cannot be empty.",
                "code": "EMPTY_DESCRIPTION",
                "details": {}
            }
        )
    return None


def check_schedule_overlap(
    db: Session,
    user_id: int,
    entry_date: date,
    start_time,
    end_time
):
    """
    Compare (start_time, end_time) against every other entry the same
    student already has on entry_date, and raise ScheduleOverlapError
    (via check_overlap) on the first conflict found.
 
    exclude_entry_id excludes the entry currently being edited from the
    comparison - required for PATCH, where the entry's own pre-edit row
    would otherwise always "conflict" with the new time range.
 
    start_time/end_time may arrive as "HH:MM:SS" strings (e.g. from a
    caller that hasn't parsed them yet); they're normalized to `time`
    objects before comparison.
    """

    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, "%H:%M:%S").time()
    if isinstance(end_time, str):
        end_time = datetime.strptime(end_time, "%H:%M:%S").time()

    entries = (
        db.query(Entry)
        .filter(
            Entry.user_id == user_id,
            Entry.date == entry_date
        )
        .all()
    )

    for entry in entries:
        check_overlap(start_time, end_time, entry.start_time, entry.end_time, entry.id) # Can throw exception. Handled in main.


def check_hours_limit(
    db: Session,
    user_id: int,
    entry_date: date,
    requested_hours: float,
    exclude_entry_id: int | None = None,
):
    """
    Verify requested_hours against both the student's daily_hours_limit
    and the 40h weekly cap (Monday-Sunday), raising DailyLimitExceededError
    or WeeklyLimitExceededError (via app.services.limits) if either is
    breached.
 
    exclude_entry_id excludes the entry currently being edited from the
    "hours already logged" totals - required for PATCH, otherwise the
    entry's own pre-edit hours would be double-counted against its own
    new requested hours (see check_schedule_overlap for the same pattern).
 
    Returns a 404 USER_NOT_FOUND JSONResponse if the user doesn't exist;
    this is the one case here that still returns a response directly
    instead of raising, since "user not found" isn't one of the domain
    errors defined in app.services.limits.
    """

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        return JSONResponse(
            status_code=404,
            content={
                "status": 404,
                "error": "NOT_FOUND",
                "message": f"User with ID {user_id} was not found.",
                "code": "USER_NOT_FOUND",
                "details": {
                    "user_id": user_id
                }
            }
        )
    
    daily_query = db.query(Entry).filter(
        Entry.user_id == user_id, 
        Entry.date == entry_date,
    )
    if exclude_entry_id is not None:
        daily_query = daily_query.filter(Entry.id != exclude_entry_id)
    existing_daily_entries = daily_query.all()
    
    current_daily_hours = sum(
        calculate_hours(e.start_time, e.end_time) for e in existing_daily_entries
    )

    check_daily_limit(current_daily_hours, requested_hours, user.daily_hours_limit) # Can throw exception. Handled in main.

    monday = entry_date - timedelta(days=entry_date.weekday())
    sunday = monday + timedelta(days=6)

    weekly_query = (
    db.query(Entry)
        .filter(
            Entry.user_id == user_id,
            Entry.date >= monday,
            Entry.date <= sunday
        )
    )

    if exclude_entry_id is not None:
        weekly_query = weekly_query.filter(
            Entry.id != exclude_entry_id
        )

    entries = weekly_query.all()

    weekly_hours = sum(
        calculate_hours(entry.start_time, entry.end_time) for entry in entries
    )

    check_weekly_limit(weekly_hours, requested_hours)


ALLOWED_EDIT_STATUSES = {"draft", "needs_revision"}


def validate_entry_status_for_patch(current_status: str):
    """
    Return a 409 WORKFLOW_STATE_LOCKED JSONResponse if current_status is
    not editable (i.e. not "draft" or "needs_revision"), else None.
 
    This blocks edits to submitted/approved entries at the PATCH
    endpoint, independently of the state-machine transitions in
    app.services.status_transitions (which govern status changes, not
    field edits).
    """
    
    if current_status not in ALLOWED_EDIT_STATUSES:
        return JSONResponse(
            status_code=409,
            content={
                "status": 409,
                "error": "CONFLICT",
                "message": (
                    "The transaction cannot proceed because the entry is "
                    f"permanently locked within an immutable state tracking state ({current_status})."
                ),
                "code": "WORKFLOW_STATE_LOCKED",
                "details": {
                    "current_status": current_status
                }
            }
        )

    return None