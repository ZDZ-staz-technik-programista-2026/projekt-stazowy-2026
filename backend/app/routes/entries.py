import datetime
from typing import Optional

from pydantic import BaseModel, field_validator
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

from app.services import validate_transition, check_overlap


router = APIRouter(prefix="/api", tags=["Entries"])


# ---------------------------------------------------------------------------
# Request Pydantic Schemas
# ---------------------------------------------------------------------------


class EntryCreateRequest(BaseModel):
    """Payload schema for creating a new time tracking entry."""

    user_id: int
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    description: str
    blockers: Optional[str] = "None"

    @field_validator("start_time", "end_time")
    @classmethod
    def reject_timezone(cls, value: datetime.time) -> datetime.time:
        """Reject time values containing timezone offsets to enforce naive UTC/local time consistency."""
        if value.tzinfo is not None:
            raise ValueError("Time value must not include timezone information.")
        return value


class EntryPatchRequest(BaseModel):
    """Payload schema for partially updating an existing time entry."""

    date: Optional[datetime.date] = None
    start_time: Optional[datetime.time] = None
    end_time: Optional[datetime.time] = None
    description: Optional[str] = None
    blockers: Optional[str] = None

    @field_validator("start_time", "end_time")
    @classmethod
    def reject_timezone(cls, value: Optional[datetime.time]) -> Optional[datetime.time]:
        """Reject time values containing timezone offsets to enforce naive time consistency."""
        if value is not None and value.tzinfo is not None:
            raise ValueError("Time value must not include timezone information.")
        return value


class SubmitEntryRequest(BaseModel):
    """Payload schema for submitting a time entry for supervisor review."""

    user_id: int


class ApproveEntryRequest(BaseModel):
    """Payload schema for approving a time entry."""

    created_by: int


class ReturnEntryRequest(BaseModel):
    """Payload schema for returning a time entry back for revision."""

    created_by: int
    comment: str


# ---------------------------------------------------------------------------
# Database & Utility Functions
# ---------------------------------------------------------------------------


def get_db():
    """Database session generator dependency for FastAPI requests.

    Yields:
        Session: Active SQLAlchemy database session context.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def entries_query(db: Session):
    """Build a base ORM query for Entry pre-configured with eager loaded relationships.

    Eagerly loads user, user role, reviews, and reviewer user role to avoid N+1 query performance degradation.

    Args:
        db (Session): Active database session.

    Returns:
        Query: Base SQLAlchemy query targeting the Entry model.
    """
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


def format_review(review: Optional[Review]) -> Optional[dict]:
    """Format a Review ORM instance into a structured dictionary payload.

    Args:
        review (Optional[Review]): The review database model instance.

    Returns:
        Optional[dict]: Dictionary representation of the review or None if input is None.
    """
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


def calculate_entry_hours(entry: Entry) -> float:
    """Calculate the total duration in decimal hours for a given time entry.

    Args:
        entry (Entry): The time entry database model.

    Returns:
        float: Duration of work in decimal hours.

    Raises:
        InvalidTimeRangeError: If start_time or end_time is missing/None.
    """
    if entry.start_time is None or entry.end_time is None:
        raise InvalidTimeRangeError()
        
    return calculate_hours(
        entry.start_time,
        entry.end_time
    )


def get_latest_review(entry: Entry) -> Optional[Review]:
    """Find the most recent review record attached to a time entry.

    Args:
        entry (Entry): The time entry containing reviews.

    Returns:
        Optional[Review]: The latest review based on created_at timestamp, or None if no reviews exist.
    """
    if not entry.reviews:
        return None

    # Determine latest review using timestamp comparison
    return max(
        entry.reviews,
        key=lambda review: review.created_at
    )


def format_entry(entry: Entry) -> dict:
    """Transform an Entry ORM model into a standardized JSON response dictionary.

    Args:
        entry (Entry): The target entry model.

    Returns:
        dict: Complete serialized dictionary representation of the entry.
    """
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


# ---------------------------------------------------------------------------
# API Route Handlers
# ---------------------------------------------------------------------------


@router.get(
    "/entries",
    summary="List time entries",
    description="Retrieve time entries visible to the requesting user based on their role (Student sees own, Supervisor sees all).",
)
def get_entries(
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Retrieve time entries filtered by user permission role.

    Args:
        user_id (int): Requesting user's ID for role authentication and scope filtering.
        db (Session): Database session dependency.

    Returns:
        list[dict] | JSONResponse: Formatted entries list, or structured JSON error on failure.
    """
    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        return JSONResponse(
            status_code=404,
            content={
                "status": 404,
                "error": "NOT_FOUND",
                "message": "User not found.",
                "code": "USER_NOT_FOUND",
                "details": {
                    "user_id": user_id
                }
            }
        )

    query = entries_query(db)

    # Role-based visibility scope enforcement:
    # Students can only see their own time entries; Supervisors can access all entries.
    if user.role.name == "Student":
        query = query.filter(Entry.user_id == user.id)

    elif user.role.name == "Supervisor":
        pass 

    else:
        return JSONResponse(
            status_code=403,
            content={
                "status": 403,
                "error": "FORBIDDEN",
                "message": "You do not have permission to access this resource.",
                "code": "INSUFFICIENT_PERMISSIONS",
                "details": {
                    "user_id": user.id,
                    "role": user.role.name
                }
            }
        )

    entries = query.all()

    try:
        return [
            format_entry(entry)
            for entry in entries
        ]

    except InvalidTimeRangeError:
        # Fallback inspection to construct detailed validation error if any DB record holds corrupt time ranges
        start_val = "..."
        end_val = "..."

        for el in entries:
            if (
                el.start_time is None
                or el.end_time is None
                or el.end_time <= el.start_time
            ):
                start_val = (
                    str(el.start_time)
                    if el.start_time is not None
                    else "..."
                )
                end_val = (
                    str(el.end_time)
                    if el.end_time is not None
                    else "..."
                )
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


@router.get(
    "/entries/{id}",
    summary="Get single entry by ID",
    description="Fetch details of a specific time entry by ID subject to user role permission checks.",
)
def get_entry(
    id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Retrieve details for a single time entry by ID.

    Args:
        id (int): Unique identifier of the requested entry.
        user_id (int): Requesting user's ID for access control.
        db (Session): Database session dependency.

    Returns:
        dict | JSONResponse: Serialized entry details or standard error response envelope.
    """
    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        return JSONResponse(
            status_code=404,
            content={
                "status": 404,
                "error": "NOT_FOUND",
                "message": "User not found.",
                "code": "USER_NOT_FOUND",
                "details": {
                    "user_id": user_id
                }
            }
        )

    query = (
        entries_query(db)
        .filter(Entry.id == id)
    )

    # Restrict lookup scope to student's own records if caller is a Student
    if user.role.name == "Student":
        query = query.filter(
            Entry.user_id == user.id
        )

    elif user.role.name == "Supervisor":
        pass  

    else:
        return JSONResponse(
            status_code=403,
            content={
                "status": 403,
                "error": "FORBIDDEN",
                "message": "You do not have permission to access this resource.",
                "code": "INSUFFICIENT_PERMISSIONS",
                "details": {
                    "user_id": user.id,
                    "role": user.role.name
                }
            }
        )

    entry = query.first()

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
                    "start_time": (
                        str(entry.start_time)
                        if entry.start_time is not None
                        else "..."
                    ),
                    "end_time": (
                        str(entry.end_time)
                        if entry.end_time is not None
                        else "..."
                    )
                }
            }
        )


@router.post(
    "/entries",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new time entry",
    description="Validate and persist a new draft time tracking entry after verifying schedule limits and overlap rules.",
)
def create_entry(
    request: EntryCreateRequest,
    db: Session = Depends(get_db)
):
    """Create and persist a new time entry.

    Executes validations:
      1. Time range validity (start_time < end_time)
      2. Future date prohibition
      3. Non-empty description checks
      4. Schedule overlap prevention
      5. Daily total hours cap compliance

    Args:
        request (EntryCreateRequest): Entry creation payload.
        db (Session): Database session dependency.

    Returns:
        dict | JSONResponse: Formatted created entry or validation error response envelope.
    """
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

    check_schedule_overlap(db=db, user_id=request.user_id, entry_date=request.date, start_time=request.start_time, end_time=request.end_time)

    user_not_found_error = check_hours_limit(
        db=db, user_id=request.user_id, entry_date=request.date, requested_hours=calculated_hours
    )
    if isinstance(user_not_found_error, JSONResponse):
        return user_not_found_error

    # Initialize new entry in 'draft' status by default
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

    # Re-query entry with joined relationships for response formatting
    full_entry = (
        entries_query(db)
        .filter(Entry.id == entry.id)
        .first()
    )

    return format_entry(full_entry)


@router.patch(
    "/entries/{id}",
    summary="Update an existing time entry",
    description="Partially update fields of a draft or editable time entry with dynamic overlap and daily hour limit re-validation.",
)
def patch_entry(
    id: int,
    request: EntryPatchRequest,
    db: Session = Depends(get_db),
):
    """Partially update an existing time entry.

    Args:
        id (int): Target entry ID to update.
        request (EntryPatchRequest): Partial update fields payload.
        db (Session): Database session dependency.

    Returns:
        dict | JSONResponse: Updated formatted entry payload or validation error response.
    """
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

    # Validate that current entry status permits modification (e.g., drafts or revisions)
    status_error = validate_entry_status_for_patch(entry.status)

    if isinstance(status_error, JSONResponse):
        return status_error
    
    # Merge existing entry values with requested partial updates for full validation
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

    # Exclude the entry being edited (Entry.id != entry.id) - otherwise editing
    # an entry's own time range would always "overlap" with its own prior
    # stored version before the PATCH is committed.
    for existing in existing_entries:
        check_overlap(new_start, new_end, existing.start_time, existing.end_time, existing.id)

    # Re-check daily hours limit ignoring the entry's previous duration
    user_not_found_error = check_hours_limit(
        db=db,
        user_id=entry.user_id,
        entry_date=new_date,
        requested_hours=hours_or_error,
        exclude_entry_id=entry.id,
    )
    if isinstance(user_not_found_error, JSONResponse):
        return user_not_found_error

    # Apply valid requested updates to model properties
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


@router.post("/entries/{id}/submit")
def submit_entry(
    id: int,
    request: SubmitEntryRequest,
    db: Session = Depends(get_db),
):
    """
    Submit a draft or needs-revision entry for supervisor approval.

    Only the student who owns the entry may submit it. Allowed status
    transitions are enforced by the shared state machine
    (app.services.validate_transition); any other transition, or the
    wrong role, returns 409 WORKFLOW_STATE_LOCKED.
    """
    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == request.user_id)
        .first()
    )

    if user is None:
        return JSONResponse(
            status_code=404,
            content={
                "status": 404,
                "error": "NOT_FOUND",
                "message": f"Target user resource record with ID '{request.user_id}' was not found.",
                "code": "USER_NOT_FOUND",
                "details": {"user_id": request.user_id},
            },
        )
    
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
                "message": f"Target time entry resource record with ID '{id}' was not found.",
                "code": "ENTRY_NOT_FOUND",
                "details": {"entry_id": id},
            },
        )
    
    if entry.user_id != user.id:
        return JSONResponse(
            status_code=403,
            content={
                "status": 403,
                "error": "FORBIDDEN",
                "message": "You do not have permission to modify this entry.",
                "code": "INSUFFICIENT_PERMISSIONS",
                "details": {"user_id": user.id, "entry_id": entry.id},
            },
    )
    
    validate_transition(entry.status, "submitted", user.role.name) # Calling this function might generate exception (InvalidStatusTransitionError) that is managed by exception handler in main.py
    
    entry.status = "submitted"
    db.commit()
    db.refresh(entry)

    updated_entry = (
        entries_query(db)
        .filter(Entry.id == entry.id)
        .first()
    )

    return format_entry(updated_entry)


@router.post("/entries/{id}/approve")
def approve_entry(
        id: int,
        request: ApproveEntryRequest,
        db: Session = Depends(get_db),
    ):
    """
    Approve a submitted entry, permanently locking it from further edits.

    Persists a Review row with decision="approved". Only a supervisor
    may perform this transition (enforced by validate_transition).
    """

    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == request.created_by)
        .first()
    )

    if user is None:
        return JSONResponse(
            status_code=404,
            content={
                "status": 404,
                "error": "NOT_FOUND",
                "message": f"Target user resource record with ID '{request.created_by}' was not found.",
                "code": "USER_NOT_FOUND",
                "details": {"user_id": request.created_by},
            }
        )

    entry = (
        db.query(Entry)
        .filter(Entry.id == id)
        .first()
    )

    if entry is None:
        return JSONResponse(
            status_code=404,
            content={
                "status": 404,
                "error": "NOT_FOUND",
                "message": f"Target time entry resource record with ID '{id}' was not found.",
                "code": "ENTRY_NOT_FOUND",
                "details": {"entry_id": id}
            }
        )

    validate_transition(entry.status, "approved", user.role.name) # Calling this function might generate exception (InvalidStatusTransitionError) that is managed by exception handler in main.py

    entry.status = "approved"

    review = Review(
            entry_id = entry.id,
            decision = entry.status,
            created_by = request.created_by,
        )
    
    db.add(review)

    db.commit()
    db.refresh(entry)
    db.refresh(review)
    
    updated_entry = (
            entries_query(db)
            .filter(Entry.id == entry.id)
            .first()
        )

    return format_entry(updated_entry)


@router.post("/entries/{id}/return")
def return_entry(
        id: int,
        request: ReturnEntryRequest,
        db: Session = Depends(get_db),
    ):
    """
    Return a submitted entry to the student for revision.

    A non-empty comment is mandatory (400 MISSING_REJECTION_COMMENT
    otherwise) - the comment is what tells the student what to fix.
    Persists a Review row with decision="needs_revision".
    """

    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == request.created_by)
        .first()
    )

    if user is None:
        return JSONResponse(
            status_code=404,
            content={
                "status": 404,
                "error": "NOT_FOUND",
                "message": f"Target user resource record with ID '{request.created_by}' was not found.",
                "code": "USER_NOT_FOUND",
                "details": {"user_id": request.created_by},
            }
        )

    entry = (
        db.query(Entry)
        .filter(Entry.id == id)
        .first()
    )

    if entry is None:
        return JSONResponse(
            status_code=404,
            content={
                "status": 404,
                "error": "NOT_FOUND",
                "message": f"Target time entry resource record with ID '{id}' was not found.",
                "code": "ENTRY_NOT_FOUND",
                "details": {"entry_id": id}
            }
        )

    if not request.comment or not request.comment.strip():
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "error": "BAD_REQUEST",
                "message": "A feedback description comment is mandatory when requesting changes or rejecting entries.",
                "code": "MISSING_REJECTION_COMMENT",
                "details": { "status_id": 3 }
            }
        )
    
    validate_transition(entry.status, "needs_revision", user.role.name) # Calling this function might generate exception (InvalidStatusTransitionError) that is managed by exception handler in main.py

    entry.status = "needs_revision"

    review = Review(
            entry_id = entry.id,
            comment = request.comment,
            decision = entry.status,
            created_by = request.created_by,
        )

    db.add(review)

    db.commit()
    db.refresh(entry)
    db.refresh(review)

    updated_entry = (
            entries_query(db)
            .filter(Entry.id == entry.id)
            .first()
        )

    return format_entry(updated_entry)