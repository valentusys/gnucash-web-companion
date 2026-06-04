import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.autonomy import supervisor


SAMPLE_QUEUE = """
# Sample Queue

## Task: docs-one
- target: docs
- goal: Improve one runbook section.
- allowed scope: docs only
- non-goals: product code; releases
- verification commands:
  - python3 scripts/check_public_status.py
  - git diff --check
- safety flags: no-private-data, no-release
- stop/continue recommendation: continue

## Task: docs-two
- target: docs
- goal: Improve another runbook section.
- allowed scope: docs only
- non-goals: product code; releases
- verification commands:
  - git diff --check
- safety flags: no-private-data, no-release
- stop/continue recommendation: stop if dirty
"""


class FakeClock:
    def __init__(self, values):
        self.values = list(values)
        self.last = self.values[-1] if self.values else 0.0

    def __call__(self):
        if self.values:
            self.last = self.values.pop(0)
        return self.last


class FakeGit:
    def __init__(self, statuses=None):
        self.statuses = list(statuses or [""])
        self.heads = []

    def head(self, repo):
        self.heads.append(repo)
        return f"head-{len(self.heads)}"

    def status(self, repo):
        if len(self.statuses) > 1:
            return self.statuses.pop(0)
        return self.statuses[0]


class FakeAgent:
    def __init__(self, results):
        self.results = list(results)
        self.prompts = []

    def run(self, prompt_path, mode):
        self.prompts.append(Path(prompt_path).read_text(encoding="utf-8"))
        return self.results.pop(0)


def write_queue(tmp_path, text=SAMPLE_QUEUE):
    queue = tmp_path / "queue.md"
    queue.write_text(text, encoding="utf-8")
    return queue


def test_parse_queue_requires_all_task_fields(tmp_path):
    queue = write_queue(tmp_path)

    tasks = supervisor.parse_queue(queue)

    assert [task.task_id for task in tasks] == ["docs-one", "docs-two"]
    assert tasks[0].verification_commands == [
        "python3 scripts/check_public_status.py",
        "git diff --check",
    ]
    assert "no-private-data" in tasks[0].safety_flags


def test_dry_run_renders_prompts_and_continues_after_early_success(tmp_path):
    queue = write_queue(tmp_path)
    git = FakeGit([""])
    agent = FakeAgent([
        supervisor.AgentResult(0, "simulated task one complete", ""),
        supervisor.AgentResult(0, "simulated task two complete", ""),
    ])

    report = supervisor.run_supervisor(
        repo=tmp_path,
        queue_path=queue,
        budget_seconds=3600,
        mode="dry-run",
        run_root=tmp_path / ".hermes" / "autonomy" / "runs" / "test",
        git=git,
        agent=agent,
        clock=FakeClock([0, 1, 2, 3, 4]),
    )

    assert report.status == "COMPLETED_NO_SAFE_TASKS"
    assert [item.task_id for item in report.tasks] == ["docs-one", "docs-two"]
    assert all(item.status == "SIMULATED" for item in report.tasks)
    assert len(agent.prompts) == 2
    assert "Never touch original/private/working/only-copy GnuCash books." in agent.prompts[0]
    assert "GNUCASH_WRITES_ENABLED=false" in agent.prompts[0]
    assert "APP_ENV=test" in agent.prompts[0]


def test_budget_expiry_stops_before_next_task(tmp_path):
    queue = write_queue(tmp_path)
    report = supervisor.run_supervisor(
        repo=tmp_path,
        queue_path=queue,
        budget_seconds=1,
        mode="dry-run",
        run_root=tmp_path / "run",
        git=FakeGit([""]),
        agent=FakeAgent([supervisor.AgentResult(0, "ok", "")]),
        clock=FakeClock([0, 0.5, 2.0]),
    )

    assert report.status == "BUDGET_EXPIRED"
    assert [item.task_id for item in report.tasks] == ["docs-one"]


def test_rate_limit_triggers_bounded_retry_then_checkpoint(tmp_path):
    queue = write_queue(tmp_path, SAMPLE_QUEUE.replace("## Task: docs-two", "## Not a task: docs-two"))
    report = supervisor.run_supervisor(
        repo=tmp_path,
        queue_path=queue,
        budget_seconds=3600,
        mode="live",
        run_root=tmp_path / "run",
        git=FakeGit([""]),
        agent=FakeAgent([
            supervisor.AgentResult(1, "", "429 rate limit"),
            supervisor.AgentResult(1, "timeout", ""),
        ]),
        clock=FakeClock([0, 1, 2, 3]),
        max_retries=1,
        sleep=lambda seconds: None,
    )

    assert report.status == "CHECKPOINT_RETRYABLE_FAILURE"
    assert len(report.tasks) == 1
    assert report.tasks[0].attempts == 2
    assert "rate limit" in report.tasks[0].message.lower() or "timeout" in report.tasks[0].message.lower()


def test_dirty_tree_blocks_continuation(tmp_path):
    queue = write_queue(tmp_path)
    report = supervisor.run_supervisor(
        repo=tmp_path,
        queue_path=queue,
        budget_seconds=3600,
        mode="dry-run",
        run_root=tmp_path / "run",
        git=FakeGit([" M docs/file.md"]),
        agent=FakeAgent([]),
        clock=FakeClock([0, 1]),
    )

    assert report.status == "CHECKPOINT_DIRTY_TREE"
    assert report.tasks == []


def test_missing_live_command_fails_closed(monkeypatch, tmp_path):
    monkeypatch.delenv("AUTONOMY_AGENT_COMMAND", raising=False)

    try:
        supervisor.SubprocessAgent.from_environment(mode="live")
    except supervisor.SupervisorError as exc:
        assert "AUTONOMY_AGENT_COMMAND" in str(exc)
    else:
        raise AssertionError("live mode without command must fail closed")


def test_rendered_prompt_contains_required_safety_patterns(tmp_path):
    task = supervisor.Task(
        task_id="safety",
        target="docs",
        goal="Document safety.",
        allowed_scope="docs only",
        non_goals="release; write mode",
        verification_commands=["git diff --check"],
        safety_flags=["no-private-data", "no-release"],
        stop_continue="continue",
    )

    prompt = supervisor.render_prompt(task)

    required = [
        "Never touch original/private/working/only-copy GnuCash books.",
        "Never commit GnuCash books",
        "Do not publish releases, tags, packages, or images.",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "No public write beta",
    ]
    for pattern in required:
        assert pattern in prompt
