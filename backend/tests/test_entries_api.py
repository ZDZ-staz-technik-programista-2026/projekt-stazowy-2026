import random
import time as time_module
from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# NOTE: these tests run against the same database used for manual Swagger
# testing - there is no dedicated, isolated test database/fixture yet.
# To avoid colliding with entries left behind by earlier test runs, each
# test uses a date far in the past, randomized per run.
_rng = random.Random(int(time_module.time()))


def _unique_past_date() -> date:
    offset_days = _rng.randint(2000, 50000)
    return date.today() - timedelta(days=offset_days)


def _get_student():
    response = client.get("/api/users")
    assert response.status_code == 200
    students = [u for u in response.json() if u["role"] == "Student"]
    assert students, "No Student user found in seed data"
    return students[0]


def test_patch_entry_above_daily_limit_is_rejected():
    student = _get_student()
    daily_limit = int(student["daily_hours_limit"])
    entry_date = _unique_past_date()

    create_response = client.post(
        "/api/entries",
        json={
            "user_id": student["id"],
            "date": str(entry_date),
            "start_time": "08:00:00",
            "end_time": "09:00:00",
            "description": "Baseline entry for daily limit PATCH test.",
            "blockers": "None",
        },
    )
    assert create_response.status_code == 201
    entry_id = create_response.json()["id"]

    # The entry being edited is excluded from "already logged" hours, so
    # requesting more than daily_limit hours in this single block is
    # enough to trigger the rejection.
    patch_response = client.patch(
        f"/api/entries/{entry_id}",
        json={"start_time": "00:00:00", "end_time": f"{daily_limit + 1:02d}:00:00"},
    )

    assert patch_response.status_code == 400
    body = patch_response.json()
    assert body["code"] == "HOURLY_LIMIT_EXCEEDED"
    assert body["details"]["type"] == "daily_limit_breach"


def test_patch_entry_above_weekly_limit_is_rejected():
    student = _get_student()
    daily_limit = int(student["daily_hours_limit"])

    monday = _unique_past_date()
    monday -= timedelta(days=monday.weekday())  # snap to Monday

    per_day_hours = min(daily_limit - 1, 7)
    for i in range(5):
        day = monday + timedelta(days=i)
        response = client.post(
            "/api/entries",
            json={
                "user_id": student["id"],
                "date": str(day),
                "start_time": "00:00:00",
                "end_time": f"{per_day_hours:02d}:00:00",
                "description": "Weekday baseline entry for weekly limit test.",
                "blockers": "None",
            },
        )
        assert response.status_code == 201

    weekday_total = per_day_hours * 5

    saturday = monday + timedelta(days=5)
    create_response = client.post(
        "/api/entries",
        json={
            "user_id": student["id"],
            "date": str(saturday),
            "start_time": "00:00:00",
            "end_time": "01:00:00",
            "description": "Saturday entry to be extended via PATCH.",
            "blockers": "None",
        },
    )
    assert create_response.status_code == 201
    entry_id = create_response.json()["id"]

    # Cross 40h total while staying within the daily limit for that day.
    requested_hours = min(41 - weekday_total, daily_limit)
    assert requested_hours > 0

    patch_response = client.patch(
        f"/api/entries/{entry_id}",
        json={"start_time": "00:00:00", "end_time": f"{requested_hours:02d}:00:00"},
    )

    assert patch_response.status_code == 400
    body = patch_response.json()
    assert body["code"] == "HOURLY_LIMIT_EXCEEDED"
    assert body["details"]["type"] == "weekly_limit_breach"


def test_patch_entry_with_timezone_aware_time_is_rejected():
    student = _get_student()
    entry_date = _unique_past_date()

    create_response = client.post(
        "/api/entries",
        json={
            "user_id": student["id"],
            "date": str(entry_date),
            "start_time": "09:00:00",
            "end_time": "12:00:00",
            "description": "Entry used to test timezone-aware time rejection.",
            "blockers": "None",
        },
    )
    assert create_response.status_code == 201
    entry_id = create_response.json()["id"]

    patch_response = client.patch(
        f"/api/entries/{entry_id}",
        json={"start_time": "09:00:00Z"},
    )

    assert patch_response.status_code == 400
    body = patch_response.json()
    assert body["code"] == "INVALID_FIELD_FORMAT"
    assert "start_time" in body["details"]["errors"]