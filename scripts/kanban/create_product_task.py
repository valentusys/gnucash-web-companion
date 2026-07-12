#!/usr/bin/env python3
"""Safe repo-local wrapper for creating Hermes Kanban product tasks.

This helper validates the operator intent, checks local product-run safety gates,
and then delegates to the installed `hermes kanban create` command using an argv
list. It intentionally does not reimplement Hermes Kanban task creation.
"""

from __future__ import annotations

import argparse
import json
import re
import secrets
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, NoReturn, Sequence, TextIO

PROJECT_SLUG = "gnucash-web-companion"
WORKSPACE_KIND = "worktree"
BRANCH_PREFIX = "run/product"
CREATED_BY = "gnucash-product-task-wrapper"
SUPPORTED_ASSIGNEES = frozenset(
    {
        "backend-worker",
        "frontend-worker",
        "pm-orchestrator",
        "qa-integrator",
    }
)

BOARD_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,80}$")
BRANCH_SUFFIX_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
TASK_ID_RE = re.compile(r"^t_[0-9a-f]{8}$")
TOKEN_RE = re.compile(r"^[a-z0-9]{8}$")
DURATION_RE = re.compile(r"^[1-9][0-9]*(?:[smhd])?$")
REMOTE_RE = re.compile(r"(^|[/:])gnucash-web-companion(?:\.git)?$")
CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
TASK_ID_SEARCH_RE = re.compile(r"\bt_[0-9a-f]{8}\b")


class ValidationError(ValueError):
    """Operator input or preflight failed safely."""


class SafeArgumentParser(argparse.ArgumentParser):
    """ArgumentParser variant that reports validation errors through main()."""

    def error(self, message: str) -> NoReturn:
        raise ValidationError(message)


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


class SubprocessRunner:
    """Small subprocess adapter that always uses argv lists and never shell=True."""

    def run(self, args: list[str], *, cwd: Path | None = None) -> CommandResult:
        completed = subprocess.run(
            args,
            cwd=str(cwd) if cwd is not None else None,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return CommandResult(completed.returncode, completed.stdout, completed.stderr)


@dataclass(frozen=True)
class ProductTaskSpec:
    board: str
    title: str
    assignee: str
    branch: str
    body: str
    max_runtime: str
    max_retries: int
    parents: tuple[str, ...]
    priority: int | None


def make_parser() -> argparse.ArgumentParser:
    parser = SafeArgumentParser(
        description="Safely create a gnucash-web-companion Hermes Kanban product task.",
    )
    parser.add_argument("--board", required=True, help="Hermes Kanban board slug")
    parser.add_argument("--title", required=True, help="Task title")
    assignee = parser.add_mutually_exclusive_group(required=True)
    assignee.add_argument("--assignee", dest="assignee", help="Hermes profile to assign")
    assignee.add_argument("--profile", dest="assignee", help="Alias for --assignee")
    parser.add_argument("--branch-suffix", required=True, help="Lowercase safe suffix after run/product/")
    body = parser.add_mutually_exclusive_group(required=True)
    body.add_argument("--body", help="Task body text")
    body.add_argument("--body-file", help="UTF-8 file containing the task body")
    parser.add_argument("--max-runtime", required=True, help="Hermes max runtime, e.g. 30m or 2h")
    parser.add_argument("--max-retries", required=True, type=int, help="Hermes max retries, minimum 1")
    parser.add_argument("--parent", action="append", default=[], help="Parent task id; repeatable")
    parser.add_argument("--priority", type=int, help="Optional task priority, 0..1000")
    parser.add_argument("--dry-run", action="store_true", help="Print a redacted structured command and exit")
    return parser


def _reject_control_chars(name: str, value: str) -> None:
    if CONTROL_CHAR_RE.search(value):
        raise ValidationError(f"{name} contains unsafe control characters")


def _validate_nonempty(name: str, value: str, *, allow_newline: bool = False) -> str:
    if value is None or not value.strip():
        raise ValidationError(f"{name} must not be empty")
    _reject_control_chars(name, value)
    if not allow_newline and ("\n" in value or "\r" in value):
        raise ValidationError(f"{name} must be a single line")
    return value.strip() if name != "body" else value


def _validate_not_arg_like(name: str, value: str) -> None:
    if value.startswith("-"):
        raise ValidationError(f"{name} must not start with '-' or look like a CLI option")


def _validate_board(board: str) -> str:
    board = _validate_nonempty("board", board)
    _validate_not_arg_like("board", board)
    if not BOARD_RE.fullmatch(board):
        raise ValidationError("board contains unsupported characters")
    return board


def _validate_title(title: str) -> str:
    title = _validate_nonempty("title", title)
    _validate_not_arg_like("title", title)
    return title


def _validate_assignee(assignee: str) -> str:
    assignee = _validate_nonempty("assignee", assignee)
    _validate_not_arg_like("assignee", assignee)
    if assignee not in SUPPORTED_ASSIGNEES:
        supported = ", ".join(sorted(SUPPORTED_ASSIGNEES))
        raise ValidationError(f"unsupported assignee {assignee!r}; supported: {supported}")
    return assignee


def _validate_branch_suffix(branch_suffix: str) -> str:
    branch_suffix = _validate_nonempty("branch suffix", branch_suffix)
    _validate_not_arg_like("branch suffix", branch_suffix)
    if not BRANCH_SUFFIX_RE.fullmatch(branch_suffix):
        raise ValidationError("branch suffix must be lowercase [a-z0-9._-], no slashes or traversal")
    if ".." in branch_suffix or branch_suffix.endswith(".lock"):
        raise ValidationError("branch suffix contains unsafe git ref syntax")
    return branch_suffix


def _validate_body(body: str) -> str:
    body = _validate_nonempty("body", body, allow_newline=True)
    return body


def _validate_max_runtime(max_runtime: str) -> str:
    max_runtime = _validate_nonempty("max runtime", max_runtime)
    _validate_not_arg_like("max runtime", max_runtime)
    if not DURATION_RE.fullmatch(max_runtime):
        raise ValidationError("max runtime must be a positive duration like 300, 30m, or 2h")
    return max_runtime


def _validate_max_retries(max_retries: int) -> int:
    if max_retries < 1 or max_retries > 10:
        raise ValidationError("max retries must be between 1 and 10")
    return max_retries


def _validate_priority(priority: int | None) -> int | None:
    if priority is None:
        return None
    if priority < 0 or priority > 1000:
        raise ValidationError("priority must be between 0 and 1000")
    return priority


def _validate_parent(parent: str) -> str:
    parent = _validate_nonempty("parent", parent)
    _validate_not_arg_like("parent", parent)
    if not TASK_ID_RE.fullmatch(parent):
        raise ValidationError("parent must be a Hermes task id like t_1234abcd")
    return parent


def _validate_body_file_arg(raw_body_file: str) -> Path:
    raw_body_file = _validate_nonempty("body-file", raw_body_file)
    if "\x00" in raw_body_file:
        raise ValidationError("body-file contains unsafe null byte")
    path = Path(raw_body_file)
    if any(part.startswith("-") for part in path.parts):
        raise ValidationError("body-file path must not contain option-like path parts")
    if not path.is_file():
        raise ValidationError("body-file must point to an existing regular file")
    return path


def read_body(args: argparse.Namespace) -> str:
    if args.body is not None:
        return _validate_body(args.body)
    body_file = _validate_body_file_arg(args.body_file)
    try:
        return _validate_body(body_file.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise ValidationError("body-file must be UTF-8 text") from exc


def make_branch(branch_suffix: str, *, now: datetime | None = None, token: str | None = None) -> str:
    suffix = _validate_branch_suffix(branch_suffix)
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    current = current.astimezone(timezone.utc)
    unique = token or secrets.token_hex(4)
    if not TOKEN_RE.fullmatch(unique):
        raise ValidationError("unique branch token must be 8 lowercase alphanumeric characters")
    return f"{BRANCH_PREFIX}/{suffix}-{current.strftime('%Y%m%dT%H%M%SZ')}-{unique}"


def prepare_spec(
    argv: Sequence[str],
    *,
    now: datetime | None = None,
    token_provider: Callable[[], str] | None = None,
) -> ProductTaskSpec:
    args = make_parser().parse_args(list(argv))
    token = token_provider() if token_provider else secrets.token_hex(4)
    return ProductTaskSpec(
        board=_validate_board(args.board),
        title=_validate_title(args.title),
        assignee=_validate_assignee(args.assignee),
        branch=make_branch(args.branch_suffix, now=now, token=token),
        body=read_body(args),
        max_runtime=_validate_max_runtime(args.max_runtime),
        max_retries=_validate_max_retries(args.max_retries),
        parents=tuple(_validate_parent(parent) for parent in args.parent),
        priority=_validate_priority(args.priority),
    )


def build_create_command(spec: ProductTaskSpec, *, redact_body: bool = False) -> list[str]:
    body_value = f"<redacted body chars={len(spec.body)}>" if redact_body else spec.body
    command = [
        "hermes",
        "kanban",
        "--board",
        spec.board,
        "create",
        spec.title,
        f"--body={body_value}",
        "--assignee",
        spec.assignee,
    ]
    for parent in spec.parents:
        command.extend(["--parent", parent])
    command.extend(
        [
            "--workspace",
            WORKSPACE_KIND,
            "--branch",
            spec.branch,
            "--project",
            PROJECT_SLUG,
            "--max-runtime",
            spec.max_runtime,
            "--created-by",
            CREATED_BY,
            "--max-retries",
            str(spec.max_retries),
        ]
    )
    if spec.priority is not None:
        command.extend(["--priority", str(spec.priority)])
    command.append("--json")
    return command


def _run_checked(runner: SubprocessRunner, args: list[str], *, cwd: Path | None, label: str) -> str:
    result = runner.run(args, cwd=cwd)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().splitlines()[:1]
        suffix = f": {detail[0]}" if detail else ""
        raise ValidationError(f"{label} failed{suffix}")
    return result.stdout.strip()


def _parse_worktrees(output: str) -> list[dict[str, str]]:
    worktrees: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in output.splitlines():
        if not line:
            if current:
                worktrees.append(current)
                current = {}
            continue
        if line.startswith("worktree "):
            current["worktree"] = line.removeprefix("worktree ")
        elif line.startswith("branch "):
            current["branch"] = line.removeprefix("branch ")
        elif line.startswith("HEAD "):
            current["head"] = line.removeprefix("HEAD ")
    if current:
        worktrees.append(current)
    return worktrees


def _same_path(left: Path, right: Path) -> bool:
    return left.resolve(strict=False) == right.resolve(strict=False)


def _find_main_worktree(worktrees: list[dict[str, str]]) -> Path:
    for item in worktrees:
        if item.get("branch") == "refs/heads/main" and item.get("worktree"):
            return Path(item["worktree"])
    raise ValidationError("main worktree was not found in git worktree list")


def _diagnostics_clean(raw_json: str) -> bool:
    try:
        payload = json.loads(raw_json or "[]")
    except json.JSONDecodeError as exc:
        raise ValidationError("board diagnostics did not return JSON") from exc
    if payload in (None, [], {}):
        return True
    if isinstance(payload, dict):
        for key in ("diagnostics", "items", "results"):
            value = payload.get(key)
            if value not in (None, [], {}):
                return False
        return not payload
    return False


def ensure_repo_ready(spec: ProductTaskSpec, runner: SubprocessRunner, *, cwd: Path) -> Path:
    repo_root = Path(_run_checked(runner, ["git", "rev-parse", "--show-toplevel"], cwd=cwd, label="git repo root"))
    remote = _run_checked(runner, ["git", "config", "--get", "remote.origin.url"], cwd=repo_root, label="git remote lookup")
    if not REMOTE_RE.search(remote):
        raise ValidationError("current repository remote is not gnucash-web-companion")

    worktree_output = _run_checked(
        runner,
        ["git", "worktree", "list", "--porcelain"],
        cwd=repo_root,
        label="git worktree list",
    )
    worktrees = _parse_worktrees(worktree_output)
    if not any(_same_path(Path(item.get("worktree", "")), repo_root) for item in worktrees):
        raise ValidationError("current git root is not listed as a repository worktree")
    main_worktree = _find_main_worktree(worktrees)

    main_status = _run_checked(
        runner,
        ["git", "-C", str(main_worktree), "status", "--porcelain"],
        cwd=repo_root,
        label="main worktree status",
    )
    if main_status.strip():
        raise ValidationError("main worktree is dirty; clean it before product task creation")

    main_head = _run_checked(
        runner,
        ["git", "-C", str(main_worktree), "rev-parse", "main"],
        cwd=repo_root,
        label="main head lookup",
    )
    origin_head = _run_checked(
        runner,
        ["git", "-C", str(main_worktree), "rev-parse", "origin/main"],
        cwd=repo_root,
        label="origin/main lookup",
    )
    if main_head != origin_head:
        raise ValidationError("main differs from origin/main; fetch/reconcile before product task creation")

    diagnostics = _run_checked(
        runner,
        ["hermes", "kanban", "--board", spec.board, "diagnostics", "--json"],
        cwd=repo_root,
        label="kanban diagnostics",
    )
    if not _diagnostics_clean(diagnostics):
        raise ValidationError("board diagnostics are not clean; resolve diagnostics before product task creation")

    return repo_root


def extract_task_id(stdout_text: str) -> str | None:
    stripped = stdout_text.strip()
    if stripped:
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, dict):
            for key in ("id", "task_id"):
                value = payload.get(key)
                if isinstance(value, str) and TASK_ID_RE.fullmatch(value):
                    return value
            task = payload.get("task")
            if isinstance(task, dict):
                value = task.get("id") or task.get("task_id")
                if isinstance(value, str) and TASK_ID_RE.fullmatch(value):
                    return value
    match = TASK_ID_SEARCH_RE.search(stdout_text)
    return match.group(0) if match else None


def _print_dry_run(spec: ProductTaskSpec, *, stdout: TextIO) -> None:
    payload = {
        "dry_run": True,
        "preflight": "skipped-for-dry-run",
        "command": build_create_command(spec, redact_body=True),
        "fixed_fields": {
            "project": PROJECT_SLUG,
            "workspace": WORKSPACE_KIND,
            "created_by": CREATED_BY,
            "branch_prefix": BRANCH_PREFIX,
        },
        "board": spec.board,
        "assignee": spec.assignee,
        "branch": spec.branch,
        "parents": list(spec.parents),
        "priority": spec.priority,
    }
    print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)


def main(
    argv: Sequence[str] | None = None,
    *,
    runner: SubprocessRunner | None = None,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
    now: datetime | None = None,
    token_provider: Callable[[], str] | None = None,
    cwd: Path | None = None,
) -> int:
    runner = runner or SubprocessRunner()
    try:
        spec = prepare_spec(sys.argv[1:] if argv is None else argv, now=now, token_provider=token_provider)
        if "--dry-run" in (sys.argv[1:] if argv is None else argv):
            _print_dry_run(spec, stdout=stdout)
            return 0
        repo_root = ensure_repo_ready(spec, runner, cwd=cwd or Path.cwd())
        command = build_create_command(spec)
        result = runner.run(command, cwd=repo_root)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip().splitlines()[:1]
            suffix = f": {detail[0]}" if detail else ""
            print(f"error: hermes kanban create failed{suffix}", file=stderr)
            return result.returncode or 1
        task_id = extract_task_id(result.stdout)
        if task_id is None:
            print("error: hermes kanban create succeeded but no task id was found in output", file=stderr)
            return 1
        print(f"created_task_id={task_id}", file=stdout)
        print(
            json.dumps(
                {
                    "task_id": task_id,
                    "board": spec.board,
                    "assignee": spec.assignee,
                    "branch": spec.branch,
                    "project": PROJECT_SLUG,
                    "workspace": WORKSPACE_KIND,
                },
                sort_keys=True,
            ),
            file=stdout,
        )
        return 0
    except ValidationError as exc:
        print(f"error: {exc}", file=stderr)
        return 2
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 2
        return code


if __name__ == "__main__":
    raise SystemExit(main())
