from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy import and_, case, func, literal_column
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
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
    week_start_date: date | None = Query(
        None, description="Monday date YYYY-MM-DD"
    ),
    db: Session = Depends(get_db),
):
    current_user = db.query(User).filter(User.id == user_id).first()

    if not current_user:
        return JSONResponse(
            status_code=404,
            content={
                "status": 404,
                "error": "NOT_FOUND",
                "message": "User not found.",
                "code": "USER_NOT_FOUND",
                "details": {"user_id": user_id},
            },
        )

    if week_start_date is None:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
    else:
        week_start = week_start_date
        if week_start.weekday() != 0:
            return JSONResponse(
                status_code=400,
                content={
                    "status": 400,
                    "error": "BAD_REQUEST",
                    "message": "week_start_date must be Monday.",
                    "code": "INVALID_WEEK_START",
                    "details": {"week_start_date": str(week_start)},
                },
            )

    week_end = week_start + timedelta(days=7)

    if engine.dialect.name == "mysql":
        hours_expression = (
            func.timestampdiff(
                literal_column("SECOND"),
                Entry.start_time,
                Entry.end_time,
            )
            / 3600.0
        )
    elif engine.dialect.name == "sqlite":
        hours_expression = (
            func.strftime("%s", Entry.end_time)
            - func.strftime("%s", Entry.start_time)
        ) / 3600.0
    else:
        hours_expression = (
            func.extract("epoch", Entry.end_time - Entry.start_time) / 3600.0
        )

    entry_count = func.count(Entry.id)
    approved_count = func.coalesce(
        func.sum(case((Entry.status == "approved", 1), else_=0)), 0
    )

    query = db.query(
        User.id.label("student_id"),
        User.name.label("student_name"),
        func.coalesce(func.sum(hours_expression), 0).label("total_hours"),
        entry_count.label("entry_count"),
        approved_count.label("approved_count"),
        func.coalesce(
            (approved_count / func.nullif(entry_count, 0) * 100), 0
        ).label("approved_percentage"),
    ).outerjoin(
        Entry,
        and_(
            User.id == Entry.user_id,
            Entry.date >= week_start,
            Entry.date < week_end,
        ),
    )

    if not current_user.role or current_user.role.name != "Supervisor":
        query = query.filter(User.id == current_user.id)

    rows = query.group_by(User.id, User.name).all()

    return [
        {
            "student_id": row.student_id,
            "student_name": row.student_name,
            "week_start": str(week_start),
            "week_end": str(week_end),
            "total_hours": round(float(row.total_hours or 0), 2),
            "entry_count": int(row.entry_count or 0),
            "approved_count": int(row.approved_count or 0),
            "approved_percentage": round(
                float(row.approved_percentage or 0), 2
            ),
        }
        for row in rows
    ]