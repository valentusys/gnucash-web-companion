"""Typed, redacted error envelope for #59 transaction CREATE control plane."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NoReturn
from uuid import uuid4


@dataclass
class TransactionCreateHTTPError(Exception):
    status_code: int
    code: str
    message_key: str
    field_path: str | None = None
    retryable: bool = False
    recovery_ref: str | None = None
    request_ref: str | None = None
    headers: dict[str, str] | None = None

    def envelope(self) -> dict[str, dict[str, str | bool | None]]:
        return {
            "error": {
                "code": self.code,
                "message_key": self.message_key,
                "field_path": self.field_path,
                "retryable": self.retryable,
                "recovery_ref": self.recovery_ref,
                "request_ref": self.request_ref or f"req_{uuid4().hex[:12]}",
            }
        }


def message_key_for_code(code: str) -> str:
    return f"transaction_create.{code.lower()}"


def raise_transaction_create_error(
    status_code: int,
    code: str,
    *,
    field_path: str | None = None,
    retryable: bool = False,
    recovery_ref: str | None = None,
    headers: dict[str, str] | None = None,
) -> NoReturn:
    raise TransactionCreateHTTPError(
        status_code=status_code,
        code=code,
        message_key=message_key_for_code(code),
        field_path=field_path,
        retryable=retryable,
        recovery_ref=recovery_ref,
        headers=headers,
    )
