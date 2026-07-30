"""Integration tests for the `/api/stats` endpoint.

Validates time tracking statistics calculation, week date normalization,
role-based visibility scopes (Student vs Supervisor), and error handling.
"""

import random
from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# Module-level random generator to ensure isolated, reproducible date offsets
_rng = random.Random()


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------


def _unique_past_date() -> date:
    """Generate a random past date between ~3 months and ~4 years ago.

    Used to avoid collisions with existing seeded test entries or fixed dates.

    Returns:
        date: A date object in the past.
    """
    # Offset by 100 to 1500 days to land safely in past data ranges
    offset_days = _rng.randint(100, 1500)
    return date.today() - timedelta(days=offset_days)


def _unique_past_week_monday() -> date:
    """Generate a random past date guaranteed to be a Monday.

    Returns:
        date: The Monday of a randomly selected past week.
    """
    d = _unique_past_date()
    # Subtracting the weekday index (0 = Mon, 6 = Sun) rolls the date back to Monday
    return d - timedelta(days=d.weekday())


def _get_student() -> dict:
    """Fetch the first available user with the 'Student' role from the API.

    Returns:
        dict: Student user payload containing ID and details.

    Raises:
        AssertionError: If API call fails or no student user is found in seed data.
    """
    response = client.get("/api/users")
    assert response.status_code == 200
    students = [u for u in response.json() if u["role"] == "Student"]
    assert students, "No Student user found in seed data"
    return students[0]


def _get_supervisor() -> dict:
    """Fetch the first available user with the 'Supervisor' role from the API.

    Returns:
        dict: Supervisor user payload containing ID and details.

    Raises:
        AssertionError: If API call fails or no supervisor user is found in seed data.
    """
    response = client.get("/api/users")
    assert response.status_code == 200
    supervisors = [u for u in response.json() if u["role"] == "Supervisor"]
    assert supervisors, "No Supervisor user found in seed data"
    return supervisors[0]


def _create_entry(
    user_id: int,
    entry_date: date,
    start_time: str,
    end_time: str,
    description: str = "Stats test entry",
) -> dict:
    """Helper to create a new time tracking entry via POST /api/entries.

    Args:
        user_id: The ID of the student creating the entry.
        entry_date: Date of the logged work.
        start_time: Start time string formatted as 'HH:MM:SS'.
        end_time: End time string formatted as 'HH:MM:SS'.
        description: Short description of the work performed.

    Returns:
        dict: The newly created entry dictionary returned by the API.
    """
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


def _stats_for(user_id: int, week_start: date):
    """Call GET /api/stats for a given user and target week.

    Args:
        user_id: Target user ID to query stats for.
        week_start: The start date parameter for the statistics calculation.

    Returns:
        httpx.Response: Raw response object from TestClient.
    """
    return client.get(
        "/api/stats",
        params={"user_id": user_id, "week_start_date": str(week_start)},
    )


def _row_for(data: list, student_id: int) -> dict | None:
    """Extract a specific student's summary row from the stats response list.

    Args:
        data: Parsed response payload from the stats endpoint (expected list).
        student_id: Student user ID to match against.

    Returns:
        dict | None: The matching student stats record, or None if not present.
    """
    if not isinstance(data, list):
        return None
    return next((row for row in data if row["student_id"] == student_id), None)


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------


def test_stats_endpoint_runs_for_existing_student():
    """Verify GET /api/stats responds with 200 OK and a list for a valid student."""
    student = _get_student()
    monday = _unique_past_week_monday()

    response = _stats_for(student["id"], monday)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_stats_reflects_created_entries_for_the_selected_week():
    """Verify entry count, total hours, and week range boundaries are calculated correctly."""
    student = _get_student()
    monday = _unique_past_week_monday()

    # Create 2 entries: Mon (4h = 08:00-12:00) and Tue (2h = 09:00-11:00) -> Total 6.0 hours
    _create_entry(student["id"], monday, "08:00:00", "12:00:00")
    _create_entry(
        student["id"], monday + timedelta(days=1), "09:00:00", "11:00:00"
    )

    response = _stats_for(student["id"], monday)
    row = _row_for(response.json(), student["id"])

    assert row is not None
    assert row["entry_count"] == 2
    assert row["total_hours"] == 6.0
    assert row["week_start"] == str(monday)
    # Week boundary check: stats period spans Mon through next Mon (7 days)
    assert row["week_end"] == str(monday + timedelta(days=7))


def test_stats_excludes_entries_from_other_weeks():
    """Ensure entries belonging to adjacent weeks are excluded from weekly aggregation."""
    student = _get_student()
    monday = _unique_past_week_monday()
    other_week_monday = monday - timedelta(days=7)

    # 2 hours in target week, 8 hours in previous week
    _create_entry(student["id"], monday, "08:00:00", "10:00:00")
    _create_entry(student["id"], other_week_monday, "08:00:00", "16:00:00")

    response = _stats_for(student["id"], monday)
    row = _row_for(response.json(), student["id"])

    # Should only count the 2 hours from the target week
    assert row["entry_count"] == 1
    assert row["total_hours"] == 2.0


def test_stats_returns_zero_for_week_with_no_entries():
    """Verify that querying an empty week returns zeroed statistics rather than 404."""
    student = _get_student()
    empty_week_monday = _unique_past_week_monday()

    response = _stats_for(student["id"], empty_week_monday)
    row = _row_for(response.json(), student["id"])

    assert row is not None
    assert row["entry_count"] == 0
    assert row["total_hours"] == 0
    assert row["approved_percentage"] == 0


def test_approved_percentage_is_zero_without_any_review():
    """Ensure approved_percentage defaults to 0 when entries exist but have not been reviewed."""
    student = _get_student()
    monday = _unique_past_week_monday()

    _create_entry(student["id"], monday, "08:00:00", "12:00:00")

    row = _row_for(_stats_for(student["id"], monday).json(), student["id"])

    assert row["entry_count"] == 1
    assert row["approved_percentage"] == 0


def test_week_start_normalizes_any_weekday_to_that_weeks_monday():
    """Verify API strict validation on week_start_date parameter (must be a Monday)."""
    student = _get_student()
    monday = _unique_past_week_monday()
    wednesday = monday + timedelta(days=2)

    _create_entry(student["id"], monday, "14:00:00", "16:00:00")

    res_monday = _stats_for(student["id"], monday)
    res_wednesday = _stats_for(student["id"], wednesday)

    # Monday is valid; mid-week start date must trigger a 400 validation error
    assert res_monday.status_code == 200
    assert res_wednesday.status_code == 400
    assert res_wednesday.json()["code"] == "INVALID_WEEK_START"


def test_supervisor_scope_includes_a_students_entries_for_the_week():
    """Verify supervisors can retrieve statistics aggregated across their supervised students."""
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
    """Verify non-existent user IDs return standard 404 error response structure."""
    # Generate a high random user ID unlikely to exist in DB
    non_existing_user_id = 999_000_000 + _rng.randint(0, 999_999)

    response = client.get(
        "/api/stats",
        params={
            "user_id": non_existing_user_id,
            "week_start_date": str(_unique_past_week_monday()),
        },
    )

    # Validate standard API error payload envelope
    assert response.status_code == 404
    body = response.json()
    assert body["status"] == 404
    assert body["error"] == "NOT_FOUND"
    assert body["code"] == "USER_NOT_FOUND"