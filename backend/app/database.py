import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


load_dotenv()

APP_DIR = Path(__file__).resolve().parent

BACKEND_DIR = APP_DIR.parent


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{APP_DIR / 'app.db'}"
)


if DATABASE_URL.startswith("sqlite"):
    # SQLite requires this option when used with FastAPI because
    # database connections can be accessed from different threads.
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

    # Allow using relative certificate paths from the backend directory.
    if not ca_path.is_absolute():
        ca_path = BACKEND_DIR / ca_path

    connect_args = {
        "ssl": {
            "ca": str(ca_path),
            "check_hostname": True,
        }
    }

else:
    connect_args = {}


engine_info = urlparse(DATABASE_URL)

print(
    f"Database engine: {engine_info.scheme}"
)


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    All database models should inherit from this class so that
    SQLAlchemy can register and manage their table metadata.
    """

    pass