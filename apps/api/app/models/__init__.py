"""SQLAlchemy ORM models for app metadata."""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
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
    __table_args__ = (
        Index(
            "uq_books_canonical_path_hash_active",
            "canonical_path_hash",
            unique=True,
            sqlite_where=text("canonical_path_hash is not null and is_archived = 0"),
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    storage_type = Column(String(64), nullable=False)
    uri_or_path = Column(String(1024), nullable=False)
    canonical_path = Column(String(1024), nullable=True)
    canonical_path_hash = Column(String(64), nullable=True)
    base_currency = Column(String(16), nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    access_entries = relationship("UserBookAccess", back_populates="book")
    audit_logs = relationship("AuditLog", back_populates="book")
    health_snapshot = relationship(
        "BookHealthSnapshot",
        back_populates="book",
        uselist=False,
        cascade="all, delete-orphan",
    )
    write_alpha_transaction_ownership = relationship(
        "WriteAlphaTransactionOwnership", back_populates="book"
    )


class BookHealthSnapshot(Base):
    """Privacy-safe typed health snapshot for one registered book."""

    __tablename__ = "book_health_snapshots"

    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)
    source_status = Column(String(64), default="not_checked", nullable=False)
    open_status = Column(String(64), default="not_checked", nullable=False)
    accounts_status = Column(String(64), default="not_checked", nullable=False)
    transactions_status = Column(String(64), default="not_checked", nullable=False)
    reports_status = Column(String(64), default="not_checked", nullable=False)
    safe_code = Column(String(64), default="not_checked", nullable=False)
    checked_at = Column(DateTime, nullable=True)

    book = relationship("Book", back_populates="health_snapshot")


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


class WriteAlphaTransactionOwnership(Base):
    """App-metadata-only marker for transactions created through write-alpha.

    This table intentionally stores only a book-scoped transaction GUID and safe
    metadata needed for later PATCH/DELETE ownership guards. It does not write
    anything into the GnuCash book and does not store amounts, account names,
    memos, request payloads, backup paths, or private file paths.
    """

    __tablename__ = "write_alpha_transaction_ownership"
    __table_args__ = (
        UniqueConstraint(
            "book_id",
            "transaction_id",
            name="uq_write_alpha_transaction_ownership_book_transaction",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    transaction_id = Column(String(64), nullable=False)
    created_by_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_by_write_alpha = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    last_mutated_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    book = relationship("Book", back_populates="write_alpha_transaction_ownership")
    created_by_user = relationship("User")
