import pytest
from datetime import date, time

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base
from app.models import Role, User, Entry


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine_test)

    db = TestingSessionLocal()

    # takie same role jak w insert_data()
    supervisor_role = Role(
        name="Supervisor"
    )

    student_role = Role(
        name="Student"
    )

    db.add_all([
        supervisor_role,
        student_role
    ])

    db.commit()

    db.refresh(supervisor_role)
    db.refresh(student_role)


    supervisor = User(
        name="Supervisor User",
        daily_hours_limit=8,
        role_id=supervisor_role.id
    )

    student = User(
        name="Student User",
        daily_hours_limit=6,
        role_id=student_role.id
    )

    db.add_all([
        supervisor,
        student
    ])

    db.commit()

    db.refresh(supervisor)
    db.refresh(student)


    entry1 = Entry(
        user_id=student.id,
        date=date(2026, 1, 10),
        start_time=time(8, 0),
        end_time=time(12, 0),
        description="Student task",
        blockers=None,
        status="approved"
    )

    entry2 = Entry(
        user_id=student.id,
        date=date(2026, 1, 11),
        start_time=time(9, 0),
        end_time=time(13, 0),
        description="Student task 2",
        blockers="blocked",
        status="draft"
    )


    db.add_all([
        entry1,
        entry2
    ])

    db.commit()

    db.close()

    yield

    Base.metadata.drop_all(bind=engine_test)



def test_stats_endpoint():
    response = client.get("api/stats?user_id=1")

    assert response.status_code == 200


def test_stats_returns_json():
    response = client.get("/api/stats?user_id=1")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)



def test_stats_counts_entries():
    response = client.get("/api/stats?user_id=1")

    data = response.json()

    assert len(data) == 1

def test_stats_status_code():
    response = client.get("/api/stats?user_id=1")

    assert response.status_code == 200



def test_stats_returns_list():
    response = client.get("/api/stats?user_id=1")

    data = response.json()

    assert isinstance(data, list)



def test_stats_not_empty_for_existing_student():
    response = client.get("/api/stats?user_id=1")

    data = response.json()

    assert len(data) > 0



def test_stats_contains_required_fields():
    response = client.get("/api/stats?user_id=1")

    data = response.json()

    stat = data[0]

    assert "student_id" in stat
    assert "student_name" in stat
    assert "week_start" in stat
    assert "week_end" in stat



def test_stats_returns_correct_student():
    response = client.get("/api/stats?user_id=1")

    data = response.json()

    assert data[0]["student_id"] == 1
    assert data[0]["student_name"] == "Test Student 1"



def test_stats_for_non_existing_user():
    response = client.get("/api/stats?user_id=99999")

    assert response.status_code == 404


def test_stats_week_dates_format():
    response = client.get("/api/stats?user_id=1")

    data = response.json()

    stat = data[0]

    assert len(stat["week_start"]) == 10
    assert len(stat["week_end"]) == 10

    assert stat["week_start"][4] == "-"
    assert stat["week_start"][7] == "-"

    assert stat["week_end"][4] == "-"
    assert stat["week_end"][7] == "-"



def test_stats_does_not_return_other_students():
    response = client.get("/api/stats?user_id=1")

    data = response.json()

    for stat in data:
        assert stat["student_id"] == 1