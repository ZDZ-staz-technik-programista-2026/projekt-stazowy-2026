import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'app.db'}"
)

print("ENV DATABASE:", DATABASE_URL)


if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }

elif DATABASE_URL.startswith("mysql"):
    connect_args = {
        "ssl": {
            "ssl": True
        }
    }

else:
    connect_args = {}


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


class Base(DeclarativeBase):
    pass