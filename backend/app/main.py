from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.database import Base, engine
from app.models import *

from app.insert_data import insert_data
from app.routes.basicAPI import router as basic_api_router
from app.routes.entries import router as entries_router


Base.metadata.create_all(bind=engine)
insert_data()


app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    
    invalid_fields = []
    for err in errors:
        field_name = err["loc"][-1] if err["loc"] else "unknown"
        invalid_fields.append(str(field_name))

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,  
        content={
            "status": 400,
            "error": "BAD_REQUEST",
            "message": "Validation failed: One or more required fields are missing or invalid.",
            "code": "MISSING_REQUIRED_FIELDS",
            "details": {
                "invalid_fields": invalid_fields,
                "errors": [
                    {
                        "field": err["loc"][-1] if err["loc"] else "unknown",
                        "msg": err["msg"],
                        "type": err["type"]
                    }
                    for err in errors
                ]
            }
        }
    )

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