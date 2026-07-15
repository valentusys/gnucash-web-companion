"""Issue #57 B3 local admin recovery CLI tests."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Query, Session as SQLAlchemySession, sessionmaker

from app.config import get_settings
from app.database import Base
from app.models import AuditLog, User
from app.services.auth import create_access_token, hash_password, verify_password

ADMIN_PASSWORD = "AdminPass123!"
RECOVERY_PASSWORD = "RecoveredPass123!"
JWT_SECRET = "test-secret-key-for-admin-recovery-issue57-32-bytes"
RAW_SENTINEL = "RAW_RECOVERY_SENTINEL"
FIXED_FAILURE_FORBIDDEN_OUTPUT = (
    RAW_SENTINEL,
    "Traceback",
    "RuntimeError",
    "argparse",
    "sqlite://",
    "APP_DATABASE_URL",
    JWT_SECRET,
    ADMIN_PASSWORD,
    RECOVERY_PASSWORD,
    "password_hash",
)


@pytest.fixture
def recovery_db(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "recovery-app.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        session.add_all(
            [
                User(
                    username="admin",
                    display_name="Admin",
                    password_hash=hash_password(ADMIN_PASSWORD),
                    is_admin=True,
                    is_enabled=False,
                    auth_version=1,
                ),
                User(
                    username="viewer",
                    display_name="Viewer",
                    password_hash=hash_password("ViewerPass123!"),
                    is_admin=False,
                    is_enabled=False,
                    auth_version=1,
                ),
            ]
        )
        session.commit()
    monkeypatch.setenv("APP_DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("JWT_SECRET", JWT_SECRET)
    get_settings.cache_clear()
    try:
        yield Session
    finally:
        get_settings.cache_clear()
        engine.dispose()


def _run_cli(argv: list[str], stdin_text: str = "") -> tuple[int, str, str]:
    from app import admin_recovery

    stdout = io.StringIO()
    stderr = io.StringIO()
    code = admin_recovery.main(
        argv,
        stdin=io.StringIO(stdin_text),
        stdout=stdout,
        stderr=stderr,
    )
    return code, stdout.getvalue(), stderr.getvalue()


def _fail_with_raw_sentinel(*_args, **_kwargs):
    raise RuntimeError(RAW_SENTINEL)


def _assert_fixed_failure(
    result: tuple[int, str, str],
    expected_stderr: str,
) -> None:
    code, stdout, stderr = result
    assert code == 1
    assert stdout == ""
    assert stderr == f"{expected_stderr}\n"
    combined_output = stdout + stderr
    for forbidden in FIXED_FAILURE_FORBIDDEN_OUTPUT:
        assert forbidden not in combined_output


def _assert_admin_unchanged_and_unaudited(recovery_db) -> None:
    with recovery_db() as session:
        admin = session.query(User).filter(User.username == "admin").one()
        assert admin.is_enabled is False
        assert admin.auth_version == 1
        assert verify_password(ADMIN_PASSWORD, admin.password_hash)
        assert not verify_password(RECOVERY_PASSWORD, admin.password_hash)
        assert session.query(AuditLog).count() == 0


def test_recovery_cli_enables_existing_admin_resets_password_and_invalidates_old_token(
    recovery_db,
):
    with recovery_db() as session:
        admin = session.query(User).filter(User.username == "admin").one()
        old_token = create_access_token(
            data={"sub": str(admin.id), "av": int(admin.auth_version)},
            secret=JWT_SECRET,
            expire_minutes=30,
        )

    code, stdout, stderr = _run_cli(
        ["--username", " ADMIN ", "--enable", "--reset-password-stdin"],
        f"{RECOVERY_PASSWORD}\n{RECOVERY_PASSWORD}\n",
    )

    assert code == 0
    assert stdout.strip() == "OK: recovery operation completed."
    assert stderr == ""
    combined_output = stdout + stderr
    assert RECOVERY_PASSWORD not in combined_output
    assert ADMIN_PASSWORD not in combined_output
    assert "ADMIN" not in combined_output
    assert "password_hash" not in combined_output

    with recovery_db() as session:
        admin = session.query(User).filter(User.username == "admin").one()
        assert admin.is_enabled is True
        assert admin.auth_version == 2
        assert verify_password(RECOVERY_PASSWORD, admin.password_hash)
        assert not verify_password(ADMIN_PASSWORD, admin.password_hash)
        token_payload = create_access_token(
            data={"sub": str(admin.id), "av": int(admin.auth_version)},
            secret=JWT_SECRET,
            expire_minutes=30,
        )
        assert token_payload != old_token
        audits = session.query(AuditLog).order_by(AuditLog.id).all()
        assert [row.action for row in audits] == ["user_enabled", "password_reset"]
        for row in audits:
            payload = json.loads(row.payload_json or "{}")
            assert set(payload).issubset(
                {"subject_user_id", "changed_fields", "result", "recovery"}
            )
            assert payload["subject_user_id"] == admin.id
            assert payload["recovery"] == "local_cli"
            payload_text = json.dumps(payload)
            assert RECOVERY_PASSWORD not in payload_text
            assert ADMIN_PASSWORD not in payload_text
            assert "password_hash" not in payload_text


def test_recovery_cli_rejects_non_admin_and_does_not_enable_or_audit(recovery_db):
    code, stdout, stderr = _run_cli(
        ["--username", "viewer", "--enable", "--reset-password-stdin"],
        f"{RECOVERY_PASSWORD}\n{RECOVERY_PASSWORD}\n",
    )

    assert code == 1
    assert stdout == ""
    assert stderr.strip() == "ERROR: admin user not found."
    assert "viewer" not in stderr
    assert RECOVERY_PASSWORD not in stderr
    with recovery_db() as session:
        viewer = session.query(User).filter(User.username == "viewer").one()
        assert viewer.is_enabled is False
        assert not verify_password(RECOVERY_PASSWORD, viewer.password_hash)
        assert session.query(AuditLog).count() == 0


def test_recovery_cli_stdin_preserves_spaces_and_only_strips_line_endings(recovery_db):
    spaced_password = " RecoveredPass123! "

    code, stdout, stderr = _run_cli(
        ["--username", "admin", "--reset-password-stdin"],
        f"{spaced_password}\r\n{spaced_password}\n",
    )

    assert code == 0
    assert stdout.strip() == "OK: recovery operation completed."
    assert stderr == ""
    assert spaced_password not in stdout + stderr
    with recovery_db() as session:
        admin = session.query(User).filter(User.username == "admin").one()
        assert verify_password(spaced_password, admin.password_hash)
        assert not verify_password(spaced_password.strip(), admin.password_hash)
        assert admin.auth_version == 2


def test_recovery_cli_rejects_mismatched_or_policy_invalid_stdin_without_secret_echo(
    recovery_db,
):
    mismatch = _run_cli(
        ["--username", "admin", "--reset-password-stdin"],
        "RecoveredPass123!\nDifferentPass123!\n",
    )
    weak = _run_cli(
        ["--username", "admin", "--reset-password-stdin"],
        "Password1234\nPassword1234\n",
    )

    for code, stdout, stderr in (mismatch, weak):
        assert code == 1
        assert stdout == ""
        assert stderr.strip() == "ERROR: password input invalid."
        assert "RecoveredPass123!" not in stderr
        assert "DifferentPass123!" not in stderr
        assert "Password1234" not in stderr

    with recovery_db() as session:
        admin = session.query(User).filter(User.username == "admin").one()
        assert admin.is_enabled is False
        assert admin.auth_version == 1
        assert verify_password(ADMIN_PASSWORD, admin.password_hash)
        assert session.query(AuditLog).count() == 0


def test_recovery_cli_requires_an_operation_and_never_accepts_password_argv(recovery_db):
    no_operation = _run_cli(["--username", "admin"])
    unsafe_arg = _run_cli(["--username", "admin", "--password", RECOVERY_PASSWORD])

    assert no_operation[0] == 1
    assert no_operation[2].strip() == "ERROR: no recovery operation requested."
    assert unsafe_arg[0] == 1
    assert unsafe_arg[2].strip() == "ERROR: unsupported recovery arguments."
    assert RECOVERY_PASSWORD not in unsafe_arg[1] + unsafe_arg[2]


def test_recovery_cli_malformed_parser_input_is_fixed_and_silent(recovery_db):
    _assert_fixed_failure(
        _run_cli(["--username"]),
        "ERROR: username is required.",
    )
    _assert_fixed_failure(
        _run_cli(["--username", "--enable"]),
        "ERROR: username is required.",
    )
    _assert_fixed_failure(
        _run_cli(["--username", "admin", "--enable", RAW_SENTINEL]),
        "ERROR: unsupported recovery arguments.",
    )


@pytest.mark.parametrize(
    "target",
    [
        "get_settings",
        "get_engine",
        "run_app_metadata_migrations",
        "get_session_factory",
    ],
)
def test_recovery_cli_setup_failures_are_fixed_and_redacted(
    recovery_db,
    monkeypatch,
    target: str,
):
    from app import admin_recovery

    monkeypatch.setattr(admin_recovery, target, _fail_with_raw_sentinel)

    _assert_fixed_failure(
        _run_cli(["--username", "admin", "--enable"]),
        "ERROR: recovery operation failed.",
    )
    _assert_admin_unchanged_and_unaudited(recovery_db)


def test_recovery_cli_session_open_failure_is_fixed_and_redacted(
    recovery_db,
    monkeypatch,
):
    from app import admin_recovery

    class BrokenSessionFactory:
        def __call__(self):
            raise RuntimeError(RAW_SENTINEL)

    monkeypatch.setattr(
        admin_recovery,
        "get_session_factory",
        lambda _engine: BrokenSessionFactory(),
    )

    _assert_fixed_failure(
        _run_cli(["--username", "admin", "--enable"]),
        "ERROR: recovery operation failed.",
    )
    _assert_admin_unchanged_and_unaudited(recovery_db)


def test_recovery_cli_admin_lookup_failure_is_fixed_and_redacted(
    recovery_db,
    monkeypatch,
):
    from app import admin_recovery

    monkeypatch.setattr(admin_recovery, "_load_existing_admin", _fail_with_raw_sentinel)

    _assert_fixed_failure(
        _run_cli(["--username", "admin", "--enable"]),
        "ERROR: recovery operation failed.",
    )
    _assert_admin_unchanged_and_unaudited(recovery_db)


def test_recovery_cli_password_input_failures_are_fixed_and_redacted(
    recovery_db,
    monkeypatch,
):
    from app import admin_recovery

    _assert_fixed_failure(
        _run_cli(["--username", "admin", "--reset-password-stdin"], "OnlyOneLine\n"),
        "ERROR: password input invalid.",
    )
    _assert_fixed_failure(
        _run_cli(
            ["--username", "admin", "--reset-password-stdin"],
            "Password1234\nPassword1234\n",
        ),
        "ERROR: password input invalid.",
    )

    def fail_getpass(*_args, **_kwargs):
        raise EOFError(RAW_SENTINEL)

    monkeypatch.setattr(admin_recovery.getpass, "getpass", fail_getpass)
    _assert_fixed_failure(
        _run_cli(["--username", "admin", "--reset-password-tty"]),
        "ERROR: password input invalid.",
    )

    monkeypatch.setattr(admin_recovery.getpass, "getpass", _fail_with_raw_sentinel)
    _assert_fixed_failure(
        _run_cli(["--username", "admin", "--reset-password-tty"]),
        "ERROR: password input invalid.",
    )
    _assert_admin_unchanged_and_unaudited(recovery_db)


def test_recovery_cli_hash_failure_is_fixed_redacted_and_does_not_mutate(
    recovery_db,
    monkeypatch,
):
    from app import admin_recovery

    monkeypatch.setattr(admin_recovery, "hash_password", _fail_with_raw_sentinel)

    _assert_fixed_failure(
        _run_cli(
            ["--username", "admin", "--reset-password-stdin"],
            f"{RECOVERY_PASSWORD}\n{RECOVERY_PASSWORD}\n",
        ),
        "ERROR: recovery operation failed.",
    )
    _assert_admin_unchanged_and_unaudited(recovery_db)


@pytest.mark.parametrize("failure_point", ["begin", "query", "flush", "commit"])
def test_recovery_cli_transaction_failures_rollback_and_redact(
    recovery_db,
    monkeypatch,
    failure_point: str,
):
    from app import admin_recovery

    if failure_point == "begin":
        monkeypatch.setattr(admin_recovery, "_begin_immediate", _fail_with_raw_sentinel)
    elif failure_point == "query":
        original_first = Query.first
        calls = 0

        def fail_second_query_first(self):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError(RAW_SENTINEL)
            return original_first(self)

        monkeypatch.setattr(Query, "first", fail_second_query_first)
    elif failure_point == "flush":
        original_flush = SQLAlchemySession.flush

        def fail_mutating_flush(self, *args, **kwargs):
            if self.new or self.dirty or self.deleted:
                raise RuntimeError(RAW_SENTINEL)
            return original_flush(self, *args, **kwargs)

        monkeypatch.setattr(SQLAlchemySession, "flush", fail_mutating_flush)
    else:
        monkeypatch.setattr(SQLAlchemySession, "commit", _fail_with_raw_sentinel)

    _assert_fixed_failure(
        _run_cli(["--username", "admin", "--enable"]),
        "ERROR: recovery operation failed.",
    )
    _assert_admin_unchanged_and_unaudited(recovery_db)
