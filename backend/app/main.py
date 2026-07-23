from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.services import InvalidStatusTransitionError
from fastapi.responses import JSONResponse
from app.database import Base, engine
from app.models import *

from app.insert_data import insert_data
from app.routes.basicAPI import router as basic_api_router
from app.routes.entries import router as entries_router


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

def _readable_message(field_name: str, error_type: str) -> str:
    if "time" in error_type:
        return "Enter a valid time in HH:MM format."
    if "date" in error_type:
        return "Enter a valid date in YYYY-MM-DD format."
    if "int" in error_type:
        return f"'{field_name}' must be a whole number."
    return f"'{field_name}' has an invalid value."

app.include_router(basic_api_router)
app.include_router(entries_router)

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
    return {
        "status" : "ok",
    }