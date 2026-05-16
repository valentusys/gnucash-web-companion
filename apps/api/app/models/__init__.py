"""SQLAlchemy ORM models for app metadata."""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(128), unique=True, nullable=False)
    display_name = Column(String(256), nullable=False)
    password_hash = Column(String(512), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    book_access = relationship("UserBookAccess", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    storage_type = Column(String(64), nullable=False)
    uri_or_path = Column(String(1024), nullable=False)
    base_currency = Column(String(16), nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    access_entries = relationship("UserBookAccess", back_populates="book")
    audit_logs = relationship("AuditLog", back_populates="book")


class UserBookAccess(Base):
    __tablename__ = "user_book_access"
    __table_args__ = (
        CheckConstraint(
            "role in ('owner', 'editor', 'viewer')",
            name="ck_user_book_access_role",
        ),
    )

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    book_id = Column(
        Integer, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
    )
    role = Column(String(16), nullable=False)  # owner | editor | viewer

    user = relationship("User", back_populates="book_access")
    book = relationship("Book", back_populates="access_entries")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(128), nullable=False)
    payload_json = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user = relationship("User", back_populates="audit_logs")
    book = relationship("Book", back_populates="audit_logs")
