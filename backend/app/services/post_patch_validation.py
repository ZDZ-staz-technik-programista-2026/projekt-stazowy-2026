from datetime import date, time, datetime, timedelta

from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.models import Entry, User
from app.services.time_calculations import (
    calculate_hours,
    InvalidTimeRangeError
)


def validate_time_range(start_time, end_time):
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
        if (
            start_time < entry.end_time
            and end_time > entry.start_time
        ):
            return JSONResponse(
                status_code=409,
                content={
                    "status": 409,
                    "error": "CONFLICT",
                    "message": f"Time entry allocation overlaps with an existing registered block (ID: {entry.id}).",
                    "code": "SCHEDULE_OVERLAP",
                    "details": {
                        "conflicting_entry_id": entry.id,
                        "conflicting_range": f"{entry.start_time.strftime('%H:%M')}-{entry.end_time.strftime('%H:%M')}"
                    }
                }
            )
    return None


def check_hours_limit(
    db: Session,
    user_id: int,
    entry_date: date,
    requested_hours: float
):
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
    existing_daily_entries = (
        db.query(Entry)
        .filter(
            Entry.user_id == user_id,
            Entry.date == entry_date
        )
        .all()
    )
    
    current_daily_hours = sum(
        calculate_hours(e.start_time, e.end_time) for e in existing_daily_entries
    )

    if current_daily_hours + requested_hours > user.daily_hours_limit:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "error": "BAD_REQUEST",
                "message": "The requested log block exceeds your daily hourly cap configuration limit (8h) or breaches the global 40-hour running weekly quota boundary.",
                "code": "HOURLY_LIMIT_EXCEEDED",
                "details": {
                    "type": "daily_limit_breach",
                    "daily_limit": float(user.daily_hours_limit),
                    "current_daily_accumulated_hours": current_daily_hours,
                    "requested_hours": requested_hours
                }
            }
        )

    monday = entry_date - timedelta(days=entry_date.weekday())
    sunday = monday + timedelta(days=6)

    entries = (
        db.query(Entry)
        .filter(
            Entry.user_id == user_id,
            Entry.date >= monday,
            Entry.date <= sunday
        )
        .all()
    )

    weekly_hours = sum(
        calculate_hours(entry.start_time, entry.end_time) for entry in entries
    )

    if weekly_hours + requested_hours > 40:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "error": "BAD_REQUEST",
                "message": "The requested log block exceeds your daily hourly cap configuration limit (8h) or breaches the global 40-hour running weekly quota boundary.",
                "code": "HOURLY_LIMIT_EXCEEDED",
                "details": {
                    "type": "weekly_limit_breach",
                    "weekly_limit": 40.0,
                    "current_weekly_accumulated_hours": weekly_hours,
                    "requested_hours": requested_hours
                }
            }
        )
    return None


ALLOWED_EDIT_STATUSES = {"draft", "needs_revision"}


def validate_entry_status_for_patch(current_status: str):
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