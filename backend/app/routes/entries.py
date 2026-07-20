import datetime
from typing import Optional

from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal
from app.models import Entry, Review, User

from app.services.time_calculations import (
    calculate_hours,
    InvalidTimeRangeError
)

from app.services.post_patch_validation import (
    validate_time_range,
    validate_future_date,
    validate_description,
    check_schedule_overlap,
    check_hours_limit,
    validate_entry_status_for_patch,
)


router = APIRouter(prefix="/api")


# ==========================
# Pydantic Models
# ==========================

class EntryCreateRequest(BaseModel):
    user_id: int

    date: datetime.date

    start_time: datetime.time
    end_time: datetime.time

    description: str

    blockers: Optional[str] = "None"


class EntryPatchRequest(BaseModel):
    date: Optional[datetime.date] = None

    start_time: Optional[datetime.time] = None
    end_time: Optional[datetime.time] = None

    description: Optional[str] = None

    blockers: Optional[str] = None


# ==========================
# Database dependency
# ==========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================
# Queries
# ==========================

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



@router.get("/entries")
def get_entries(
    user_id: int | None = Query(default=None),
    db: Session = Depends(get_db)
):
    query = entries_query(db)

    if user_id is not None:
        query = query.filter(Entry.user_id == user_id)

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


@router.post("/entries", status_code=status.HTTP_201_CREATED)
def create_entry(
    request: EntryCreateRequest,
    db: Session = Depends(get_db)
):
    hours_or_error = validate_time_range(request.start_time, request.end_time)
    if isinstance(hours_or_error, JSONResponse):
        return hours_or_error
    
    calculated_hours = hours_or_error

    future_date_error = validate_future_date(request.date)
    if isinstance(future_date_error, JSONResponse):
        return future_date_error

    description_error = validate_description(request.description)
    if isinstance(description_error, JSONResponse):
        return description_error

    overlap_error = check_schedule_overlap(
        db=db,
        user_id=request.user_id,
        entry_date=request.date,
        start_time=request.start_time,
        end_time=request.end_time
    )
    if isinstance(overlap_error, JSONResponse):
        return overlap_error

    limit_error = check_hours_limit(
        db=db,
        user_id=request.user_id,
        entry_date=request.date,
        requested_hours=calculated_hours
    )
    if isinstance(limit_error, JSONResponse):
        return limit_error

    entry = Entry(
        user_id=request.user_id,
        date=request.date,
        start_time=request.start_time,
        end_time=request.end_time,
        description=request.description,
        blockers=request.blockers,
        status="draft"
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    full_entry = (
        entries_query(db)
        .filter(Entry.id == entry.id)
        .first()
    )

    return format_entry(full_entry)


@router.patch("/entries/{id}")
def patch_entry(
    id: int,
    request: EntryPatchRequest,
    db: Session = Depends(get_db),
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

    status_error = validate_entry_status_for_patch(entry.status)

    if isinstance(status_error, JSONResponse):
        return status_error
    
    new_date = (
        request.date
        if request.date is not None
        else entry.date
    )

    new_start = (
        request.start_time
        if request.start_time is not None
        else entry.start_time
    )

    new_end = (
        request.end_time
        if request.end_time is not None
        else entry.end_time
    )

    new_description = (
        request.description
        if request.description is not None
        else entry.description
    )

    hours_or_error = validate_time_range(
        new_start,
        new_end
    )

    if isinstance(hours_or_error, JSONResponse):
        return hours_or_error

    future_error = validate_future_date(new_date)
    if isinstance(future_error, JSONResponse):
        return future_error

    description_error = validate_description(new_description)
    if isinstance(description_error, JSONResponse):
        return description_error

    existing_entries = (
        db.query(Entry)
        .filter(
            Entry.user_id == entry.user_id,
            Entry.date == new_date,
            Entry.id != entry.id
        )
        .all()
    )

    for existing in existing_entries:
        if (
            new_start < existing.end_time
            and new_end > existing.start_time
        ):
            return JSONResponse(
                status_code=409,
                content={
                    "status": 409,
                    "error": "CONFLICT",
                    "message": (
                        f"Time entry allocation overlaps with an existing "
                        f"registered block (ID: {existing.id})."
                    ),
                    "code": "SCHEDULE_OVERLAP",
                    "details": {
                        "conflicting_entry_id": existing.id,
                        "conflicting_range": (
                            f"{existing.start_time.strftime('%H:%M')}-"
                            f"{existing.end_time.strftime('%H:%M')}"
                        )
                    }
                }
            )

    if request.date is not None:
        entry.date = request.date

    if request.start_time is not None:
        entry.start_time = request.start_time

    if request.end_time is not None:
        entry.end_time = request.end_time

    if request.description is not None:
        entry.description = request.description

    if request.blockers is not None:
        entry.blockers = request.blockers

    db.commit()
    db.refresh(entry)

    updated_entry = (
        entries_query(db)
        .filter(Entry.id == entry.id)
        .first()
    )

    return format_entry(updated_entry)