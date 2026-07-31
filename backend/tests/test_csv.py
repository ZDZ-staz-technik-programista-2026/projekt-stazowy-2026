from datetime import date, time

from app.database import SessionLocal
from app.models import User, Entry


def get_existing_user():
    db = SessionLocal()

    user = (
        db.query(User)
        .first()
    )

    db.close()

    assert user is not None, "Test database has no users"

    return user


def get_second_user():
    db = SessionLocal()

    users = (
        db.query(User)
        .limit(2)
        .all()
    )

    db.close()

    assert len(users) >= 2, "Test database needs two users"

    return users[1]


def test_export_csv_returns_csv_file(client):
    user = get_existing_user()

    response = client.get(
        f"/api/export_csv?user_id={user.id}"
    )

    assert response.status_code == 200

    assert response.headers[
        "content-type"
    ].startswith("text/csv")

    assert "attachment" in response.headers[
        "content-disposition"
    ]


def test_export_csv_supports_polish_utf8_text(client):
    user = get_existing_user()

    db = SessionLocal()

    entry = Entry(
        user_id=user.id,
        date=date(2026, 7, 31),
        start_time=time(9, 0),
        end_time=time(10, 0),
        description="Zażółć gęślą jaźń",
        blockers="",
        status="DONE",
    )

    db.add(entry)
    db.commit()

    db.close()

    response = client.get(
        f"/api/export_csv?user_id={user.id}"
    )

    content = response.content.decode(
        "utf-8-sig"
    )

    assert "Zażółć gęślą jaźń" in content


def test_export_csv_escapes_csv_special_characters(client):
    user = get_existing_user()

    db = SessionLocal()

    entry = Entry(
        user_id=user.id,
        date=date(2026, 7, 31),
        start_time=time(9, 0),
        end_time=time(10, 0),
        description='Text with, comma and "quotes"\nsecond line',
        blockers="",
        status="DONE",
    )

    db.add(entry)
    db.commit()

    db.close()

    response = client.get(
        f"/api/export_csv?user_id={user.id}"
    )

    content = response.content.decode(
        "utf-8-sig"
    )

    assert 'Text with, comma and ""quotes""' in content
    assert "second line" in content


def test_export_csv_contains_only_selected_user_entries(client):
    user_one = get_existing_user()
    user_two = get_second_user()

    db = SessionLocal()

    entry_one = Entry(
        user_id=user_one.id,
        date=date(2026, 7, 31),
        start_time=time(9, 0),
        end_time=time(10, 0),
        description="USER_ONE_ENTRY",
        blockers="",
        status="DONE",
    )

    entry_two = Entry(
        user_id=user_two.id,
        date=date(2026, 7, 31),
        start_time=time(9, 0),
        end_time=time(10, 0),
        description="USER_TWO_ENTRY",
        blockers="",
        status="DONE",
    )

    db.add_all(
        [
            entry_one,
            entry_two,
        ]
    )

    db.commit()

    db.close()

    response = client.get(
        f"/api/export_csv?user_id={user_one.id}"
    )

    content = response.content.decode(
        "utf-8-sig"
    )

    assert "USER_ONE_ENTRY" in content
    assert "USER_TWO_ENTRY" not in content


def test_export_csv_empty_journal_returns_header_only(client):
    db = SessionLocal()

    user = (
        db.query(User)
        .filter(
            ~User.entries.any()
        )
        .first()
    )

    db.close()

    assert user is not None, "Need a user without entries"

    response = client.get(
        f"/api/export_csv?user_id={user.id}"
    )

    assert response.status_code == 200

    content = response.content.decode(
        "utf-8-sig"
    )

    lines = content.strip().splitlines()

    assert len(lines) == 1
    assert "Date" in lines[0]


def test_export_csv_unknown_user_returns_404(client):
    response = client.get(
        "/api/export_csv?user_id=999999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["error"] == "USER_NOT_FOUND"
    assert data["message"] == "User not found."