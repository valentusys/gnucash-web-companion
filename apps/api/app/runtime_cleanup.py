"""Safe stopped-runtime cleanup helper for ignored Docker data artifacts.

This module intentionally exposes only path classes and counts. It is for local
operator recovery after synthetic/disposable dogfood runs create root-owned
runtime files under the ignored data volume. It must not inspect private book
contents or return raw filesystem paths.
"""

from __future__ import annotations

import fcntl
import os
import shutil
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

STOPPED_RUNTIME_ACK = "I_CONFIRM_RUNTIME_STOPPED"
RUNTIME_CLASSES = ("books", "app", "backups", "locks")
RUNTIME_DIR_NAMES = {
    "books": "books",
    "app": "app",
    "backups": "backups",
    "locks": "locks",
}


class RuntimeCleanupError(ValueError):
    """Raised when cleanup input fails closed."""


class LockState(str, Enum):
    ACTIVE = "active"
    STALE = "stale_released"
    UNREADABLE = "unreadable"
    NOT_LOCK = "not_lock"


@dataclass(frozen=True)
class CleanupItem:
    path_class: str
    kind: str
    lock_state: LockState | None
    action: str


@dataclass(frozen=True)
class CleanupSummary:
    mode: str
    execute: bool
    counts: dict[str, int]
    statuses: dict[str, int]
    messages: tuple[str, ...]


def require_stopped_runtime_ack(ack: str | None) -> None:
    if ack != STOPPED_RUNTIME_ACK:
        raise RuntimeCleanupError(
            "stopped runtime acknowledgement required; run docker compose down first and pass the exact acknowledgement token"
        )


def validate_runtime_root(repo_root: Path, data_root: Path) -> Path:
    repo = repo_root.resolve()
    root = data_root.resolve()
    expected = repo / "data"
    if root != expected:
        raise RuntimeCleanupError("data root must be the repository ignored data directory")
    if not root.is_dir():
        raise RuntimeCleanupError("data root is missing")
    return root


def runtime_class_dir(data_root: Path, path_class: str) -> Path:
    if path_class not in RUNTIME_DIR_NAMES:
        raise RuntimeCleanupError("unsupported runtime path class")
    path = data_root / RUNTIME_DIR_NAMES[path_class]
    path.mkdir(parents=True, exist_ok=True)
    resolved = path.resolve()
    if resolved.parent != data_root.resolve():
        raise RuntimeCleanupError("runtime path class escapes data root")
    return resolved


def _is_placeholder(path: Path) -> bool:
    return path.name == ".gitkeep"


def _scan_runtime_dir(path_class: str, class_dir: Path) -> list[CleanupItem]:
    items: list[CleanupItem] = []
    if not class_dir.exists():
        return items
    for child in class_dir.iterdir():
        if _is_placeholder(child):
            continue
        if path_class == "locks":
            if not child.is_file() or child.suffix != ".lock":
                items.append(CleanupItem(path_class, "unsupported", None, "skip_unsupported"))
                continue
            state = inspect_lock_file(child)
            action = {
                LockState.ACTIVE: "skip_active_lock",
                LockState.STALE: "cleanup_stale_lock",
                LockState.UNREADABLE: "cleanup_unreadable_lock_with_stopped_ack",
                LockState.NOT_LOCK: "skip_unsupported",
            }[state]
            items.append(CleanupItem(path_class, "lock", state, action))
            continue
        kind = "dir" if child.is_dir() else "file"
        items.append(CleanupItem(path_class, kind, None, "cleanup_runtime_artifact"))
    return items


def inspect_lock_file(path: Path) -> LockState:
    try:
        fd = os.open(str(path), os.O_RDWR)
    except PermissionError:
        return LockState.UNREADABLE
    except OSError:
        return LockState.UNREADABLE
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return LockState.ACTIVE
        finally:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                pass
    finally:
        os.close(fd)
    return LockState.STALE


def collect_cleanup_items(repo_root: Path, data_root: Path, classes: tuple[str, ...] = RUNTIME_CLASSES) -> list[CleanupItem]:
    root = validate_runtime_root(repo_root, data_root)
    items: list[CleanupItem] = []
    for path_class in classes:
        class_dir = runtime_class_dir(root, path_class)
        items.extend(_scan_runtime_dir(path_class, class_dir))
    return items


def _remove_child(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def cleanup_runtime(
    repo_root: Path,
    data_root: Path,
    *,
    ack: str | None,
    execute: bool = False,
    classes: tuple[str, ...] = RUNTIME_CLASSES,
) -> CleanupSummary:
    require_stopped_runtime_ack(ack)
    root = validate_runtime_root(repo_root, data_root)
    items: list[CleanupItem] = []
    removed = 0
    active_locks = 0
    unreadable_locks = 0

    for path_class in classes:
        class_dir = runtime_class_dir(root, path_class)
        for child in list(class_dir.iterdir()) if class_dir.exists() else []:
            if _is_placeholder(child):
                continue
            if path_class == "locks":
                if not child.is_file() or child.suffix != ".lock":
                    item = CleanupItem(path_class, "unsupported", None, "skip_unsupported")
                    items.append(item)
                    continue
                state = inspect_lock_file(child)
                if state == LockState.ACTIVE:
                    active_locks += 1
                    items.append(CleanupItem(path_class, "lock", state, "skip_active_lock"))
                    continue
                if state == LockState.UNREADABLE:
                    unreadable_locks += 1
                    items.append(CleanupItem(path_class, "lock", state, "cleanup_unreadable_lock_with_stopped_ack"))
                else:
                    items.append(CleanupItem(path_class, "lock", state, "cleanup_stale_lock"))
                if execute:
                    _remove_child(child)
                    removed += 1
                continue
            item = CleanupItem(path_class, "dir" if child.is_dir() else "file", None, "cleanup_runtime_artifact")
            items.append(item)
            if execute:
                _remove_child(child)
                removed += 1

    counts: dict[str, int] = {path_class: 0 for path_class in RUNTIME_CLASSES}
    statuses: dict[str, int] = {}
    for item in items:
        counts[item.path_class] = counts.get(item.path_class, 0) + 1
        statuses[item.action] = statuses.get(item.action, 0) + 1
        if item.lock_state is not None:
            key = f"lock_{item.lock_state.value}"
            statuses[key] = statuses.get(key, 0) + 1
    if execute:
        statuses["removed"] = removed
    messages = [
        "stopped-runtime acknowledgement accepted",
        "output is redacted to path classes and counts only",
    ]
    if active_locks:
        messages.append("active lock files were preserved")
    if unreadable_locks:
        messages.append("unreadable lock files were handled only after stopped-runtime acknowledgement")
    return CleanupSummary(
        mode="cleanup" if execute else "dry_run",
        execute=execute,
        counts=counts,
        statuses=statuses,
        messages=tuple(messages),
    )


def format_summary(summary: CleanupSummary) -> str:
    lines = [f"mode={summary.mode}", "path_classes:"]
    for path_class in RUNTIME_CLASSES:
        lines.append(f"  {path_class}: count={summary.counts.get(path_class, 0)}")
    lines.append("statuses:")
    for status in sorted(summary.statuses):
        lines.append(f"  {status}: count={summary.statuses[status]}")
    lines.append("messages:")
    for message in summary.messages:
        lines.append(f"  - {message}")
    return "\n".join(lines)
