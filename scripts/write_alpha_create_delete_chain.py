#!/usr/bin/env python3
"""Run a safe write-alpha CREATE-to-DELETE chain on a copied GnuCash book.

The runner uses the FastAPI write-alpha routes against a temporary app metadata
SQLite DB outside git:

1. bootstrap admin + copied-book metadata;
2. enable write-alpha only with APP_ENV=test;
3. POST /books/{id}/transactions to create one disposable transaction;
4. verify app ownership metadata;
5. DELETE /books/{id}/transactions/{tx_id} for the same transaction;
6. verify read-back absence, backup restore, audit summary, and disabled reset.

Artifacts written by --work-dir/--evidence-dir are operator evidence only and
must not be committed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DISPOSABLE_TARGET_HINTS = frozenset(
    {
        "copy",
        "copied",
        "disposable",
        "dogfood",
        "scratch",
        "synthetic",
        "test",
        "tmp",
    }
)
FORBIDDEN_TARGET_HINTS = frozenset(
    {
        "only copy",
        "only-copy",
        "only_copy",
        "original",
        "private",
        "sole copy",
        "sole-copy",
        "sole_copy",
        "syncthing",
        "working",
    }
)
sys.path.insert(0, str(REPO_ROOT / "apps" / "api"))

import piecash  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.config import Settings, get_settings  # noqa: E402
from app.database import Base  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Book, User, UserBookAccess, WriteAlphaTransactionOwnership  # noqa: E402
from app.routers.auth import get_db  # noqa: E402
from app.services.auth import hash_password  # noqa: E402


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_inside_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT)
        return True
    except ValueError:
        return False


def _is_inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _git_ignored(path: Path, *, repo_root: Path) -> bool:
    try:
        relative = path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    try:
        result = subprocess.run(
            ["git", "check-ignore", "--quiet", "--", str(relative)],
            cwd=repo_root,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return False
    return result.returncode == 0


def classify_runtime_artifact_dir(path: Path, *, repo_root: Path = REPO_ROOT) -> str:
    """Classify where disposable drill work/evidence artifacts would be written."""

    resolved_repo = repo_root.resolve()
    resolved_path = path.expanduser().resolve()
    if not _is_inside(resolved_path, resolved_repo):
        return "external"
    if _git_ignored(resolved_path, repo_root=resolved_repo):
        return "ignored"
    return "unsafe"


def ensure_safe_runtime_artifact_dir(path: Path, label: str, *, repo_root: Path = REPO_ROOT) -> str:
    """Fail closed before writing any work/evidence artifact to a tracked repo path."""

    location_class = classify_runtime_artifact_dir(path, repo_root=repo_root)
    if location_class == "unsafe":
        raise RuntimeError(f"{label} must be outside git working tree or git-ignored runtime storage")
    return location_class


def opaque(value: str, n: int = 12) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:n]


def disposable_target_blocker(path: Path) -> str | None:
    """Return a path-safe blocker unless a target is explicitly disposable-like."""

    marker_text = path.name.lower()
    context_text = " ".join(part.lower() for part in path.parts)
    if any(marker in context_text for marker in FORBIDDEN_TARGET_HINTS):
        return (
            "book filename contains forbidden "
            "owner/private/original/working/Syncthing/only-copy marker"
        )
    if not any(marker in marker_text for marker in DISPOSABLE_TARGET_HINTS):
        return "book filename must mark it as copied/disposable/synthetic test data"
    return None


def ensure_disposable_target_path(path: Path) -> None:
    """Fail closed before any piecash open/read when the target is not disposable-like."""

    blocker = disposable_target_blocker(path)
    if blocker is not None:
        raise RuntimeError(blocker)


def pick_two_accounts(book_path: Path) -> tuple[str, str, str]:
    book = piecash.open_book(str(book_path), readonly=True)
    try:
        by_currency: dict[str, list[Any]] = {}
        for acc in book.accounts:
            if getattr(acc, "placeholder", False):
                continue
            commodity = getattr(acc, "commodity", None)
            guid = getattr(acc, "guid", None)
            if commodity is None or not guid:
                continue
            currency = str(getattr(commodity, "mnemonic", ""))
            if len(currency) == 3 and currency.isalpha():
                by_currency.setdefault(currency.upper(), []).append(acc)
        for currency, accounts in by_currency.items():
            if len(accounts) >= 2:
                return accounts[0].guid, accounts[1].guid, currency
    finally:
        close = getattr(book, "close", None)
        if callable(close):
            close()
    raise RuntimeError("no two postable accounts in the same currency")


def transaction_exists(book_path: Path, tx_id: str) -> bool:
    book = piecash.open_book(str(book_path), readonly=True)
    try:
        return any(getattr(tx, "guid", None) == tx_id for tx in book.transactions)
    finally:
        close = getattr(book, "close", None)
        if callable(close):
            close()


def read_counts(book_path: Path) -> dict[str, int]:
    book = piecash.open_book(str(book_path), readonly=True)
    try:
        return {
            "account_count": len(list(book.accounts)),
            "transaction_count": len(list(book.transactions)),
            "commodity_count": len(list(book.commodities)),
        }
    finally:
        close = getattr(book, "close", None)
        if callable(close):
            close()


def configure_app(db_path: Path, book_path: Path, writes_enabled: bool):
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    settings = Settings(
        app_env="test",
        app_database_url=f"sqlite:///{db_path}",
        gnucash_default_book_path=str(book_path),
        jwt_secret="test-secret-key-for-write-alpha-dogfood-32-bytes",
        jwt_token_expire_minutes=30,
        app_admin_username="admin",
        app_admin_password="testpassword123",
        gnucash_writes_enabled=writes_enabled,
    )

    def override_get_db():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db] = override_get_db
    get_settings.cache_clear()
    return engine, SessionLocal


def bootstrap_metadata(session_factory, book_path: Path) -> int:
    with session_factory() as session:
        user = session.query(User).filter(User.username == "admin").one_or_none()
        if user is None:
            user = User(
                username="admin",
                display_name="Admin",
                password_hash=hash_password("testpassword123"),
                is_admin=True,
            )
            session.add(user)
            session.flush()
        book = Book(
            name="copied-restorable-write-alpha-dogfood",
            storage_type="sqlite",
            uri_or_path=str(book_path),
            base_currency=None,
            is_default=True,
        )
        session.add(book)
        session.flush()
        session.add(UserBookAccess(user_id=user.id, book_id=book.id, role="owner"))
        session.commit()
        return int(book.id)


def login(client: TestClient) -> dict[str, str]:
    response = client.post("/auth/login", json={"username": "admin", "password": "testpassword123"})
    if response.status_code != 200:
        raise RuntimeError(f"login failed: {response.status_code}")
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def run(book_path: Path, work_dir: Path, evidence_dir: Path) -> dict[str, Any]:
    if not book_path.is_file():
        raise RuntimeError("book file missing")
    if is_inside_repo(book_path):
        raise RuntimeError("book must be outside git working tree")
    ensure_disposable_target_path(book_path)
    work_dir_class = ensure_safe_runtime_artifact_dir(work_dir, "work-dir")
    evidence_dir_class = ensure_safe_runtime_artifact_dir(evidence_dir, "evidence-dir")

    work_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    app_db = work_dir / "app-metadata.sqlite"
    if app_db.exists():
        app_db.unlink()

    before = sha256(book_path)
    account_a, account_b, currency = pick_two_accounts(book_path)
    before_counts = read_counts(book_path)

    engine, session_factory = configure_app(app_db, book_path, writes_enabled=True)
    try:
        book_id = bootstrap_metadata(session_factory, book_path)
        client = TestClient(app)
        headers = login(client)

        payload = {
            "date": "2026-05-25",
            "description": "Write-alpha CREATE-to-DELETE disposable test transaction",
            "splits": [
                {"account_id": account_a, "amount": "-1", "currency": currency, "memo": ""},
                {"account_id": account_b, "amount": "1", "currency": currency, "memo": ""},
            ],
        }
        create_response = client.post(f"/books/{book_id}/transactions", json=payload, headers=headers)
        if create_response.status_code != 201:
            raise RuntimeError(f"create failed: {create_response.status_code} {create_response.text[:200]}")
        create_json = create_response.json()
        tx_id = create_json["transaction_id"]
        create_backup = Path(create_json["backup_path"])

        with session_factory() as session:
            ownership_count = session.query(WriteAlphaTransactionOwnership).filter(
                WriteAlphaTransactionOwnership.book_id == book_id,
                WriteAlphaTransactionOwnership.transaction_id == tx_id,
                WriteAlphaTransactionOwnership.created_by_write_alpha == True,  # noqa: E712
            ).count()
        if ownership_count != 1:
            raise RuntimeError("ownership metadata was not recorded exactly once")
        if not transaction_exists(book_path, tx_id):
            raise RuntimeError("created transaction missing before delete")

        pre_delete_sha = sha256(book_path)
        delete_response = client.delete(f"/books/{book_id}/transactions/{tx_id}", headers=headers)
        if delete_response.status_code != 200:
            raise RuntimeError(f"delete failed: {delete_response.status_code} {delete_response.text[:200]}")
        delete_json = delete_response.json()
        delete_backup = Path(delete_json["backup_path"])
        after = sha256(book_path)
        absent = not transaction_exists(book_path, tx_id)
        if not absent:
            raise RuntimeError("deleted transaction still present")

        audit_response = client.get(f"/books/{book_id}/write-alpha-audit-summary", headers=headers)
        if audit_response.status_code != 200:
            raise RuntimeError(f"audit summary failed: {audit_response.status_code}")
        audit_json = audit_response.json()
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()
        engine.dispose()

    restore_target = work_dir / "restore-from-pre-delete.gnucash.sqlite"
    shutil.copy2(delete_backup, restore_target)
    restore_present = transaction_exists(restore_target, tx_id)
    restored_sha_matches = sha256(restore_target) == sha256(delete_backup)
    compat_counts = read_counts(book_path)

    # Reset/disabled probe: same metadata DB, writes disabled, DELETE must be forbidden.
    engine, session_factory = configure_app(app_db, book_path, writes_enabled=False)
    try:
        client = TestClient(app)
        headers = login(client)
        disabled_response = client.delete(f"/books/{book_id}/transactions/{tx_id}", headers=headers)
        disabled_status = disabled_response.status_code
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()
        engine.dispose()

    evidence = {
        "result": "pass",
        "scenario_type": "copied-book-write-alpha-create-to-delete-chain",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "book_outside_git": True,
        "runtime_artifacts": {
            "work_dir_class": work_dir_class,
            "evidence_dir_class": evidence_dir_class,
            "tracked_artifacts_prevented": True,
            "raw_paths_redacted": True,
        },
        "book_sha_before_prefix": before[:12],
        "book_sha_pre_delete_prefix": pre_delete_sha[:12],
        "book_sha_after_prefix": after[:12],
        "book_checksum_changed_by_chain": before != after,
        "before_counts": before_counts,
        "after_counts": compat_counts,
        "currency": currency,
        "transaction_opaque_ref": opaque(tx_id),
        "create": {
            "status": "success",
            "backup_created": create_backup.exists(),
            "backup_sha_prefix": sha256(create_backup)[:12] if create_backup.exists() else None,
            "transaction_present_before_delete": True,
        },
        "ownership": {"write_alpha_rows_for_created_tx": ownership_count},
        "delete": {
            "status": "success",
            "backup_created": delete_backup.exists(),
            "backup_sha_prefix": sha256(delete_backup)[:12] if delete_backup.exists() else None,
            "transaction_absent_after_delete": absent,
        },
        "restore": {
            "restored_from_delete_backup": True,
            "restored_sha_matches_backup": restored_sha_matches,
            "transaction_present_in_restored_backup": restore_present,
        },
        "audit_summary": {
            "returned_count": audit_json.get("returned_count"),
            "counts_by_action": audit_json.get("counts_by_action"),
            "counts_by_result": audit_json.get("counts_by_result"),
            "ownership_summary": audit_json.get("ownership_summary"),
        },
        "default_disabled_probe": {
            "delete_after_reset_status": disabled_status,
            "writes_disabled_forbidden": disabled_status == 403,
        },
        "redaction": "No private paths/account names/descriptions/memos/amounts are stored in committed docs.",
    }
    if not (absent and restore_present and restored_sha_matches and disabled_status == 403):
        evidence["result"] = "fail"
    evidence_file = evidence_dir / "write-alpha-create-delete-chain-evidence.json"
    evidence_file.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", required=True)
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()
    try:
        evidence = run(Path(args.book).resolve(), Path(args.work_dir).resolve(), Path(args.evidence_dir).resolve())
    except Exception as exc:
        print(f"FAIL: {exc.__class__.__name__}: {exc}; paths redacted", file=sys.stderr)
        return 2
    print("PASS: write-alpha CREATE-to-DELETE chain completed")
    print(f"  result={evidence['result']}")
    print(f"  ownership_rows={evidence['ownership']['write_alpha_rows_for_created_tx']}")
    print(f"  delete_absent={evidence['delete']['transaction_absent_after_delete']}")
    print(f"  restore_present={evidence['restore']['transaction_present_in_restored_backup']}")
    print(f"  disabled_status={evidence['default_disabled_probe']['delete_after_reset_status']}")
    print("  paths redacted")
    return 0 if evidence["result"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
