from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _unique_past_week_monday() -> date:
    return date(2026, 1, 5)


def _get_student():
    response = client.get("/api/users")

    assert response.status_code == 200

    students = [
        u for u in response.json()
        if u["role"] == "Student"
    ]

    assert students, "No Student user found"

    return students[0]


def _get_supervisor():
    response = client.get("/api/users")

    assert response.status_code == 200

    supervisors = [
        u for u in response.json()
        if u["role"] == "Supervisor"
    ]

    assert supervisors, "No Supervisor user found"

    return supervisors[0]


def _create_entry(
    user_id,
    entry_date,
    start_time,
    end_time,
    description="Stats test entry",
):
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
        params={
            "user_id": user_id,
            "week_start_date": str(week_start),
        },
    )


def _row_for(data, student_id):
    if not isinstance(data, list):
        return None

    return next(
        (
            row
            for row in data
            if row["student_id"] == student_id
        ),
        None,
    )


def test_stats_endpoint_runs_for_existing_student():

    student = _get_student()

    response = _stats_for(
        student["id"],
        _unique_past_week_monday(),
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_stats_reflects_created_entries_for_selected_week():

    student = _get_student()
    monday = _unique_past_week_monday()

    _create_entry(
        student["id"],
        monday,
        "08:00:00",
        "12:00:00",
    )

    _create_entry(
        student["id"],
        monday + timedelta(days=1),
        "09:00:00",
        "11:00:00",
    )

    response = _stats_for(
        student["id"],
        monday,
    )

    row = _row_for(
        response.json(),
        student["id"],
    )

    assert row is not None
    assert row["entry_count"] == 2
    assert row["total_hours"] == 6.0


def test_stats_excludes_entries_from_other_weeks():

    student = _get_student()
    monday = _unique_past_week_monday()

    _create_entry(
        student["id"],
        monday,
        "08:00:00",
        "10:00:00",
    )

    _create_entry(
        student["id"],
        monday - timedelta(days=7),
        "08:00:00",
        "16:00:00",
    )

    row = _row_for(
        _stats_for(
            student["id"],
            monday,
        ).json(),
        student["id"],
    )

    assert row["entry_count"] == 1
    assert row["total_hours"] == 2.0


def test_stats_returns_zero_for_week_with_no_entries():

    student = _get_student()

    row = _row_for(
        _stats_for(
            student["id"],
            _unique_past_week_monday(),
        ).json(),
        student["id"],
    )

    assert row is not None
    assert row["entry_count"] == 0
    assert row["total_hours"] == 0
    assert row["approved_percentage"] == 0


def test_approved_percentage_is_zero_without_review():

    student = _get_student()
    monday = _unique_past_week_monday()

    _create_entry(
        student["id"],
        monday,
        "08:00:00",
        "12:00:00",
    )

    row = _row_for(
        _stats_for(
            student["id"],
            monday,
        ).json(),
        student["id"],
    )

    assert row["entry_count"] == 1
    assert row["approved_percentage"] == 0


def test_approved_percentage_is_50_when_one_of_two_entries_is_approved():

    student = _get_student()
    supervisor = _get_supervisor()

    monday = _unique_past_week_monday()

    first_entry = _create_entry(
        student["id"],
        monday,
        "08:00:00",
        "12:00:00",
    )

    _create_entry(
        student["id"],
        monday + timedelta(days=1),
        "08:00:00",
        "12:00:00",
    )


    # draft -> submitted
    submit_response = client.post(
        f"/api/entries/{first_entry['id']}/submit",
        json={
            "user_id": student["id"],
        },
    )

    assert submit_response.status_code == 200


    # submitted -> approved
    approve_response = client.post(
        f"/api/entries/{first_entry['id']}/approve",
        json={
            "created_by": supervisor["id"],
        },
    )

    assert approve_response.status_code == 200


    response = _stats_for(
        student["id"],
        monday,
    )


    row = _row_for(
        response.json(),
        student["id"],
    )


    assert row is not None
    assert row["entry_count"] == 2
    assert row["approved_count"] == 1
    assert row["approved_percentage"] == 50.0


def test_week_start_rejects_non_monday():

    student = _get_student()

    monday = _unique_past_week_monday()

    response = _stats_for(
        student["id"],
        monday + timedelta(days=2),
    )

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_WEEK_START"


def test_supervisor_scope_includes_students_entries():

    supervisor = _get_supervisor()
    student = _get_student()

    monday = _unique_past_week_monday()

    _create_entry(
        student["id"],
        monday,
        "08:00:00",
        "13:00:00",
    )

    response = _stats_for(
        supervisor["id"],
        monday,
    )

    row = _row_for(
        response.json(),
        student["id"],
    )

    assert response.status_code == 200
    assert row is not None
    assert row["entry_count"] == 1
    assert row["total_hours"] == 5.0


def test_stats_for_non_existing_user_returns_404():

    response = _stats_for(
        999999999,
        _unique_past_week_monday(),
    )

    assert response.status_code == 404

    body = response.json()

    assert body["status"] == 404
    assert body["error"] == "NOT_FOUND"
    assert body["code"] == "USER_NOT_FOUND"