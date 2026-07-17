from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from fastapi.responses import JSONResponse

from app.database import SessionLocal
from app.models import Entry, Review, User
from app.services.time_calculations import (
    calculate_hours,
    InvalidTimeRangeError
)

router = APIRouter(prefix="/api")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def format_review(review):
    if review is None:
        return None

    return {
        "id": review.id,
        "comment": review.comment,
        "decision": review.decision,
        "created_at": review.created_at,
        "created_by": {
            "id": review.created_by_user.id,
            "name": review.created_by_user.name,
            "role": review.created_by_user.role.name
        }
    }


def calculate_entry_hours(entry):
    if entry.start_time is None or entry.end_time is None:
        raise InvalidTimeRangeError()
        
    return calculate_hours(
        entry.start_time,
        entry.end_time
    )


def get_latest_review(entry):
    if not entry.reviews:
        return None

    return max(
        entry.reviews,
        key=lambda review: review.created_at
    )


def format_entry(entry):
    hours = calculate_entry_hours(entry)
    
    return {
        "id": entry.id,
        "user_id": entry.user_id,
        "date": entry.date,
        "start_time": entry.start_time,
        "end_time": entry.end_time,
        "calculated_hours": hours,
        "description": entry.description,
        "blockers": entry.blockers,
        "status": entry.status,
        "created_at": entry.created_at,
        "latest_review": format_review(
            get_latest_review(entry)
        )
    }


def entries_query(db: Session):
    return (
        db.query(Entry)
        .options(
            joinedload(Entry.user)
            .joinedload(User.role),

            joinedload(Entry.reviews)
            .joinedload(Review.created_by_user)
            .joinedload(User.role)
        )
    )


@router.get("/entries")
def get_entries(
    user_id: int | None = Query(default=None),
    db: Session = Depends(get_db)
):
    query = entries_query(db)

    if user_id is not None:
        query = query.filter(
            Entry.user_id == user_id
        )

    entries = query.all()

    try:
        return [
            format_entry(entry)
            for entry in entries
        ]
    except InvalidTimeRangeError:
        start_val = "..."
        end_val = "..."
        
        for el in entries:
            if el.start_time is None or el.end_time is None or el.end_time <= el.start_time:
                start_val = str(el.start_time) if el.start_time is not None else "..."
                end_val = str(el.end_time) if el.end_time is not None else "..."
                break

        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "error": "BAD_REQUEST",
                "message": "Validation failed: 'end_time' cannot occur before or equal to 'start_time'.",
                "code": "INVALID_TIME_RANGE",
                "details": {
                    "start_time": start_val,
                    "end_time": end_val
                }
            }
        )


@router.get("/entries/{id}")
def get_entry(
    id: int,
    db: Session = Depends(get_db)
):
    entry = (
        entries_query(db)
        .filter(Entry.id == id)
        .first()
    )

    if entry is None:
        return JSONResponse(
            status_code=404,
            content={
                "status": 404,
                "error": "NOT_FOUND",
                "message": f"Target time entry resource record with ID {id} was not found.",
                "code": "ENTRY_NOT_FOUND",
                "details": {
                    "entry_id": id
                }
            }
        )

    try:
        return format_entry(entry)
    except InvalidTimeRangeError:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "error": "BAD_REQUEST",
                "message": "Validation failed: 'end_time' cannot occur before or equal to 'start_time'.",
                "code": "INVALID_TIME_RANGE",
                "details": {
                    "start_time": str(entry.start_time) if entry.start_time is not None else "...",
                    "end_time": str(entry.end_time) if entry.end_time is not None else "..."
                }
            }
        )