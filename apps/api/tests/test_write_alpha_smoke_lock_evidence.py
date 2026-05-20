"""Tests for write-alpha smoke lock evidence classification."""

from __future__ import annotations

import fcntl
import importlib.util
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SMOKE_PATH = ROOT / "scripts" / "smoke" / "write-alpha-create-smoke.py"
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

    result = smoke._lock_evidence(lock_root)

    assert result.status == "unreadable"
    assert result.is_active is False
    assert "API container" in result.message
    assert "book-specific stale lock" in result.message
    assert "book-1" not in result.message
    assert str(lock_root) not in result.message
    assert "/" not in result.message
