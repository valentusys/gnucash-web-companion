"""Regression tests for redacted dogfood evidence helper."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "redact_dogfood_evidence.py"

spec = importlib.util.spec_from_file_location("redact_dogfood_evidence", SCRIPT_PATH)
assert spec is not None
redactor = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["redact_dogfood_evidence"] = redactor
spec.loader.exec_module(redactor)


def _safe_evidence() -> dict[str, object]:
    return {
        "phase_number": 236,
        "scenario_type": "schema-only-redaction-helper",
        "classification": "synthetic",
        "commands_run": ["python3 scripts/redact_dogfood_evidence.py --mode reject <evidence-json>"],
        "result": "pass",
        "artifact_refs": ["<redacted-artifact-ref:phase-236-helper-test>"],
        "backup_count": 0,
        "audit_row_count": 0,
        "lock_status": "not-acquired-no-mutation",
        "restore_proof_status": "not-applicable-no-mutation",
        "disabled_reset_status": "not-applicable-default-unchanged",
    }


def test_safe_schema_shape_passes_without_redaction():
    evidence = _safe_evidence()

    sanitized = redactor.sanitize_evidence(evidence, mode="reject")

    assert sanitized == evidence


def test_reject_mode_blocks_raw_path_amount_and_sensitive_fields():
    evidence = _safe_evidence() | {
        "artifact_refs": ["/private/example/book.gnucash.sqlite"],
        "notes": "Observed value 123.45 in copied evidence",
        "memo": "private counterparty note",
    }

    try:
        redactor.sanitize_evidence(evidence, mode="reject")
    except redactor.EvidenceRejected as exc:
        reasons = {finding.reason for finding in exc.findings}
        pointers = {finding.pointer for finding in exc.findings}
    else:
        raise AssertionError("unsafe evidence should be rejected")

    assert {"path", "amount", "sensitive"}.issubset(reasons)
    assert "/artifact_refs/0" in pointers
    assert "/notes" in pointers
    assert "/memo" in pointers


def test_redact_mode_removes_path_like_amount_like_and_sensitive_values():
    evidence = _safe_evidence() | {
        "artifact_refs": ["data/books/private-copy.gnucash.sqlite"],
        "command_output": "created backup at C:\\secret\\book.backup and amount 999.00",
        "account_name": "Private:Checking",
    }

    sanitized = redactor.sanitize_evidence(evidence, mode="redact")
    rendered = json.dumps(sanitized, sort_keys=True)

    assert "private-copy" not in rendered
    assert "C:\\secret" not in rendered
    assert "999.00" not in rendered
    assert "Private:Checking" not in rendered
    assert "<redacted-path>" in rendered
    assert "<redacted-sensitive-field>" in rendered


def test_cli_rejects_unsafe_json_without_leaking_value(tmp_path):
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(
        json.dumps(_safe_evidence() | {"artifact_refs": ["/secret/book.gnucash.sqlite"]}),
        encoding="utf-8",
    )

    result = subprocess.run(
        ["python3", str(SCRIPT_PATH), str(evidence_path)],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "dogfood evidence rejected" in result.stderr
    assert "/secret/book" not in result.stderr
    assert "book.gnucash.sqlite" not in result.stderr


def test_cli_redacts_unsafe_json(tmp_path):
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(
        json.dumps(_safe_evidence() | {"path": "~/private/book.gnucash.sqlite"}),
        encoding="utf-8",
    )

    result = subprocess.run(
        ["python3", str(SCRIPT_PATH), "--mode", "redact", str(evidence_path)],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert "~/private" not in result.stdout
    assert "book.gnucash.sqlite" not in result.stdout
    assert "<redacted-path>" in result.stdout


def test_reject_mode_blocks_owner_evidence_schema_failure_cases():
    evidence = _safe_evidence() | {
        "artifact_refs": ["<redacted-artifact-ref:phase-264>"],
        "operator_private_path": "/Users/example/private/book.gnucash.sqlite",
        "account_name": "Assets:Checking",
        "split_memo": "Dinner with private counterparty",
        "observed_amount": "42.99 USD",
        "request_payload": {
            "transaction": {
                "description": "Private transaction description",
                "splits": [{"account": "Expenses:Private", "value": "21.00"}],
            }
        },
    }

    try:
        redactor.sanitize_evidence(evidence, mode="reject")
    except redactor.EvidenceRejected as exc:
        pointers = {finding.pointer for finding in exc.findings}
        reasons = {finding.reason for finding in exc.findings}
    else:  # pragma: no cover - defensive
        raise AssertionError("owner evidence containing private schema fields should be rejected")

    assert "path" in reasons
    assert "amount" in reasons
    assert "sensitive" in reasons
    assert "/operator_private_path" in pointers
    assert "/account_name" in pointers
    assert "/split_memo" in pointers
    assert "/observed_amount" in pointers
    assert "/request_payload/transaction/description" in pointers
    assert "/request_payload/transaction/splits/0/account" in pointers
    assert "/request_payload/transaction/splits/0/value" in pointers


def test_redact_mode_preserves_useful_bounded_evidence_and_redacts_private_payload():
    evidence = _safe_evidence() | {
        "phase_number": 264,
        "scenario_type": "owner-dry-run-redaction-acceptance",
        "classification": "copied_disposable",
        "commands_run": ["python3 scripts/write_alpha_owner_dry_run.py <redacted-target>"],
        "backup_count": 1,
        "audit_row_count": 0,
        "lock_status": "not-inspected-by-wrapper",
        "restore_proof_status": "operator-required-after-mutation",
        "disabled_reset_status": "verified-default-disabled",
        "request_payload": {"description": "Private transaction description", "amount": "10.00"},
        "operator_path": "C:\\Private\\book.gnucash.sqlite",
    }

    sanitized = redactor.sanitize_evidence(evidence, mode="redact")
    rendered = json.dumps(sanitized, sort_keys=True)

    assert sanitized["phase_number"] == 264
    assert sanitized["classification"] == "copied_disposable"
    assert sanitized["backup_count"] == 1
    assert sanitized["audit_row_count"] == 0
    assert sanitized["disabled_reset_status"] == "verified-default-disabled"
    assert "Private transaction" not in rendered
    assert "10.00" not in rendered
    assert "C:\\Private" not in rendered
    assert "<redacted-sensitive-field>" in rendered
    assert "<redacted-path>" in rendered
