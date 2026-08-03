from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.services import InvalidStatusTransitionError, ScheduleOverlapError, DailyLimitExceededError, WeeklyLimitExceededError
from fastapi.responses import JSONResponse
from app.database import Base, engine
from app.models import *

from app.insert_data import insert_data
from app.routes.basicAPI import router as basic_api_router
from app.routes.entries import router as entries_router
from app.routes.stats import router as stats_router
from app.routes.csv import router as csv_router


Base.metadata.create_all(bind=engine)
insert_data()


app = FastAPI()

@app.exception_handler(InvalidStatusTransitionError)
def handle_invalid_status_transition(request: Request, exc: InvalidStatusTransitionError):
    return JSONResponse(
        status_code=409,
        content={
            "status": 409,
            "error": "CONFLICT",
            "message": str(exc),
            "code": "WORKFLOW_STATE_LOCKED",
            "details": {"current_status": exc.current_status} if exc.current_status else {},
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Central handler for all Pydantic validation errors.

    Distinguishes two cases that the frontend needs to treat differently:
    - a required field is entirely missing -> MISSING_REQUIRED_FIELDS
    - a field was provided but has an invalid format (e.g. malformed
      time, timezone-aware time) -> INVALID_FIELD_FORMAT

    Both cases return details.errors as a dict keyed by field name
    (not a list), since that is the shape the frontend forms expect.
    """
    errors = exc.errors()

    missing_errors = {}
    format_errors = {}

    for err in errors:
        field_name = str(err["loc"][-1]) if err["loc"] else "unknown"
        error_type = err["type"]

        if error_type == "missing":
            missing_errors[field_name] = "This field is required."
        else:
            format_errors[field_name] = _readable_message(field_name, error_type)

    if format_errors:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": 400,
                "error": "BAD_REQUEST",
                "message": "One or more fields have an invalid format.",
                "code": "INVALID_FIELD_FORMAT",
                "details": {"errors": format_errors},
            },
        )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": 400,
            "error": "BAD_REQUEST",
            "message": "Validation failed: One or more required fields are missing.",
            "code": "MISSING_REQUIRED_FIELDS",
            "details": {"errors": missing_errors},
        },
    )


@app.exception_handler(ScheduleOverlapError)
def handle_schedule_overlap(request: Request, exc: ScheduleOverlapError):
    return JSONResponse(
        status_code=409,
        content={
            "status": 409,
            "error": "CONFLICT",
            "message": str(exc),
            "code": "SCHEDULE_OVERLAP",
            "details": {
                "conflicting_entry_id": exc.conflicting_entry_id,
                "conflicting_range": exc.conflicting_range,
            },
        },
    )

@app.exception_handler(DailyLimitExceededError)
def handle_daily_limit_exceeded(request: Request, exc: DailyLimitExceededError):
    return JSONResponse(
        status_code=400,
        content={
            "status": 400,
            "error": "BAD_REQUEST",
            "message": "The requested log block exceeds your daily hourly cap configuration limit (8h) or breaches the global 40-hour running weekly quota boundary.",
            "code": "HOURLY_LIMIT_EXCEEDED",
            "details": {
                "type": "daily_limit_breach",
                "daily_limit": exc.daily_limit,
                "current_daily_accumulated_hours": exc.current_daily_hours,
                "requested_hours": exc.requested_hours,
            },
        },
    )


@app.exception_handler(WeeklyLimitExceededError)
def handle_weekly_limit_exceeded(request: Request, exc: WeeklyLimitExceededError):
    return JSONResponse(
        status_code=400,
        content={
            "status": 400,
            "error": "BAD_REQUEST",
            "message": "The requested log block exceeds your daily hourly cap configuration limit (8h) or breaches the global 40-hour running weekly quota boundary.",
            "code": "HOURLY_LIMIT_EXCEEDED",
            "details": {
                "type": "weekly_limit_breach",
                "weekly_limit": exc.weekly_limit,
                "current_weekly_accumulated_hours": exc.current_weekly_hours,
                "requested_hours": exc.requested_hours,
            },
        },
    )
def _readable_message(field_name: str, error_type: str) -> str:
    """Map a Pydantic error `type` to a short, frontend-displayable message."""
    if "time" in error_type:
        return "Enter a valid time in HH:MM format."
    if "date" in error_type:
        return "Enter a valid date in YYYY-MM-DD format."
    if "int" in error_type:
        return f"'{field_name}' must be a whole number."
    return f"'{field_name}' has an invalid value."

app.include_router(basic_api_router)
app.include_router(entries_router)
app.include_router(stats_router)
app.include_router(csv_router)
origins = [
    "http://localhost:5173", # default Vite URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = False,  # No cookies | Can change later when doing authentication
    allow_methods = ["*"],
    allow_headers = ["*"],
)


@app.get("/health")
def health_check():
    """
    Checks whether the backend application is running.

    Returns:
        HTTP 200 response with application status.
    """
    return {
        "status": "ok",
    }