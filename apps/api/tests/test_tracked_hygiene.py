import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.check_tracked_hygiene as guard


def test_path_violations_reject_private_artifact_classes(tmp_path):
    repo = guard.REPO_ROOT
    candidates = [
        repo / ".env",
        repo / ".hermes" / "cache" / "prompt.txt",
        repo / "data" / "books" / "book.gnucash.sqlite",
        repo / "data" / "app" / "app.db",
        repo / "secrets" / "api.key",
        repo / "docs" / "evidence.csv",
        repo / "docs" / "raw-ledger-export.sql",
        repo / "docs" / "book-backup.zip",
        repo / "docs" / "evidence-screenshot.png",
        repo / "docs" / "copied-book.gnucash.sqlite-wal",
        repo / "docs" / "app.db-shm",
    ]

    problems = guard.path_violations(candidates)

    assert len(problems) >= len(candidates)
    assert any("copied-book.gnucash.sqlite-wal" in problem for problem in problems)
    assert any("app.db-shm" in problem for problem in problems)


def test_path_violations_allow_safe_docs_and_code():
    repo = guard.REPO_ROOT
    candidates = [
        repo / "README.md",
        repo / "docs" / "community" / "public-readonly-beta-feedback-packet.md",
        repo / "docs" / "images" / "dashboard-desktop.png",
        repo / "apps" / "api" / "app" / "diagnostics.py",
    ]

    assert guard.path_violations(candidates) == []


def test_path_violations_reject_local_env_variants_but_allow_examples():
    repo = guard.REPO_ROOT
    candidates = [
        repo / ".env.example",
        repo / ".env.writealpha.example",
        repo / ".env.local",
        repo / "deploy" / ".env.production",
        repo / ".envrc",
    ]

    problems = guard.path_violations(candidates)

    assert not any(".env.example" in problem for problem in problems)
    assert not any(".env.writealpha.example" in problem for problem in problems)
    assert any(".env.local" in problem for problem in problems)
    assert any("deploy/.env.production" in problem for problem in problems)
    assert any(".envrc" in problem for problem in problems)


def test_content_violations_reject_private_key_marker(tmp_path, monkeypatch):
    sample = tmp_path / "safe-name.txt"
    marker = "-----BEGIN " + "OPENSSH" + " PRIVATE KEY-----"
    sample.write_text(f"{marker}\nredacted\n", encoding="utf-8")
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    problems = guard.content_violations([sample])

    assert problems == ["tracked private-key marker in: safe-name.txt"]


def test_content_violations_reject_raw_private_evidence_markers(tmp_path, monkeypatch):
    sample = tmp_path / "public-report.md"
    sample.write_text(
        "RAW_PRIVATE_EVIDENCE_BEGIN\nPRIVATE_BOOK_PATH=/redacted\nACCOUNT_NAME=Redacted Account\n"
        "ACCOUNT_DESCRIPTION=Redacted Account Description\nTRANSACTION_AMOUNT=0.00\n"
        "ACCOUNT_NAME: Redacted Account\nTRANSACTION_MEMO: Redacted memo\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    problems = guard.content_violations([sample])

    assert problems == [
        "tracked raw private-evidence marker 'RAW_PRIVATE_EVIDENCE_BEGIN' in: public-report.md",
        "tracked raw private-evidence marker 'PRIVATE_BOOK_PATH=' in: public-report.md",
        "tracked raw private-evidence marker 'ACCOUNT_NAME=' in: public-report.md",
        "tracked raw private-evidence marker 'ACCOUNT_NAME:' in: public-report.md",
        "tracked raw private-evidence marker 'ACCOUNT_DESCRIPTION=' in: public-report.md",
        "tracked raw private-evidence marker 'TRANSACTION_MEMO:' in: public-report.md",
        "tracked raw private-evidence marker 'TRANSACTION_AMOUNT=' in: public-report.md",
        "tracked raw private-evidence label in public-report.md:2: PRIVATE_BOOK_PATH=/redacted",
        "tracked raw private-evidence label in public-report.md:3: ACCOUNT_NAME=Redacted Account",
        "tracked raw private-evidence label in public-report.md:4: ACCOUNT_DESCRIPTION=Redacted Account Description",
        "tracked raw private-evidence label in public-report.md:5: TRANSACTION_AMOUNT=0.00",
        "tracked raw private-evidence label in public-report.md:6: ACCOUNT_NAME: Redacted Account",
        "tracked raw private-evidence label in public-report.md:7: TRANSACTION_MEMO: Redacted memo",
    ]


def test_content_violations_reject_private_account_description_and_balance_markers(tmp_path, monkeypatch):
    sample = tmp_path / "public-report.md"
    sample.write_text(
        "PRIVATE_ACCOUNT_NAME=Redacted Account\n"
        "REAL_ACCOUNT_DESCRIPTION=Redacted account description\n"
        "ACCOUNT_BALANCE=0.00\n"
        "BALANCE=0.00\n"
        "PRIVATE_TRANSACTION_DESCRIPTION=Redacted transaction\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    assert guard.content_violations([sample]) == [
        "tracked raw private-evidence marker 'PRIVATE_ACCOUNT_NAME=' in: public-report.md",
        "tracked raw private-evidence marker 'REAL_ACCOUNT_DESCRIPTION=' in: public-report.md",
        "tracked raw private-evidence marker 'ACCOUNT_BALANCE=' in: public-report.md",
        "tracked raw private-evidence marker 'BALANCE=' in: public-report.md",
        "tracked raw private-evidence marker 'PRIVATE_TRANSACTION_DESCRIPTION=' in: public-report.md",
        "tracked raw private-evidence label in public-report.md:2: REAL_ACCOUNT_DESCRIPTION=Redacted account description",
        "tracked raw private-evidence label in public-report.md:3: ACCOUNT_BALANCE=0.00",
        "tracked raw private-evidence label in public-report.md:4: BALANCE=0.00",
        "tracked raw private-evidence label in public-report.md:5: PRIVATE_TRANSACTION_DESCRIPTION=Redacted transaction",
    ]


def test_content_violations_reject_real_private_transaction_detail_markers(tmp_path, monkeypatch):
    sample = tmp_path / "public-report.md"
    sample.write_text(
        "REAL_TRANSACTION_DESCRIPTION=Redacted transaction\n"
        "REAL_TRANSACTION_MEMO: Redacted memo\n"
        "PRIVATE_TRANSACTION_MEMO=Redacted memo\n"
        "PRIVATE_TRANSACTION_AMOUNT: 0.00\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    assert guard.content_violations([sample]) == [
        "tracked raw private-evidence marker 'REAL_TRANSACTION_DESCRIPTION=' in: public-report.md",
        "tracked raw private-evidence marker 'REAL_TRANSACTION_MEMO:' in: public-report.md",
        "tracked raw private-evidence marker 'PRIVATE_TRANSACTION_MEMO=' in: public-report.md",
        "tracked raw private-evidence marker 'PRIVATE_TRANSACTION_AMOUNT:' in: public-report.md",
        "tracked raw private-evidence label in public-report.md:1: REAL_TRANSACTION_DESCRIPTION=Redacted transaction",
        "tracked raw private-evidence label in public-report.md:2: REAL_TRANSACTION_MEMO: Redacted memo",
        "tracked raw private-evidence label in public-report.md:3: PRIVATE_TRANSACTION_MEMO=Redacted memo",
        "tracked raw private-evidence label in public-report.md:4: PRIVATE_TRANSACTION_AMOUNT: 0.00",
    ]


def test_content_violations_reject_generic_account_label(tmp_path, monkeypatch):
    sample = tmp_path / "handoff.md"
    sample.write_text("Account: Redacted account name\n", encoding="utf-8")
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    assert guard.content_violations([sample]) == [
        "tracked raw private-evidence label in handoff.md:1: Account: Redacted account name"
    ]


def test_content_violations_reject_private_path_label_variants(tmp_path, monkeypatch):
    sample = tmp_path / "handoff.md"
    sample.write_text(
        "PRIVATE_PATH: /redacted\nORIGINAL_GNUCASH_PATH=/redacted\nONLY_COPY_GNUCASH_PATH=/redacted\n"
        "ORIGINAL_BOOK_PATH=/redacted\nONLY_COPY_BOOK_PATH=/redacted\nWORKING_BOOK_PATH=/redacted\n"
        "LOCAL_BOOK_PATH=/redacted\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    problems = guard.content_violations([sample])

    assert problems == [
        "tracked raw private-evidence marker 'PRIVATE_PATH:' in: handoff.md",
        "tracked raw private-evidence marker 'ORIGINAL_GNUCASH_PATH=' in: handoff.md",
        "tracked raw private-evidence marker 'ONLY_COPY_GNUCASH_PATH=' in: handoff.md",
        "tracked raw private-evidence marker 'ORIGINAL_BOOK_PATH=' in: handoff.md",
        "tracked raw private-evidence marker 'ONLY_COPY_BOOK_PATH=' in: handoff.md",
        "tracked raw private-evidence marker 'WORKING_BOOK_PATH=' in: handoff.md",
        "tracked raw private-evidence marker 'LOCAL_BOOK_PATH=' in: handoff.md",
        "tracked raw private-evidence label in handoff.md:1: PRIVATE_PATH: /redacted",
        "tracked raw private-evidence label in handoff.md:2: ORIGINAL_GNUCASH_PATH=/redacted",
        "tracked raw private-evidence label in handoff.md:3: ONLY_COPY_GNUCASH_PATH=/redacted",
        "tracked raw private-evidence label in handoff.md:4: ORIGINAL_BOOK_PATH=/redacted",
        "tracked raw private-evidence label in handoff.md:5: ONLY_COPY_BOOK_PATH=/redacted",
        "tracked raw private-evidence label in handoff.md:6: WORKING_BOOK_PATH=/redacted",
        "tracked raw private-evidence label in handoff.md:7: LOCAL_BOOK_PATH=/redacted",
    ]


def test_content_violations_reject_private_scoped_path_markers(tmp_path, monkeypatch):
    sample = tmp_path / "handoff.md"
    sample.write_text(
        "PRIVATE_LOCAL_PATH=/redacted\n"
        "PRIVATE_SOURCE_PATH: /redacted\n"
        "PRIVATE_TARGET_PATH=/redacted\n"
        "PRIVATE_EVIDENCE_PATH: /redacted\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    assert guard.content_violations([sample]) == [
        "tracked raw private-evidence marker 'PRIVATE_LOCAL_PATH=' in: handoff.md",
        "tracked raw private-evidence marker 'PRIVATE_SOURCE_PATH:' in: handoff.md",
        "tracked raw private-evidence marker 'PRIVATE_TARGET_PATH=' in: handoff.md",
        "tracked raw private-evidence marker 'PRIVATE_EVIDENCE_PATH:' in: handoff.md",
    ]


def test_content_violations_reject_inline_private_evidence_labels(tmp_path, monkeypatch):
    sample = tmp_path / "table-report.md"
    sample.write_text(
        "| note | PRIVATE_BOOK_PATH = /redacted |\n"
        "Summary includes private evidence path: /redacted/report.txt\n"
        "Audit row says real transaction memo = redacted memo\n"
        "Operator note: private account description: redacted account\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    assert guard.content_violations([sample]) == [
        "tracked raw private-evidence inline label in table-report.md:1: | note | PRIVATE_BOOK_PATH = /redacted |",
        "tracked raw private-evidence inline label in table-report.md:2: Summary includes private evidence path: /redacted/report.txt",
        "tracked raw private-evidence inline label in table-report.md:3: Audit row says real transaction memo = redacted memo",
        "tracked raw private-evidence inline label in table-report.md:4: Operator note: private account description: redacted account",
    ]


def test_content_violations_reject_export_screenshot_and_raw_evidence_path_markers(tmp_path, monkeypatch):
    sample = tmp_path / "handoff.md"
    sample.write_text(
        "RAW_EVIDENCE_PATH=/redacted\n"
        "EXPORT_PATH: /redacted/export.csv\n"
        "CSV_EXPORT_PATH=/redacted/export.csv\n"
        "SCREENSHOT_PATH: /redacted/screen.png\n"
        "PRIVATE_SCREENSHOT_PATH=/redacted/screen.png\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    assert guard.content_violations([sample]) == [
        "tracked raw private-evidence marker 'RAW_EVIDENCE_PATH=' in: handoff.md",
        "tracked raw private-evidence marker 'EXPORT_PATH:' in: handoff.md",
        "tracked raw private-evidence marker 'CSV_EXPORT_PATH=' in: handoff.md",
        "tracked raw private-evidence marker 'SCREENSHOT_PATH:' in: handoff.md",
        "tracked raw private-evidence marker 'PRIVATE_SCREENSHOT_PATH=' in: handoff.md",
        "tracked raw private-evidence label in handoff.md:1: RAW_EVIDENCE_PATH=/redacted",
        "tracked raw private-evidence label in handoff.md:2: EXPORT_PATH: /redacted/export.csv",
        "tracked raw private-evidence label in handoff.md:3: CSV_EXPORT_PATH=/redacted/export.csv",
        "tracked raw private-evidence label in handoff.md:4: SCREENSHOT_PATH: /redacted/screen.png",
        "tracked raw private-evidence label in handoff.md:5: PRIVATE_SCREENSHOT_PATH=/redacted/screen.png",
    ]


def test_content_violations_reject_human_written_private_evidence_labels(tmp_path, monkeypatch):
    sample = tmp_path / "public-report.md"
    sample.write_text(
        "Private path: /redacted\n"
        "Private evidence: redacted summary should not use this label\n"
        "Raw private evidence = pasted raw packet\n"
        "Unredacted GnuCash evidence: raw row dump\n"
        "GnuCash evidence = raw row dump\n"
        "Original GnuCash path = /redacted\n"
        "Original book path = /redacted\n"
        "Working book path: /redacted\n"
        "Local book path: /redacted\n"
        "GnuCash path: /redacted\n"
        "Book path = /redacted\n"
        "Source path: /redacted\n"
        "Target path: /redacted\n"
        "Backup path: /redacted\n"
        "Fixture path: /redacted\n"
        "Evidence path: /redacted\n"
        "Report path: /redacted\n"
        "Output path: /redacted\n"
        "Log path: /redacted\n"
        "Raw evidence path: /redacted\n"
        "Export path: /redacted/export.csv\n"
        "CSV export path: /redacted/export.csv\n"
        "Screenshot path: /redacted/screen.png\n"
        "Private screenshot path: /redacted/screen.png\n"
        "Image path: /redacted/screen.png\n"
        "Artifact path: /redacted/artifact.txt\n"
        "Real account name: Redacted Account\n"
        "Account name: Redacted Account\n"
        "Account description: Redacted account description\n"
        "Private account description: Redacted account description\n"
        "Memo: Redacted memo\n"
        "Amount: 0.00\n"
        "Balance: 0.00\n"
        "Account balance: 0.00\n"
        "Transaction amount: 0.00\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    problems = guard.content_violations([sample])

    assert problems == [
        "tracked raw private-evidence label in public-report.md:1: Private path: /redacted",
        "tracked raw private-evidence label in public-report.md:2: Private evidence: redacted summary should not use this label",
        "tracked raw private-evidence label in public-report.md:3: Raw private evidence = pasted raw packet",
        "tracked raw private-evidence label in public-report.md:4: Unredacted GnuCash evidence: raw row dump",
        "tracked raw private-evidence label in public-report.md:5: GnuCash evidence = raw row dump",
        "tracked raw private-evidence label in public-report.md:6: Original GnuCash path = /redacted",
        "tracked raw private-evidence label in public-report.md:7: Original book path = /redacted",
        "tracked raw private-evidence label in public-report.md:8: Working book path: /redacted",
        "tracked raw private-evidence label in public-report.md:9: Local book path: /redacted",
        "tracked raw private-evidence label in public-report.md:10: GnuCash path: /redacted",
        "tracked raw private-evidence label in public-report.md:11: Book path = /redacted",
        "tracked raw private-evidence label in public-report.md:12: Source path: /redacted",
        "tracked raw private-evidence label in public-report.md:13: Target path: /redacted",
        "tracked raw private-evidence label in public-report.md:14: Backup path: /redacted",
        "tracked raw private-evidence label in public-report.md:15: Fixture path: /redacted",
        "tracked raw private-evidence label in public-report.md:16: Evidence path: /redacted",
        "tracked raw private-evidence label in public-report.md:17: Report path: /redacted",
        "tracked raw private-evidence label in public-report.md:18: Output path: /redacted",
        "tracked raw private-evidence label in public-report.md:19: Log path: /redacted",
        "tracked raw private-evidence label in public-report.md:20: Raw evidence path: /redacted",
        "tracked raw private-evidence label in public-report.md:21: Export path: /redacted/export.csv",
        "tracked raw private-evidence label in public-report.md:22: CSV export path: /redacted/export.csv",
        "tracked raw private-evidence label in public-report.md:23: Screenshot path: /redacted/screen.png",
        "tracked raw private-evidence label in public-report.md:24: Private screenshot path: /redacted/screen.png",
        "tracked raw private-evidence label in public-report.md:25: Image path: /redacted/screen.png",
        "tracked raw private-evidence label in public-report.md:26: Artifact path: /redacted/artifact.txt",
        "tracked raw private-evidence label in public-report.md:27: Real account name: Redacted Account",
        "tracked raw private-evidence label in public-report.md:28: Account name: Redacted Account",
        "tracked raw private-evidence label in public-report.md:29: Account description: Redacted account description",
        "tracked raw private-evidence label in public-report.md:30: Private account description: Redacted account description",
        "tracked raw private-evidence label in public-report.md:31: Memo: Redacted memo",
        "tracked raw private-evidence label in public-report.md:32: Amount: 0.00",
        "tracked raw private-evidence label in public-report.md:33: Balance: 0.00",
        "tracked raw private-evidence label in public-report.md:34: Account balance: 0.00",
        "tracked raw private-evidence label in public-report.md:35: Transaction amount: 0.00",
    ]


def test_content_violations_reject_markdown_private_evidence_labels(tmp_path, monkeypatch):
    sample = tmp_path / "public-report.md"
    sample.write_text(
        "- Private path: /redacted\n"
        "* Original GnuCash path = /redacted\n"
        "+ Real account name: Redacted Account\n"
        "> Transaction memo: Redacted memo\n"
        "- Account description: Redacted account description\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    problems = guard.content_violations([sample])

    assert problems == [
        "tracked raw private-evidence label in public-report.md:1: - Private path: /redacted",
        "tracked raw private-evidence label in public-report.md:2: * Original GnuCash path = /redacted",
        "tracked raw private-evidence label in public-report.md:3: + Real account name: Redacted Account",
        "tracked raw private-evidence label in public-report.md:4: > Transaction memo: Redacted memo",
        "tracked raw private-evidence label in public-report.md:5: - Account description: Redacted account description",
    ]


def test_content_violations_reject_unsafe_affirmative_wording(tmp_path, monkeypatch):
    sample = tmp_path / "release.md"
    sample.write_text(
        "Public write beta is ready.\n"
        "Broad GnuCash compatibility is supported.\n"
        "Only-copy books are safe for writes.\n"
        "Public write beta launch is authorized.\n"
        "Broad GnuCash Desktop compatibility is confirmed.\n"
        "All GnuCash versions are supported.\n"
        "Compatible with any GnuCash Desktop version.\n"
        "Production-ready release published.\n"
        "Stable release is ready.\n"
        "Public writes are enabled.\n"
        "Public write mode is available.\n"
        "Write mode is stable.\n"
        "Works with all GnuCash versions.\n"
        "All GnuCash SQL backends are supported.\n"
        "Validated across all GnuCash Desktop releases.\n"
        "Tested against any GnuCash SQL books.\n"
        "Safe to use with private books.\n"
        "Write beta has shipped.\n"
        "Write-beta has launched.\n"
        "Public write beta rolled out.\n"
        "Public write beta rollout is complete.\n"
        "Public write beta can be used.\n"
        "Public write beta is recommended for users.\n"
        "Write beta is production-grade.\n"
        "Write beta may be enabled.\n"
        "Write-beta is acceptable for public use.\n"
        "Write beta released.\n"
        "Writebeta is ready.\n"
        "Writebeta published.\n"
        "Owner write beta is ready.\n"
        "Owner write beta authorized.\n"
        "Owner writebeta is available.\n"
        "Owner writebeta released.\n"
        "Owner-write beta is available.\n"
        "Writebeta has launched.\n"
        "Owner write beta has launched.\n"
        "Owner-writebeta rollout is released.\n"
        "Owner write beta rollout is released.\n"
        "Public write beta for private books is acceptable.\n"
        "Real books are safe for writes.\n"
        "Private book writes are safe.\n"
        "Original books are safe for mutation.\n"
        "Write beta is safe for private books.\n"
        "Write-beta supported for original books.\n"
        "Owner write beta is safe for private books.\n"
        "Owner-write beta is acceptable for only-copy books.\n"
        "Write beta is production ready.\n"
        "This release is production ready.\n"
        "Production ready release published.\n"
        "Write beta is general availability.\n"
        "Write beta GA is released.\n"
        "Owner-writebeta is production-safe.\n"
        "Owner write beta is field-tested.\n"
        "Broad GnuCash compatibility is complete.\n"
        "Public write beta is release-ready.\n"
        "Public write beta is safe for users.\n"
        "Write beta is ship ready.\n"
        "Write-beta is suitable for public use.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    problems = guard.content_violations([sample])

    assert problems == [
        "tracked unsafe affirmative wording in release.md:1: Public write beta is ready.",
        "tracked unsafe affirmative wording in release.md:2: Broad GnuCash compatibility is supported.",
        "tracked unsafe affirmative wording in release.md:3: Only-copy books are safe for writes.",
        "tracked unsafe affirmative wording in release.md:4: Public write beta launch is authorized.",
        "tracked unsafe affirmative wording in release.md:5: Broad GnuCash Desktop compatibility is confirmed.",
        "tracked unsafe affirmative wording in release.md:6: All GnuCash versions are supported.",
        "tracked unsafe affirmative wording in release.md:7: Compatible with any GnuCash Desktop version.",
        "tracked unsafe affirmative wording in release.md:8: Production-ready release published.",
        "tracked unsafe affirmative wording in release.md:9: Stable release is ready.",
        "tracked unsafe affirmative wording in release.md:10: Public writes are enabled.",
        "tracked unsafe affirmative wording in release.md:11: Public write mode is available.",
        "tracked unsafe affirmative wording in release.md:12: Write mode is stable.",
        "tracked unsafe affirmative wording in release.md:13: Works with all GnuCash versions.",
        "tracked unsafe affirmative wording in release.md:14: All GnuCash SQL backends are supported.",
        "tracked unsafe affirmative wording in release.md:15: Validated across all GnuCash Desktop releases.",
        "tracked unsafe affirmative wording in release.md:16: Tested against any GnuCash SQL books.",
        "tracked unsafe affirmative wording in release.md:17: Safe to use with private books.",
        "tracked unsafe affirmative wording in release.md:18: Write beta has shipped.",
        "tracked unsafe affirmative wording in release.md:19: Write-beta has launched.",
        "tracked unsafe affirmative wording in release.md:20: Public write beta rolled out.",
        "tracked unsafe affirmative wording in release.md:21: Public write beta rollout is complete.",
        "tracked unsafe affirmative wording in release.md:22: Public write beta can be used.",
        "tracked unsafe affirmative wording in release.md:23: Public write beta is recommended for users.",
        "tracked unsafe affirmative wording in release.md:24: Write beta is production-grade.",
        "tracked unsafe affirmative wording in release.md:25: Write beta may be enabled.",
        "tracked unsafe affirmative wording in release.md:26: Write-beta is acceptable for public use.",
        "tracked unsafe affirmative wording in release.md:27: Write beta released.",
        "tracked unsafe affirmative wording in release.md:28: Writebeta is ready.",
        "tracked unsafe affirmative wording in release.md:29: Writebeta published.",
        "tracked unsafe affirmative wording in release.md:30: Owner write beta is ready.",
        "tracked unsafe affirmative wording in release.md:31: Owner write beta authorized.",
        "tracked unsafe affirmative wording in release.md:32: Owner writebeta is available.",
        "tracked unsafe affirmative wording in release.md:33: Owner writebeta released.",
        "tracked unsafe affirmative wording in release.md:34: Owner-write beta is available.",
        "tracked unsafe affirmative wording in release.md:35: Writebeta has launched.",
        "tracked unsafe affirmative wording in release.md:36: Owner write beta has launched.",
        "tracked unsafe affirmative wording in release.md:37: Owner-writebeta rollout is released.",
        "tracked unsafe affirmative wording in release.md:38: Owner write beta rollout is released.",
        "tracked unsafe affirmative wording in release.md:39: Public write beta for private books is acceptable.",
        "tracked unsafe affirmative wording in release.md:40: Real books are safe for writes.",
        "tracked unsafe affirmative wording in release.md:41: Private book writes are safe.",
        "tracked unsafe affirmative wording in release.md:42: Original books are safe for mutation.",
        "tracked unsafe affirmative wording in release.md:43: Write beta is safe for private books.",
        "tracked unsafe affirmative wording in release.md:44: Write-beta supported for original books.",
        "tracked unsafe affirmative wording in release.md:45: Owner write beta is safe for private books.",
        "tracked unsafe affirmative wording in release.md:46: Owner-write beta is acceptable for only-copy books.",
        "tracked unsafe affirmative wording in release.md:47: Write beta is production ready.",
        "tracked unsafe affirmative wording in release.md:48: This release is production ready.",
        "tracked unsafe affirmative wording in release.md:49: Production ready release published.",
        "tracked unsafe affirmative wording in release.md:50: Write beta is general availability.",
        "tracked unsafe affirmative wording in release.md:51: Write beta GA is released.",
        "tracked unsafe affirmative wording in release.md:52: Owner-writebeta is production-safe.",
        "tracked unsafe affirmative wording in release.md:53: Owner write beta is field-tested.",
        "tracked unsafe affirmative wording in release.md:54: Broad GnuCash compatibility is complete.",
        "tracked unsafe affirmative wording in release.md:55: Public write beta is release-ready.",
        "tracked unsafe affirmative wording in release.md:56: Public write beta is safe for users.",
        "tracked unsafe affirmative wording in release.md:57: Write beta is ship ready.",
        "tracked unsafe affirmative wording in release.md:58: Write-beta is suitable for public use.",
    ]


def test_content_violations_reject_general_stable_security_audited_claims(tmp_path, monkeypatch):
    sample = tmp_path / "release.md"
    sample.write_text(
        "Release is stable.\n"
        "Deployment is security-audited.\n"
        "Software is production ready.\n"
        "Build is production-ready.\n"
        "Broad GnuCash compatibility has been validated.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    assert guard.content_violations([sample]) == [
        "tracked unsafe affirmative wording in release.md:1: Release is stable.",
        "tracked unsafe affirmative wording in release.md:2: Deployment is security-audited.",
        "tracked unsafe affirmative wording in release.md:3: Software is production ready.",
        "tracked unsafe affirmative wording in release.md:4: Build is production-ready.",
        "tracked unsafe affirmative wording in release.md:5: Broad GnuCash compatibility has been validated.",
    ]


def test_content_violations_reject_compatibility_guarantee_wording(tmp_path, monkeypatch):
    sample = tmp_path / "compatibility.md"
    sample.write_text(
        "Fully compatible with GnuCash Desktop releases.\n"
        "Guaranteed compatible with GnuCash SQL books.\n"
        "Production-ready compatibility for write beta.\n"
        "All SQL backends are supported.\n"
        "GnuCash Desktop 5.12 compatibility is supported.\n"
        "Supports GnuCash Desktop 5.12.\n"
        "Validated GnuCash Desktop 5.12.1.\n"
        "PostgreSQL/MySQL/MariaDB GnuCash backends are supported.\n"
        "PostgreSQL/MySQL/MariaDB SQL backends are compatible.\n"
        "Broad GnuCash compatibility is verified.\n"
        "GnuCash Desktop 5.12 is verified.\n"
        "Verified GnuCash Desktop 5.12.1.\n"
        "Every GnuCash version is supported.\n"
        "Works with every GnuCash Desktop version.\n"
        "Tested across every GnuCash SQL backend.\n"
        "Compatible with every GnuCash Desktop version.\n"
        "Every GnuCash Desktop version is write-compatible.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    problems = guard.content_violations([sample])

    assert problems == [
        "tracked unsafe affirmative wording in compatibility.md:1: Fully compatible with GnuCash Desktop releases.",
        "tracked unsafe affirmative wording in compatibility.md:2: Guaranteed compatible with GnuCash SQL books.",
        "tracked unsafe affirmative wording in compatibility.md:3: Production-ready compatibility for write beta.",
        "tracked unsafe affirmative wording in compatibility.md:4: All SQL backends are supported.",
        "tracked unsafe affirmative wording in compatibility.md:5: GnuCash Desktop 5.12 compatibility is supported.",
        "tracked unsafe affirmative wording in compatibility.md:6: Supports GnuCash Desktop 5.12.",
        "tracked unsafe affirmative wording in compatibility.md:7: Validated GnuCash Desktop 5.12.1.",
        "tracked unsafe affirmative wording in compatibility.md:8: PostgreSQL/MySQL/MariaDB GnuCash backends are supported.",
        "tracked unsafe affirmative wording in compatibility.md:9: PostgreSQL/MySQL/MariaDB SQL backends are compatible.",
        "tracked unsafe affirmative wording in compatibility.md:10: Broad GnuCash compatibility is verified.",
        "tracked unsafe affirmative wording in compatibility.md:11: GnuCash Desktop 5.12 is verified.",
        "tracked unsafe affirmative wording in compatibility.md:12: Verified GnuCash Desktop 5.12.1.",
        "tracked unsafe affirmative wording in compatibility.md:13: Every GnuCash version is supported.",
        "tracked unsafe affirmative wording in compatibility.md:14: Works with every GnuCash Desktop version.",
        "tracked unsafe affirmative wording in compatibility.md:15: Tested across every GnuCash SQL backend.",
        "tracked unsafe affirmative wording in compatibility.md:16: Compatible with every GnuCash Desktop version.",
        "tracked unsafe affirmative wording in compatibility.md:17: Every GnuCash Desktop version is write-compatible.",
    ]


def test_content_violations_reject_write_beta_ready_without_public_prefix(tmp_path, monkeypatch):
    sample = tmp_path / "release.md"
    sample.write_text(
        "Write beta is ready.\n"
        "Write beta available for public use.\n"
        "Write beta is authorized.\n"
        "Public write beta is published.\n"
        "Write beta is stable.\n"
        "Write-beta is stable.\n"
        "Write beta is security-audited.\n"
        "Write-beta is security-audited.\n"
        "Write beta release is production-ready.\n"
        "Write-beta release is production-ready.\n"
        "Write beta launch is authorized.\n"
        "Write-beta rollout is released.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    problems = guard.content_violations([sample])

    assert problems == [
        "tracked unsafe affirmative wording in release.md:1: Write beta is ready.",
        "tracked unsafe affirmative wording in release.md:2: Write beta available for public use.",
        "tracked unsafe affirmative wording in release.md:3: Write beta is authorized.",
        "tracked unsafe affirmative wording in release.md:4: Public write beta is published.",
        "tracked unsafe affirmative wording in release.md:5: Write beta is stable.",
        "tracked unsafe affirmative wording in release.md:6: Write-beta is stable.",
        "tracked unsafe affirmative wording in release.md:7: Write beta is security-audited.",
        "tracked unsafe affirmative wording in release.md:8: Write-beta is security-audited.",
        "tracked unsafe affirmative wording in release.md:9: Write beta release is production-ready.",
        "tracked unsafe affirmative wording in release.md:10: Write-beta release is production-ready.",
        "tracked unsafe affirmative wording in release.md:11: Write beta launch is authorized.",
        "tracked unsafe affirmative wording in release.md:12: Write-beta rollout is released.",
    ]


def test_content_violations_reject_public_write_beta_action_claims(tmp_path, monkeypatch):
    sample = tmp_path / "release.md"
    sample.write_text(
        "Ready to release public write beta.\n"
        "We can publish the write-beta rollout.\n"
        "Ship the owner-writebeta release to users.\n"
        "Ship the owner write beta release to users.\n"
        "Launch public writes for real books.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    assert guard.content_violations([sample]) == [
        "tracked unsafe affirmative wording in release.md:1: Ready to release public write beta.",
        "tracked unsafe affirmative wording in release.md:2: We can publish the write-beta rollout.",
        "tracked unsafe affirmative wording in release.md:3: Ship the owner-writebeta release to users.",
        "tracked unsafe affirmative wording in release.md:4: Ship the owner write beta release to users.",
        "tracked unsafe affirmative wording in release.md:5: Launch public writes for real books.",
    ]


def test_content_violations_reject_only_copy_safety_posture_claims(tmp_path, monkeypatch):
    sample = tmp_path / "safety.md"
    sample.write_text(
        "Only-copy write-safety is verified.\n"
        "Original book safety is confirmed.\n"
        "Private safety is proven.\n"
        "Real/private book write safety is validated.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    assert guard.content_violations([sample]) == [
        "tracked unsafe affirmative wording in safety.md:1: Only-copy write-safety is verified.",
        "tracked unsafe affirmative wording in safety.md:2: Original book safety is confirmed.",
        "tracked unsafe affirmative wording in safety.md:3: Private safety is proven.",
        "tracked unsafe affirmative wording in safety.md:4: Real/private book write safety is validated.",
    ]


def test_content_violations_allow_negative_safety_wording(tmp_path, monkeypatch):
    sample = tmp_path / "limits.md"
    sample.write_text(
        "No public write beta is ready.\n"
        "Is owner-writebeta published? No. It remains unpublished.\n"
        "Do not claim broad GnuCash compatibility is supported.\n"
        "Only-copy books are not safe for writes.\n"
        "Even future closure must not mean:\n"
        "- real working-book writes are safe;\n"
        "Do not release public write beta.\n"
        "This prevents consent to\n"
        "ship owner-writebeta.\n"
        "- forbidden implication: clean checks publish owner-writebeta.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    assert guard.content_violations([sample]) == []


def test_content_violations_reject_unbulleted_claim_after_negative_colon(tmp_path, monkeypatch):
    sample = tmp_path / "limits.md"
    sample.write_text(
        "Even future closure must not mean:\n"
        "The public write beta is ready for users.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    assert guard.content_violations([sample]) == [
        "tracked unsafe affirmative wording in limits.md:2: The public write beta is ready for users."
    ]


def test_content_violations_reject_private_book_path_like_values(tmp_path, monkeypatch):
    sample = tmp_path / "evidence.md"
    sample.write_text(
        "Probe command used /home/example-user/synthetic-fixtures/sample-book.gnucash.\n"
        "Windows source E:\\SyntheticFixtures\\sample-book.gnucash.sqlite was referenced.\n"
        "Mac source /Users/example-user/SyntheticFixtures/source.sqlite3 was referenced.\n"
        "File URI file:///home/example-user/synthetic-fixtures/source.sqlite was referenced.\n"
        "Windows slash path C:/SyntheticFixtures/source.gnucash was referenced.\n"
        "Mount source /mnt/private-ledgers/source.gnucash was referenced.\n"
        "Media source /media/operator/source.sqlite was referenced.\n"
        "Volume source /Volumes/PrivateBooks/source.sqlite3 was referenced.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    assert guard.content_violations([sample]) == [
        "tracked private book path-like value in evidence.md:1: Probe command used /home/example-user/synthetic-fixtures/sample-book.gnucash.",
        "tracked private book path-like value in evidence.md:2: Windows source E:\\SyntheticFixtures\\sample-book.gnucash.sqlite was referenced.",
        "tracked private book path-like value in evidence.md:3: Mac source /Users/example-user/SyntheticFixtures/source.sqlite3 was referenced.",
        "tracked private book path-like value in evidence.md:4: File URI file:///home/example-user/synthetic-fixtures/source.sqlite was referenced.",
        "tracked private book path-like value in evidence.md:5: Windows slash path C:/SyntheticFixtures/source.gnucash was referenced.",
        "tracked private book path-like value in evidence.md:6: Mount source /mnt/private-ledgers/source.gnucash was referenced.",
        "tracked private book path-like value in evidence.md:7: Media source /media/operator/source.sqlite was referenced.",
        "tracked private book path-like value in evidence.md:8: Volume source /Volumes/PrivateBooks/source.sqlite3 was referenced.",
    ]


def test_content_violations_allow_redacted_or_synthetic_non_private_placeholders(tmp_path, monkeypatch):
    sample = tmp_path / "safe-placeholders.md"
    sample.write_text(
        "book_path=<redacted>\n"
        "GnuCash path: <redacted>\n"
        "- amount: a trivial synthetic value only, never a real amount.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    assert guard.content_violations([sample]) == []
