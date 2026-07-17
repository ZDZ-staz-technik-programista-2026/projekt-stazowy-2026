from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models import *

from app.insert_data import insert_data
from app.routes.basicAPI import router as basic_api_router
from app.routes.entries import router as entries_router


Base.metadata.create_all(bind=engine)
insert_data()


app = FastAPI()

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