from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    daily_hours_limit = Column(Integer, nullable=False, default=8)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    role = relationship("Role", back_populates="users")
    entries = relationship("Entry", back_populates="user")
    reviews = relationship("Review", back_populates="created_by_user")


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    description = Column(String(1000), nullable=False)
    blockers = Column(String(1000))
    status = Column(String(30), nullable=False, default="draft")
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    user = relationship("User", back_populates="entries")
    reviews = relationship("Review", back_populates="entry")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("entries.id"), nullable=False)
    comment = Column(String(1000), nullable=True)
    decision = Column(String(20), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    entry = relationship("Entry", back_populates="reviews")
    created_by_user = relationship("User", back_populates="reviews")
