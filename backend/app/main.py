from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173", # defualt vite url
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = False,  # No cookies | Can change later when doing authentication
    allow_methods = ["*"],    # * - GET, POST, DELETE etc.
    allow_headers = ["Content-Type"],
)


@app.get("/health")
def health_check():
    return {
        "status" : "ok",
    }