import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from urllib.parse import urlparse

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'app.db'}"
)

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }

elif DATABASE_URL.startswith("mysql"):
    ssl_ca = os.getenv("MYSQL_SSL_CA")
    if not ssl_ca:
        raise RuntimeError(
            "MYSQL_SSL_CA environment variable is required for MySQL SSL connection"
        )

    ca_path = Path(ssl_ca)
    if not ca_path.is_absolute():
        ca_path = BASE_DIR / ca_path

    connect_args = {
        "ssl": {
            "ca": str(ca_path),
            "check_hostname": True
        }
    }

else:
    connect_args = {}

parsed = urlparse(DATABASE_URL)

print(
    f"Database engine: {parsed.scheme}, "
    f"host: {parsed.hostname}, "
    f"database: {parsed.path.replace('/', '')}"
)

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class Base(DeclarativeBase):
    pass