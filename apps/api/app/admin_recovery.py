"""Local app-metadata admin recovery CLI.

This module intentionally touches only the app metadata database. It never reads,
opens, probes, or mutates any GnuCash source.
"""

from __future__ import annotations

import argparse
import getpass
import json
import sys
from collections.abc import Sequence
from typing import TextIO

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_engine, get_session_factory
from app.models import AuditLog, User
from app.schemas.users import (
    PasswordPolicyError,
    UsernameValidationError,
    normalize_username,
    validate_password_policy,
)
from app.services.auth import hash_password
from app.services.metadata_migrations import run_app_metadata_migrations

SUCCESS_MESSAGE = "OK: recovery operation completed."
ERR_UNSUPPORTED_ARGS = "ERROR: unsupported recovery arguments."
ERR_MISSING_USERNAME = "ERROR: username is required."
ERR_NO_OPERATION = "ERROR: no recovery operation requested."
ERR_ADMIN_NOT_FOUND = "ERROR: admin user not found."
ERR_PASSWORD_INPUT = "ERROR: password input invalid."
ERR_RECOVERY_FAILED = "ERROR: recovery operation failed."


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--username")
    parser.add_argument("--enable", action="store_true")
    parser.add_argument("--reset-password-stdin", action="store_true")
    parser.add_argument("--reset-password-tty", action="store_true")
    parser.add_argument("--help", action="store_true")
    return parser


def _write_error(stderr: TextIO, message: str) -> int:
    print(message, file=stderr)
    return 1


def _read_password_stdin(stdin: TextIO) -> str:
    first = stdin.readline()
    second = stdin.readline()
    if first == "" or second == "":
        raise PasswordPolicyError("password_policy")
    password = first.rstrip("\r\n")
    confirmation = second.rstrip("\r\n")
    if password != confirmation:
        raise PasswordPolicyError("password_policy")
    return password


def _read_password_tty(stderr: TextIO) -> str:
    password = getpass.getpass("New password: ", stream=stderr)
    confirmation = getpass.getpass("Repeat new password: ", stream=stderr)
    if password != confirmation:
        raise PasswordPolicyError("password_policy")
    return password


def _begin_immediate(session: Session) -> None:
    bind = session.get_bind()
    if session.in_transaction():
        session.rollback()
    if bind.dialect.name == "sqlite":
        session.execute(text("BEGIN IMMEDIATE"))
    else:
        session.begin()


def _audit_recovery(
    session: Session,
    *,
    subject_user_id: int,
    action: str,
    changed_fields: list[str],
    result: str,
) -> None:
    payload = {
        "subject_user_id": int(subject_user_id),
        "changed_fields": list(changed_fields),
        "result": result,
        "recovery": "local_cli",
    }
    session.add(
        AuditLog(
            user_id=int(subject_user_id),
            book_id=None,
            action=action,
            payload_json=json.dumps(payload, sort_keys=True, separators=(",", ":")),
        )
    )


def _load_existing_admin(session: Session, username: str) -> User | None:
    try:
        username_normalized = normalize_username(username)
    except UsernameValidationError:
        return None
    return (
        session.query(User)
        .filter(User.username_normalized == username_normalized, User.is_admin.is_(True))
        .first()
    )


def main(
    argv: Sequence[str] | None = None,
    *,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run the recovery CLI and return a process exit code."""

    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    args, unknown = _parser().parse_known_args(list(argv) if argv is not None else None)
    if args.help:
        print(
            "usage: python -m app.admin_recovery --username <admin> [--enable] "
            "[--reset-password-stdin|--reset-password-tty]",
            file=stdout,
        )
        return 0
    if unknown:
        return _write_error(stderr, ERR_UNSUPPORTED_ARGS)
    if args.reset_password_stdin and args.reset_password_tty:
        return _write_error(stderr, ERR_UNSUPPORTED_ARGS)
    if not args.username:
        return _write_error(stderr, ERR_MISSING_USERNAME)
    if not args.enable and not args.reset_password_stdin and not args.reset_password_tty:
        return _write_error(stderr, ERR_NO_OPERATION)

    settings = get_settings()
    engine = get_engine()
    run_app_metadata_migrations(engine, settings)
    SessionLocal = get_session_factory(engine)

    with SessionLocal() as session:
        user = _load_existing_admin(session, args.username)
        if user is None:
            return _write_error(stderr, ERR_ADMIN_NOT_FOUND)
        subject_user_id = int(user.id)
        username_normalized = str(user.username_normalized)

        password_hash: str | None = None
        if args.reset_password_stdin or args.reset_password_tty:
            try:
                password = (
                    _read_password_stdin(stdin)
                    if args.reset_password_stdin
                    else _read_password_tty(stderr)
                )
                validate_password_policy(password, username_normalized)
                password_hash = hash_password(password)
            except PasswordPolicyError:
                return _write_error(stderr, ERR_PASSWORD_INPUT)

        _begin_immediate(session)
        try:
            user = (
                session.query(User)
                .filter(User.id == subject_user_id, User.is_admin.is_(True))
                .first()
            )
            if user is None:
                session.rollback()
                return _write_error(stderr, ERR_ADMIN_NOT_FOUND)
            if args.enable and not bool(user.is_enabled):
                user.is_enabled = True
                _audit_recovery(
                    session,
                    subject_user_id=subject_user_id,
                    action="user_enabled",
                    changed_fields=["status"],
                    result="enabled",
                )
            if password_hash is not None:
                user.password_hash = password_hash
                user.auth_version = int(user.auth_version) + 1
                _audit_recovery(
                    session,
                    subject_user_id=subject_user_id,
                    action="password_reset",
                    changed_fields=["credentials", "session_version"],
                    result="reset",
                )
            session.flush()
            session.commit()
        except Exception:
            session.rollback()
            return _write_error(stderr, ERR_RECOVERY_FAILED)

    print(SUCCESS_MESSAGE, file=stdout)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
