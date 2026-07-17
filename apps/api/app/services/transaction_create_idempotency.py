"""Durable idempotency state-machine primitives for #59 transaction CREATE."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import re
from typing import Any
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import Book, TransactionCreateIdempotency
from app.services.transaction_create_tokens import hash_idempotency_key

TERMINAL_STATES = ("succeeded", "rejected")
RETENTION_DAYS = 30
TERMINAL_ROW_LIMIT_PER_BOOK = 2_000
PRUNE_BATCH_LIMIT = 100
IN_PROGRESS_STALE_AFTER_SECONDS = 15 * 60
_GUID_RE = re.compile(r"^[0-9a-f]{32}$")
_AUDIT_REF_RE = re.compile(r"^aud_[0-9a-f]{12}$")
_BACKUP_REF_RE = re.compile(r"^bkp_[A-Za-z0-9_]{8,64}$")


@dataclass(frozen=True)
class IdempotencyReservation:
    status: str
    record: TransactionCreateIdempotency
    safe_result: dict[str, Any] | None = None


class TransactionCreateIdempotencyService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def reserve(
        self,
        *,
        book_id: int,
        user_id: int,
        raw_key: str,
        request_hash: str,
        token_jti_hash: str,
        now: datetime | None = None,
    ) -> IdempotencyReservation:
        timestamp = _as_naive_utc(now or datetime.now(timezone.utc))
        key_hash = hash_idempotency_key(raw_key, self.settings)
        record = TransactionCreateIdempotency(
            user_id=user_id,
            book_id=book_id,
            key_hash=key_hash,
            request_hash=request_hash,
            token_jti_hash=token_jti_hash,
            planned_transaction_guid=uuid4().hex,
            state="in_progress",
            created_at=timestamp,
            updated_at=timestamp,
            expires_at=timestamp + timedelta(days=RETENTION_DAYS),
        )
        self.session.add(record)
        try:
            self.session.commit()
            self.session.refresh(record)
            return IdempotencyReservation(status="reserved", record=record)
        except IntegrityError:
            self.session.rollback()

        existing = (
            self.session.query(TransactionCreateIdempotency)
            .filter(
                TransactionCreateIdempotency.book_id == book_id,
                TransactionCreateIdempotency.user_id == user_id,
                TransactionCreateIdempotency.key_hash == key_hash,
            )
            .one()
        )
        if existing.request_hash != request_hash or existing.token_jti_hash != token_jti_hash:
            return IdempotencyReservation(status="payload_mismatch", record=existing)
        if existing.state == "succeeded":
            return IdempotencyReservation(
                status="already_succeeded",
                record=existing,
                safe_result=_loads_safe_result(existing.safe_result_json),
            )
        if existing.state == "in_progress":
            updated_at = _as_naive_utc(existing.updated_at or existing.created_at or timestamp)
            if timestamp - updated_at > timedelta(seconds=IN_PROGRESS_STALE_AFTER_SECONDS):
                self.mark_indeterminate(
                    existing,
                    "CREATE_RECOVERY_REQUIRED",
                    now=timestamp,
                )
                return IdempotencyReservation(status="recovery_required", record=existing)
            return IdempotencyReservation(status="in_progress", record=existing)
        if existing.state == "indeterminate":
            return IdempotencyReservation(status="recovery_required", record=existing)
        return IdempotencyReservation(status="rejected", record=existing)

    def find_existing(
        self,
        *,
        book_id: int,
        user_id: int,
        raw_key: str,
    ) -> TransactionCreateIdempotency | None:
        """Return an existing idempotency row without creating or mutating one."""

        key_hash = hash_idempotency_key(raw_key, self.settings)
        return (
            self.session.query(TransactionCreateIdempotency)
            .filter(
                TransactionCreateIdempotency.book_id == book_id,
                TransactionCreateIdempotency.user_id == user_id,
                TransactionCreateIdempotency.key_hash == key_hash,
            )
            .one_or_none()
        )

    def mark_succeeded(
        self,
        record: TransactionCreateIdempotency,
        safe_result: dict[str, Any],
        *,
        now: datetime | None = None,
    ) -> None:
        timestamp = _as_naive_utc(now or datetime.now(timezone.utc))
        safe_result = _validate_safe_result(safe_result)
        record.state = "succeeded"
        record.safe_error_code = None
        record.safe_result_json = json.dumps(safe_result, sort_keys=True, separators=(",", ":"))
        record.updated_at = timestamp
        record.expires_at = timestamp + timedelta(days=RETENTION_DAYS)
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)

    def mark_rejected(
        self,
        record: TransactionCreateIdempotency,
        safe_error_code: str,
        *,
        now: datetime | None = None,
    ) -> None:
        timestamp = _as_naive_utc(now or datetime.now(timezone.utc))
        record.state = "rejected"
        record.safe_error_code = safe_error_code
        record.safe_result_json = None
        record.updated_at = timestamp
        record.expires_at = timestamp + timedelta(days=RETENTION_DAYS)
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)

    def mark_indeterminate(
        self,
        record: TransactionCreateIdempotency,
        safe_error_code: str,
        *,
        now: datetime | None = None,
    ) -> None:
        timestamp = _as_naive_utc(now or datetime.now(timezone.utc))
        record.state = "indeterminate"
        record.safe_error_code = safe_error_code
        record.safe_result_json = None
        record.updated_at = timestamp
        book = self.session.query(Book).filter(Book.id == record.book_id).first()
        if book is not None:
            book.transaction_create_recovery_required = True
            self.session.add(book)
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)

    def prune(self, *, book_id: int, now: datetime | None = None) -> int:
        timestamp = _as_naive_utc(now or datetime.now(timezone.utc))
        deleted = 0
        expired = (
            self.session.query(TransactionCreateIdempotency)
            .filter(
                TransactionCreateIdempotency.book_id == book_id,
                TransactionCreateIdempotency.state.in_(TERMINAL_STATES),
                TransactionCreateIdempotency.expires_at < timestamp,
            )
            .order_by(TransactionCreateIdempotency.expires_at, TransactionCreateIdempotency.id)
            .limit(PRUNE_BATCH_LIMIT)
            .all()
        )
        for row in expired:
            self.session.delete(row)
            deleted += 1
        if deleted:
            self.session.commit()
            return deleted

        terminal_count = (
            self.session.query(TransactionCreateIdempotency)
            .filter(
                TransactionCreateIdempotency.book_id == book_id,
                TransactionCreateIdempotency.state.in_(TERMINAL_STATES),
            )
            .count()
        )
        excess = max(0, terminal_count - TERMINAL_ROW_LIMIT_PER_BOOK)
        if excess <= 0:
            return 0
        victims = (
            self.session.query(TransactionCreateIdempotency)
            .filter(
                TransactionCreateIdempotency.book_id == book_id,
                TransactionCreateIdempotency.state.in_(TERMINAL_STATES),
            )
            .order_by(TransactionCreateIdempotency.updated_at, TransactionCreateIdempotency.id)
            .limit(min(PRUNE_BATCH_LIMIT, excess))
            .all()
        )
        for row in victims:
            self.session.delete(row)
            deleted += 1
        self.session.commit()
        return deleted


def _loads_safe_result(raw: str | None) -> dict[str, Any] | None:
    if not raw:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(value, dict):
        return None
    try:
        return _validate_safe_result(value)
    except ValueError:
        return None


def _validate_safe_result(value: dict[str, Any]) -> dict[str, Any]:
    allowed_top = {"status", "transaction_id", "audit_ref", "backup_ref", "readback", "links"}
    if set(value) - allowed_top:
        raise ValueError("unsafe idempotency result keys")
    status_value = value.get("status")
    if status_value not in {"created", "already_created"}:
        raise ValueError("unsafe idempotency result status")
    transaction_id = value.get("transaction_id")
    if not isinstance(transaction_id, str) or not _GUID_RE.fullmatch(transaction_id):
        raise ValueError("unsafe idempotency transaction id")
    audit_ref = value.get("audit_ref")
    if not isinstance(audit_ref, str) or not _AUDIT_REF_RE.fullmatch(audit_ref):
        raise ValueError("unsafe idempotency audit ref")
    backup_ref = value.get("backup_ref")
    if not isinstance(backup_ref, str) or not _BACKUP_REF_RE.fullmatch(backup_ref):
        raise ValueError("unsafe idempotency backup ref")
    readback = value.get("readback")
    if not isinstance(readback, dict):
        raise ValueError("unsafe idempotency readback")
    allowed_readback = {
        "verified",
        "transaction_present",
        "split_count",
        "balanced",
        "currency_consistent",
        "account_balance_deltas_verified",
    }
    if set(readback) - allowed_readback:
        raise ValueError("unsafe idempotency readback keys")
    for key in {"verified", "transaction_present", "balanced", "currency_consistent"}:
        if not isinstance(readback.get(key), bool):
            raise ValueError("unsafe idempotency readback bool")
    if not isinstance(readback.get("split_count"), int) or readback["split_count"] < 2:
        raise ValueError("unsafe idempotency split count")
    if "account_balance_deltas_verified" in readback and not isinstance(
        readback["account_balance_deltas_verified"],
        bool,
    ):
        raise ValueError("unsafe idempotency delta bool")
    links = value.get("links")
    if not isinstance(links, dict) or set(links) != {"transaction", "explorer"}:
        raise ValueError("unsafe idempotency links")
    for link in links.values():
        if (
            not isinstance(link, str)
            or not link.startswith("/books/")
            or ".." in link
            or "\\" in link
        ):
            raise ValueError("unsafe idempotency link")
    return value


def _as_naive_utc(value: datetime) -> datetime:
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value
