"""Authentication service: password hashing, JWT, and admin seeding."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import User

logger = logging.getLogger(__name__)

JWT_ALGORITHM = "HS256"
INSECURE_JWT_SECRET_VALUES = {
    "",
    "change-me",
    "change-me-use-a-long-random-secret",
}


class AuthConfigurationError(RuntimeError):
    """Raised when authentication is not safely configured."""


def require_configured_jwt_secret(secret: str) -> str:
    """Return a usable JWT secret or raise a controlled configuration error."""
    normalized = secret.strip()
    if normalized in INSECURE_JWT_SECRET_VALUES:
        raise AuthConfigurationError(
            "JWT_SECRET is not configured. Set a long random JWT_SECRET before logging in."
        )
    return normalized


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        return False


def create_access_token(
    data: dict[str, Any],
    secret: str,
    expire_minutes: int,
) -> str:
    """Create a signed JWT access token."""
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload = data.copy()
    payload.update({"exp": expires_at})
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str, secret: str) -> dict[str, Any] | None:
    """Decode a JWT access token or return None if invalid/expired."""
    try:
        return jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
    except InvalidTokenError:
        return None


def authenticate_user(session: Session, username: str, password: str) -> User | None:
    """Return a user when credentials are valid."""
    user = session.query(User).filter(User.username == username).first()
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def seed_admin_user(session: Session) -> User | None:
    """Seed one admin user when the users table is empty.

    APP_ADMIN_PASSWORD_HASH is preferred. APP_ADMIN_PASSWORD is accepted only as
    a bootstrap convenience and is hashed before storage.
    """
    settings = get_settings()

    if session.query(User).first() is not None:
        return None

    username = settings.app_admin_username.strip() or "admin"

    if settings.app_admin_password_hash:
        password_hash = settings.app_admin_password_hash
        logger.info("Seeding admin user '%s' from APP_ADMIN_PASSWORD_HASH", username)
    elif settings.app_admin_password:
        password_hash = hash_password(settings.app_admin_password)
        logger.warning(
            "Seeding admin user '%s' from plaintext APP_ADMIN_PASSWORD; "
            "prefer APP_ADMIN_PASSWORD_HASH in production",
            username,
        )
    else:
        logger.warning(
            "No admin credentials configured; skipping admin seed. "
            "Set APP_ADMIN_PASSWORD_HASH or APP_ADMIN_PASSWORD."
        )
        return None

    user = User(
        username=username,
        display_name="Admin",
        password_hash=password_hash,
        is_admin=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    logger.info("Admin user '%s' seeded (id=%d)", username, user.id)
    return user
