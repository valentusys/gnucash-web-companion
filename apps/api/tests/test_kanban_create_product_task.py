"""Tests for the repo-local Hermes product-task creation wrapper."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "kanban" / "create_product_task.py"

spec = importlib.util.spec_from_file_location("create_product_task", SCRIPT_PATH)
assert spec is not None
create_product_task = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["create_product_task"] = create_product_task
spec.loader.exec_module(create_product_task)

FIXED_NOW = datetime(2026, 7, 12, 20, 30, 45, tzinfo=timezone.utc)
CURRENT_WORKTREE = Path("/tmp/gnucash-web-companion/.worktrees/t_task")
MAIN_WORKTREE = Path("/tmp/gnucash-web-companion")


def base_args(*extra: str) -> list[str]:
    return [
        "--board",
        "gnucash-product-run-3",
        "--title",
        "Implement safe product task",
        "--assignee",
        "backend-worker",
        "--branch-suffix",
        "issue53-backend",
        "--body",
        "Concrete bounded task body.",
        "--max-runtime",
        "2h",
        "--max-retries",
        "1",
        *extra,
    ]


class FakeRunner:
    def __init__(
        self,
        *,
        main_status: str = "",
        main_head: str = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        origin_head: str = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        diagnostics: str = "[]",
        create_stdout: str = '{"task_id": "t_deadbeef"}',
    ) -> None:
        self.main_status = main_status
        self.main_head = main_head
        self.origin_head = origin_head
        self.diagnostics = diagnostics
        self.create_stdout = create_stdout
        self.calls: list[tuple[list[str], Path | None]] = []

    def run(self, args: list[str], *, cwd: Path | None = None):
        assert isinstance(args, list)
        assert all(isinstance(item, str) for item in args)
        assert "shell=True" not in args
        self.calls.append((list(args), cwd))
        if args == ["git", "rev-parse", "--show-toplevel"]:
            return create_product_task.CommandResult(0, f"{CURRENT_WORKTREE}\n", "")
        if args == ["git", "config", "--get", "remote.origin.url"]:
            return create_product_task.CommandResult(0, "https://github.com/valentusys/gnucash-web-companion.git\n", "")
        if args == ["git", "worktree", "list", "--porcelain"]:
            return create_product_task.CommandResult(
                0,
                (
                    f"worktree {MAIN_WORKTREE}\n"
                    f"HEAD {self.main_head}\n"
                    "branch refs/heads/main\n\n"
                    f"worktree {CURRENT_WORKTREE}\n"
                    "HEAD bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n"
                    "branch refs/heads/kanban-product-3/task-wrapper\n"
                ),
                "",
            )
        if args == ["git", "-C", str(MAIN_WORKTREE), "status", "--porcelain"]:
            return create_product_task.CommandResult(0, self.main_status, "")
        if args == ["git", "-C", str(MAIN_WORKTREE), "rev-parse", "main"]:
            return create_product_task.CommandResult(0, f"{self.main_head}\n", "")
        if args == ["git", "-C", str(MAIN_WORKTREE), "rev-parse", "origin/main"]:
            return create_product_task.CommandResult(0, f"{self.origin_head}\n", "")
        if args == ["hermes", "kanban", "--board", "gnucash-product-run-3", "diagnostics", "--json"]:
            return create_product_task.CommandResult(0, self.diagnostics, "")
        if args[:5] == ["hermes", "kanban", "--board", "gnucash-product-run-3", "create"]:
            return create_product_task.CommandResult(0, self.create_stdout, "")
        raise AssertionError(f"unexpected command: {args!r}")


def test_build_command_sets_fixed_linkage_fields_unique_branch_and_parents() -> None:
    spec_obj = create_product_task.prepare_spec(
        base_args("--parent", "t_1234abcd", "--parent", "t_deadbeef", "--priority", "90"),
        now=FIXED_NOW,
        token_provider=lambda: "abc12345",
    )

    command = create_product_task.build_create_command(spec_obj)

    assert command[:5] == ["hermes", "kanban", "--board", "gnucash-product-run-3", "create"]
    assert command[5] == "Implement safe product task"
    assert command[command.index("--project") + 1] == "gnucash-web-companion"
    assert command[command.index("--workspace") + 1] == "worktree"
    assert command[command.index("--created-by") + 1] == "gnucash-product-task-wrapper"
    assert command[command.index("--max-runtime") + 1] == "2h"
    assert command[command.index("--max-retries") + 1] == "1"
    assert command[command.index("--priority") + 1] == "90"
    assert command[command.index("--branch") + 1] == "run/product/issue53-backend-20260712T203045Z-abc12345"
    parent_positions = [index for index, item in enumerate(command) if item == "--parent"]
    assert [command[index + 1] for index in parent_positions] == ["t_1234abcd", "t_deadbeef"]
    assert "--json" in command


def test_body_value_is_single_argument_even_when_it_looks_option_like() -> None:
    spec_obj = create_product_task.prepare_spec(
        base_args("--body", "--not-a-cli-option\nreal body"),
        now=FIXED_NOW,
        token_provider=lambda: "abc12345",
    )

    command = create_product_task.build_create_command(spec_obj)

    assert "--body=--not-a-cli-option\nreal body" in command
    assert "--not-a-cli-option\nreal body" not in command


def test_unique_branch_generation_changes_token() -> None:
    first = create_product_task.make_branch("issue53-backend", now=FIXED_NOW, token="abc12345")
    second = create_product_task.make_branch("issue53-backend", now=FIXED_NOW, token="def67890")

    assert first == "run/product/issue53-backend-20260712T203045Z-abc12345"
    assert second == "run/product/issue53-backend-20260712T203045Z-def67890"
    assert first != second


def test_empty_body_unsafe_branch_unsupported_assignee_and_argument_paths_rejected() -> None:
    bad_cases = [
        base_args("--body", "   "),
        base_args("--branch-suffix", "../escape"),
        base_args("--branch-suffix", "--flag"),
        base_args("--assignee", "unknown-worker"),
        base_args("--board", "--help"),
        base_args("--parent", "--not-a-task"),
        [arg for arg in base_args() if arg not in {"--body", "Concrete bounded task body."}] + ["--body-file=--help"],
    ]

    for args in bad_cases:
        stdout = io.StringIO()
        stderr = io.StringIO()
        rc = create_product_task.main(args, runner=FailingRunner(), stdout=stdout, stderr=stderr)
        assert rc == 2
        assert stdout.getvalue() == ""
        assert stderr.getvalue().startswith("error: ")


class FailingRunner:
    def run(self, args: list[str], *, cwd: Path | None = None):
        raise AssertionError(f"dry-run/validation must not spawn subprocesses: {args!r}")


def test_dry_run_outputs_redacted_command_and_creates_no_subprocess() -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()

    rc = create_product_task.main(
        base_args("--dry-run", "--parent", "t_1234abcd"),
        runner=FailingRunner(),
        stdout=stdout,
        stderr=stderr,
        now=FIXED_NOW,
        token_provider=lambda: "abc12345",
    )

    assert rc == 0
    assert stderr.getvalue() == ""
    payload = json.loads(stdout.getvalue())
    assert payload["dry_run"] is True
    assert "--body=<redacted body chars=27>" in payload["command"]
    assert "Concrete bounded task body." not in stdout.getvalue()
    assert payload["preflight"] == "skipped-for-dry-run"
    assert payload["command"][payload["command"].index("--parent") + 1] == "t_1234abcd"


def test_live_create_refuses_dirty_main_before_create() -> None:
    runner = FakeRunner(main_status=" M README.md\n")
    stdout = io.StringIO()
    stderr = io.StringIO()

    rc = create_product_task.main(
        base_args(),
        runner=runner,
        stdout=stdout,
        stderr=stderr,
        now=FIXED_NOW,
        token_provider=lambda: "abc12345",
        cwd=CURRENT_WORKTREE,
    )

    assert rc == 2
    assert "main worktree is dirty" in stderr.getvalue()
    assert not any(call[0][:5] == ["hermes", "kanban", "--board", "gnucash-product-run-3", "create"] for call in runner.calls)


def test_live_create_refuses_when_main_differs_from_origin() -> None:
    runner = FakeRunner(origin_head="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
    stdout = io.StringIO()
    stderr = io.StringIO()

    rc = create_product_task.main(
        base_args(),
        runner=runner,
        stdout=stdout,
        stderr=stderr,
        now=FIXED_NOW,
        token_provider=lambda: "abc12345",
        cwd=CURRENT_WORKTREE,
    )

    assert rc == 2
    assert "main differs from origin/main" in stderr.getvalue()
    assert not any(call[0][:5] == ["hermes", "kanban", "--board", "gnucash-product-run-3", "create"] for call in runner.calls)


def test_live_create_refuses_non_clean_board_diagnostics() -> None:
    runner = FakeRunner(diagnostics='[{"severity": "error", "message": "blocked"}]')
    stdout = io.StringIO()
    stderr = io.StringIO()

    rc = create_product_task.main(
        base_args(),
        runner=runner,
        stdout=stdout,
        stderr=stderr,
        now=FIXED_NOW,
        token_provider=lambda: "abc12345",
        cwd=CURRENT_WORKTREE,
    )

    assert rc == 2
    assert "board diagnostics are not clean" in stderr.getvalue()
    assert not any(call[0][:5] == ["hermes", "kanban", "--board", "gnucash-product-run-3", "create"] for call in runner.calls)


def test_live_create_uses_list_args_no_shell_and_prints_created_task_id() -> None:
    runner = FakeRunner(create_stdout='{"task": {"id": "t_deadbeef"}}')
    stdout = io.StringIO()
    stderr = io.StringIO()

    rc = create_product_task.main(
        base_args("--parent", "t_1234abcd"),
        runner=runner,
        stdout=stdout,
        stderr=stderr,
        now=FIXED_NOW,
        token_provider=lambda: "abc12345",
        cwd=CURRENT_WORKTREE,
    )

    assert rc == 0
    assert stderr.getvalue() == ""
    assert "created_task_id=t_deadbeef" in stdout.getvalue()
    create_calls = [call for call in runner.calls if call[0][:5] == ["hermes", "kanban", "--board", "gnucash-product-run-3", "create"]]
    assert len(create_calls) == 1
    command = create_calls[0][0]
    assert command[command.index("--parent") + 1] == "t_1234abcd"
    assert "--body=Concrete bounded task body." in command


def test_json_task_id_parser_accepts_known_hermes_shapes() -> None:
    assert create_product_task.extract_task_id('{"id": "t_deadbeef"}') == "t_deadbeef"
    assert create_product_task.extract_task_id('{"task_id": "t_deadbeef"}') == "t_deadbeef"
    assert create_product_task.extract_task_id('{"task": {"id": "t_deadbeef"}}') == "t_deadbeef"
    assert create_product_task.extract_task_id("created task t_deadbeef") == "t_deadbeef"
