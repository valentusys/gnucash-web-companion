#!/usr/bin/env python3
"""Path-redacted evidence helpers for write-alpha smoke scripts.

These helpers deliberately return counts/statuses only. They never print raw
runtime paths, backup filenames, app DB rows, payloads, account names, memos, or
amounts. Host-side probes fall back to a read-only probe inside the running API
container when local permissions prevent inspection of root-owned runtime files.
"""

from __future__ import annotations

import fcntl
import json
import os
import sqlite3
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class EvidenceFailure(Exception):
    """Raised when redacted runtime evidence cannot be collected."""


@dataclass(frozen=True)
class CountEvidence:
    count: int
    source: str
    status: str
    message: str


@dataclass(frozen=True)
class LockEvidence:
    status: str
    is_active: bool
    message: str
    source: str = "host"


@dataclass(frozen=True)
class BackupTransactionEvidence:
    status: str
    source: str
    present: bool
    split_count: int | None = None
    split_fingerprint: tuple[str, ...] | None = None
    message: str = ""


@dataclass(frozen=True)
class RestoreEvidence:
    performed: bool
    status: str
    message: str


def _safe_message(kind: str, status: str) -> str:
    return f"{kind} evidence status={status}; output is path-redacted"


def _data_container_path(path: Path) -> str:
    parts = path.as_posix().split("/")
    if "data" in parts:
        idx = len(parts) - 1 - parts[::-1].index("data")
        tail = "/".join(parts[idx + 1 :])
        return f"/data/{tail}" if tail else "/data"
    return path.as_posix()


def host_path_for_api_path(api_path: str, data_root: Path = Path("data")) -> Path:
    if api_path.startswith("/data/"):
        return data_root / api_path.removeprefix("/data/")
    return Path(api_path)


def _container_probe(payload: dict[str, Any], *, service: str = "api") -> dict[str, Any]:
    code = r'''
import fcntl, json, os, sqlite3, sys
from pathlib import Path

payload=json.loads(sys.argv[1])
probe=payload.get('probe')

def count_files(root):
    p=Path(root)
    if not p.exists():
        return 0
    return sum(1 for child in p.rglob('*') if child.is_file())

def audit_count(db_path, action, result, backup_path_is_none):
    p=Path(db_path)
    if not p.exists():
        raise RuntimeError('app db missing')
    count=0
    with sqlite3.connect(p) as connection:
        rows=connection.execute('select payload_json from audit_logs where action = ?', (action,)).fetchall()
    for (raw,) in rows:
        try:
            item=json.loads(raw or '{}')
        except json.JSONDecodeError:
            continue
        if item.get('result') != result:
            continue
        if backup_path_is_none is True and item.get('backup_path') is not None:
            continue
        if backup_path_is_none is False and item.get('backup_path') is None:
            continue
        if item.get('transaction_id') or result == 'failed':
            count += 1
    return count

def lock_evidence(root, route_label):
    p=Path(root)
    if not p.exists():
        return {'status':'not_present','is_active':False,'message':'no lock files remain'}
    saw_stale=False
    for child in p.glob('*.lock'):
        if not child.is_file():
            continue
        try:
            fd=os.open(child, os.O_RDWR)
        except PermissionError:
            return {'status':'unreadable','is_active':False,'message':'lock file is not readable by this process; inspect with stopped-runtime cleanup only'}
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return {'status':'active','is_active':True,'message':f'write lock remains actively held after {route_label}'}
            finally:
                try:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                except OSError:
                    pass
            saw_stale=True
        finally:
            os.close(fd)
    if saw_stale:
        return {'status':'stale_released','is_active':False,'message':'lock file remains but is not actively held; with the app stopped an operator may remove only the book-specific stale lock from ignored runtime storage'}
    return {'status':'not_present','is_active':False,'message':'no lock files remain'}

def backup_transaction(path, transaction_id):
    p=Path(path)
    if not p.exists() or not p.is_file():
        return {'present':False,'status':'missing','message':'backup artifact missing'}
    with sqlite3.connect(f'file:{p}?mode=ro', uri=True) as connection:
        tx=connection.execute('select guid from transactions where guid = ?', (transaction_id,)).fetchone()
        if tx is None:
            return {'present':False,'status':'transaction_missing','message':'backup lacks target transaction'}
        rows=connection.execute('select guid, value_num, value_denom from splits where tx_guid = ? order by guid', (transaction_id,)).fetchall()
    return {'present':True,'status':'present','split_count':len(rows),'split_fingerprint':[f'{row[0]}:{row[1]}/{row[2]}' for row in rows], 'message':'backup contains bounded target evidence'}

try:
    if probe == 'file_count':
        result={'count':count_files(payload['path'])}
    elif probe == 'audit_count':
        result={'count':audit_count(payload['path'], payload['action'], payload['result'], payload.get('backup_path_is_none'))}
    elif probe == 'lock_evidence':
        result=lock_evidence(payload['path'], payload.get('route_label','write'))
    elif probe == 'backup_transaction':
        result=backup_transaction(payload['path'], payload['transaction_id'])
    else:
        raise RuntimeError('unknown probe')
    result['ok']=True
except Exception:
    result={'ok':False,'error':'container probe failed'}
print(json.dumps(result, sort_keys=True))
'''
    command = ["docker", "compose", "exec", "-T", service, "python", "-c", code, json.dumps(payload, sort_keys=True)]
    env = os.environ.copy()
    env.setdefault("JWT_SECRET", "dummy-smoke-container-probe-secret")
    env.setdefault("APP_ADMIN_PASSWORD", "dummy-smoke-container-probe-password")
    completed = subprocess.run(command, check=False, text=True, capture_output=True, timeout=30, env=env)
    if completed.returncode != 0:
        raise EvidenceFailure("container evidence probe failed with redacted output")
    try:
        data = json.loads(completed.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError) as exc:
        raise EvidenceFailure("container evidence probe returned non-json redacted output") from exc
    if not data.get("ok"):
        raise EvidenceFailure("container evidence probe failed with redacted output")
    return data


def file_count_evidence(root: Path, *, kind: str, use_container: bool = True) -> CountEvidence:
    try:
        if not root.exists():
            return CountEvidence(0, "host", "ok", _safe_message(kind, "ok"))
        count = sum(1 for path in root.rglob("*") if path.is_file())
        return CountEvidence(count, "host", "ok", _safe_message(kind, "ok"))
    except (PermissionError, OSError):
        if not use_container:
            raise EvidenceFailure(f"{kind} host evidence unreadable and container probe disabled")
        data = _container_probe({"probe": "file_count", "path": _data_container_path(root)})
        return CountEvidence(int(data["count"]), "api_container", "host_unreadable_container_ok", _safe_message(kind, "host_unreadable_container_ok"))


def audit_count_evidence(
    app_db: Path,
    *,
    action: str,
    result: str = "success",
    backup_path_is_none: bool | None = None,
    use_container: bool = True,
) -> CountEvidence:
    def read_count(path: Path) -> int:
        if not path.exists():
            raise EvidenceFailure("app DB is missing after runtime smoke")
        count = 0
        with sqlite3.connect(path) as connection:
            rows = connection.execute("select payload_json from audit_logs where action = ?", (action,)).fetchall()
        for (payload_raw,) in rows:
            try:
                payload = json.loads(payload_raw or "{}")
            except json.JSONDecodeError:
                continue
            if payload.get("result") != result:
                continue
            if backup_path_is_none is True and payload.get("backup_path") is not None:
                continue
            if backup_path_is_none is False and payload.get("backup_path") is None:
                continue
            if payload.get("transaction_id") or result == "failed":
                count += 1
        return count

    try:
        return CountEvidence(read_count(app_db), "host", "ok", _safe_message("audit", "ok"))
    except (PermissionError, sqlite3.Error, OSError, EvidenceFailure):
        if not use_container:
            raise
        data = _container_probe(
            {
                "probe": "audit_count",
                "path": _data_container_path(app_db),
                "action": action,
                "result": result,
                "backup_path_is_none": backup_path_is_none,
            }
        )
        return CountEvidence(int(data["count"]), "api_container", "host_unreadable_container_ok", _safe_message("audit", "host_unreadable_container_ok"))


def lock_evidence(lock_root: Path, *, route_label: str, use_container: bool = True) -> LockEvidence:
    def host_probe() -> LockEvidence:
        if not lock_root.exists():
            return LockEvidence("not_present", False, "no lock files remain")
        saw_stale = False
        for path in lock_root.glob("*.lock"):
            if not path.is_file():
                continue
            try:
                fd = os.open(path, os.O_RDWR)
            except PermissionError:
                raise PermissionError
            try:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    return LockEvidence("active", True, f"write lock remains actively held after {route_label}")
                finally:
                    try:
                        fcntl.flock(fd, fcntl.LOCK_UN)
                    except OSError:
                        pass
                saw_stale = True
            finally:
                os.close(fd)
        if saw_stale:
            return LockEvidence(
                "stale_released",
                False,
                "lock file remains but is not actively held; with the app stopped an operator may remove only the book-specific stale lock from ignored runtime storage",
            )
        return LockEvidence("not_present", False, "no lock files remain")

    try:
        return host_probe()
    except (PermissionError, OSError):
        if not use_container:
            return LockEvidence(
                "unreadable",
                False,
                "lock file is not readable by this smoke user; inspect from the API container or fix runtime ownership before removing only the book-specific stale lock with the app stopped",
            )
        data = _container_probe({"probe": "lock_evidence", "path": _data_container_path(lock_root), "route_label": route_label})
        return LockEvidence(str(data["status"]), bool(data["is_active"]), str(data["message"]), "api_container")


def backup_transaction_evidence(
    backup_path: Path,
    *,
    transaction_id: str,
    data_root: Path = Path("data"),
    use_container: bool = True,
) -> BackupTransactionEvidence:
    try:
        if not backup_path.exists() or not backup_path.is_file():
            raise EvidenceFailure("backup artifact missing")
        with sqlite3.connect(f"file:{backup_path}?mode=ro", uri=True) as connection:
            tx_row = connection.execute("select guid from transactions where guid = ?", (transaction_id,)).fetchone()
            if tx_row is None:
                return BackupTransactionEvidence("transaction_missing", "host", False, message="backup lacks target transaction")
            rows = connection.execute(
                "select guid, value_num, value_denom from splits where tx_guid = ? order by guid", (transaction_id,)
            ).fetchall()
        return BackupTransactionEvidence(
            "present",
            "host",
            True,
            len(rows),
            tuple(f"{row[0]}:{row[1]}/{row[2]}" for row in rows),
            "backup contains bounded target evidence",
        )
    except (PermissionError, sqlite3.Error, OSError, EvidenceFailure):
        if not use_container:
            raise
        container_path = _data_container_path(backup_path)
        data = _container_probe({"probe": "backup_transaction", "path": container_path, "transaction_id": transaction_id})
        return BackupTransactionEvidence(
            str(data["status"]),
            "api_container",
            bool(data.get("present")),
            int(data["split_count"]) if data.get("split_count") is not None else None,
            tuple(data.get("split_fingerprint") or ()),
            str(data.get("message") or "backup evidence collected inside API container"),
        )
