#!/usr/bin/env python3
"""Guard committed write-safety defaults without opening runtime data.

This script reads only tracked configuration/docs. It verifies that committed
examples and rendered Compose defaults keep GnuCash writes disabled by default
and that public/default write-readiness docs still mention the APP_ENV=test gate.
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WRITE_DEFAULT_TEXT = "GNUCASH_WRITES_ENABLED=false"
COMPOSE_WRITE_DEFAULT_TEXT = "GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}"
APP_ENV_DEFAULT_TEXT = "APP_ENV=development"
COMPOSE_APP_ENV_DEFAULT_TEXT = "APP_ENV=${APP_ENV:-development}"
APP_ENV_GATE_TEXT = "APP_ENV=test"
EXPLICIT_WRITE_ENABLE_TEXT = "explicit write enablement"
RESET_TEXT = "reset"
DISABLED_PROBE_TEXT = "disabled-probe"
CHECKLIST_REQUIRED_TEXTS = (
    "#36",
    "keep #36 open",
    "no-release/no-public-write posture",
    "GNUCASH_WRITES_ENABLED=false",
    "APP_ENV=test",
    "owner-input/real-book/copy-book constraints",
    "next worker packages",
)
WRITE_COMPATIBILITY_DOCS = (
    Path("docs/write-alpha/evidence-matrix.md"),
    Path("docs/v0.2-controlled-writes.md"),
)
ISSUE_36_REMAINING_GATES_DOC = Path("docs/write-alpha/issue-36-remaining-gates.md")
ISSUE_36_DASHBOARD_DOC = Path("docs/write-alpha/controlled-write-readiness-dashboard.md")
RESTORE_BOUNDARY_DOC = Path("docs/write-alpha/restore-safety-boundary.md")
COPIED_DOGFOOD_PACKET_DOC = Path("docs/write-alpha/copied-book-dogfood-readiness-packet.md")
AFTER_W3_READINESS_BOUNDARY_DOC = Path("docs/write-alpha/after-w3-readiness-boundary.md")
BACKUP_RESTORE_READINESS_DOC = Path("docs/write-alpha/backup-restore-readiness-checklist.md")
BACKUP_RESTORE_UX_DOC = Path("docs/write-alpha/backup-restore-ux-design.md")
BACKUP_RECOVERY_RUNBOOK_DOC = Path("docs/operations/backup-and-recovery.md")
OWNER_WRITEBETA_OPERATING_GUIDE_DOC = Path("docs/write-alpha/owner-writebeta-operating-guide.md")
OWNER_WRITEBETA_APPROVAL_BOUNDARY_DOC = Path("docs/release/owner-writebeta-owner-approval-boundary.md")
OWNER_WRITEBETA_UNRELEASED_DOC = Path("docs/release/v0.4-owner-writebeta-readiness-unreleased.md")
OWNER_WRITEBETA_NO_RELEASE_DECISION_DOC = Path("docs/release/v0.4-owner-writebeta-no-release-decision.md")
API_CONFIG_FILE = Path("apps/api/app/config.py")
WRITE_ROUTES_FILE = Path("apps/api/app/routers/transactions.py")
WRITE_ROUTE_FUNCTIONS = (
    "validate_book_transaction",
    "create_book_transaction",
    "patch_book_transaction",
    "delete_book_transaction",
)
WRITE_ROUTE_GATED_CALLS = (
    "_resolve_viewable_book",
    "_require_book_edit_access",
    "_write_service_for",
    "_audit_log",
    "_require_write_alpha_transaction_ownership",
    "require_owner_writebeta_if_active",
)
WRITE_COMPATIBILITY_REQUIRED_TEXTS = (
    "supported-version write compatibility remains pending",
    "synthetic/disposable or copied/restorable evidence only",
    "not a real-book claim",
    "broad GnuCash compatibility",
    "public write beta",
    "production",
    "security-audited",
)
WRITE_COMPATIBILITY_FORBIDDEN_PATTERNS = (
    "broad GnuCash write compatibility is supported",
    "all GnuCash versions are write-compatible",
    "production-book write safety is proven",
    "real/private-book write-safety is proven",
    "public write beta is ready",
    "write mode is production-ready",
    "write mode is security-audited",
)
DOTENV_ASSIGNMENT_RE = re.compile(
    r"^(?:export\s+)?(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)$"
)


def _normalized(text: str) -> str:
    """Collapse Markdown wrapping so phrase guards do not depend on line breaks."""
    return " ".join(text.lower().split())


class GuardError(ValueError):
    """Path-redacted write-safety guard failure."""


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise GuardError("required safety file could not be read") from exc


def _strip_dotenv_inline_comment(value: str) -> str:
    """Strip unquoted dotenv inline comments while preserving literal values."""
    quote: str | None = None
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
            continue
        if quote == '"' and character == "\\":
            escaped = True
            continue
        if quote is not None:
            if character == quote:
                quote = None
            continue
        if character in {'"', "'"}:
            quote = character
            continue
        if character == "#" and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.strip()


def _env_file_assignments(env_text: str, key: str) -> list[str]:
    """Return uncommented dotenv assignment values for key without expanding them."""
    values: list[str] = []
    for raw_line in env_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = DOTENV_ASSIGNMENT_RE.match(line)
        if match is not None and match.group("key") == key:
            values.append(_strip_dotenv_inline_comment(match.group("value")))
    return values


def _env_file_mentions_unsafe_write_default_example(env_text: str) -> bool:
    """Return whether .env.example mentions public write/test defaults anywhere."""
    normalized_lines = [line.strip().lower().replace(" ", "") for line in env_text.splitlines()]
    return any(
        "gnucash_writes_enabled=true" in line or "app_env=test" in line for line in normalized_lines
    )


def _parse_python(path: Path) -> ast.Module:
    try:
        return ast.parse(_read(path), filename=str(path.name))
    except SyntaxError as exc:
        raise GuardError("required safety Python file could not be parsed") from exc


def _call_lines(node: ast.AST) -> dict[str, list[int]]:
    lines: dict[str, list[int]] = {}
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        func = child.func
        if isinstance(func, ast.Name):
            name = func.id
        elif isinstance(func, ast.Attribute):
            name = func.attr
        else:
            continue
        lines.setdefault(name, []).append(child.lineno)
    return lines


def _first_call_line(call_lines: dict[str, list[int]], name: str) -> int | None:
    lines = call_lines.get(name)
    return min(lines) if lines else None


def _top_level_call_name(statement: ast.stmt) -> str | None:
    """Return the direct call name for simple top-level function-body call statements."""
    if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
        return None
    func = statement.value.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _direct_executable_statement_call_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str | None]:
    """Return direct call statement names after skipping an optional function docstring."""
    body = node.body
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        body = body[1:]
    return [_top_level_call_name(statement) for statement in body]


def _is_settings_app_env_lower_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "lower"
        and isinstance(node.func.value, ast.Attribute)
        and node.func.value.attr == "app_env"
        and isinstance(node.func.value.value, ast.Name)
        and node.func.value.value.id == "settings"
    )


def _is_settings_gnucash_writes_enabled_attr(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "gnucash_writes_enabled"
        and isinstance(node.value, ast.Name)
        and node.value.id == "settings"
    )


def _has_disabled_write_rejection_condition(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.UnaryOp)
        and isinstance(node.op, ast.Not)
        and _is_settings_gnucash_writes_enabled_attr(node.operand)
    )


def _body_starts_with_direct_raise(statements: list[ast.stmt]) -> bool:
    """Return whether a guarded branch immediately raises.

    A nested raise under another conditional can be bypassed while still making
    the AST contain a Raise node. A direct raise after a return or other branch
    statement can also be unreachable. The write-default and APP_ENV=test
    helpers must fail closed as the first executable statement in the guarded
    branch.
    """
    return bool(statements) and isinstance(statements[0], ast.Raise)


def _executable_body(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[ast.stmt]:
    """Return function body after skipping an optional docstring."""
    body = node.body
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        return body[1:]
    return body


def _function_has_disabled_write_rejection_gate(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return whether a helper starts with fail-closed write-default rejection logic."""
    body = _executable_body(node)
    return (
        bool(body)
        and isinstance(body[0], ast.If)
        and _has_disabled_write_rejection_condition(body[0].test)
        and _body_starts_with_direct_raise(body[0].body)
    )


def _has_non_test_app_env_rejection_comparison(node: ast.AST) -> bool:
    if not isinstance(node, ast.Compare):
        return False
    if len(node.ops) != 1 or len(node.comparators) != 1:
        return False
    if not isinstance(node.ops[0], ast.NotEq):
        return False
    comparator = node.comparators[0]
    return (
        _is_settings_app_env_lower_call(node.left)
        and isinstance(comparator, ast.Constant)
        and comparator.value == "test"
    )


def _function_has_non_test_app_env_rejection_gate(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return whether a helper starts with settings.app_env.lower() != \"test\" gating logic."""
    body = _executable_body(node)
    return (
        bool(body)
        and isinstance(body[0], ast.If)
        and _has_non_test_app_env_rejection_comparison(body[0].test)
        and _body_starts_with_direct_raise(body[0].body)
    )


def _decorated_transaction_write_route_functions(tree: ast.Module) -> set[str]:
    """Return transaction write route function names declared in the router source."""
    route_functions: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            func = decorator.func
            if not isinstance(func, ast.Attribute):
                continue
            if func.attr not in {"post", "put", "patch", "delete"}:
                continue
            if not decorator.args:
                continue
            path_arg = decorator.args[0]
            if isinstance(path_arg, ast.Constant) and isinstance(path_arg.value, str):
                if "/transactions" in path_arg.value:
                    route_functions.add(node.name)
    return route_functions


def _settings_literal_defaults(config_path: Path) -> dict[str, object]:
    tree = _parse_python(config_path)
    defaults: dict[str, object] = {}
    settings_class = next(
        (node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Settings"),
        None,
    )
    if settings_class is None:
        return defaults
    for node in settings_class.body:
        if not isinstance(node, ast.AnnAssign):
            continue
        if not isinstance(node.target, ast.Name):
            continue
        if isinstance(node.value, ast.Constant):
            defaults[node.target.id] = node.value.value
        else:
            defaults[node.target.id] = None
    return defaults


def _check_api_write_defaults(config_path: Path = REPO_ROOT / API_CONFIG_FILE) -> list[str]:
    failures: list[str] = []
    defaults = _settings_literal_defaults(config_path)
    write_default = defaults.get("gnucash_writes_enabled")
    if write_default is not False:
        failures.append("API Settings must default gnucash_writes_enabled to False")
    if "gnucash_writes_enabled" in defaults and write_default is not False:
        failures.append("API Settings must not default gnucash_writes_enabled to a non-False value")
    return failures


def _check_api_app_env_defaults(config_path: Path = REPO_ROOT / API_CONFIG_FILE) -> list[str]:
    failures: list[str] = []
    defaults = _settings_literal_defaults(config_path)
    app_env_default = defaults.get("app_env")
    if app_env_default != "development":
        failures.append("API Settings must default app_env to development")
    if app_env_default == "test":
        failures.append("API Settings must not default app_env to test")
    return failures


def _check_write_route_test_gates(routes_path: Path = REPO_ROOT / WRITE_ROUTES_FILE) -> list[str]:
    failures: list[str] = []
    text = _read(routes_path)
    normalized = _normalized(text)
    if 'settings.app_env.lower() != "test"' not in text:
        failures.append("write-alpha test-scope helper must explicitly block non-test APP_ENV")
    if "controlled write-alpha routes are limited to explicit test-environment" not in normalized:
        failures.append("write-alpha non-test failure detail must preserve test-environment scope wording")

    tree = _parse_python(routes_path)
    functions = {node.name: node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    writes_enabled_helper = functions.get("_ensure_writes_enabled")
    if writes_enabled_helper is None or not _function_has_disabled_write_rejection_gate(writes_enabled_helper):
        failures.append(
            "write default helper must enforce executable not settings.gnucash_writes_enabled rejection logic"
        )
    test_scope_helper = functions.get("_ensure_write_alpha_test_scope")
    if test_scope_helper is None or not _function_has_non_test_app_env_rejection_gate(test_scope_helper):
        failures.append("write-alpha test-scope helper must enforce executable settings.app_env.lower() != test rejection logic")
    guarded_routes = set(WRITE_ROUTE_FUNCTIONS)
    decorated_write_routes = _decorated_transaction_write_route_functions(tree)
    for function_name in sorted(decorated_write_routes - guarded_routes):
        failures.append(f"write route {function_name} must be registered in WRITE_ROUTE_FUNCTIONS")
    for function_name in sorted(guarded_routes - decorated_write_routes):
        failures.append(f"write route {function_name} must be declared as a transaction write router endpoint")
    for function_name in WRITE_ROUTE_FUNCTIONS:
        node = functions.get(function_name)
        if node is None:
            failures.append(f"write route {function_name} must exist")
            continue
        call_lines = _call_lines(node)
        writes_enabled_line = _first_call_line(call_lines, "_ensure_writes_enabled")
        test_scope_line = _first_call_line(call_lines, "_ensure_write_alpha_test_scope")
        if writes_enabled_line is None:
            failures.append(f"write route {function_name} must call _ensure_writes_enabled")
        if test_scope_line is None:
            failures.append(f"write route {function_name} must call _ensure_write_alpha_test_scope")
        if writes_enabled_line is not None and test_scope_line is not None:
            if writes_enabled_line > test_scope_line:
                failures.append(
                    f"write route {function_name} must check _ensure_writes_enabled before APP_ENV=test scope"
                )
            direct_call_names = _direct_executable_statement_call_names(node)
            if direct_call_names[:2] != ["_ensure_writes_enabled", "_ensure_write_alpha_test_scope"]:
                failures.append(
                    f"write route {function_name} first executable statements must be "
                    "_ensure_writes_enabled then _ensure_write_alpha_test_scope"
                )
            try:
                writes_enabled_index = direct_call_names.index("_ensure_writes_enabled")
            except ValueError:
                writes_enabled_index = -1
            try:
                test_scope_index = direct_call_names.index("_ensure_write_alpha_test_scope")
            except ValueError:
                test_scope_index = -1
            if writes_enabled_index < 0:
                failures.append(
                    f"write route {function_name} must call _ensure_writes_enabled as a direct guard statement"
                )
            if test_scope_index < 0:
                failures.append(
                    f"write route {function_name} must call _ensure_write_alpha_test_scope "
                    "as a direct guard statement"
                )
            has_non_adjacent_guard = writes_enabled_index >= 0 and (
                writes_enabled_index + 1 >= len(direct_call_names)
                or direct_call_names[writes_enabled_index + 1] != "_ensure_write_alpha_test_scope"
            )
            if has_non_adjacent_guard:
                failures.append(
                    f"write route {function_name} must call _ensure_write_alpha_test_scope immediately after _ensure_writes_enabled"
                )
            for gated_call in WRITE_ROUTE_GATED_CALLS:
                gated_call_line = _first_call_line(call_lines, gated_call)
                if gated_call_line is not None and gated_call_line < test_scope_line:
                    failures.append(
                        f"write route {function_name} must call {gated_call} only after APP_ENV=test scope"
                    )
    return failures


def _check_write_compatibility_docs(paths: tuple[Path, ...]) -> list[str]:
    failures: list[str] = []
    combined_text = ""
    for path in paths:
        doc_text = _read(REPO_ROOT / path if not path.is_absolute() else path)
        normalized = _normalized(doc_text)
        combined_text += " " + normalized
        for forbidden in WRITE_COMPATIBILITY_FORBIDDEN_PATTERNS:
            if _normalized(forbidden) in normalized:
                failures.append(f"write compatibility docs must not claim: {forbidden}")
    missing = [required for required in WRITE_COMPATIBILITY_REQUIRED_TEXTS if _normalized(required) not in combined_text]
    if missing:
        failures.append("write compatibility docs must preserve: " + ", ".join(missing))
    return failures


def _check_issue_36_remaining_gates(path: Path) -> list[str]:
    text = _read(REPO_ROOT / path if not path.is_absolute() else path)
    normalized = _normalized(text)
    required = (
        "keep #36 open",
        "copied-book dogfood gate accepted",
        "W3 CREATE 2 / PATCH 1 / DELETE 1",
        "supported-version write compatibility evidence",
        "future copied/restorable mutation evidence packet",
        "same-context owner + PM authorization",
        "real/private/original/only-copy",
        "no public write beta",
        "no stable, production-ready, or security-audited claim",
        "no real/private/original/working/only-copy safety claim",
        "NO_RELEASE",
        "CREATE 0 / PATCH 0 / DELETE 0",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
    )
    missing = [needle for needle in required if _normalized(needle) not in normalized]
    return ["#36 remaining gates doc must preserve: " + ", ".join(missing)] if missing else []


def _check_issue_36_dashboard(path: Path) -> list[str]:
    text = _read(REPO_ROOT / path if not path.is_absolute() else path)
    normalized = _normalized(text)
    required = (
        "keep #36 open",
        "state-machine evidence",
        "copied-book evidence",
        "restore evidence",
        "default-disabled probes",
        "compatibility gaps",
        "same-context owner + PM authorization",
        "no broad compatibility claim",
        "no stable, production-ready, or security-audited claim",
        "no real/private/original/working/only-copy safety claim",
        "no only-copy safety claim",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "NO_RELEASE",
        "CREATE 0 / PATCH 0 / DELETE 0",
    )
    missing = [needle for needle in required if _normalized(needle) not in normalized]
    return ["#36 readiness dashboard must preserve: " + ", ".join(missing)] if missing else []


def _check_restore_boundary(path: Path) -> list[str]:
    text = _read(REPO_ROOT / path if not path.is_absolute() else path)
    normalized = _normalized(text)
    required = (
        "restore-to-copy",
        "not destructive restore",
        "not real-book safety evidence",
        "independent backup",
        "redacted evidence only",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "CREATE 0 / PATCH 0 / DELETE 0",
    )
    missing = [needle for needle in required if _normalized(needle) not in normalized]
    return ["restore boundary doc must preserve: " + ", ".join(missing)] if missing else []


def _check_copied_dogfood_packet(path: Path) -> list[str]:
    text = _read(REPO_ROOT / path if not path.is_absolute() else path)
    normalized = _normalized(text)
    required = (
        "non-mutating packet",
        "same-context owner + PM authorization",
        "route family and operation counts",
        "backup/read-back/audit/lock/restore/reset",
        "redacted evidence only",
        "no original/private/real-working/only-copy",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "CREATE 0 / PATCH 0 / DELETE 0",
    )
    missing = [needle for needle in required if _normalized(needle) not in normalized]
    return ["copied-book dogfood packet must preserve: " + ", ".join(missing)] if missing else []


def _check_after_w3_readiness_boundary(path: Path) -> list[str]:
    text = _read(REPO_ROOT / path if not path.is_absolute() else path)
    normalized = _normalized(text)
    required = (
        "#36 remains open",
        "NO_RELEASE",
        "no public write beta",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "reset/default-disabled probes",
        "hard stop",
        "restore-to-copy",
        "supported-version write compatibility remains pending",
        "not a broad GnuCash compatibility claim",
        "not a real-book claim",
        "#22 closed only for narrow Desktop-generated synthetic SQLite fixture evidence",
        "PostgreSQL/MySQL/MariaDB GnuCash backends remain unclaimed",
        "same-context owner + PM authorization",
        "CREATE 0 / PATCH 0 / DELETE 0",
    )
    missing = [needle for needle in required if _normalized(needle) not in normalized]
    return ["after-W3 readiness boundary must preserve: " + ", ".join(missing)] if missing else []


def _check_backup_restore_readiness(path: Path) -> list[str]:
    text = _read(REPO_ROOT / path if not path.is_absolute() else path)
    normalized = _normalized(text)
    required = (
        "non-mutating",
        "restore-to-copy",
        "copied/restorable or synthetic/disposable",
        "must not create backups",
        "must not restore into books",
        "must not run product dogfood",
        "real/original/private/working/only-copy book",
        "docs/tests-only restore-readiness wording check",
        "tracked docs, pure Python guard output, and pytest assertions",
        "not recovery proof",
        "documented no-op expectation",
        "app DB records",
        "private path snippets",
        "backup manifest and checksum wording",
        "opaque refs plus redacted status summaries only",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "public write beta readiness",
        "production safety",
        "security-audited status",
        "NOT_RESTORE_DRILL",
        "NO_BACKUP_ARTIFACT_CREATED",
        "DO_NOT_ENABLE_WRITES",
        "NO_PRIVATE_DATA_REVIEWED",
        "backup_restore_readiness_scope=docs-tests-only",
        "restore_drill_performed=false",
        "backup_artifact_created=false",
        "private_data_reviewed=false",
        "writes_enabled_or_app_env_gate_relaxed=false",
        "runtime_backup_manifest_reviewed=false",
        "restore_target_opened=false",
        "app_db_opened_or_modified=false",
    )
    missing = [needle for needle in required if _normalized(needle) not in normalized]
    return ["backup/restore readiness checklist must preserve: " + ", ".join(missing)] if missing else []


def _check_backup_restore_ux_design(path: Path) -> list[str]:
    text = _read(REPO_ROOT / path if not path.is_absolute() else path)
    normalized = _normalized(text)
    required = (
        "docs/tests-only restore-readiness wording check",
        "not recovery proof",
        "documented no-op expectation",
        "must not create backup artifacts",
        "restore artifacts",
        "app DB records",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "public write beta readiness",
        "production safety",
        "security-audited status",
        "copied/restorable or synthetic/disposable",
        "NOT_RESTORE_DRILL",
        "NO_BACKUP_ARTIFACT_CREATED",
        "DO_NOT_ENABLE_WRITES",
        "NO_PRIVATE_DATA_REVIEWED",
        "no restore command was run and no restored book was opened",
        "does not authorize changing `GNUCASH_WRITES_ENABLED=false` or relaxing the `APP_ENV=test` gate",
    )
    missing = [needle for needle in required if _normalized(needle) not in normalized]
    return ["backup/restore UX design must preserve docs/tests-only safety wording: " + ", ".join(missing)] if missing else []


def _check_backup_recovery_runbook(path: Path) -> list[str]:
    text = _read(REPO_ROOT / path if not path.is_absolute() else path)
    normalized = _normalized(text)
    required = (
        "docs/tests-only restore-readiness wording checks are not restore drills",
        "tracked docs, guard output, and pytest assertions",
        "must not create backup artifacts",
        "restore artifacts",
        "app DB records",
        "filesystem evidence",
        "private paths, account names, memos, amounts, books, or backups",
        "documented no-op expectation under `GNUCASH_WRITES_ENABLED=false`",
        "not an executed product mutation or recovery proof",
        "copied/restorable or synthetic/disposable fixture",
        "APP_ENV=test",
        "prerequisites only",
        "public write beta readiness",
        "production safety",
        "security-audited status",
        "broad compatibility",
        "only-copy safety",
        "NOT_RESTORE_DRILL",
        "NO_BACKUP_ARTIFACT_CREATED",
        "DO_NOT_ENABLE_WRITES",
        "NO_PRIVATE_DATA_REVIEWED",
        "review packets must summarize readiness as redacted pass/fail markers only",
        "backup_restore_readiness_scope=docs-tests-only",
        "restore_drill_performed=false",
        "backup_artifact_created=false",
        "private_data_reviewed=false",
        "writes_enabled_or_app_env_gate_relaxed=false",
        "runtime_backup_manifest_reviewed=false",
        "restore_target_opened=false",
        "app_db_opened_or_modified=false",
    )
    missing = [needle for needle in required if _normalized(needle) not in normalized]
    return ["backup/recovery runbook must preserve docs/tests-only restore-readiness boundary: " + ", ".join(missing)] if missing else []


def _check_owner_writebeta_operating_guide(path: Path) -> list[str]:
    text = _read(REPO_ROOT / path if not path.is_absolute() else path)
    normalized = _normalized(text)
    required = (
        "#36 remains open",
        "W3 copied/restorable CREATE/PATCH/DELETE evidence is accepted narrowly",
        "recorded staged-copy scope only",
        "not a public write beta",
        "not broad GnuCash compatibility",
        "not a real working-book safety claim",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "Real/private/original/working/only-copy books remain blocked as write targets",
        "Future copied/restorable mutation remains blocked unless the owner and PM authorize exact target class",
    )
    missing = [needle for needle in required if _normalized(needle) not in normalized]
    return ["owner-writebeta operating guide must preserve: " + ", ".join(missing)] if missing else []


def _check_owner_writebeta_release_boundaries(paths: tuple[Path, ...]) -> list[str]:
    combined = ""
    for path in paths:
        combined += " " + _normalized(_read(REPO_ROOT / path if not path.is_absolute() else path))
    required = (
        "NO_RELEASE_KEEP_MAINTENANCE",
        "UNRELEASED_UNTIL_OWNER_APPROVAL",
        "not release notes",
        "not release authorization",
        "owner/PM release-candidate approval",
        "no public write beta",
        "no stable, production-ready, or security-audited claim",
        "no broad GnuCash version compatibility claim",
        "no real/private/original/working/only-copy book safety claim",
        "GNUCASH_WRITES_ENABLED=false",
        "APP_ENV=test",
        "No tag, GitHub release, package, image, or release notes are authorized",
        "narrow Desktop-generated synthetic SQLite fixture evidence only",
    )
    missing = [needle for needle in required if _normalized(needle) not in combined]
    return ["owner-writebeta release boundary docs must preserve: " + ", ".join(missing)] if missing else []


def _strip_yaml_inline_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _split_inline_yaml_items(value: str) -> list[str]:
    """Split a simple Compose inline sequence/mapping without expanding variables."""
    items: list[str] = []
    current: list[str] = []
    quote: str | None = None
    for character in value:
        if quote is not None:
            current.append(character)
            if character == quote:
                quote = None
            continue
        if character in {'"', "'"}:
            quote = character
            current.append(character)
            continue
        if character == ",":
            item = "".join(current).strip()
            if item:
                items.append(item)
            current = []
            continue
        current.append(character)
    item = "".join(current).strip()
    if item:
        items.append(item)
    return items


def _compose_inline_environment_entries(value: str) -> list[str]:
    """Normalize Compose one-line environment list/mapping entries."""
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        entries: list[str] = []
        for item in _split_inline_yaml_items(value[1:-1]):
            entry = _strip_yaml_inline_quotes(item)
            if entry:
                entries.append(entry)
        return entries
    if value.startswith("{") and value.endswith("}"):
        entries = []
        for item in _split_inline_yaml_items(value[1:-1]):
            if ":" not in item:
                continue
            key, entry_value = item.split(":", 1)
            key = _strip_yaml_inline_quotes(key)
            entry_value = _strip_yaml_inline_quotes(entry_value)
            if key and entry_value:
                entries.append(f"{key}={entry_value}")
        return entries
    return []


def _compose_service_environment_lines(compose_text: str, service_name: str) -> list[str]:
    """Extract normalized environment entries for one Compose service.

    The guard intentionally avoids loading arbitrary Compose interpolation or
    requiring PyYAML; it only needs to prove the committed service defaults stay
    pinned in the rendered Compose source posture.
    """
    lines = compose_text.splitlines()
    services_indent: int | None = None
    service_indent: int | None = None
    service_start: int | None = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if services_indent is None:
            if stripped == "services:":
                services_indent = indent
            continue
        if indent <= services_indent:
            break
        if service_indent is None:
            service_indent = indent
        if indent == service_indent and stripped.endswith(":"):
            candidate = _strip_yaml_inline_quotes(stripped[:-1])
            if candidate == service_name:
                service_start = index + 1
                break
    if service_indent is None or service_start is None:
        return []

    environment_indent: int | None = None
    environment_lines: list[str] = []
    for line in lines[service_start:]:
        stripped = line.strip()
        if not stripped:
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= service_indent:
            break
        if environment_indent is None:
            if stripped == "environment:":
                environment_indent = indent
                continue
            if stripped.startswith("environment:"):
                _, inline_environment = stripped.split(":", 1)
                environment_lines.extend(_compose_inline_environment_entries(inline_environment))
                break
            continue
        if indent <= environment_indent:
            break
        if stripped.startswith("-"):
            environment_lines.append(_strip_yaml_inline_quotes(stripped[1:].strip()))
            continue
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            if key and value.strip():
                environment_lines.append(
                    f"{_strip_yaml_inline_quotes(key)}={_strip_yaml_inline_quotes(value)}"
                )
    return environment_lines


def _compose_service_names(compose_text: str) -> list[str]:
    """Return service names declared directly under the Compose services block."""
    lines = compose_text.splitlines()
    services_indent: int | None = None
    service_indent: int | None = None
    service_names: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if services_indent is None:
            if stripped == "services:":
                services_indent = indent
            continue
        if indent <= services_indent:
            break
        if service_indent is None:
            service_indent = indent
        if indent == service_indent and stripped.endswith(":"):
            service_names.append(_strip_yaml_inline_quotes(stripped[:-1]))
    return service_names


def _compose_service_environment_values(environment_lines: list[str], key: str) -> list[str]:
    prefix = f"{key}="
    return [
        _strip_yaml_inline_quotes(line[len(prefix) :])
        for line in environment_lines
        if line.startswith(prefix)
    ]


def _compose_app_env_value_defaults_to_test(value: str) -> bool:
    normalized = _strip_yaml_inline_quotes(value).strip().lower().replace(" ", "")
    return normalized in {"test", "${app_env:-test}", "${app_env-test}", "${app_env:=test}"}


def _check_compose_service_env_exact(
    environment_lines: list[str],
    *,
    service_name: str,
    key: str,
    expected_value: str,
    expected_entry: str,
) -> list[str]:
    values = _compose_service_environment_values(environment_lines, key)
    failures: list[str] = []
    if expected_entry not in environment_lines:
        failures.append(f"Docker Compose {service_name} service must render {key} default {expected_value}")
    unsafe_values = [value for value in values if value != expected_value]
    if unsafe_values:
        failures.append(f"Docker Compose {service_name} service must not include alternate {key} defaults")
    return failures


def _check_compose_all_service_env_safe(compose_text: str) -> list[str]:
    """Reject unsafe write/app-env defaults in any committed Compose service."""
    failures: list[str] = []
    for service_name in _compose_service_names(compose_text):
        environment_lines = _compose_service_environment_lines(compose_text, service_name)
        write_values = _compose_service_environment_values(environment_lines, "GNUCASH_WRITES_ENABLED")
        app_env_values = _compose_service_environment_values(environment_lines, "APP_ENV")
        if any(value != "${GNUCASH_WRITES_ENABLED:-false}" for value in write_values):
            failures.append(
                f"Docker Compose {service_name} service must not include alternate GNUCASH_WRITES_ENABLED defaults"
            )
        if any(_compose_app_env_value_defaults_to_test(value) for value in app_env_values):
            failures.append(f"Docker Compose {service_name} service must not default APP_ENV to test")
    return failures


def _check(env_example: Path, compose: Path, gate_doc: Path, checklist_doc: Path | None = None) -> list[str]:
    env_text = _read(env_example)
    compose_text = _read(compose)
    gate_text = _read(gate_doc)
    gate_text_normalized = _normalized(gate_text)
    env_write_values = _env_file_assignments(env_text, "GNUCASH_WRITES_ENABLED")
    env_app_env_values = _env_file_assignments(env_text, "APP_ENV")
    api_compose_environment = _compose_service_environment_lines(compose_text, "api")
    web_compose_environment = _compose_service_environment_lines(compose_text, "web")
    failures: list[str] = []

    if "false" not in env_write_values:
        failures.append(".env.example must set GNUCASH_WRITES_ENABLED=false as an uncommented assignment")
    if any(value != "false" for value in env_write_values):
        failures.append(".env.example must not default or suggest alternate GNUCASH_WRITES_ENABLED values")
    if "development" not in env_app_env_values:
        failures.append(".env.example must default APP_ENV to development as an uncommented assignment")
    if any(value != "development" for value in env_app_env_values):
        failures.append(".env.example must not default or suggest alternate APP_ENV values")
    if _env_file_mentions_unsafe_write_default_example(env_text):
        failures.append(".env.example must not mention GNUCASH_WRITES_ENABLED=true or APP_ENV=test defaults")
    if COMPOSE_WRITE_DEFAULT_TEXT not in compose_text:
        failures.append("Docker Compose must render GNUCASH_WRITES_ENABLED default false")
    failures.extend(
        _check_compose_service_env_exact(
            api_compose_environment,
            service_name="api",
            key="GNUCASH_WRITES_ENABLED",
            expected_value="${GNUCASH_WRITES_ENABLED:-false}",
            expected_entry=COMPOSE_WRITE_DEFAULT_TEXT,
        )
    )
    failures.extend(
        _check_compose_service_env_exact(
            web_compose_environment,
            service_name="web",
            key="GNUCASH_WRITES_ENABLED",
            expected_value="${GNUCASH_WRITES_ENABLED:-false}",
            expected_entry=COMPOSE_WRITE_DEFAULT_TEXT,
        )
    )
    if "GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-true}" in compose_text:
        failures.append("Docker Compose must not default GNUCASH_WRITES_ENABLED true")
    if COMPOSE_APP_ENV_DEFAULT_TEXT not in compose_text:
        failures.append("Docker Compose must render APP_ENV default development, not test")
    failures.extend(
        _check_compose_service_env_exact(
            api_compose_environment,
            service_name="api",
            key="APP_ENV",
            expected_value="${APP_ENV:-development}",
            expected_entry=COMPOSE_APP_ENV_DEFAULT_TEXT,
        )
    )
    if "APP_ENV=${APP_ENV:-test}" in compose_text:
        failures.append("Docker Compose must not default APP_ENV=test")
    failures.extend(_check_compose_all_service_env_safe(compose_text))
    if APP_ENV_GATE_TEXT not in gate_text:
        failures.append("write-readiness documentation must preserve APP_ENV=test gate text")
    if EXPLICIT_WRITE_ENABLE_TEXT not in gate_text_normalized:
        failures.append("write-readiness documentation must require explicit write enablement")
    if RESET_TEXT not in gate_text_normalized or DISABLED_PROBE_TEXT not in gate_text_normalized:
        failures.append("write-readiness documentation must preserve reset/default-disabled probe wording")

    if checklist_doc is not None:
        checklist_text = _read(checklist_doc)
        checklist_text_normalized = _normalized(checklist_text)
        missing = [
            required
            for required in CHECKLIST_REQUIRED_TEXTS
            if _normalized(required) not in checklist_text_normalized
        ]
        if missing:
            failures.append("#36 audit checklist must preserve: " + ", ".join(missing))
    failures.extend(_check_api_write_defaults())
    failures.extend(_check_api_app_env_defaults())
    failures.extend(_check_write_route_test_gates())
    failures.extend(_check_write_compatibility_docs(WRITE_COMPATIBILITY_DOCS))
    failures.extend(_check_issue_36_remaining_gates(ISSUE_36_REMAINING_GATES_DOC))
    failures.extend(_check_issue_36_dashboard(ISSUE_36_DASHBOARD_DOC))
    failures.extend(_check_restore_boundary(RESTORE_BOUNDARY_DOC))
    failures.extend(_check_copied_dogfood_packet(COPIED_DOGFOOD_PACKET_DOC))
    failures.extend(_check_after_w3_readiness_boundary(AFTER_W3_READINESS_BOUNDARY_DOC))
    failures.extend(_check_backup_restore_readiness(BACKUP_RESTORE_READINESS_DOC))
    failures.extend(_check_backup_restore_ux_design(BACKUP_RESTORE_UX_DOC))
    failures.extend(_check_backup_recovery_runbook(BACKUP_RECOVERY_RUNBOOK_DOC))
    failures.extend(_check_owner_writebeta_operating_guide(OWNER_WRITEBETA_OPERATING_GUIDE_DOC))
    failures.extend(
        _check_owner_writebeta_release_boundaries(
            (
                OWNER_WRITEBETA_APPROVAL_BOUNDARY_DOC,
                OWNER_WRITEBETA_UNRELEASED_DOC,
                OWNER_WRITEBETA_NO_RELEASE_DECISION_DOC,
            )
        )
    )
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check committed/default write-safety posture.")
    parser.add_argument("--env-example", default=str(REPO_ROOT / ".env.example"))
    parser.add_argument("--compose", default=str(REPO_ROOT / "docker-compose.yml"))
    parser.add_argument(
        "--gate-doc",
        default=str(REPO_ROOT / "docs/write-alpha/owner-writebeta-operating-guide.md"),
    )
    parser.add_argument(
        "--checklist-doc",
        default=str(REPO_ROOT / "docs/write-alpha-maintainer-checklist.md"),
    )
    args = parser.parse_args(argv)

    try:
        failures = _check(
            Path(args.env_example),
            Path(args.compose),
            Path(args.gate_doc),
            Path(args.checklist_doc),
        )
    except GuardError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if failures:
        print("unsafe write-safety defaults: " + "; ".join(failures), file=sys.stderr)
        return 2
    print(
        "write-safety defaults ok: GNUCASH_WRITES_ENABLED=false; "
        "APP_ENV=development default present; "
        "APP_ENV=test gate text present; explicit write enablement present; "
        "reset/default-disabled probe wording present"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
