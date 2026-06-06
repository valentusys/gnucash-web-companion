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

SAMPLE_POLICY = """
# Sample backlog policy

## Task: generated-audit
- target: issue #36 / generated audit
- goal: Audit owner-writebeta remaining gates without touching private data.
- allowed scope: docs and tests only
- non-goals: GnuCash mutations; private books; releases; public write beta claims
- verification commands:
  - python3 scripts/check_public_status.py
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, preserve-write-defaults, app-env-test-gated-writes
- stop/continue recommendation: continue if clean

## Task: generated-final-gate
- target: issue #36 / generated final gate
- goal: Prepare a final gate report without dogfood or release publication.
- allowed scope: docs/handoff only
- non-goals: GnuCash mutations; private books; releases; public write beta claims
- verification commands:
  - cd apps/api && pytest -q
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release, final-gates
- stop/continue recommendation: stop when full gate is recorded
"""

UNSAFE_POLICY = """
# Unsafe backlog policy

## Task: unsafe-release
- target: release
- goal: Publish a write beta release.
- allowed scope: release tooling
- non-goals: none
- verification commands:
  - git diff --check
- safety flags: release, touches-private-data
- stop/continue recommendation: continue
"""

UNSAFE_GENERATED_RELEASE_POLICY = """
# Unsafe generated backlog policy

## Task: unsafe-generated-release
- target: issue #36 / unsafe generated release
- goal: Publish a write beta release announcement.
- allowed scope: docs/release only
- non-goals: private books; GnuCash mutations
- verification commands:
  - git diff --check
- safety flags: generated-safe, no-private-data, no-release
- stop/continue recommendation: continue
"""

UNSAFE_GENERATED_VERIFICATION_POLICY = """
# Unsafe generated verification policy

## Task: unsafe-generated-verification
- target: issue #36 / unsafe generated verification
- goal: Prepare safe owner-writebeta docs.
- allowed scope: docs only
- non-goals: private books; GnuCash mutations; release publication
- verification commands:
  - git diff --check
  - gh release create v0.2.9-writealpha
- safety flags: generated-safe, no-private-data, no-release
- stop/continue recommendation: continue
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


class RepeatingFakeAgent:
    def __init__(self, result=None):
        self.result = result or supervisor.AgentResult(0, "ok", "")
        self.prompts = []

    def run(self, prompt_path, mode):
        self.prompts.append(Path(prompt_path).read_text(encoding="utf-8"))
        return self.result


def write_queue(tmp_path, text=SAMPLE_QUEUE):
    queue = tmp_path / "queue.md"
    queue.write_text(text, encoding="utf-8")
    return queue


def write_policy(tmp_path, text=SAMPLE_POLICY):
    policy = tmp_path / "policy.md"
    policy.write_text(text, encoding="utf-8")
    return policy


def test_parse_queue_requires_all_task_fields(tmp_path):
    queue = write_queue(tmp_path)

    tasks = supervisor.parse_queue(queue)

    assert [task.task_id for task in tasks] == ["docs-one", "docs-two"]
    assert tasks[0].verification_commands == [
        "python3 scripts/check_public_status.py",
        "git diff --check",
    ]
    assert "no-private-data" in tasks[0].safety_flags


def test_finite_queue_still_exits_as_before_by_default(tmp_path):
    queue = write_queue(tmp_path)
    agent = RepeatingFakeAgent()

    report = supervisor.run_supervisor(
        repo=tmp_path,
        queue_path=queue,
        budget_seconds=3600,
        mode="dry-run",
        run_root=tmp_path / "run",
        git=FakeGit([""]),
        agent=agent,
        clock=FakeClock([0, 1, 2, 3, 4]),
    )

    assert report.status == "COMPLETED_NO_SAFE_TASKS"
    assert [item.task_id for item in report.tasks] == ["docs-one", "docs-two"]
    assert len(agent.prompts) == 2


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


def test_min_tasks_with_generated_policy_continues_after_queue_exhaustion(tmp_path):
    queue = write_queue(tmp_path, SAMPLE_QUEUE.replace("## Task: docs-two", "## Not a task: docs-two"))
    policy = write_policy(tmp_path)
    agent = RepeatingFakeAgent()

    report = supervisor.run_supervisor(
        repo=tmp_path,
        queue_path=queue,
        budget_seconds=3600,
        mode="dry-run",
        run_root=tmp_path / "run",
        git=FakeGit([""]),
        agent=agent,
        clock=FakeClock([0, 1, 2, 3, 4, 5]),
        min_tasks=3,
        on_empty="generate-from-policy",
        backlog_policy_path=policy,
    )

    assert report.status == "COMPLETED_MINIMUMS_MET"
    assert [item.task_id for item in report.tasks] == [
        "docs-one",
        "generated-audit",
        "generated-final-gate",
    ]
    assert len(agent.prompts) == 3
    assert "Generated from backlog policy" in agent.prompts[-1]


def test_min_runtime_hours_does_not_report_early_if_safe_generated_tasks_remain(tmp_path):
    queue = write_queue(tmp_path, SAMPLE_QUEUE.replace("## Task: docs-two", "## Not a task: docs-two"))
    policy = write_policy(tmp_path)
    agent = RepeatingFakeAgent()

    report = supervisor.run_supervisor(
        repo=tmp_path,
        queue_path=queue,
        budget_seconds=3600,
        mode="dry-run",
        run_root=tmp_path / "run",
        git=FakeGit([""]),
        agent=agent,
        clock=FakeClock([0, 1, 2, 1801, 1802]),
        min_runtime_seconds=1800,
        on_empty="generate-from-policy",
        backlog_policy_path=policy,
    )

    assert report.status == "COMPLETED_MINIMUMS_MET"
    assert [item.task_id for item in report.tasks] == [
        "docs-one",
        "generated-audit",
        "generated-final-gate",
    ]


def test_generate_from_policy_stops_fail_closed_if_policy_has_no_safe_tasks(tmp_path):
    queue = write_queue(tmp_path, SAMPLE_QUEUE.replace("## Task: docs-two", "## Not a task: docs-two"))
    policy = write_policy(tmp_path, UNSAFE_POLICY)

    report = supervisor.run_supervisor(
        repo=tmp_path,
        queue_path=queue,
        budget_seconds=3600,
        mode="dry-run",
        run_root=tmp_path / "run",
        git=FakeGit([""]),
        agent=RepeatingFakeAgent(),
        clock=FakeClock([0, 1, 2, 3]),
        min_tasks=2,
        on_empty="generate-from-policy",
        backlog_policy_path=policy,
    )

    assert report.status == "HARD_NO_SAFE_TASKS"
    assert len(report.tasks) == 1
    assert "No safe backlog policy task" in report.stop_reason


def test_generated_policy_rejects_public_write_beta_release_claims(tmp_path):
    policy = write_policy(tmp_path, UNSAFE_GENERATED_RELEASE_POLICY)

    assert supervisor.load_safe_policy_tasks(policy) == []


def test_generated_policy_rejects_broad_compatibility_claims(tmp_path):
    policy = write_policy(
        tmp_path,
        SAMPLE_POLICY.replace(
            "Audit owner-writebeta remaining gates without touching private data.",
            "Declare broad compatibility is proven for owner-writebeta.",
        ),
    )

    safe_tasks = supervisor.load_safe_policy_tasks(policy)

    assert [task.task_id for task in safe_tasks] == ["generated-final-gate"]


def test_generated_policy_rejects_unsafe_targets(tmp_path):
    policy = write_policy(
        tmp_path,
        SAMPLE_POLICY.replace(
            "- target: issue #36 / generated audit",
            "- target: issue #36 / public write beta rollout",
        ),
    )

    safe_tasks = supervisor.load_safe_policy_tasks(policy)

    assert [task.task_id for task in safe_tasks] == ["generated-final-gate"]


def test_generated_policy_rejects_tag_package_and_image_publication_goals(tmp_path):
    unsafe_goals = (
        "Create tag v0.2.9-writealpha for owner-writebeta.",
        "Publish package artifacts for owner-writebeta.",
        "Publish image artifacts for owner-writebeta.",
    )
    for goal in unsafe_goals:
        policy = write_policy(
            tmp_path,
            SAMPLE_POLICY.replace(
                "Audit owner-writebeta remaining gates without touching private data.",
                goal,
            ),
        )

        assert [task.task_id for task in supervisor.load_safe_policy_tasks(policy)] == [
            "generated-final-gate"
        ]


def test_generated_policy_rejects_release_verification_commands(tmp_path):
    policy = write_policy(tmp_path, UNSAFE_GENERATED_VERIFICATION_POLICY)

    assert supervisor.load_safe_policy_tasks(policy) == []


def test_generated_policy_rejects_release_commands_with_extra_whitespace(tmp_path):
    policy = write_policy(
        tmp_path,
        UNSAFE_GENERATED_VERIFICATION_POLICY.replace(
            "gh release create v0.2.9-writealpha",
            "gh    release create v0.2.9-writealpha",
        ),
    )

    assert supervisor.load_safe_policy_tasks(policy) == []


def test_generated_policy_rejects_indirect_release_publication_commands(tmp_path):
    for command in (
        "git push origin --tags",
        "git push origin main --follow-tags",
        "git push origin v0.2.9-writealpha",
        "git push origin refs/tags/v0.2.9-writealpha",
        "git push origin tag v0.2.9-writealpha",
        "gh api repos/:owner/:repo/releases -f tag_name=v0.2.9-writealpha",
        "docker buildx build . --push -t example/unsafe:latest",
    ):
        policy = write_policy(
            tmp_path,
            UNSAFE_GENERATED_VERIFICATION_POLICY.replace(
                "gh release create v0.2.9-writealpha",
                command,
            ),
        )

        assert supervisor.load_safe_policy_tasks(policy) == []


def test_generated_policy_rejects_indirect_image_publication_commands(tmp_path):
    for command in (
        "docker compose push",
        "docker buildx build . --output=type=registry -t example/unsafe:latest",
        "docker buildx build . --output type=registry -t example/unsafe:latest",
        "docker buildx build . -o=type=registry -t example/unsafe:latest",
        "docker buildx build . -o type=registry -t example/unsafe:latest",
    ):
        policy = write_policy(
            tmp_path,
            UNSAFE_GENERATED_VERIFICATION_POLICY.replace(
                "gh release create v0.2.9-writealpha",
                command,
            ),
        )

        assert supervisor.load_safe_policy_tasks(policy) == []


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


def test_dirty_tree_still_checkpoints(tmp_path):
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


def test_live_mode_still_requires_agent_command(monkeypatch, tmp_path):
    monkeypatch.delenv("AUTONOMY_AGENT_COMMAND", raising=False)

    try:
        supervisor.SubprocessAgent.from_environment(mode="live")
    except supervisor.SupervisorError as exc:
        assert "AUTONOMY_AGENT_COMMAND" in str(exc)
    else:
        raise AssertionError("live mode without command must fail closed")


def test_dry_run_never_invokes_real_agent(monkeypatch, tmp_path):
    monkeypatch.setenv("AUTONOMY_AGENT_COMMAND", "false")
    queue = write_queue(tmp_path)

    report = supervisor.run_supervisor(
        repo=tmp_path,
        queue_path=queue,
        budget_seconds=3600,
        mode="dry-run",
        run_root=tmp_path / "run",
        git=FakeGit([""]),
        clock=FakeClock([0, 1, 2, 3]),
    )

    assert report.status == "COMPLETED_NO_SAFE_TASKS"
    report_text = Path(report.final_report_path).read_text(encoding="utf-8")
    assert "dry-run rendered prompt; agent not invoked" in report_text


def test_parse_args_accepts_v2_options():
    args = supervisor.parse_args([
        "--budget-hours",
        "5",
        "--queue",
        "q.md",
        "--min-runtime-hours",
        "4.5",
        "--min-tasks",
        "8",
        "--on-empty",
        "generate-from-policy",
        "--backlog-policy",
        "policy.md",
    ])

    assert args.min_runtime_hours == 4.5
    assert args.min_tasks == 8
    assert args.on_empty == "generate-from-policy"
    assert args.backlog_policy == "policy.md"


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
        "commit only those safe tracked changes after verification",
        "Treat the allowed scope as a ceiling",
        "no remaining safe scoped change",
        "Run each verification command from the repository root in an isolated shell",
        "Do not commit ignored `.hermes` runtime files",
        "Final non-interactive worker instruction",
        "run the task verification commands, then commit those safe tracked changes before final response",
    ]
    for pattern in required:
        assert pattern in prompt


def test_owner_writebeta_backup_restore_policy_prompt_is_non_mutating():
    policy = REPO_ROOT / "docs/autonomy/backlog-policies/issue36-owner-writebeta.md"

    tasks = supervisor.load_safe_policy_tasks(policy)
    task = next(task for task in tasks if task.task_id == "backup-restore-readiness-docs-tests")
    prompt = supervisor.render_prompt(task)

    required = [
        "Improve non-mutating backup/restore readiness docs or tests",
        "apps/api tests for non-mutating backup/restore documentation or guard behavior",
        "creating backups from private books",
        "restore into real books",
        "dogfood",
        "public write beta claims",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "python3 scripts/check_write_safety_defaults.py",
        "python3 scripts/check_tracked_hygiene.py",
    ]
    for pattern in required:
        assert pattern in prompt


def test_backup_restore_ux_doc_preserves_default_disabled_non_mutating_boundary():
    doc = REPO_ROOT / "docs/write-alpha/backup-restore-ux-design.md"

    text = doc.read_text(encoding="utf-8")

    required = [
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "restore to a separate temporary copy",
        "never overwrite the working book during validation",
        "Backups must never be committed",
        "disabled-write probe must remain a no-op",
        "Failed restore, read-back, or audit evidence is a hard stop",
        "must not claim public write beta readiness",
        "only-copy safety",
        "prerequisites only",
        "must not change the default disabled state",
        "checkpoint and escalate instead of creating backup or restore evidence",
        "NOT_RESTORE_DRILL",
        "NO_BACKUP_ARTIFACT_CREATED",
        "DO_NOT_ENABLE_WRITES",
        "NO_PRIVATE_DATA_REVIEWED",
        "no restore command was run and no restored book was opened",
        "does not authorize changing `GNUCASH_WRITES_ENABLED=false` or relaxing the `APP_ENV=test` gate",
    ]
    for pattern in required:
        assert pattern in text


def test_backup_restore_readiness_checklist_keeps_restore_validation_non_mutating():
    doc = REPO_ROOT / "docs/write-alpha/backup-restore-readiness-checklist.md"

    text = doc.read_text(encoding="utf-8")

    required = [
        "non-mutating guard",
        "does not authorize any CREATE, PATCH, or DELETE operation",
        "must not create backups",
        "must not restore into books",
        "restore-to-copy validation remains non-mutating",
        "does not create backup artifacts, restore artifacts, or app DB records",
        "opaque restore refs and redacted marker summaries only",
        "do not publish filenames, private paths, account names, descriptions, memos, amounts",
        "does not prove broad compatibility or only-copy safety",
        "docs/tests-only restore-readiness wording check",
        "documented no-op expectation under `GNUCASH_WRITES_ENABLED=false`",
        "docs/tests-only wording validation is not recovery proof",
        "filesystem backup copies, restore artifacts, app DB records",
        "private path snippets, account names, transaction descriptions, memos, amounts",
        "backup manifest and checksum wording must use opaque refs plus redacted status summaries only",
        "never raw paths, filenames, account names, memos, amounts, app DB rows, books, or backup artifacts",
        "tracked docs, pure Python guard output, and pytest assertions",
        "write routes are still expected to reject mutation attempts",
        "expected-failure/no-write statement",
        "separate disposable copy",
        "must not overwrite the current copied fixture, original book, working book, or only-copy book",
        "not approval to run dogfood or touch private data",
        "not a fallback to creating filesystem backup or restore evidence",
        "NOT_RESTORE_DRILL",
        "NO_BACKUP_ARTIFACT_CREATED",
        "DO_NOT_ENABLE_WRITES",
        "NO_PRIVATE_DATA_REVIEWED",
        "no restore command was run and no restored book was opened",
        "checkpoint rather than broadening scope into backup creation, restore execution, dogfood, or private-data inspection",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "backup_restore_readiness_scope=docs-tests-only",
        "restore_drill_performed=false",
        "backup_artifact_created=false",
        "private_data_reviewed=false",
        "writes_enabled_or_app_env_gate_relaxed=false",
        "runtime_backup_manifest_reviewed=false",
        "restore_target_opened=false",
    ]
    for pattern in required:
        assert pattern in text


def test_backup_recovery_runbook_keeps_docs_tests_only_readiness_non_mutating():
    doc = REPO_ROOT / "docs/operations/backup-and-recovery.md"

    text = doc.read_text(encoding="utf-8")

    required = [
        "Docs/tests-only restore-readiness wording checks are not restore drills",
        "tracked docs, guard output, and pytest assertions",
        "must not create backup artifacts, restore artifacts, app DB records, filesystem evidence",
        "private paths, account names, memos, amounts, books, or backups",
        "documented no-op expectation under `GNUCASH_WRITES_ENABLED=false`",
        "not an executed product mutation or recovery proof",
        "copied/restorable or synthetic/disposable fixture",
        "APP_ENV=test",
        "prerequisites only",
        "must not claim public write beta readiness",
        "production safety",
        "security-audited status",
        "broad compatibility",
        "only-copy safety",
        "review packets must summarize readiness as redacted pass/fail markers only",
        "must not paste raw manifest output, checksum lines, filenames, private paths, account names, descriptions, memos, amounts, screenshots, exports, app DB rows, books, backups, or runtime logs",
        "Default-disabled safety remains the key assertion: `GNUCASH_WRITES_ENABLED=false` is the committed/default posture",
        "NOT_RESTORE_DRILL",
        "NO_BACKUP_ARTIFACT_CREATED",
        "DO_NOT_ENABLE_WRITES",
        "NO_PRIVATE_DATA_REVIEWED",
        "checkpoint instead of broadening into backup creation, restore execution, dogfood, or private-data inspection",
        "backup_restore_readiness_scope=docs-tests-only",
        "restore_drill_performed=false",
        "backup_artifact_created=false",
        "private_data_reviewed=false",
        "writes_enabled_or_app_env_gate_relaxed=false",
        "runtime_backup_manifest_reviewed=false",
        "restore_target_opened=false",
    ]
    for pattern in required:
        assert pattern in text


def test_restore_safety_boundary_keeps_docs_tests_only_review_non_operational():
    doc = REPO_ROOT / "docs/write-alpha/restore-safety-boundary.md"

    text = doc.read_text(encoding="utf-8")

    required = [
        "Status: non-mutating guard document",
        "Restore-to-copy means a copied/restorable fixture or synthetic/disposable target",
        "must not overwrite a real working book",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "Mutation counts for this boundary package: CREATE 0 / PATCH 0 / DELETE 0",
        "Generated docs/tests-only readiness tasks may inspect tracked wording and guard assertions only",
        "NOT_RESTORE_DRILL",
        "NO_BACKUP_ARTIFACT_CREATED",
        "DO_NOT_ENABLE_WRITES",
        "NO_PRIVATE_DATA_REVIEWED",
        "must not run restore commands, create backup artifacts, open books, mutate GnuCash data",
        "inspect runtime logs, or collect private path evidence",
        "no retry on the same copied/restorable fixture after failed restore, read-back, or audit evidence",
        "recover/regenerate the disposable target and re-run read-only checks first",
        "disabled-write reset probe is a documented no-op expectation under `GNUCASH_WRITES_ENABLED=false`",
        "checkpoint rather than broadening into dogfood, backup creation, restore execution, or private-data inspection",
        "By itself this boundary keeps #36 open",
    ]
    for pattern in required:
        assert pattern in text


def test_render_prompt_for_backup_restore_readiness_docs_task_keeps_non_mutating_bounds():
    task = supervisor.Task(
        task_id="backup-restore-readiness-docs-tests-r7",
        target="issue #36 / backup and restore readiness",
        goal="Improve non-mutating backup/restore readiness docs or tests that validate wording and default-disabled safety without touching private data.",
        allowed_scope="docs/**, scripts/check_* guards, apps/api tests for non-mutating backup/restore documentation or guard behavior",
        non_goals="creating backups from private books; restore into real books; dogfood; release publication; public write beta claims",
        verification_commands=[
            "cd apps/api && pytest tests/test_autonomy_supervisor.py -q",
            "python3 scripts/check_write_safety_defaults.py",
            "python3 scripts/check_tracked_hygiene.py",
            "git diff --check",
        ],
        safety_flags=[
            "generated-safe",
            "no-private-data",
            "no-release",
            "no-dogfood",
            "preserve-write-defaults",
            "app-env-test-gated-writes",
        ],
        stop_continue="continue if changes are non-mutating docs/tests only",
        generated_from_policy="docs/autonomy/backlog-policies/issue36-owner-writebeta.md",
    )

    prompt = supervisor.render_prompt(task)

    assert "Never touch original/private/working/only-copy GnuCash books." in prompt
    assert "Never commit GnuCash books, SQLite books, app DBs, backups" in prompt
    assert "Preserve GNUCASH_WRITES_ENABLED=false" in prompt
    assert "Preserve APP_ENV=test gates" in prompt
    assert "Do not run product dogfood or GnuCash mutations" in prompt
    assert "creating backups from private books; restore into real books" in prompt
    assert "docs/**, scripts/check_* guards, apps/api tests" in prompt
    assert "If a generated or repeated task has no remaining safe scoped change" in prompt
    assert "python3 scripts/check_write_safety_defaults.py" in prompt


def test_discovered_safe_quality_policy_task_remains_bounded_and_guarded():
    policy = REPO_ROOT / "docs/autonomy/backlog-policies/issue36-owner-writebeta.md"

    tasks = supervisor.load_safe_policy_tasks(policy)
    task = next(task for task in tasks if task.task_id == "discovered-safe-quality-fixes-related-to-issue36")
    prompt = supervisor.render_prompt(task)

    assert task.allowed_scope == (
        "docs/**, scripts/check_* guards, apps/api tests, scripts/autonomy/** if the issue relates to autonomous readiness"
    )
    assert "unrelated refactors" in task.non_goals
    assert "GnuCash mutations" in task.non_goals
    assert "dogfood" in task.non_goals
    assert "private/original/working/only-copy books" in task.non_goals
    assert "public write beta claims" in task.non_goals
    assert "no-dogfood" in task.safety_flags
    assert "preserve-write-defaults" in task.safety_flags
    assert "app-env-test-gated-writes" in task.safety_flags
    assert "cd apps/api && pytest tests/test_autonomy_supervisor.py -q" in task.verification_commands
    assert "python3 scripts/check_public_status.py" in task.verification_commands
    assert "python3 scripts/check_write_safety_defaults.py" in task.verification_commands
    assert "python3 scripts/check_markdown_readability.py" in task.verification_commands
    assert "python3 scripts/check_tracked_hygiene.py" in task.verification_commands
    assert "git diff --check" in task.verification_commands
    assert "Generated from backlog policy" in prompt
    assert "Treat the allowed scope as a ceiling" in prompt
    assert "Do not spawn nested Hermes/Codex/tmux/cron workers" in prompt
    assert "no remaining safe scoped change" in prompt


def test_prompt_paths_sanitize_generated_task_ids(tmp_path):
    queue = write_queue(
        tmp_path,
        SAMPLE_QUEUE.replace("## Task: docs-one", "## Task: ../../unsafe/task:id")
        .replace("## Task: docs-two", "## Not a task: docs-two"),
    )

    report = supervisor.run_supervisor(
        repo=tmp_path,
        queue_path=queue,
        budget_seconds=3600,
        mode="dry-run",
        run_root=tmp_path / ".hermes" / "autonomy" / "runs" / "test",
        git=FakeGit([""]),
        agent=RepeatingFakeAgent(),
        clock=FakeClock([0, 1, 2]),
    )

    prompt_path = Path(report.tasks[0].prompt_path)
    prompt_dir = tmp_path / ".hermes" / "autonomy" / "runs" / "test" / "prompts"
    assert prompt_path.parent == prompt_dir
    assert prompt_path.name == "001-unsafe-task-id.md"
    assert prompt_path.exists()


def test_owner_writebeta_operating_guide_preserves_repeated_backup_restore_docs_only_boundary():
    guide = (REPO_ROOT / "docs/write-alpha/owner-writebeta-operating-guide.md").read_text(encoding="utf-8")

    required = [
        "Repeated backup/restore readiness docs/tests tasks",
        "Generated backup/restore readiness maintenance may update tracked wording, guard assertions, or pytest",
        "NOT_RESTORE_DRILL",
        "NO_BACKUP_ARTIFACT_CREATED",
        "DO_NOT_ENABLE_WRITES",
        "NO_PRIVATE_DATA_REVIEWED",
        "no restore command was run",
        "no restored book was opened",
        "no backup artifact, app DB",
        "runtime log, or private path evidence was created or reviewed",
        "did not authorize changing `GNUCASH_WRITES_ENABLED=false` or relaxing the `APP_ENV=test` gate",
        "checkpoint",
        "not backup creation, restore execution, dogfood, or private-data inspection",
        "explicit no-change checkpoint",
        "Do not create operational backup/restore evidence, runtime",
        "manifests, or cosmetic edits solely to produce a diff",
    ]
    for pattern in required:
        assert pattern in guide


def test_backup_restore_readiness_checklist_preserves_docs_only_safety_labels():
    checklist = (
        REPO_ROOT / "docs" / "write-alpha" / "backup-restore-readiness-checklist.md"
    ).read_text(encoding="utf-8")

    required_labels = (
        "NOT_RESTORE_DRILL",
        "NO_BACKUP_ARTIFACT_CREATED",
        "DO_NOT_ENABLE_WRITES",
        "NO_PRIVATE_DATA_REVIEWED",
    )
    for label in required_labels:
        assert label in checklist

    assert "docs/tests-only restore-readiness wording check" in checklist
    assert "GNUCASH_WRITES_ENABLED=false" in checklist
    assert "APP_ENV=test" in checklist
    assert "not recovery proof" in checklist
    assert "must not overwrite" in checklist
    assert "must not create backups" in checklist
    assert "must not restore into books" in checklist
    assert "must not open private data" in checklist
    assert "must not run product dogfood" in checklist
    assert "Repeated generated docs/tests tasks must also avoid churn" in checklist
    assert "explicit no-change checkpoint" in checklist
    assert (
        "not creating a new backup/restore procedure, operational evidence, runtime manifest, or cosmetic edit solely to produce a diff"
        in checklist
    )


def test_backup_restore_readiness_checklist_has_docs_only_assertion_template():
    checklist = (
        REPO_ROOT / "docs" / "write-alpha" / "backup-restore-readiness-checklist.md"
    ).read_text(encoding="utf-8")

    required_assertions = [
        "backup_restore_readiness_scope=docs-tests-only",
        "restore_drill_performed=false",
        "backup_artifact_created=false",
        "private_data_reviewed=false",
        "writes_enabled_or_app_env_gate_relaxed=false",
        "runtime_backup_manifest_reviewed=false",
        "restore_target_opened=false",
        "app_db_opened_or_modified=false",
        "raw backup manifests, checksum lines, restore filenames",
        "runtime logs, app DB inspection output, or product dogfood output",
        "not an operational restore-readiness claim",
    ]
    for pattern in required_assertions:
        assert pattern in checklist


def test_backup_restore_readiness_checklist_forbids_assumed_operational_markers():
    checklist = (
        REPO_ROOT / "docs" / "write-alpha" / "backup-restore-readiness-checklist.md"
    ).read_text(encoding="utf-8")

    required = [
        "do not fill operational markers",
        "`backup_location`",
        "`restore_hash_verified`",
        "`restore_row_count_verified`",
        "`restore_schema_marker_verified`",
        "from assumptions when no authorized restore drill was run",
    ]
    for pattern in required:
        assert pattern in checklist
