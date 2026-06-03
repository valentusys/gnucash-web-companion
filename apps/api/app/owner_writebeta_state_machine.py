"""Owner-writebeta state-machine primitives.

This module is intentionally app-metadata-only. It stores opaque references and
state names, not financial values, book paths, account names, descriptions,
memos, amounts, backups paths, or raw evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any, ClassVar, Mapping
from uuid import uuid4


class OwnerWritebetaState(StrEnum):
    DISABLED = "disabled"
    PREFLIGHT = "preflight"
    PREVIEW = "preview"
    CONFIRMATION = "confirmation"
    MUTATING = "mutating"
    VERIFICATION = "verification"
    RESET_REQUIRED = "reset_required"
    COMPLETE = "complete"
    FAILED_HARD_STOP = "failed_hard_stop"


class OwnerWritebetaTransitionError(RuntimeError):
    """Raised when a writebeta transition would weaken safety."""


@dataclass
class OwnerWritebetaSession:
    state: OwnerWritebetaState = OwnerWritebetaState.DISABLED
    session_ref: str = field(default_factory=lambda: f"owb-{uuid4().hex[:12]}")
    operation_ref: str | None = None
    backup_ref: str | None = None
    audit_ref: str | None = None
    restore_ref: str | None = None
    restore_readiness_ref: str | None = None
    preview_hash: str | None = None
    confirmation_token_ref: str | None = None
    operation_count: int = 0
    expires_at: datetime | None = None
    lock_released: bool = False
    defaults_reset: bool = False
    failed_reason: str | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    ALLOWED: ClassVar[dict[OwnerWritebetaState, set[OwnerWritebetaState]]] = {
        OwnerWritebetaState.DISABLED: {OwnerWritebetaState.PREFLIGHT},
        OwnerWritebetaState.PREFLIGHT: {OwnerWritebetaState.PREVIEW, OwnerWritebetaState.FAILED_HARD_STOP},
        OwnerWritebetaState.PREVIEW: {OwnerWritebetaState.CONFIRMATION, OwnerWritebetaState.FAILED_HARD_STOP},
        OwnerWritebetaState.CONFIRMATION: {OwnerWritebetaState.MUTATING, OwnerWritebetaState.FAILED_HARD_STOP},
        OwnerWritebetaState.MUTATING: {OwnerWritebetaState.VERIFICATION, OwnerWritebetaState.FAILED_HARD_STOP},
        OwnerWritebetaState.VERIFICATION: {OwnerWritebetaState.RESET_REQUIRED, OwnerWritebetaState.FAILED_HARD_STOP},
        OwnerWritebetaState.RESET_REQUIRED: {OwnerWritebetaState.COMPLETE, OwnerWritebetaState.FAILED_HARD_STOP},
        OwnerWritebetaState.COMPLETE: {OwnerWritebetaState.DISABLED},
        OwnerWritebetaState.FAILED_HARD_STOP: set(),
    }

    def transition(self, target: OwnerWritebetaState, *, reason: str | None = None, **refs: str | None) -> "OwnerWritebetaSession":
        if target not in self.ALLOWED[self.state]:
            raise OwnerWritebetaTransitionError(f"unsafe owner-writebeta transition: {self.state} -> {target}")
        # Apply incoming refs as tentative values so state-specific checks can
        # validate them before the transition is committed.
        tentative = {}
        for key in ("operation_ref", "backup_ref", "audit_ref", "restore_ref", "restore_readiness_ref", "preview_hash", "confirmation_token_ref"):
            value = refs.get(key)
            if value:
                tentative[key] = _bounded_opaque_ref(key, value)
        if self.state == OwnerWritebetaState.CONFIRMATION and target == OwnerWritebetaState.MUTATING:
            effective_operation_ref = tentative.get("operation_ref", self.operation_ref)
            effective_backup_ref = tentative.get("backup_ref", self.backup_ref)
            effective_restore_readiness_ref = tentative.get("restore_readiness_ref", self.restore_readiness_ref)
            if not all([effective_operation_ref, effective_backup_ref, effective_restore_readiness_ref]):
                raise OwnerWritebetaTransitionError("mutation requires opaque operation_ref, backup_ref, and restore_readiness_ref")
            if self.expires_at is not None and datetime.now(timezone.utc) > self.expires_at:
                raise OwnerWritebetaTransitionError("confirmed owner-writebeta preview expired")
        if self.state == OwnerWritebetaState.MUTATING and target == OwnerWritebetaState.VERIFICATION and not refs.get("audit_ref"):
            raise OwnerWritebetaTransitionError("verification requires opaque audit_ref")
        if self.state == OwnerWritebetaState.VERIFICATION and target == OwnerWritebetaState.RESET_REQUIRED and not refs.get("restore_ref"):
            raise OwnerWritebetaTransitionError("reset_required requires opaque restore_ref")
        self.state = target
        self.failed_reason = reason if target == OwnerWritebetaState.FAILED_HARD_STOP else None
        for key, value in tentative.items():
            setattr(self, key, value)
        if target == OwnerWritebetaState.DISABLED:
            # Disabled is the fail-closed terminal posture. Preserve opaque audit
            # evidence refs, but drop stale active-arm material so a completed
            # reset cannot look like it still has a confirmed write preview.
            self.preview_hash = None
            self.confirmation_token_ref = None
            self.restore_readiness_ref = None
            self.expires_at = None
        if target in {OwnerWritebetaState.RESET_REQUIRED, OwnerWritebetaState.FAILED_HARD_STOP}:
            # Reset-required and failed-hard-stop are post-mutation states.
            # Clear active-arm material so the operator cannot reuse a stale
            # confirmation without starting a fresh preflight→confirm flow.
            self.preview_hash = None
            self.confirmation_token_ref = None
            self.restore_readiness_ref = None
            self.expires_at = None
        self.updated_at = datetime.now(timezone.utc)
        return self

    @property
    def writes_blocked(self) -> bool:
        return self.state in {
            OwnerWritebetaState.DISABLED,
            OwnerWritebetaState.PREFLIGHT,
            OwnerWritebetaState.PREVIEW,
            OwnerWritebetaState.RESET_REQUIRED,
            OwnerWritebetaState.COMPLETE,
            OwnerWritebetaState.FAILED_HARD_STOP,
        }

    def redacted_summary(self) -> dict[str, str | bool | None]:
        return {
            "session_ref": self.session_ref,
            "state": self.state.value,
            "writes_blocked": self.writes_blocked,
            "operation_ref": self.operation_ref,
            "backup_ref": self.backup_ref,
            "audit_ref": self.audit_ref,
            "restore_ref": self.restore_ref,
            "restore_readiness_ref": self.restore_readiness_ref,
            "preview_hash": self.preview_hash,
            "confirmation_token_ref": self.confirmation_token_ref,
            "operation_count": str(self.operation_count),
            "lock_released": self.lock_released,
            "defaults_reset": self.defaults_reset,
            "failed_reason": self._sanitized_failed_reason(),
        }

    _SAFE_FAILED_REASONS: ClassVar[set[str]] = {
        "post-mutation verification incomplete",
        "restore readiness failed",
    }

    def _sanitized_failed_reason(self) -> str | None:
        if self.failed_reason is None:
            return None
        if self.failed_reason in self._SAFE_FAILED_REASONS:
            return self.failed_reason
        return "owner-writebeta session failed; see opaque audit refs only."


def _bounded_opaque_ref(key: str, value: str) -> str:
    """Validate and return a bounded opaque reference.

    Opaque refs may be identifiers from backup/audit/restore subsystems, but
    must not be raw paths, URLs, whitespace-bearing text, or evidence strings.
    """
    candidate = value[:80]
    if not candidate or any(ch in candidate for ch in "/\\:\t\r\n "):
        raise OwnerWritebetaTransitionError(f"{key} must be an opaque reference")
    return candidate


def _safe_shape(value: Any, _key_index: list[int] | None = None) -> Any:
    """Return a structure shape without serializing private field values or keys.

    Dict keys are replaced with opaque field_N placeholders to prevent
    user-provided key names from leaking into hashes or logs.
    """
    if _key_index is None:
        _key_index = [0]
    if isinstance(value, Mapping):
        result = {}
        for _, child in sorted(value.items(), key=lambda item: str(item[0])):
            field_name = f"field_{_key_index[0]}"
            _key_index[0] += 1
            result[field_name] = _safe_shape(child, _key_index)
        return result
    if isinstance(value, (list, tuple)):
        return ["item" for _ in value]
    return type(value).__name__


def preview_operation_hash(operation: str, payload_shape: Mapping[str, Any] | None = None, *, count: int = 1) -> str:
    """Build an opaque preview hash from operation type/count and payload shape only.

    The hash intentionally excludes account names, descriptions, memos, amounts,
    book paths, backup paths, and raw payload values so it is safe for committed
    evidence and audit docs.
    """
    if operation not in {"CREATE", "PATCH", "DELETE"}:
        raise OwnerWritebetaTransitionError("unsupported owner-writebeta operation")
    if count < 1 or count > 4:
        raise OwnerWritebetaTransitionError("owner-writebeta operation count outside authorized bounds")
    shape = _safe_shape(payload_shape or {})
    digest = hashlib.sha256(f"{operation}:{count}:{shape!r}".encode("utf-8")).hexdigest()[:16]
    return f"owb-prev-{digest}"


def confirmation_token_ref(raw_token: str) -> str:
    """Return a bounded opaque reference for a confirmation token."""
    digest = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()[:16]
    return f"owb-conf-{digest}"


def prepare_preview(session: OwnerWritebetaSession, operation: str, payload_shape: Mapping[str, Any] | None = None, *, count: int = 1) -> OwnerWritebetaSession:
    """Move PREFLIGHT -> PREVIEW with an exact, redacted operation preview hash."""
    preview_hash = preview_operation_hash(operation, payload_shape, count=count)
    session.operation_count = count
    return session.transition(OwnerWritebetaState.PREVIEW, preview_hash=preview_hash)


def arm_confirmed_preview(
    session: OwnerWritebetaSession,
    *,
    preview_hash: str,
    backup_ref: str,
    restore_readiness_ref: str | None = None,
    ttl_seconds: int = 600,
) -> tuple[OwnerWritebetaSession, str]:
    """Move PREVIEW -> CONFIRMATION and return the raw one-time token.

    Only the derived token reference belongs in durable evidence; the raw token
    is for the active request/session context only.
    """
    if session.preview_hash != preview_hash:
        raise OwnerWritebetaTransitionError("confirmation preview hash mismatch")
    if ttl_seconds < 1 or ttl_seconds > 3600:
        raise OwnerWritebetaTransitionError("confirmation token ttl outside safe bounds")
    raw_token = secrets.token_urlsafe(24)
    token_ref = confirmation_token_ref(raw_token)
    session.expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
    session.transition(
        OwnerWritebetaState.CONFIRMATION,
        operation_ref=preview_hash,
        backup_ref=backup_ref,
        confirmation_token_ref=token_ref,
        restore_readiness_ref=restore_readiness_ref,
    )
    return session, raw_token


def require_matching_confirmation(session: OwnerWritebetaSession, *, preview_hash: str, raw_token: str) -> None:
    """Fail closed unless the current confirmation matches the armed preview."""
    if session.state != OwnerWritebetaState.CONFIRMATION:
        raise OwnerWritebetaTransitionError("owner-writebeta session is not armed")
    if session.operation_ref != preview_hash or session.preview_hash != preview_hash:
        raise OwnerWritebetaTransitionError("owner-writebeta operation does not match armed preview")
    if session.confirmation_token_ref != confirmation_token_ref(raw_token):
        raise OwnerWritebetaTransitionError("owner-writebeta confirmation token mismatch")
    if session.expires_at is not None and datetime.now(timezone.utc) > session.expires_at:
        raise OwnerWritebetaTransitionError("confirmed owner-writebeta preview expired")


def mark_post_mutation_checks(
    session: OwnerWritebetaSession,
    *,
    audit_ref: str,
    restore_ref: str,
    lock_released: bool,
    defaults_reset: bool,
) -> OwnerWritebetaSession:
    """Record required post-mutation proof and move toward reset completion.

    Any missing read-back/audit/restore/lock/default-reset evidence hard-stops
    the session rather than allowing another mutation.
    """
    if audit_ref:
        _bounded_opaque_ref("audit_ref", audit_ref)
    if restore_ref:
        _bounded_opaque_ref("restore_ref", restore_ref)
    if not audit_ref or not restore_ref or not lock_released or not defaults_reset:
        return session.transition(OwnerWritebetaState.FAILED_HARD_STOP, reason="post-mutation verification incomplete")
    session.transition(OwnerWritebetaState.VERIFICATION, audit_ref=audit_ref)
    session.lock_released = True
    session.defaults_reset = True
    return session.transition(OwnerWritebetaState.RESET_REQUIRED, restore_ref=restore_ref)
