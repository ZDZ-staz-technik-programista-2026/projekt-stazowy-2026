from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models import *

from app.insert_data import insert_data
from app.routes import *


Base.metadata.create_all(bind=engine)
insert_data()


app = FastAPI()
app.include_router(router)

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