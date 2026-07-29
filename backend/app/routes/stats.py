from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case, text
from datetime import date, timedelta

from app.database import SessionLocal
from app.models import Entry, User


router = APIRouter(prefix="/api")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





@router.get("/stats")
def get_stats(
    user_id: int,
    db: Session = Depends(get_db)
):

    current_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not current_user:
        return {
            "error": "User not found"
        }


    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=7)


    hours_expression = (
        func.timestampdiff(
            text("MINUTE"),
            Entry.start_time,
            Entry.end_time
        ) / 60
    )


    query = (
        db.query(
            User.id.label("student_id"),
            User.name.label("student_name"),

            func.coalesce(
                func.sum(hours_expression),
                0
            ).label("total_hours"),

            func.count(
                Entry.id
            ).label("entry_count"),
            
            func.coalesce(
                func.sum(
                    case(
                        (
                            Entry.status == "approved",
                            1
                        ),
                        else_=0
                    )
                ),
                0
            ).label("approved_count"),

            func.round(
                    (
                        func.coalesce(
                            func.sum(
                                case(
                                    (
                                        Entry.status == "approved",
                                        1
                                    ),
                                    else_=0
                                )
                            ),
                            0
                        )
                        /
                        func.nullif(
                            func.count(Entry.id),
                            0
                        )
                        * 100
                    ),
                    2
            ).label("approved_percentage")

        )
        .join(
            Entry,
            User.id == Entry.user_id,
            isouter=True
        )
        .filter(
            Entry.date >= week_start,
            Entry.date < week_end
        )
    )


    if current_user.role.name != "Supervisor":
        query = query.filter(
            User.id == current_user.id
        )


    query = query.group_by(
        User.id,
        User.name
    )


    results = query.all()


    return [
        {
            "student_id": r.student_id,
            "student_name": r.student_name,
            "total_hours": float(r.total_hours or 0),
            "entry_count": r.entry_count,
            "approved_count": r.approved_count,
            "approved_percentage": float(
                r.approved_percentage or 0
            )
        }
        for r in results
    ]