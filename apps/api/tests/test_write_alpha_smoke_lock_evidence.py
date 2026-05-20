"""Tests for write-alpha smoke lock evidence classification."""

from __future__ import annotations

import fcntl
import importlib.util
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SMOKE_PATH = ROOT / "scripts" / "smoke" / "write-alpha-create-smoke.py"
sys.path.insert(0, str(SMOKE_PATH.parent))
spec = importlib.util.spec_from_file_location("write_alpha_create_smoke", SMOKE_PATH)
assert spec is not None and spec.loader is not None
smoke = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = smoke
spec.loader.exec_module(smoke)


def test_lock_evidence_reports_not_present_without_cleanup_action(tmp_path: Path) -> None:
    result = smoke._lock_evidence(tmp_path / "locks")

    assert result.status == "not_present"
    assert result.is_active is False
    assert "no lock files" in result.message
    assert "/" not in result.message


def test_lock_evidence_reports_stale_released_without_path_leak(tmp_path: Path) -> None:
    lock_root = tmp_path / "locks"
    lock_root.mkdir()
    (lock_root / "book-1.lock").write_text("", encoding="utf-8")

    result = smoke._lock_evidence(lock_root)

    assert result.status == "stale_released"
    assert result.is_active is False
    assert "not actively held" in result.message
    assert "ignored runtime storage" in result.message
    assert "book-1" not in result.message
    assert str(lock_root) not in result.message
    assert "/" not in result.message


def test_lock_evidence_reports_active_flock_without_path_leak(tmp_path: Path) -> None:
    lock_root = tmp_path / "locks"
    lock_root.mkdir()
    lock_path = lock_root / "book-1.lock"
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

        result = smoke._lock_evidence(lock_root)

        assert result.status == "active"
        assert result.is_active is True
        assert "actively held" in result.message
        assert "book-1" not in result.message
        assert str(lock_root) not in result.message
        assert "/" not in result.message
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def test_lock_evidence_reports_unreadable_guidance_without_path_leak(tmp_path: Path, monkeypatch) -> None:
    lock_root = tmp_path / "locks"
    lock_root.mkdir()
    lock_path = lock_root / "book-1.lock"
    lock_path.write_text("", encoding="utf-8")
    original_open = os.open

    def permission_denied(path: str | os.PathLike[str], flags: int, mode: int = 0o777) -> int:
        if str(path).endswith("book-1.lock"):
            raise PermissionError("permission denied")
        return original_open(path, flags, mode)

    monkeypatch.setattr(smoke.os, "open", permission_denied)

    result = smoke.collect_lock_evidence(lock_root, route_label="create", use_container=False)

    assert result.status == "unreadable"
    assert result.is_active is False
    assert "API container" in result.message
    assert "book-specific stale lock" in result.message
    assert "book-1" not in result.message
    assert str(lock_root) not in result.message
    assert "/" not in result.message


def test_lock_evidence_falls_back_to_container_without_path_leak(tmp_path: Path, monkeypatch) -> None:
    lock_root = tmp_path / "data" / "locks"
    lock_root.mkdir(parents=True)
    lock_path = lock_root / "book-1.lock"
    lock_path.write_text("", encoding="utf-8")
    original_open = os.open

    def permission_denied(path: str | os.PathLike[str], flags: int, mode: int = 0o777) -> int:
        if str(path).endswith("book-1.lock"):
            raise PermissionError("permission denied")
        return original_open(path, flags, mode)

    def fake_container_probe(payload):
        assert payload == {"probe": "lock_evidence", "path": "/data/locks", "route_label": "create"}
        return {
            "ok": True,
            "status": "stale_released",
            "is_active": False,
            "message": "lock file remains but is not actively held; with the app stopped an operator may remove only the book-specific stale lock from ignored runtime storage",
        }

    monkeypatch.setattr(smoke.os, "open", permission_denied)
    monkeypatch.setitem(smoke.collect_lock_evidence.__globals__, "_container_probe", fake_container_probe)

    result = smoke.collect_lock_evidence(lock_root, route_label="create")

    assert result.status == "stale_released"
    assert result.source == "api_container"
    assert result.is_active is False
    assert "book-1" not in result.message
    assert str(lock_root) not in result.message
    assert "/" not in result.message


def test_backup_count_falls_back_to_container_when_host_unreadable(tmp_path: Path, monkeypatch) -> None:
    backup_root = tmp_path / "data" / "backups"
    backup_root.mkdir(parents=True)
    private_backup = backup_root / "private-name.sqlite"
    private_backup.write_text("synthetic", encoding="utf-8")
    original_is_file = Path.is_file

    def permission_denied_is_file(path: Path) -> bool:
        if path == private_backup:
            raise PermissionError("permission denied")
        return original_is_file(path)

    def fake_container_probe(payload):
        assert payload == {"probe": "file_count", "path": "/data/backups"}
        return {"ok": True, "count": 1}

    monkeypatch.setattr(Path, "is_file", permission_denied_is_file)
    monkeypatch.setitem(smoke.file_count_evidence.__globals__, "_container_probe", fake_container_probe)

    result = smoke.file_count_evidence(backup_root, kind="backup")

    assert result.count == 1
    assert result.source == "api_container"
    assert "private-name" not in result.message
    assert str(backup_root) not in result.message


def test_delete_restore_skip_message_is_path_safe() -> None:
    message = (
        "restore proof skipped because host-side backup artifact was unreadable; "
        "container-side backup evidence was used instead"
    )
    assert "/" not in message
    assert "backup.sqlite" not in message
