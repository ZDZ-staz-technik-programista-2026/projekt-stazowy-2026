import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# Load environment variables from a .env file into os.environ
load_dotenv()

# Define project base directory paths for relative resolution
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent

# Retrieve target Database URL from environment or fallback to a local SQLite database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{APP_DIR / 'app.db'}"
)

# ---------------------------------------------------------------------------
# Database Connection Arguments Configuration
# ---------------------------------------------------------------------------
# Customize connection parameters dynamically based on the underlying driver/dialect

if DATABASE_URL.startswith("sqlite"):
    # SQLite default connection check requires multithreading support for FastAPI async context
    connect_args = {
        "check_same_thread": False
    }

elif DATABASE_URL.startswith("mysql"):
    # Secure MySQL connection setup requiring a valid CA certificate path
    ssl_ca = os.getenv("MYSQL_SSL_CA")
    if not ssl_ca:
        raise RuntimeError(
            "MYSQL_SSL_CA environment variable is required for MySQL SSL connection"
        )

    # Resolve relative SSL CA certificate paths against backend root directory
    ca_path = Path(ssl_ca)
    if not ca_path.is_absolute():
        ca_path = BACKEND_DIR / ca_path

    connect_args = {
        "ssl": {
            "ca": str(ca_path),
            "check_hostname": True
        }
    }

else:
    # Default empty arguments for standard connectors (e.g., PostgreSQL)
    connect_args = {}


# Log active database scheme dialect to standard output on startup
engine_info = urlparse(DATABASE_URL)
print(f"Database engine: {engine_info.scheme}")

# ---------------------------------------------------------------------------
# SQLAlchemy Engine & Session Configuration
# ---------------------------------------------------------------------------

# Primary database connection engine instance
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

# Configured session factory for creating transactional database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy ORM models.
    """
    pass