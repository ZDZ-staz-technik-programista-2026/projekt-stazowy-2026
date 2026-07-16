from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal
from app.models import Role, User


router = APIRouter(prefix="/api")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/roles")
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()

    return [
        {
            "id": role.id,
            "name": role.name
        }
        for role in roles
    ]


@router.get("/statuses")
def get_statuses():
    return [
        {"id": 1, "name": "draft"},
        {"id": 2, "name": "submitted"},
        {"id": 3, "name": "needs_revision"},
        {"id": 4, "name": "approved"}
    ]


@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "name": user.name,
            "daily_hours_limit": user.daily_hours_limit,
            "role": user.role.name
        }
        for user in users
    ]


@router.get("/users/{id}")
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": user.id,
        "name": user.name,
        "daily_hours_limit": user.daily_hours_limit,
        "role": user.role.name
    }
    