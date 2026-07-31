# Moved routes.py into routes folder and renamed it to basicAPI.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Role, User


router = APIRouter(prefix="/api")


def get_db():
    """
    Provides a database session for FastAPI endpoints.

    Creates a new SQLAlchemy session and closes it automatically
    after the request has finished.

    Yields:
        Session: Active database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/roles")
def get_roles(db: Session = Depends(get_db)):
    """
    Returns all available user roles.

    Args:
        db:
            Database session provided by dependency injection.

    Returns:
        list[dict]:
            List of roles containing their IDs and names.
    """
    roles = db.query(Role).all()

    return [
        {
            "id": role.id,
            "name": role.name,
        }
        for role in roles
    ]


@router.get("/statuses")
def get_statuses():
    """
    Returns all available entry statuses.

    The statuses are currently defined as a fixed list because
    they represent application workflow states rather than
    database entities.

    Returns:
        list[dict]:
            List of available statuses with IDs and names.
    """
    return [
        {"id": 1, "name": "draft"},
        {"id": 2, "name": "submitted"},
        {"id": 3, "name": "needs_revision"},
        {"id": 4, "name": "approved"},
    ]


@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    """
    Returns all users with their basic profile information.

    Args:
        db:
            Database session provided by dependency injection.

    Returns:
        list[dict]:
            List of users containing:
            - user ID,
            - name,
            - daily working hours limit,
            - assigned role.
    """
    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "name": user.name,
            "daily_hours_limit": user.daily_hours_limit,
            "role": user.role.name,
        }
        for user in users
    ]


@router.get("/users/{id}")
def get_user(id: int, db: Session = Depends(get_db)):
    """
    Returns details of a single user.

    Args:
        id:
            ID of the requested user.
        db:
            Database session provided by dependency injection.

    Raises:
        HTTPException:
            Returns 404 when the user does not exist.

    Returns:
        dict:
            User information including ID, name,
            daily hours limit and role.
    """
    user = db.query(User).filter(User.id == id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return {
        "id": user.id,
        "name": user.name,
        "daily_hours_limit": user.daily_hours_limit,
        "role": user.role.name,
    }