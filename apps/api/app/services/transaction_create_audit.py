"""Allowlisted audit serialization for #59 transaction CREATE control plane."""

from __future__ import annotations

import re
from typing import Any
from uuid import uuid4

_ALLOWED_KEYS = frozenset(
    {
        "schema_version",
        "event_ref",
        "result",
        "error_code",
        "retryable",
        "request_hash_prefix",
        "token_jti_hash_prefix",
        "idempotency_key_hash_prefix",
        "split_count",
        "currency",
        "create_generation",
        "duplicate",
        "stale",
        "lock_acquired",
        "backup_present",
        "backup_artifact_ref",
        "transaction_ref",
        "readback_verified",
        "recovery_ref",
        "duration_bucket_ms",
        "old_enabled",
        "new_enabled",
    }
)

_RESULT_VALUES = frozenset(
    {"started", "success", "already_created", "rejected", "busy", "indeterminate", "failed"}
)
_HASH_PREFIX_RE = re.compile(r"^[0-9a-f]{8,16}$")
_ERROR_CODE_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,63}$")
_EVENT_REF_RE = re.compile(r"^evt_[0-9a-f]{12}$")
_BACKUP_REF_RE = re.compile(r"^bkp_[A-Za-z0-9_]{8,64}$")
_TX_REF_RE = re.compile(r"^tx_[0-9a-f]{8,16}$")
_RECOVERY_REF_RE = re.compile(r"^rec_[0-9]{1,20}$")
_PRIVATE_SENTINEL_RE = re.compile(
    r"(private|secret|token|cookie|passwd|password|credential|\.gnucash|sqlite|traceback)",
    re.IGNORECASE,
)


def _safe_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _safe_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _safe_short_text(value: Any, *, max_length: int = 64) -> str | None:
    if not isinstance(value, str):
        return None
    if (
        not value
        or len(value) > max_length
        or "\x00" in value
        or "/" in value
        or "\\" in value
        or ".." in value
        or _PRIVATE_SENTINEL_RE.search(value)
    ):
        return None
    return value


def _safe_ref_for_key(key: str, value: Any) -> str | None:
    text = _safe_short_text(value)
    if text is None:
        return None
    if key in {"request_hash_prefix", "token_jti_hash_prefix", "idempotency_key_hash_prefix"}:
        return text if _HASH_PREFIX_RE.fullmatch(text) else None
    if key == "error_code":
        return text if _ERROR_CODE_RE.fullmatch(text) else None
    if key == "backup_artifact_ref":
        return text if _BACKUP_REF_RE.fullmatch(text) else None
    if key == "transaction_ref":
        return text if _TX_REF_RE.fullmatch(text) else None
    if key == "recovery_ref":
        return text if _RECOVERY_REF_RE.fullmatch(text) else None
    if key == "event_ref":
        return text if _EVENT_REF_RE.fullmatch(text) else None
    return text


def serialize_transaction_create_audit_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return only closed, non-private audit keys for CREATE control-plane events."""

    safe: dict[str, Any] = {"schema_version": 1}
    event_ref = _safe_ref_for_key("event_ref", payload.get("event_ref"))
    safe["event_ref"] = event_ref or f"evt_{uuid4().hex[:12]}"

    for key in _ALLOWED_KEYS:
        if key in {"schema_version", "event_ref"} or key not in payload:
            continue
        value = payload[key]
        if key == "result":
            result = _safe_short_text(value, max_length=32)
            if result in _RESULT_VALUES:
                safe[key] = result
        elif key in {"retryable", "duplicate", "stale", "lock_acquired", "backup_present", "readback_verified", "old_enabled", "new_enabled"}:
            bool_value = _safe_bool(value)
            if bool_value is not None:
                safe[key] = bool_value
        elif key in {"split_count", "create_generation", "duration_bucket_ms"}:
            int_value = _safe_int(value)
            if int_value is not None:
                safe[key] = int_value
        elif key == "currency":
            currency = _safe_short_text(value, max_length=3)
            if currency and currency.isalpha() and currency.isupper():
                safe[key] = currency
        else:
            text_value = _safe_ref_for_key(key, value)
            if text_value is not None:
                safe[key] = text_value
    return safe
