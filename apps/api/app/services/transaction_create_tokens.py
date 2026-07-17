"""Signed preview token and fingerprint primitives for #59 transaction CREATE."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import hmac
import json
import math
import re
from typing import Any
from uuid import uuid4

from app.config import Settings
from app.models import Book, User

TOKEN_PREFIX = "pt1"
TOKEN_TTL_SECONDS = 600
TOKEN_CLOCK_SKEW_SECONDS = 30
_SIGNING_LABEL = b"transaction-create-preview-signing-key-v1"
_IDEMPOTENCY_LABEL = b"transaction-create-idempotency-key-hash-v1"
_SOURCE_LABEL = b"transaction-create-source-fingerprint-v1"
_JTI_LABEL = b"transaction-create-token-jti-hash-v1"
_DECIMAL_RE = re.compile(r"^-?(?:0|[1-9]\d*)(?:\.\d+)?$")


@dataclass(frozen=True)
class PreviewTokenVerification:
    valid: bool
    code: str | None
    payload: dict[str, Any]


def _utc_timestamp(value: datetime) -> int:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return int(value.timestamp())


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def _secret_bytes(settings: Settings) -> bytes:
    return str(settings.jwt_secret or "").encode("utf-8")


def _derived_key(settings: Settings, label: bytes) -> bytes:
    return hmac.new(_secret_bytes(settings), label, hashlib.sha256).digest()


def _hex_hmac(settings: Settings, label: bytes, payload: bytes) -> str:
    return hmac.new(_derived_key(settings, label), payload, hashlib.sha256).hexdigest()


def _normalize_decimal_string(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("amount must be a decimal string")
    stripped = value.strip()
    if len(stripped) > 64 or not _DECIMAL_RE.fullmatch(stripped):
        raise ValueError("amount must be a plain decimal string")
    amount = Decimal(stripped)
    if not amount.is_finite():
        raise ValueError("amount must be finite")
    return stripped


def _normalize_text(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("text fields must be strings")
    return value.strip()


def normalize_transaction_create_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize the general #59 preview/confirm request for hashing."""

    if not isinstance(payload, dict):
        raise ValueError("request must be an object")
    splits = payload.get("splits")
    if not isinstance(splits, list):
        raise ValueError("splits must be a list")
    return {
        "date": _normalize_text(payload.get("date")),
        "description": _normalize_text(payload.get("description")),
        "currency": _normalize_text(payload.get("currency")).upper(),
        "splits": [
            {
                "account_id": _normalize_text(split.get("account_id")),
                "amount": _normalize_decimal_string(split.get("amount")),
                "memo": _normalize_text(split.get("memo", "")),
            }
            for split in splits
            if isinstance(split, dict)
        ],
    }


def canonical_transaction_create_request_hash(payload: dict[str, Any]) -> str:
    normalized = normalize_transaction_create_request(payload)
    raw = json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def hash_idempotency_key(raw_key: str, settings: Settings) -> str:
    return _hex_hmac(settings, _IDEMPOTENCY_LABEL, str(raw_key).encode("utf-8"))


def hash_token_jti(jti: str, settings: Settings) -> str:
    return _hex_hmac(settings, _JTI_LABEL, str(jti).encode("utf-8"))


def source_fingerprint_for_book(
    book: Book,
    settings: Settings,
    *,
    source_identity: Any | None = None,
    versions: dict[str, Any] | None = None,
    source_base_currency: str | None = None,
) -> str:
    """Build an opaque source fingerprint from metadata plus optional live evidence."""

    snapshot = getattr(book, "health_snapshot", None)
    identity_payload: dict[str, Any] | None = None
    if source_identity is not None:
        hmac_payload = getattr(source_identity, "hmac_payload", None)
        if callable(hmac_payload):
            raw_identity_payload = hmac_payload()
            identity_payload = raw_identity_payload if isinstance(raw_identity_payload, dict) else {}
        else:
            identity_payload = {
                "canonical_path_hash": str(getattr(source_identity, "canonical_path_hash", "") or ""),
                "st_dev": int(getattr(source_identity, "st_dev", 0) or 0),
                "st_ino": int(getattr(source_identity, "st_ino", 0) or 0),
                "st_size": int(getattr(source_identity, "st_size", 0) or 0),
                "st_mtime_ns": int(getattr(source_identity, "st_mtime_ns", 0) or 0),
            }
    evidence = {
        "book_id": int(getattr(book, "id", 0) or 0),
        "canonical_path_hash": str(getattr(book, "canonical_path_hash", "") or ""),
        "registered_base_currency": str(getattr(book, "base_currency", "") or "").upper(),
        "source_base_currency": str(source_base_currency or getattr(book, "base_currency", "") or "").upper(),
        "create_generation": int(getattr(book, "transaction_create_generation", 1) or 1),
        "health_safe_code": str(getattr(snapshot, "safe_code", "not_checked") if snapshot is not None else "not_checked"),
        "last_successful_at": str(getattr(snapshot, "last_successful_at", "") if snapshot is not None else ""),
        "source_identity": identity_payload,
        "versions": versions or {},
    }
    raw = json.dumps(evidence, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return _hex_hmac(settings, _SOURCE_LABEL, raw)


def issue_preview_token(
    *,
    settings: Settings,
    user: User,
    book: Book,
    request_hash: str,
    idempotency_key_hash: str,
    source_fingerprint: str,
    now: datetime | None = None,
    jti: str | None = None,
) -> str:
    issued_at = now or _now()
    iat = _utc_timestamp(issued_at)
    token_jti = jti or uuid4().hex
    payload = {
        "v": 1,
        "jti": token_jti,
        "iat": iat,
        "exp": iat + TOKEN_TTL_SECONDS,
        "user_id": int(user.id),
        "auth_version": int(getattr(user, "auth_version", 1) or 1),
        "book_id": int(book.id),
        "transaction_create_generation": int(getattr(book, "transaction_create_generation", 1) or 1),
        "idempotency_key_hash": idempotency_key_hash,
        "request_hash": request_hash,
        "source_fingerprint": source_fingerprint,
    }
    payload_raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    payload_part = _b64url_encode(payload_raw)
    signed = f"{TOKEN_PREFIX}.{payload_part}".encode("ascii")
    signature = hmac.new(_derived_key(settings, _SIGNING_LABEL), signed, hashlib.sha256).digest()
    return f"{TOKEN_PREFIX}.{payload_part}.{_b64url_encode(signature)}"


def _invalid(code: str, payload: dict[str, Any] | None = None) -> PreviewTokenVerification:
    return PreviewTokenVerification(valid=False, code=code, payload=payload or {})


def verify_preview_token(
    token: str,
    settings: Settings,
    *,
    expected_user_id: int | None = None,
    expected_auth_version: int | None = None,
    expected_book_id: int | None = None,
    expected_generation: int | None = None,
    expected_request_hash: str | None = None,
    expected_idempotency_key_hash: str | None = None,
    expected_source_fingerprint: str | None = None,
    now: datetime | None = None,
    allow_expired: bool = False,
) -> PreviewTokenVerification:
    try:
        prefix, payload_part, signature_part = str(token).split(".", 2)
        if prefix != TOKEN_PREFIX:
            return _invalid("PREVIEW_TOKEN_INVALID")
        signed = f"{prefix}.{payload_part}".encode("ascii")
        expected_sig = hmac.new(_derived_key(settings, _SIGNING_LABEL), signed, hashlib.sha256).digest()
        supplied_sig = _b64url_decode(signature_part)
        if not hmac.compare_digest(expected_sig, supplied_sig):
            return _invalid("PREVIEW_TOKEN_INVALID")
        payload = json.loads(_b64url_decode(payload_part).decode("utf-8"))
    except Exception:
        return _invalid("PREVIEW_TOKEN_INVALID")

    if payload.get("v") != 1:
        return _invalid("PREVIEW_TOKEN_INVALID", payload)
    current = _utc_timestamp(now or _now())
    try:
        iat = int(payload["iat"])
        exp = int(payload["exp"])
    except Exception:
        return _invalid("PREVIEW_TOKEN_INVALID", payload)
    if current < iat - TOKEN_CLOCK_SKEW_SECONDS:
        return _invalid("PREVIEW_TOKEN_INVALID", payload)
    if current > exp + TOKEN_CLOCK_SKEW_SECONDS and not allow_expired:
        return _invalid("PREVIEW_TOKEN_EXPIRED", payload)

    checks = (
        (expected_user_id, payload.get("user_id"), "PREVIEW_TOKEN_INVALID"),
        (expected_auth_version, payload.get("auth_version"), "PREVIEW_TOKEN_INVALID"),
        (expected_book_id, payload.get("book_id"), "PREVIEW_TOKEN_INVALID"),
        (expected_generation, payload.get("transaction_create_generation"), "PREVIEW_STALE"),
        (expected_request_hash, payload.get("request_hash"), "PREVIEW_PAYLOAD_MISMATCH"),
        (expected_idempotency_key_hash, payload.get("idempotency_key_hash"), "IDEMPOTENCY_PAYLOAD_MISMATCH"),
        (expected_source_fingerprint, payload.get("source_fingerprint"), "PREVIEW_STALE"),
    )
    for expected, actual, code in checks:
        if expected is None:
            continue
        if isinstance(expected, int):
            if int(actual) != expected:
                return _invalid(code, payload)
        elif not hmac.compare_digest(str(expected), str(actual)):
            return _invalid(code, payload)
    return PreviewTokenVerification(valid=True, code=None, payload=payload)
