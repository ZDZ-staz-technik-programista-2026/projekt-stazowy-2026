import os
from pathlib import Path

TEST_DB_PATH = Path(__file__).parent / "test_database.db"

# pytest uses a separate database file to avoid affecting application data.
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"


import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import Entry


@pytest.fixture
def client():
    """
    Provides a FastAPI test client for API endpoint tests.

    The client lifecycle is managed by pytest and the application
    is properly started and closed after the test finishes.

    Yields:
        TestClient:
            Client used to send HTTP requests to the application.
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def clean_entries():
    """
    Cleans database entries after each test execution.

    This fixture runs automatically for every test to ensure that
    test cases do not affect each other through previously created
    time entries.
    """
    yield

    db = SessionLocal()

    try:
        db.query(Entry).delete()
        db.commit()

    finally:
        db.close()