# Moved routes.py into routes folder and renamed it to basicAPI.py
"""Basic lookup and user management API endpoints.

Provides read-only access to dictionary data (roles, workflow statuses)
and system user details.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal
from app.models import Role, User


router = APIRouter(prefix="/api")


def get_db():
    """Database session generator dependency for FastAPI requests.

    Yields:
        Session: Active SQLAlchemy database session context.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/roles",
    summary="Get all roles",
    description="Retrieve a complete list of system roles defined in the database.",
)
def get_roles(db: Session = Depends(get_db)):
    """Fetch all user roles from the database."""
    roles = db.query(Role).all()

    return [
        {
            "id": role.id,
            "name": role.name
        }
        for role in roles
    ]


@router.get(
    "/statuses",
    summary="Get entry workflow statuses",
    description="Retrieve the static list of allowed approval statuses for time tracking entries.",
)
def get_statuses():
    """Return static dictionary of available entry workflow statuses."""
    return [
        {"id": 1, "name": "draft"},
        {"id": 2, "name": "submitted"},
        {"id": 3, "name": "needs_revision"},
        {"id": 4, "name": "approved"}
    ]


@router.get(
    "/users",
    summary="List all users",
    description="Retrieve all registered users alongside their assigned role and daily limit.",
)
def get_users(db: Session = Depends(get_db)):
    """Fetch all registered system users."""
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


@router.get(
    "/users/{id}",
    summary="Get user by ID",
    description="Fetch single user details by their unique database identifier.",
)
def get_user(id: int, db: Session = Depends(get_db)):
    """Fetch a specific user by identifier.

    Args:
        id (int): Unique identifier of the user.

    Raises:
        HTTPException: 404 NOT FOUND if no user matches the given ID.
    """
    user = db.query(User).filter(User.id == id).first()

    # Check if the requested user exists in the database
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