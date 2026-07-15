"""User normalization and credential policy helpers."""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

USERNAME_PATTERN = re.compile(r"^[a-z][a-z0-9._-]{2,63}$")
BCRYPT_MAX_BYTES = 72
PASSWORD_MIN_CODEPOINTS = 12
PASSWORD_MAX_CODEPOINTS = 128

WEAK_PASSWORD_DENYLIST = frozenset(
    {
        "password123!",
        "Password123!",
        "password1234",
        "Password1234",
        "adminadmin12!",
        "qwerty12345!",
        "letmein12345!",
        "changeme123!",
        "welcome1234!",
        "1234567890Aa!",
    }
)


class UsernameValidationError(ValueError):
    """Raised when a username cannot become a valid canonical key."""


class DisplayNameValidationError(ValueError):
    """Raised when a display name is unsafe or out of bounds."""


class PasswordPolicyError(ValueError):
    """Raised when a password does not satisfy the local policy."""


def normalize_username(username: str) -> str:
    """Return the canonical username key or raise a bounded validation error."""

    if not isinstance(username, str):
        raise UsernameValidationError("username_invalid")
    normalized = unicodedata.normalize("NFKC", username.strip()).casefold()
    if USERNAME_PATTERN.fullmatch(normalized) is None:
        raise UsernameValidationError("username_invalid")
    return normalized


def normalize_display_name(display_name: str) -> str:
    """Normalize a safe display name without exposing a mutation route yet."""

    if not isinstance(display_name, str):
        raise DisplayNameValidationError("display_name_invalid")
    normalized = unicodedata.normalize("NFKC", display_name).strip()
    if not (1 <= len(normalized) <= 100):
        raise DisplayNameValidationError("display_name_invalid")
    if any(unicodedata.category(char).startswith("C") for char in normalized):
        raise DisplayNameValidationError("display_name_invalid")
    return normalized


def validate_password_policy(password: str, username_normalized: str | None = None) -> None:
    """Validate the #57 local-user password policy without returning secrets."""

    if not isinstance(password, str):
        raise PasswordPolicyError("password_policy")
    codepoints = len(password)
    if codepoints < PASSWORD_MIN_CODEPOINTS or codepoints > PASSWORD_MAX_CODEPOINTS:
        raise PasswordPolicyError("password_policy")
    try:
        encoded = password.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise PasswordPolicyError("password_policy") from exc
    if len(encoded) > BCRYPT_MAX_BYTES:
        raise PasswordPolicyError("password_policy")
    if username_normalized is not None:
        normalized_password = unicodedata.normalize("NFKC", password.strip()).casefold()
        if normalized_password == username_normalized:
            raise PasswordPolicyError("password_policy")
    if password in WEAK_PASSWORD_DENYLIST:
        raise PasswordPolicyError("password_policy")

    classes = 0
    classes += any(char.islower() for char in password)
    classes += any(char.isupper() for char in password)
    classes += any(char.isdigit() for char in password)
    classes += any(
        not char.islower() and not char.isupper() and not char.isdigit()
        for char in password
    )
    if classes < 3:
        raise PasswordPolicyError("password_policy")


class AdminUserCreateRequest(BaseModel):
    """Admin-only local user creation request.

    Business validation is performed by the service so API errors remain fixed
    and do not echo raw credentials or user-supplied identity values.
    """

    model_config = ConfigDict(extra="forbid")

    username: str
    display_name: str
    password: str
    is_admin: bool = False


class AdminUserPatchRequest(BaseModel):
    """Admin-only mutable user fields."""

    model_config = ConfigDict(extra="forbid")

    display_name: str


class AdminUserPasswordResetRequest(BaseModel):
    """Admin-only password reset request."""

    model_config = ConfigDict(extra="forbid")

    new_password: str


AdminUserSafeCode = Literal[
    "username_invalid",
    "username_taken",
    "display_name_invalid",
    "password_policy",
    "user_not_found",
    "self_disable_forbidden",
    "last_enabled_admin",
    "admin_required",
    "invalid_state",
    "unknown",
]

AdminUserAccessRole = Literal["owner", "editor", "viewer"]


class AdminUserProblem(BaseModel):
    safe_code: AdminUserSafeCode


class AdminUserAssignment(BaseModel):
    book_id: int
    book_name: str
    role: AdminUserAccessRole


class AdminUserDetail(BaseModel):
    id: int
    username: str
    display_name: str
    is_admin: bool
    is_enabled: bool
    assignment_count: int
    assignments: list[AdminUserAssignment]
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def _coerce_sqlite_datetime(cls, value: Any) -> Any:
        if isinstance(value, str) and value:
            return datetime.fromisoformat(value)
        return value


class AdminUserListResponse(BaseModel):
    items: list[AdminUserDetail]
    total_count: int
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
    has_next: bool


class AdminUserPasswordResetResponse(BaseModel):
    status: Literal["password_reset"] = "password_reset"
    subject_user_id: int
    session_invalidated: bool = True
