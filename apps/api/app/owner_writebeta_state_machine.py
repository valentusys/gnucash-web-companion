"""Owner-writebeta state-machine primitives.

This module is intentionally app-metadata-only. It stores opaque references and
state names, not financial values, book paths, account names, descriptions,
memos, amounts, backups paths, or raw evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import ClassVar
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
        if self.state == OwnerWritebetaState.CONFIRMATION and target == OwnerWritebetaState.MUTATING:
            required = [self.operation_ref, self.backup_ref]
            if not all(required):
                raise OwnerWritebetaTransitionError("mutation requires opaque operation_ref and backup_ref")
        if self.state == OwnerWritebetaState.MUTATING and target == OwnerWritebetaState.VERIFICATION and not refs.get("audit_ref"):
            raise OwnerWritebetaTransitionError("verification requires opaque audit_ref")
        if self.state == OwnerWritebetaState.VERIFICATION and target == OwnerWritebetaState.RESET_REQUIRED and not refs.get("restore_ref"):
            raise OwnerWritebetaTransitionError("reset_required requires opaque restore_ref")
        self.state = target
        self.failed_reason = reason if target == OwnerWritebetaState.FAILED_HARD_STOP else None
        for key in ("operation_ref", "backup_ref", "audit_ref", "restore_ref"):
            value = refs.get(key)
            if value:
                setattr(self, key, value[:80])
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
            "failed_reason": self.failed_reason,
        }
