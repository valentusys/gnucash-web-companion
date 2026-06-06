#!/usr/bin/env python3
"""Repo-local autonomous worker supervisor.

The supervisor owns wall-clock budget, renders one bounded worker prompt per
queue task, and either simulates or invokes a configured local agent command.
Runtime prompts/reports are intended to live under ignored .hermes/autonomy/.
"""

from __future__ import annotations

import argparse
import dataclasses
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Sequence


TRANSIENT_MARKERS = (
    "429",
    "rate limit",
    "ratelimit",
    "timeout",
    "tls reset",
    "tls handshake timeout",
    "eof",
    "network reset",
    "connection reset",
    "temporarily unavailable",
)

ON_EMPTY_CHOICES = ("stop", "repeat-safe-final", "generate-from-policy")
TASK_FIELD_NAMES = (
    "target",
    "goal",
    "allowed scope",
    "non-goals",
    "verification commands",
    "safety flags",
    "stop/continue recommendation",
)
FORBIDDEN_POLICY_MARKERS = (
    "publish release",
    "publish a write beta release",
    "public write beta",
    "private book",
    "original book",
    "working book",
    "only-copy",
    "gnucash mutation",
    "production-ready",
    "stable release",
    "security-audited",
    "broad compatibility is",
    "broad compatibility proven",
    "broad compatibility claim authorized",
    "broad compatibility ready",
)
FORBIDDEN_VERIFICATION_COMMAND_MARKERS = (
    "gh release",
    "git tag",
    "docker push",
    "docker buildx build --push",
    "twine upload",
    "npm publish",
    "pnpm publish",
    "yarn publish",
    "publish release",
    "publish a write beta release",
)
FORBIDDEN_VERIFICATION_COMMAND_PATTERNS = (
    re.compile(r"\bgit\s+push\b[^\n;]*\s--(?:follow-)?tags\b", re.I),
    re.compile(r"\bgit\s+push\b[^\n;]*\b(?:refs/tags/[^\s;]+|tag\s+[^\s;]+|v\d+(?:\.\d+)+[^\s;]*)\b", re.I),
    re.compile(r"\bgh\s+api\b[^\n;]*(?:\brepos/[^\s;]+/[^\s;]+/releases\b|/releases\b)", re.I),
    re.compile(r"\bdocker\s+buildx\s+build\b[^\n;]*\s--push\b", re.I),
)

SAFETY_RULES = """Repository safety rules:
1. Never touch original/private/working/only-copy GnuCash books.
2. Never commit GnuCash books, SQLite books, app DBs, backups, CSV exports, screenshots, .env, tokens, keys, certs, private paths, account names, transaction descriptions, memos, amounts, or raw private evidence.
3. Do not run product dogfood or GnuCash mutations unless the task explicitly authorizes a copied/disposable test fixture and the verification scope says so.
4. Do not publish releases, tags, packages, or images.
5. Do not change default write posture.
6. Preserve GNUCASH_WRITES_ENABLED=false in defaults and rendered Compose.
7. Preserve APP_ENV=test gates for enabled writes.
8. No public write beta, stable, production-ready, security-audited, broad compatibility, or only-copy safety claim is authorized.
9. Keep runtime prompts/reports under ignored .hermes/autonomy/ unless explicitly asked to create a tracked handoff.
10. If blocked, checkpoint honestly; do not fabricate success.
"""

GATE_PRESETS: dict[str, list[str]] = {
    "quick-docs": [
        "python3 scripts/check_public_status.py",
        "python3 scripts/check_markdown_readability.py",
        "python3 scripts/check_tracked_hygiene.py",
        "git diff --check",
    ],
    "api": ["cd apps/api && pytest -q"],
    "web": [
        "cd apps/web && npm run check",
        "cd apps/web && npm run test:auth-routes",
        "cd apps/web && npm run build",
    ],
    "full": [
        "cd apps/api && pytest -q",
        "cd apps/web && npm run check",
        "cd apps/web && npm run test:auth-routes",
        "cd apps/web && npm run build",
        "JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet",
        "python3 scripts/check_public_status.py",
        "python3 scripts/check_markdown_readability.py",
        "python3 scripts/check_write_safety_defaults.py",
        "python3 scripts/check_tracked_hygiene.py",
        "git diff --check",
    ],
}


class SupervisorError(RuntimeError):
    """Fail-closed supervisor error."""


@dataclasses.dataclass(frozen=True)
class Task:
    task_id: str
    target: str
    goal: str
    allowed_scope: str
    non_goals: str
    verification_commands: list[str]
    safety_flags: list[str]
    stop_continue: str
    generated_from_policy: str | None = None


@dataclasses.dataclass(frozen=True)
class AgentResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def combined_output(self) -> str:
        return "\n".join(part for part in (self.stdout, self.stderr) if part)


@dataclasses.dataclass
class TaskReport:
    task_id: str
    status: str
    attempts: int
    head_before: str
    prompt_path: str
    message: str


@dataclasses.dataclass
class SupervisorReport:
    status: str
    mode: str
    queue_path: str
    run_root: str
    tasks: list[TaskReport]
    github_state_path: str | None = None
    final_report_path: str | None = None
    stop_reason: str = ""
    min_runtime_seconds: float = 0.0
    min_tasks: int = 0
    on_empty: str = "stop"
    backlog_policy_path: str | None = None


class GitGuard:
    def head(self, repo: Path) -> str:
        return run_text(["git", "rev-parse", "HEAD"], repo).strip()

    def status(self, repo: Path) -> str:
        status = run_text(["git", "status", "--porcelain"], repo)
        for line in status.splitlines():
            path = line[3:] if len(line) > 3 else line
            if path.startswith(".hermes/autonomy/"):
                continue
            return status
        return ""


def run_text(command: Sequence[str], cwd: Path, timeout: int = 120) -> str:
    completed = subprocess.run(
        list(command), cwd=cwd, text=True, capture_output=True, timeout=timeout
    )
    if completed.returncode != 0:
        raise SupervisorError(
            f"command failed ({' '.join(command)}): {completed.stderr.strip()}"
        )
    return completed.stdout


class SubprocessAgent:
    def __init__(self, command: Sequence[str]):
        self.command = list(command)

    @classmethod
    def from_environment(cls, mode: str) -> "SubprocessAgent":
        if mode == "dry-run":
            return cls([sys.executable, "-c", "import sys; sys.stdin.read(); print('dry-run')"])
        command = os.environ.get("AUTONOMY_AGENT_COMMAND", "").strip()
        if not command:
            raise SupervisorError(
                "live mode requires AUTONOMY_AGENT_COMMAND; refusing to invoke an implicit agent"
            )
        return cls(shlex.split(command))

    def run(self, prompt_path: Path, mode: str) -> AgentResult:
        prompt = prompt_path.read_text(encoding="utf-8")
        if mode == "dry-run":
            return AgentResult(0, "DRY_RUN_SIMULATED", "")
        cwd = None
        parts = list(prompt_path.parents)
        for index, parent in enumerate(parts):
            if parent.name == ".hermes" and index + 1 < len(parts):
                cwd = parts[index + 1]
                break
        completed = subprocess.run(
            self.command,
            input=prompt,
            text=True,
            capture_output=True,
            cwd=cwd,
        )
        return AgentResult(completed.returncode, completed.stdout, completed.stderr)


def parse_queue(path: Path) -> list[Task]:
    text = path.read_text(encoding="utf-8")
    tasks: list[Task] = []
    current_id: str | None = None
    fields: dict[str, object] = {}
    current_list_field: str | None = None

    def flush() -> None:
        nonlocal current_id, fields, current_list_field
        if current_id is None:
            return
        required = list(TASK_FIELD_NAMES)
        missing = [name for name in required if not fields.get(name)]
        if missing:
            raise SupervisorError(f"task {current_id} missing required field(s): {', '.join(missing)}")
        verification = fields["verification commands"]
        if isinstance(verification, str):
            verification = [verification]
        flags = fields["safety flags"]
        if isinstance(flags, str):
            flags = [item.strip() for item in flags.split(",") if item.strip()]
        tasks.append(
            Task(
                task_id=current_id,
                target=str(fields["target"]),
                goal=str(fields["goal"]),
                allowed_scope=str(fields["allowed scope"]),
                non_goals=str(fields["non-goals"]),
                verification_commands=list(verification),
                safety_flags=list(flags),
                stop_continue=str(fields["stop/continue recommendation"]),
            )
        )
        current_id = None
        fields = {}
        current_list_field = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## Task:"):
            flush()
            current_id = line.split(":", 1)[1].strip()
            fields = {}
            current_list_field = None
            continue
        if current_id is None:
            continue
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- ") and ":" in stripped:
            key, value = stripped[2:].split(":", 1)
            key = key.strip().lower()
            if key in TASK_FIELD_NAMES:
                value = value.strip()
                if value:
                    fields[key] = value
                    current_list_field = None
                else:
                    fields[key] = []
                    current_list_field = key
                continue
        if stripped.startswith("- ") and current_list_field:
            value = stripped[2:].strip()
            current = fields.setdefault(current_list_field, [])
            if not isinstance(current, list):
                raise SupervisorError(f"field {current_list_field} is not a list in task {current_id}")
            current.append(value)
            continue

    flush()
    if not tasks:
        raise SupervisorError(f"no tasks found in queue: {path}")
    return tasks


def normalized_safety_text(text: str) -> str:
    """Normalize task prose/commands so safety marker checks survive spacing drift."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def task_is_safe_for_policy(task: Task) -> bool:
    flags = {flag.strip().lower() for flag in task.safety_flags}
    if "generated-safe" not in flags:
        return False
    if "no-release" not in flags or "no-private-data" not in flags:
        return False
    forbidden_flags = {"release", "touches-private-data", "dogfood", "gnucash-mutation"}
    if flags & forbidden_flags:
        return False
    text = normalized_safety_text(f"{task.goal}\n{task.allowed_scope}\n{task.stop_continue}")
    if any(marker in text for marker in FORBIDDEN_POLICY_MARKERS):
        return False
    verification_text = normalized_safety_text("\n".join(task.verification_commands))
    if any(marker in verification_text for marker in FORBIDDEN_VERIFICATION_COMMAND_MARKERS):
        return False
    return not any(pattern.search(verification_text) for pattern in FORBIDDEN_VERIFICATION_COMMAND_PATTERNS)


def load_safe_policy_tasks(path: Path) -> list[Task]:
    tasks = parse_queue(path)
    safe: list[Task] = []
    for task in tasks:
        if task_is_safe_for_policy(task):
            safe.append(dataclasses.replace(task, generated_from_policy=str(path)))
    return safe


def render_prompt(task: Task) -> str:
    verification = "\n".join(f"- {cmd}" for cmd in task.verification_commands)
    safety_flags = ", ".join(task.safety_flags)
    generated = (
        f"Generated from backlog policy: {task.generated_from_policy}\n"
        if task.generated_from_policy
        else ""
    )
    return f"""You are a bounded local coding worker inside this repository.

{SAFETY_RULES}{generated}Task id: {task.task_id}
Target issue/area: {task.target}
Goal:
{task.goal}

Allowed scope:
{task.allowed_scope}

Non-goals:
{task.non_goals}

Safety flags: {safety_flags}
Stop/continue recommendation: {task.stop_continue}

Verification commands for this task:
{verification}

Worker requirements:
- Work only on this task's allowed scope.
- Treat the allowed scope as a ceiling; do not broaden scope to create work.
- If a generated or repeated task has no remaining safe scoped change, report that honestly instead of inventing edits.
- Do not spawn nested Hermes/Codex/tmux/cron workers.
- Run the relevant verification commands you can safely run.
- Run each verification command from the repository root in an isolated shell; do not let a `cd ... && ...` command change the working directory for later root-relative guard commands.
- If you make safe tracked changes, commit only those safe tracked changes after verification so the supervisor can continue from a clean tree.
- Do not commit ignored `.hermes` runtime files, private data, generated backups, exports, screenshots, secrets, or other runtime artifacts.
- If you cannot safely commit, leave an honest checkpoint with the exact dirty files and blocker.
- Report concise status, changed files, test output, and safety notes.

Final non-interactive worker instruction: if you make safe tracked changes, run the task verification commands, then commit those safe tracked changes before final response so the supervisor can continue with a clean tree. Do not commit ignored `.hermes` runtime files or private/runtime artifacts. If you cannot safely commit, explain the exact blocker.
"""


def detect_transient_failure(result: AgentResult) -> bool:
    output = result.combined_output.lower()
    return any(marker in output for marker in TRANSIENT_MARKERS)


def write_github_state(repo: Path, run_root: Path) -> str | None:
    gh = shutil_which("gh")
    if not gh:
        return None
    out = run_root / "github-state.txt"
    lines: list[str] = []
    commands = [
        ["gh", "issue", "list", "--state", "open", "--limit", "50"],
        ["gh", "pr", "list", "--state", "open", "--limit", "20"],
        ["gh", "release", "list", "--limit", "20"],
        ["gh", "run", "list", "--limit", "10"],
    ]
    for cmd in commands:
        lines.append(f"$ {' '.join(cmd)}")
        try:
            completed = subprocess.run(cmd, cwd=repo, text=True, capture_output=True, timeout=60)
            lines.append(f"rc={completed.returncode}")
            lines.append(completed.stdout.strip())
            if completed.stderr.strip():
                lines.append("stderr: " + completed.stderr.strip())
        except Exception as exc:  # best effort only
            lines.append(f"error: {exc}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(out)


def shutil_which(name: str) -> str | None:
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(directory) / name
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def write_report(report: SupervisorReport, path: Path) -> None:
    lines = [
        f"# Autonomy supervisor run report",
        "",
        f"Status: {report.status}",
        f"Mode: {report.mode}",
        f"Queue: {report.queue_path}",
        f"Run root: {report.run_root}",
        f"Min runtime seconds: {report.min_runtime_seconds:g}",
        f"Min tasks: {report.min_tasks}",
        f"On empty: {report.on_empty}",
    ]
    if report.backlog_policy_path:
        lines.append(f"Backlog policy: {report.backlog_policy_path}")
    if report.stop_reason:
        lines.extend(["", f"Stop reason: {report.stop_reason}"])
    lines.extend(["", "## Tasks"])
    for item in report.tasks:
        lines.extend(
            [
                f"- {item.task_id}: {item.status}",
                f"  - attempts: {item.attempts}",
                f"  - head_before: {item.head_before}",
                f"  - prompt_path: {item.prompt_path}",
                f"  - message: {item.message}",
            ]
        )
    if report.github_state_path:
        lines.extend(["", f"GitHub state: {report.github_state_path}"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    report.final_report_path = str(path)


def minimums_met(task_count: int, elapsed: float, min_tasks: int, min_runtime_seconds: float) -> bool:
    return task_count >= min_tasks and elapsed >= min_runtime_seconds


def make_generated_task(template: Task, generation: int, cycle: int) -> Task:
    if cycle <= 1:
        return template
    return dataclasses.replace(template, task_id=f"{template.task_id}-r{cycle}")


def safe_prompt_slug(task_id: str) -> str:
    """Return a path-safe slug for prompt filenames derived from policy task IDs."""
    slug = re.sub(r"[^A-Za-z0-9_-]+", "-", task_id).strip("-_")
    return (slug or "task")[:120]


def choose_next_task(
    *,
    base_tasks: list[Task],
    queue_index: int,
    on_empty: str,
    backlog_policy_path: Path | None,
    safe_policy_tasks: list[Task] | None,
    generated_count: int,
    mode: str,
) -> tuple[Task | None, int, list[Task] | None, str | None]:
    if queue_index < len(base_tasks):
        return base_tasks[queue_index], queue_index + 1, safe_policy_tasks, None
    if on_empty == "stop":
        return None, queue_index, safe_policy_tasks, None
    if on_empty == "repeat-safe-final":
        if not base_tasks:
            return None, queue_index, safe_policy_tasks, "No queue task exists to repeat safely"
        final_task = base_tasks[-1]
        flags = {flag.lower() for flag in final_task.safety_flags}
        if "no-release" not in flags or "no-private-data" not in flags:
            return None, queue_index, safe_policy_tasks, "Final queue task is not marked safe to repeat"
        return make_generated_task(final_task, generated_count + 1, 1), queue_index, safe_policy_tasks, None
    if on_empty != "generate-from-policy":
        return None, queue_index, safe_policy_tasks, f"unsupported on-empty mode: {on_empty}"
    if backlog_policy_path is None:
        return None, queue_index, safe_policy_tasks, "--backlog-policy is required for generate-from-policy"
    if safe_policy_tasks is None:
        safe_policy_tasks = load_safe_policy_tasks(backlog_policy_path)
    if not safe_policy_tasks:
        return None, queue_index, safe_policy_tasks, f"No safe backlog policy task found in {backlog_policy_path}"
    if mode == "dry-run" and generated_count >= len(safe_policy_tasks):
        return None, queue_index, safe_policy_tasks, "No further safe dry-run policy templates remain after one preview pass"
    index = generated_count % len(safe_policy_tasks)
    cycle = generated_count // len(safe_policy_tasks) + 1
    return make_generated_task(safe_policy_tasks[index], generated_count + 1, cycle), queue_index, safe_policy_tasks, None


def run_supervisor(
    *,
    repo: Path,
    queue_path: Path,
    budget_seconds: float,
    mode: str,
    run_root: Path,
    git: GitGuard | object | None = None,
    agent: SubprocessAgent | object | None = None,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    max_retries: int = 2,
    backoff_seconds: float = 30.0,
    final_report_path: Path | None = None,
    collect_github: bool = False,
    min_runtime_seconds: float = 0.0,
    min_tasks: int = 0,
    on_empty: str = "stop",
    backlog_policy_path: Path | None = None,
) -> SupervisorReport:
    if mode not in {"dry-run", "live"}:
        raise SupervisorError("mode must be dry-run or live")
    if on_empty not in ON_EMPTY_CHOICES:
        raise SupervisorError(f"on-empty must be one of: {', '.join(ON_EMPTY_CHOICES)}")
    if min_runtime_seconds < 0 or min_tasks < 0:
        raise SupervisorError("minimum runtime/tasks must be non-negative")
    repo = repo.resolve()
    queue_path = queue_path.resolve()
    backlog_policy_path = backlog_policy_path.resolve() if backlog_policy_path else None
    run_root.mkdir(parents=True, exist_ok=True)
    prompt_dir = run_root / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    git = git or GitGuard()
    agent = agent or SubprocessAgent.from_environment(mode)
    base_tasks = parse_queue(queue_path)
    safe_policy_tasks: list[Task] | None = None
    started = clock()
    task_reports: list[TaskReport] = []
    status = "COMPLETED_NO_SAFE_TASKS"
    stop_reason = "finite queue exhausted"
    queue_index = 0
    generated_count = 0

    while True:
        now = clock()
        elapsed = now - started
        if elapsed >= budget_seconds:
            status = "BUDGET_EXPIRED"
            stop_reason = "wall-clock budget expired"
            break

        task, queue_index, safe_policy_tasks, empty_reason = choose_next_task(
            base_tasks=base_tasks,
            queue_index=queue_index,
            on_empty=on_empty,
            backlog_policy_path=backlog_policy_path,
            safe_policy_tasks=safe_policy_tasks,
            generated_count=generated_count,
            mode=mode,
        )
        if task is None:
            if minimums_met(len(task_reports), elapsed, min_tasks, min_runtime_seconds):
                status = "COMPLETED_MINIMUMS_MET" if (min_tasks or min_runtime_seconds) else "COMPLETED_NO_SAFE_TASKS"
                stop_reason = empty_reason or "queue exhausted and configured minimums are met"
            elif on_empty == "stop" and not (min_tasks or min_runtime_seconds):
                status = "COMPLETED_NO_SAFE_TASKS"
                stop_reason = "finite queue exhausted"
            else:
                status = "HARD_NO_SAFE_TASKS"
                stop_reason = empty_reason or "queue exhausted before configured minimums and no safe task source is available"
            break
        if task.generated_from_policy or (on_empty == "repeat-safe-final" and queue_index >= len(base_tasks)):
            generated_count += 1

        dirty_before = git.status(repo)
        if dirty_before:
            status = "CHECKPOINT_DIRTY_TREE"
            stop_reason = "dirty tree before task"
            break
        head_before = git.head(repo)
        prompt_path = prompt_dir / f"{len(task_reports)+1:03d}-{safe_prompt_slug(task.task_id)}.md"
        prompt_path.write_text(render_prompt(task), encoding="utf-8")
        attempts = 0
        while True:
            attempts += 1
            last_result = agent.run(prompt_path, mode)
            if mode == "dry-run":
                task_status = "SIMULATED"
                message = "dry-run rendered prompt; agent not invoked"
                break
            if last_result.returncode == 0:
                task_status = "SUCCESS"
                message = (last_result.stdout or "worker completed successfully").strip()[:1000]
                break
            transient = detect_transient_failure(last_result)
            if transient and attempts <= max_retries:
                sleep(backoff_seconds * attempts)
                continue
            if transient:
                status = "CHECKPOINT_RETRYABLE_FAILURE"
                task_status = "RETRYABLE_FAILURE"
                stop_reason = "retryable worker failure exhausted retries"
            else:
                status = "CHECKPOINT_WORKER_FAILURE"
                task_status = "WORKER_FAILURE"
                stop_reason = "worker failed with non-transient error"
            message = last_result.combined_output.strip()[:1000]
            break
        task_reports.append(
            TaskReport(
                task_id=task.task_id,
                status=task_status,
                attempts=attempts,
                head_before=head_before,
                prompt_path=str(prompt_path),
                message=message,
            )
        )
        if status.startswith("CHECKPOINT"):
            break
        dirty_after = git.status(repo)
        if dirty_after:
            status = "CHECKPOINT_DIRTY_TREE"
            stop_reason = "dirty tree after task"
            break

    github_state_path = write_github_state(repo, run_root) if collect_github else None
    report = SupervisorReport(
        status=status,
        mode=mode,
        queue_path=str(queue_path),
        run_root=str(run_root),
        tasks=task_reports,
        github_state_path=github_state_path,
        stop_reason=stop_reason,
        min_runtime_seconds=min_runtime_seconds,
        min_tasks=min_tasks,
        on_empty=on_empty,
        backlog_policy_path=str(backlog_policy_path) if backlog_policy_path else None,
    )
    if final_report_path is None:
        final_report_path = run_root / "final-report.md"
    write_report(report, final_report_path)
    return report


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="repository root, default current directory")
    parser.add_argument("--queue", required=True, help="queue file under docs/autonomy/queues/")
    parser.add_argument("--budget-hours", type=float, required=True, help="wall-clock budget upper bound")
    parser.add_argument("--mode", choices=["dry-run", "live"], default="dry-run")
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--backoff-seconds", type=float, default=30.0)
    parser.add_argument("--final-report", help="report path; defaults to ignored run directory")
    parser.add_argument("--collect-github", action="store_true", help="best-effort gh state snapshot")
    parser.add_argument("--min-runtime-hours", type=float, default=0.0, help="minimum desired runtime before stopping when safe tasks remain")
    parser.add_argument("--min-tasks", type=int, default=0, help="minimum desired number of tasks before stopping when safe tasks remain")
    parser.add_argument("--on-empty", choices=ON_EMPTY_CHOICES, default="stop", help="behavior when the queue is exhausted before minimums")
    parser.add_argument("--backlog-policy", help="Markdown backlog policy used by --on-empty generate-from-policy")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo = Path(args.repo).resolve()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_root = repo / ".hermes" / "autonomy" / "runs" / stamp
    try:
        report = run_supervisor(
            repo=repo,
            queue_path=Path(args.queue),
            budget_seconds=args.budget_hours * 3600,
            mode=args.mode,
            run_root=run_root,
            max_retries=args.max_retries,
            backoff_seconds=args.backoff_seconds,
            final_report_path=Path(args.final_report) if args.final_report else None,
            collect_github=args.collect_github,
            min_runtime_seconds=args.min_runtime_hours * 3600,
            min_tasks=args.min_tasks,
            on_empty=args.on_empty,
            backlog_policy_path=Path(args.backlog_policy) if args.backlog_policy else None,
        )
    except SupervisorError as exc:
        print(f"supervisor: {exc}", file=sys.stderr)
        return 2
    print(f"status={report.status}")
    print(f"run_root={report.run_root}")
    print(f"final_report={report.final_report_path}")
    if report.stop_reason:
        print(f"stop_reason={report.stop_reason}")
    ok_statuses = {"COMPLETED_NO_SAFE_TASKS", "BUDGET_EXPIRED", "COMPLETED_MINIMUMS_MET"}
    return 0 if report.status in ok_statuses else 1


if __name__ == "__main__":
    raise SystemExit(main())
