"""Guards for write-alpha runtime artifact locations."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "write_alpha_create_delete_chain.py"

spec = importlib.util.spec_from_file_location("write_alpha_create_delete_chain", SCRIPT_PATH)
assert spec is not None
chain = importlib.util.module_from_spec(spec)
sys.modules["write_alpha_create_delete_chain"] = chain
assert spec.loader is not None
spec.loader.exec_module(chain)


def _init_repo(repo_root: Path) -> None:
    repo_root.mkdir(parents=True, exist_ok=True)
    (repo_root / ".gitignore").write_text(
        ".hermes/autonomy/\n"
        "data/backups/*\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init"], cwd=repo_root, check=True, stdout=subprocess.DEVNULL)


def test_runtime_artifact_dir_may_be_outside_git(tmp_path):
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    outside = tmp_path / "outside-runtime" / "evidence"

    assert chain.classify_runtime_artifact_dir(outside, repo_root=repo_root) == "external"
    assert chain.ensure_safe_runtime_artifact_dir(outside, "evidence-dir", repo_root=repo_root) == "external"


def test_runtime_artifact_dir_may_be_ignored_inside_git(tmp_path):
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    ignored = repo_root / ".hermes" / "autonomy" / "issue50" / "evidence"

    assert chain.classify_runtime_artifact_dir(ignored, repo_root=repo_root) == "ignored"
    assert chain.ensure_safe_runtime_artifact_dir(ignored, "evidence-dir", repo_root=repo_root) == "ignored"


def test_runtime_artifact_dir_blocks_tracked_repo_paths_without_leaking_path(tmp_path):
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    unsafe = repo_root / "docs" / "handoff" / "raw-evidence"

    assert chain.classify_runtime_artifact_dir(unsafe, repo_root=repo_root) == "unsafe"
    try:
        chain.ensure_safe_runtime_artifact_dir(unsafe, "work-dir", repo_root=repo_root)
    except RuntimeError as exc:
        message = str(exc)
    else:
        raise AssertionError("unignored in-repo runtime artifact dir should be blocked")

    assert "work-dir must be outside git working tree or git-ignored runtime storage" == message
    assert str(unsafe) not in message
    assert "raw-evidence" not in message
    assert "docs" not in message


def test_create_delete_chain_run_blocks_tracked_runtime_dir_before_opening_book(tmp_path):
    copied_book = tmp_path / "copied-disposable-book.gnucash.sqlite"
    copied_book.write_bytes(b"not opened before runtime-dir guard")
    unsafe_work_dir = REPO_ROOT / "docs" / "handoff" / "runtime-artifact-guard-should-not-be-created"
    external_evidence_dir = tmp_path / "evidence"

    with pytest.raises(RuntimeError) as excinfo:
        chain.run(copied_book, unsafe_work_dir, external_evidence_dir)

    assert str(excinfo.value) == "work-dir must be outside git working tree or git-ignored runtime storage"
    assert not unsafe_work_dir.exists()
    assert not external_evidence_dir.exists()
