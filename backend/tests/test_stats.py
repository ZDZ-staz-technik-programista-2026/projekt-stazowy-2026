import random
from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

_rng = random.Random()


def _unique_past_date() -> date:
    offset_days = _rng.randint(100, 1500)
    return date.today() - timedelta(days=offset_days)


def _unique_past_week_monday() -> date:
    d = _unique_past_date()
    return d - timedelta(days=d.weekday())


def _get_student():
    response = client.get("/api/users")
    assert response.status_code == 200
    students = [u for u in response.json() if u["role"] == "Student"]
    assert students, "No Student user found in seed data"
    return students[0]


def _get_supervisor():
    response = client.get("/api/users")
    assert response.status_code == 200
    supervisors = [u for u in response.json() if u["role"] == "Supervisor"]
    assert supervisors, "No Supervisor user found in seed data"
    return supervisors[0]


def _create_entry(user_id, entry_date, start_time, end_time, description="Stats test entry"):
    response = client.post(
        "/api/entries",
        json={
            "user_id": user_id,
            "date": str(entry_date),
            "start_time": start_time,
            "end_time": end_time,
            "description": description,
            "blockers": "None",
        },
    )
    assert response.status_code == 201
    return response.json()


def _stats_for(user_id, week_start):
    return client.get(
        "/api/stats",
        params={"user_id": user_id, "week_start_date": str(week_start)},
    )


def _row_for(data, student_id):
    if not isinstance(data, list):
        return None
    return next((row for row in data if row["student_id"] == student_id), None)


def test_stats_endpoint_runs_for_existing_student():
    student = _get_student()
    monday = _unique_past_week_monday()

    response = _stats_for(student["id"], monday)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_stats_reflects_created_entries_for_the_selected_week():
    student = _get_student()
    monday = _unique_past_week_monday()

    _create_entry(student["id"], monday, "08:00:00", "12:00:00")
    _create_entry(student["id"], monday + timedelta(days=1), "09:00:00", "11:00:00")

    response = _stats_for(student["id"], monday)
    row = _row_for(response.json(), student["id"])

    assert row is not None
    assert row["entry_count"] == 2
    assert row["total_hours"] == 6.0
    assert row["week_start"] == str(monday)
    assert row["week_end"] == str(monday + timedelta(days=7))


def test_stats_excludes_entries_from_other_weeks():
    student = _get_student()
    monday = _unique_past_week_monday()
    other_week_monday = monday - timedelta(days=7)

    _create_entry(student["id"], monday, "08:00:00", "10:00:00")
    _create_entry(student["id"], other_week_monday, "08:00:00", "16:00:00")

    response = _stats_for(student["id"], monday)
    row = _row_for(response.json(), student["id"])

    assert row["entry_count"] == 1
    assert row["total_hours"] == 2.0


def test_stats_returns_zero_for_week_with_no_entries():
    student = _get_student()
    empty_week_monday = _unique_past_week_monday()

    response = _stats_for(student["id"], empty_week_monday)
    row = _row_for(response.json(), student["id"])

    assert row is not None
    assert row["entry_count"] == 0
    assert row["total_hours"] == 0
    assert row["approved_percentage"] == 0


def test_approved_percentage_is_zero_without_any_review():
    student = _get_student()
    monday = _unique_past_week_monday()

    _create_entry(student["id"], monday, "08:00:00", "12:00:00")

    row = _row_for(_stats_for(student["id"], monday).json(), student["id"])

    assert row["entry_count"] == 1
    assert row["approved_percentage"] == 0


def test_week_start_normalizes_any_weekday_to_that_weeks_monday():
    student = _get_student()
    monday = _unique_past_week_monday()
    wednesday = monday + timedelta(days=2)

    _create_entry(student["id"], monday, "14:00:00", "16:00:00")

    res_monday = _stats_for(student["id"], monday)
    res_wednesday = _stats_for(student["id"], wednesday)

    assert res_monday.status_code == 200
    assert res_wednesday.status_code == 400
    assert res_wednesday.json()["code"] == "INVALID_WEEK_START"


def test_supervisor_scope_includes_a_students_entries_for_the_week():
    supervisor = _get_supervisor()
    student = _get_student()
    monday = _unique_past_week_monday()

    _create_entry(student["id"], monday, "08:00:00", "13:00:00")

    response = _stats_for(supervisor["id"], monday)
    row = _row_for(response.json(), student["id"])

    assert response.status_code == 200
    assert row is not None
    assert row["entry_count"] == 1
    assert row["total_hours"] == 5.0


def test_stats_for_non_existing_user_returns_404_with_standard_error_envelope():
    non_existing_user_id = 999_000_000 + _rng.randint(0, 999_999)

    response = client.get(
        "/api/stats",
        params={
            "user_id": non_existing_user_id,
            "week_start_date": str(_unique_past_week_monday()),
        },
    )

    assert response.status_code == 404
    body = response.json()
    assert body["status"] == 404
    assert body["error"] == "NOT_FOUND"
    assert body["code"] == "USER_NOT_FOUND"