import csv
import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Entry, User


router = APIRouter(prefix="/api")


def get_db():
    """
    Creates a database session for the API request.

    The session is closed after finishing the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/export_csv")
def export_csv(
    user_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """
    Export user's time entries as a CSV file.

    The exported file contains entry dates, working hours,
    descriptions, blockers and current statuses.
    """

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        return {
            "error": "USER_NOT_FOUND",
            "message": "User not found."
        }


    entries = (
        db.query(Entry)
        .filter(
            Entry.user_id == user_id
        )
        .order_by(
            Entry.date
        )
        .all()
    )


    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow(
        [
            "Date",
            "Start time",
            "End time",
            "Description",
            "Blockers",
            "Status",
            "Created at",
        ]
    )


    for entry in entries:
        writer.writerow(
            [
                entry.date,
                entry.start_time,
                entry.end_time,
                entry.description,
                entry.blockers or "",
                entry.status,
                entry.created_at,
            ]
        )

    csv_content = (
        "\ufeff" + output.getvalue()
    ).encode("utf-8")


    filename = (
        f"{user.name}_entries.csv"
        .replace(" ", "_")
    )


    return StreamingResponse(
        io.BytesIO(csv_content),
        media_type="text/csv",
        headers={
            "Content-Disposition":
            f"attachment; filename={filename}"
        },
    )