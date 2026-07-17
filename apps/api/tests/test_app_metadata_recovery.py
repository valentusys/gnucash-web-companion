"""Issue #58 safe app metadata recovery CLI tests."""

from __future__ import annotations

import builtins
import hashlib
import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

import app.models  # noqa: F401 - register SQLAlchemy metadata for synthetic DBs
from app.database import Base
from app.services import app_metadata_recovery as recovery
from app.services.app_metadata_schema import (
    APP_METADATA_TABLE_ALLOWLIST,
    CURRENT_APP_METADATA_SCHEMA_VERSION,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "app_metadata_recovery.py"


def _load_recovery_cli_module():
    spec = importlib.util.spec_from_file_location("app_metadata_recovery_cli", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module

PRIVATE_FRAGMENTS = (
    "leaky-user",
    "Leaky User",
    "Synthetic Private Book",
    "hash-secret-sentinel",
    "audit-secret-sentinel",
    "txn-guid-secret-sentinel",
    "synthetic-app-only-uri-sentinel",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _create_synthetic_app_db(
    path: Path,
    *,
    user_version: int = CURRENT_APP_METADATA_SCHEMA_VERSION,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    engine.dispose()
    with sqlite3.connect(path) as conn:
        conn.execute(f"pragma user_version = {user_version}")
        conn.execute(
            "insert into users "
            "(id, username, username_normalized, display_name, password_hash, "
            "is_admin, is_enabled, auth_version, created_at, updated_at) "
            "values (1, 'leaky-user', 'leaky-user', 'Leaky User', "
            "'hash-secret-sentinel', 1, 1, 7, "
            "'2026-01-01 00:00:00.000000', '2026-01-01 00:00:00.000000')"
        )
        conn.execute(
            "insert into books "
            "(id, name, storage_type, uri_or_path, canonical_path, canonical_path_hash, "
            "base_currency, is_default, is_archived, is_enabled, created_at, updated_at) "
            "values (10, 'Synthetic Private Book', 'sqlite', "
            "'synthetic-app-only-uri-sentinel', null, 'canonicalhashsentinel', "
            "'USD', 1, 0, 1, '2026-01-01 00:00:00.000000', "
            "'2026-01-01 00:00:00.000000')"
        )
        conn.execute(
            "insert into user_book_access (user_id, book_id, role) values (1, 10, 'owner')"
        )
        conn.execute(
            "insert into book_health_snapshots "
            "(book_id, source_status, open_status, accounts_status, transactions_status, "
            "reports_status, safe_code, checked_at, last_successful_at) "
            "values (10, 'ok', 'ok', 'ok', 'ok', 'ok', 'ok', "
            "'2026-01-01 00:00:00.000000', '2026-01-01 00:00:00.000000')"
        )
        conn.execute(
            "insert into audit_logs (id, user_id, book_id, action, payload_json, created_at) "
            "values (100, 1, 10, 'synthetic.audit', "
            "'{\"secret\":\"audit-secret-sentinel\"}', '2026-01-01 00:00:00.000000')"
        )
        conn.execute(
            "insert into write_alpha_transaction_ownership "
            "(id, book_id, transaction_id, created_by_user_id, created_by_write_alpha, "
            "created_at, last_mutated_at) "
            "values (1000, 10, 'txn-guid-secret-sentinel', 1, 1, "
            "'2026-01-01 00:00:00.000000', '2026-01-01 00:00:00.000000')"
        )
        conn.commit()


def _row_counts(path: Path) -> dict[str, int]:
    with sqlite3.connect(path) as conn:
        return {
            table_name: int(conn.execute(f"select count(*) from {table_name}").fetchone()[0])
            for table_name in APP_METADATA_TABLE_ALLOWLIST
        }


def _load_manifest(bundle: Path) -> dict[str, object]:
    return json.loads((bundle / recovery.MANIFEST_FILENAME).read_text(encoding="utf-8"))


def _write_manifest(bundle: Path, manifest: dict[str, object]) -> None:
    (bundle / recovery.MANIFEST_FILENAME).write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def test_backup_verify_restore_rehearsal_preserves_counts_redacts_and_source_hash(tmp_path):
    source = tmp_path / "source-app.db"
    bundle = tmp_path / "backup-bundle"
    restored = tmp_path / "restored-app.db"
    _create_synthetic_app_db(source)
    source_hash_before = _sha256(source)

    backup_result = recovery.backup_app_metadata(
        source_db=source,
        bundle_dir=bundle,
        runtime_stopped=True,
        repo_root=REPO_ROOT,
        timestamp="2026-07-16T00:00:00Z",
    )
    verify_result = recovery.verify_bundle(bundle_dir=bundle, repo_root=REPO_ROOT)
    second_verify = recovery.verify_bundle(bundle_dir=bundle, repo_root=REPO_ROOT)
    restore_result = recovery.restore_rehearsal(
        bundle_dir=bundle,
        destination_db=restored,
        repo_root=REPO_ROOT,
    )

    assert source_hash_before == _sha256(source)
    assert backup_result.status == verify_result.status == second_verify.status == "ok"
    assert restore_result.operation == "restore-rehearsal"
    assert restored.exists()
    assert _row_counts(restored) == {
        "users": 1,
        "books": 1,
        "user_book_access": 1,
        "book_health_snapshots": 1,
        "audit_logs": 1,
        "write_alpha_transaction_ownership": 1,
        "transaction_create_idempotency": 0,
    }
    assert backup_result.manifest == verify_result.manifest == second_verify.manifest
    manifest = backup_result.manifest
    assert set(manifest) == recovery.MANIFEST_KEYS
    assert manifest["app_schema_version"] == CURRENT_APP_METADATA_SCHEMA_VERSION
    assert manifest["tables"] == list(APP_METADATA_TABLE_ALLOWLIST)
    assert manifest["backup_method"] == recovery.BACKUP_METHOD
    assert manifest["runtime_mode"] == recovery.RUNTIME_MODE_STOPPED
    assert manifest["verification_status"] == "verified"
    manifest_text = json.dumps(manifest, ensure_ascii=False, sort_keys=True)
    for fragment in PRIVATE_FRAGMENTS + (str(source), str(restored), str(bundle)):
        assert fragment not in manifest_text
    if os.name == "posix":
        assert stat_mode(bundle) == 0o700
        assert stat_mode(bundle / recovery.BACKUP_DB_FILENAME) == 0o600
        assert stat_mode(bundle / recovery.MANIFEST_FILENAME) == 0o600


def stat_mode(path: Path) -> int:
    return path.stat().st_mode & 0o777


def test_backup_restore_preserve_existing_parent_modes_and_private_outputs(tmp_path):
    if os.name != "posix":
        pytest.skip("POSIX permission regression")

    source = tmp_path / "source-app.db"
    backup_parent = tmp_path / "operator-backups"
    restore_parent = tmp_path / "operator-restores"
    bundle = backup_parent / "backup-bundle"
    restored = restore_parent / "restored-app.db"
    _create_synthetic_app_db(source)
    backup_parent.mkdir()
    restore_parent.mkdir()
    os.chmod(backup_parent, 0o755)
    os.chmod(restore_parent, 0o755)
    backup_parent_mode_before = stat_mode(backup_parent)
    restore_parent_mode_before = stat_mode(restore_parent)

    backup_result = recovery.backup_app_metadata(
        source_db=source,
        bundle_dir=bundle,
        runtime_stopped=True,
        repo_root=REPO_ROOT,
        timestamp="2026-07-16T00:00:00Z",
    )
    restore_result = recovery.restore_rehearsal(
        bundle_dir=bundle,
        destination_db=restored,
        repo_root=REPO_ROOT,
    )

    assert backup_parent_mode_before == 0o755
    assert restore_parent_mode_before == 0o755
    assert stat_mode(backup_parent) == backup_parent_mode_before
    assert stat_mode(restore_parent) == restore_parent_mode_before
    assert stat_mode(bundle) == 0o700
    assert stat_mode(bundle / recovery.BACKUP_DB_FILENAME) == 0o600
    assert stat_mode(bundle / recovery.MANIFEST_FILENAME) == 0o600
    assert stat_mode(restored) == 0o600
    manifest_text = json.dumps(backup_result.manifest, ensure_ascii=False, sort_keys=True)
    for fragment in PRIVATE_FRAGMENTS + (str(source), str(restored), str(bundle)):
        assert fragment not in manifest_text
    assert restore_result.manifest == backup_result.manifest


def test_backup_restore_create_missing_parent_directories_private(tmp_path):
    if os.name != "posix":
        pytest.skip("POSIX permission regression")

    source = tmp_path / "source-app.db"
    backup_root = tmp_path / "missing-backups"
    backup_parent = backup_root / "nested"
    restore_root = tmp_path / "missing-restores"
    restore_parent = restore_root / "nested"
    bundle = backup_parent / "backup-bundle"
    restored = restore_parent / "restored-app.db"
    _create_synthetic_app_db(source)

    recovery.backup_app_metadata(
        source_db=source,
        bundle_dir=bundle,
        runtime_stopped=True,
        repo_root=REPO_ROOT,
        timestamp="2026-07-16T00:00:00Z",
    )
    recovery.restore_rehearsal(
        bundle_dir=bundle,
        destination_db=restored,
        repo_root=REPO_ROOT,
    )

    assert stat_mode(backup_root) == 0o700
    assert stat_mode(backup_parent) == 0o700
    assert stat_mode(restore_root) == 0o700
    assert stat_mode(restore_parent) == 0o700
    assert stat_mode(bundle) == 0o700
    assert stat_mode(bundle / recovery.BACKUP_DB_FILENAME) == 0o600
    assert stat_mode(bundle / recovery.MANIFEST_FILENAME) == 0o600
    assert stat_mode(restored) == 0o600


def test_backup_accepts_legacy_zero_user_version_only_for_exact_current_signature(tmp_path):
    source = tmp_path / "legacy-zero-current.db"
    _create_synthetic_app_db(source, user_version=0)

    result = recovery.backup_app_metadata(
        source_db=source,
        bundle_dir=tmp_path / "legacy-zero-bundle",
        runtime_stopped=True,
        repo_root=REPO_ROOT,
        timestamp="2026-07-16T00:00:00Z",
    )

    assert result.status == "ok"
    assert result.manifest["app_schema_version"] == CURRENT_APP_METADATA_SCHEMA_VERSION


def test_backup_requires_runtime_stopped_ack(tmp_path):
    source = tmp_path / "source-app.db"
    _create_synthetic_app_db(source)

    with pytest.raises(recovery.AppMetadataRecoveryError) as exc_info:
        recovery.backup_app_metadata(
            source_db=source,
            bundle_dir=tmp_path / "bundle",
            runtime_stopped=False,
            repo_root=REPO_ROOT,
        )

    assert exc_info.value.code == recovery.RUNTIME_ACK_MISSING
    assert exc_info.value.exit_code == recovery.ERROR_EXIT_CODES[recovery.RUNTIME_ACK_MISSING]


def test_required_safe_codes_have_stable_distinct_exit_codes():
    required_codes = (
        recovery.SOURCE_MISSING,
        recovery.SOURCE_NOT_REGULAR,
        recovery.RUNTIME_ACK_MISSING,
        recovery.DESTINATION_EXISTS,
        recovery.DESTINATION_INSIDE_REPO,
        recovery.PERMISSION_DENIED,
        recovery.SQLITE_INTEGRITY_FAIL,
        recovery.CHECKSUM_MISMATCH,
        recovery.UNSUPPORTED_SCHEMA,
        recovery.MANIFEST_INVALID,
        recovery.UNSAFE_RESTORE_DESTINATION,
        recovery.PARTIAL_CLEANUP_FAILURE,
    )

    assert set(required_codes).issubset(recovery.ERROR_EXIT_CODES)
    assert len({recovery.ERROR_EXIT_CODES[code] for code in required_codes}) == len(
        required_codes
    )
    for code in required_codes:
        assert recovery.AppMetadataRecoveryError(code).exit_code == recovery.ERROR_EXIT_CODES[code]


def test_backup_rejects_missing_directory_symlink_and_existing_or_repo_destinations(tmp_path):
    source = tmp_path / "source-app.db"
    _create_synthetic_app_db(source)

    with pytest.raises(recovery.AppMetadataRecoveryError) as missing:
        recovery.backup_app_metadata(
            source_db=tmp_path / "missing.db",
            bundle_dir=tmp_path / "missing-bundle",
            runtime_stopped=True,
            repo_root=REPO_ROOT,
        )
    assert missing.value.code == recovery.SOURCE_MISSING

    with pytest.raises(recovery.AppMetadataRecoveryError) as directory:
        recovery.backup_app_metadata(
            source_db=tmp_path,
            bundle_dir=tmp_path / "directory-bundle",
            runtime_stopped=True,
            repo_root=REPO_ROOT,
        )
    assert directory.value.code == recovery.SOURCE_NOT_REGULAR

    symlink = tmp_path / "source-link.db"
    symlink.symlink_to(source)
    with pytest.raises(recovery.AppMetadataRecoveryError) as symlink_error:
        recovery.backup_app_metadata(
            source_db=symlink,
            bundle_dir=tmp_path / "symlink-bundle",
            runtime_stopped=True,
            repo_root=REPO_ROOT,
        )
    assert symlink_error.value.code == recovery.SOURCE_NOT_REGULAR

    existing_bundle = tmp_path / "existing-bundle"
    existing_bundle.mkdir()
    with pytest.raises(recovery.AppMetadataRecoveryError) as exists:
        recovery.backup_app_metadata(
            source_db=source,
            bundle_dir=existing_bundle,
            runtime_stopped=True,
            repo_root=REPO_ROOT,
        )
    assert exists.value.code == recovery.DESTINATION_EXISTS

    with pytest.raises(recovery.AppMetadataRecoveryError) as repo_dest:
        recovery.backup_app_metadata(
            source_db=source,
            bundle_dir=REPO_ROOT / "recovery-bundle-must-not-be-created",
            runtime_stopped=True,
            repo_root=REPO_ROOT,
        )
    assert repo_dest.value.code == recovery.DESTINATION_INSIDE_REPO


def test_verify_detects_checksum_mismatch_manifest_extra_key_and_corrupt_db(tmp_path):
    source = tmp_path / "source-app.db"
    _create_synthetic_app_db(source)

    mismatch_bundle = tmp_path / "mismatch-bundle"
    recovery.backup_app_metadata(
        source_db=source,
        bundle_dir=mismatch_bundle,
        runtime_stopped=True,
        repo_root=REPO_ROOT,
    )
    with (mismatch_bundle / recovery.BACKUP_DB_FILENAME).open("ab") as handle:
        handle.write(b"tamper")
    with pytest.raises(recovery.AppMetadataRecoveryError) as checksum:
        recovery.verify_bundle(bundle_dir=mismatch_bundle, repo_root=REPO_ROOT)
    assert checksum.value.code == recovery.CHECKSUM_MISMATCH

    extra_key_bundle = tmp_path / "extra-key-bundle"
    recovery.backup_app_metadata(
        source_db=source,
        bundle_dir=extra_key_bundle,
        runtime_stopped=True,
        repo_root=REPO_ROOT,
    )
    manifest = _load_manifest(extra_key_bundle)
    manifest["source_path"] = "must-not-be-accepted"
    _write_manifest(extra_key_bundle, manifest)
    with pytest.raises(recovery.AppMetadataRecoveryError) as extra_key:
        recovery.verify_bundle(bundle_dir=extra_key_bundle, repo_root=REPO_ROOT)
    assert extra_key.value.code == recovery.MANIFEST_INVALID

    corrupt_bundle = tmp_path / "corrupt-bundle"
    recovery.backup_app_metadata(
        source_db=source,
        bundle_dir=corrupt_bundle,
        runtime_stopped=True,
        repo_root=REPO_ROOT,
    )
    corrupt_bytes = b"not a sqlite database"
    (corrupt_bundle / recovery.BACKUP_DB_FILENAME).write_bytes(corrupt_bytes)
    corrupt_manifest = _load_manifest(corrupt_bundle)
    corrupt_manifest["file_size_bytes"] = len(corrupt_bytes)
    corrupt_manifest["sha256"] = hashlib.sha256(corrupt_bytes).hexdigest()
    corrupt_manifest["sqlite_page_count"] = 1
    _write_manifest(corrupt_bundle, corrupt_manifest)
    with pytest.raises(recovery.AppMetadataRecoveryError) as corrupt:
        recovery.verify_bundle(bundle_dir=corrupt_bundle, repo_root=REPO_ROOT)
    assert corrupt.value.code == recovery.SQLITE_INTEGRITY_FAIL


def test_restore_rehearsal_rejects_existing_repo_relative_and_symlink_destinations(tmp_path):
    source = tmp_path / "source-app.db"
    bundle = tmp_path / "backup-bundle"
    _create_synthetic_app_db(source)
    recovery.backup_app_metadata(
        source_db=source,
        bundle_dir=bundle,
        runtime_stopped=True,
        repo_root=REPO_ROOT,
    )

    existing = tmp_path / "existing-restored.db"
    existing.write_bytes(b"")
    with pytest.raises(recovery.AppMetadataRecoveryError) as exists:
        recovery.restore_rehearsal(bundle_dir=bundle, destination_db=existing, repo_root=REPO_ROOT)
    assert exists.value.code == recovery.DESTINATION_EXISTS

    with pytest.raises(recovery.AppMetadataRecoveryError) as repo_dest:
        recovery.restore_rehearsal(
            bundle_dir=bundle,
            destination_db=REPO_ROOT / "restored-app-must-not-be-created.db",
            repo_root=REPO_ROOT,
        )
    assert repo_dest.value.code == recovery.DESTINATION_INSIDE_REPO

    with pytest.raises(recovery.AppMetadataRecoveryError) as relative_dest:
        recovery.restore_rehearsal(
            bundle_dir=bundle,
            destination_db=Path("relative-restored.db"),
            repo_root=REPO_ROOT,
        )
    assert relative_dest.value.code == recovery.UNSAFE_RESTORE_DESTINATION

    symlink = tmp_path / "dangling-restored-link.db"
    symlink.symlink_to(tmp_path / "missing-target.db")
    with pytest.raises(recovery.AppMetadataRecoveryError) as symlink_dest:
        recovery.restore_rehearsal(bundle_dir=bundle, destination_db=symlink, repo_root=REPO_ROOT)
    assert symlink_dest.value.code == recovery.UNSAFE_RESTORE_DESTINATION


def test_schema_mismatch_and_unsupported_user_version_are_rejected(tmp_path):
    newer = tmp_path / "newer.db"
    _create_synthetic_app_db(newer, user_version=CURRENT_APP_METADATA_SCHEMA_VERSION + 1)
    with pytest.raises(recovery.AppMetadataRecoveryError) as newer_error:
        recovery.backup_app_metadata(
            source_db=newer,
            bundle_dir=tmp_path / "newer-bundle",
            runtime_stopped=True,
            repo_root=REPO_ROOT,
        )
    assert newer_error.value.code == recovery.UNSUPPORTED_SCHEMA

    partial = tmp_path / "partial.db"
    _create_synthetic_app_db(partial, user_version=0)
    with sqlite3.connect(partial) as conn:
        conn.execute("drop table audit_logs")
        conn.commit()
    with pytest.raises(recovery.AppMetadataRecoveryError) as partial_error:
        recovery.backup_app_metadata(
            source_db=partial,
            bundle_dir=tmp_path / "partial-bundle",
            runtime_stopped=True,
            repo_root=REPO_ROOT,
        )
    assert partial_error.value.code == recovery.UNSUPPORTED_SCHEMA


def test_backup_cleans_partial_output_after_controlled_failure(tmp_path, monkeypatch):
    source = tmp_path / "source-app.db"
    bundle = tmp_path / "partial-bundle"
    _create_synthetic_app_db(source)

    def fail_write_json(*_args, **_kwargs):
        raise recovery.AppMetadataRecoveryError(recovery.MANIFEST_INVALID)

    monkeypatch.setattr(recovery, "_write_json_file", fail_write_json)
    with pytest.raises(recovery.AppMetadataRecoveryError) as exc_info:
        recovery.backup_app_metadata(
            source_db=source,
            bundle_dir=bundle,
            runtime_stopped=True,
            repo_root=REPO_ROOT,
        )

    assert exc_info.value.code == recovery.MANIFEST_INVALID
    assert not bundle.exists()
    assert not list(tmp_path.glob(".partial-bundle.tmp-*"))


def test_cli_help_and_json_errors_are_typed_and_redacted(tmp_path):
    help_result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert help_result.returncode == 0
    assert "backup" in help_result.stdout
    assert "verify" in help_result.stdout
    assert "restore-rehearsal" in help_result.stdout
    assert "upgrade-rehearsal" in help_result.stdout

    missing_source = tmp_path / "missing-private-app.db"
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--json",
            "backup",
            "--source",
            str(missing_source),
            "--bundle",
            str(tmp_path / "bundle"),
            "--runtime-stopped",
        ],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert proc.returncode == recovery.ERROR_EXIT_CODES[recovery.SOURCE_MISSING]
    payload = json.loads(proc.stderr)
    assert payload == {
        "exit_code": recovery.ERROR_EXIT_CODES[recovery.SOURCE_MISSING],
        "safe_code": recovery.SOURCE_MISSING,
        "status": "error",
    }
    assert str(missing_source) not in proc.stderr
    assert proc.stdout == ""


def test_cli_upgrade_rehearsal_delegates_to_synthetic_smoke(tmp_path, monkeypatch):
    cli = _load_recovery_cli_module()
    calls = []

    def fake_run(command, *, cwd, check):
        calls.append({"command": command, "cwd": cwd, "check": check})
        return subprocess.CompletedProcess(command, 23)

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    result = cli.main(
        [
            "upgrade-rehearsal",
            "--repo",
            str(REPO_ROOT),
            "--previous-ref",
            "v0.5.0-public-readonly-beta",
            "--current-ref",
            "HEAD",
            "--workdir",
            str(tmp_path),
            "--port",
            "18086",
            "--keep-workdir",
        ]
    )

    assert result == 23
    assert calls == [
        {
            "command": [
                "bash",
                str(REPO_ROOT / "scripts" / "smoke" / "synthetic-upgrade-smoke.sh"),
                "--repo",
                str(REPO_ROOT),
                "--previous-ref",
                "v0.5.0-public-readonly-beta",
                "--current-ref",
                "HEAD",
                "--workdir",
                str(tmp_path),
                "--port",
                "18086",
                "--keep-workdir",
            ],
            "cwd": REPO_ROOT,
            "check": False,
        }
    ]


def test_cli_upgrade_rehearsal_validates_port():
    cli = _load_recovery_cli_module()

    with pytest.raises(SystemExit) as exc_info:
        cli.build_parser().parse_args(
            [
                "upgrade-rehearsal",
                "--repo",
                str(REPO_ROOT),
                "--workdir",
                "/tmp/upgrade-smoke",
                "--port",
                "70000",
            ]
        )

    assert exc_info.value.code == 2


def test_recovery_paths_do_not_import_gnucash_helpers(tmp_path, monkeypatch):
    source = tmp_path / "source-app.db"
    bundle = tmp_path / "bundle"
    restored = tmp_path / "restored.db"
    _create_synthetic_app_db(source)

    original_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "piecash" or name.startswith("app.services.gnucash_book") or name.startswith(
            "app.services.book_preflight"
        ):
            raise AssertionError(f"forbidden recovery import: {name}")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    recovery.backup_app_metadata(
        source_db=source,
        bundle_dir=bundle,
        runtime_stopped=True,
        repo_root=REPO_ROOT,
    )
    recovery.verify_bundle(bundle_dir=bundle, repo_root=REPO_ROOT)
    recovery.restore_rehearsal(bundle_dir=bundle, destination_db=restored, repo_root=REPO_ROOT)


def test_migration_sets_positive_user_version_after_current_schema(tmp_path):
    from app.config import Settings
    from app.services.metadata_migrations import run_app_metadata_migrations

    db_path = tmp_path / "migration-app.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    settings = Settings(
        app_env="test",
        app_database_url=f"sqlite:///{db_path}",
        gnucash_book_allowed_roots=[str(tmp_path)],
        jwt_secret="test-secret-key-for-recovery-migration-32-bytes",
        app_admin_username="admin",
        app_admin_password="ValidPass123!",
    )

    run_app_metadata_migrations(engine, settings)
    run_app_metadata_migrations(engine, settings)

    with engine.connect() as conn:
        user_version = conn.execute(text("pragma user_version")).scalar_one()
    assert user_version == CURRENT_APP_METADATA_SCHEMA_VERSION
