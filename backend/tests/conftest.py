import os
from pathlib import Path

TEST_DB_PATH = Path(__file__).parent / "test_database.db"

# pytest use test database from tests
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"


import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import Entry


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def clean_entries():
    yield

    db = SessionLocal()

    try:
        db.query(Entry).delete()
        db.commit()

    finally:
        db.close()