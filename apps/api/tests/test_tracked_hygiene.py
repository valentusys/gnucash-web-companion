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
        "ACCOUNT_DESCRIPTION=Redacted Account Description\nTRANSACTION_AMOUNT=0.00\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    problems = guard.content_violations([sample])

    assert problems == [
        "tracked raw private-evidence marker 'RAW_PRIVATE_EVIDENCE_BEGIN' in: public-report.md",
        "tracked raw private-evidence marker 'PRIVATE_BOOK_PATH=' in: public-report.md",
        "tracked raw private-evidence marker 'ACCOUNT_NAME=' in: public-report.md",
        "tracked raw private-evidence marker 'ACCOUNT_DESCRIPTION=' in: public-report.md",
        "tracked raw private-evidence marker 'TRANSACTION_AMOUNT=' in: public-report.md",
        "tracked raw private-evidence label in public-report.md:2: PRIVATE_BOOK_PATH=/redacted",
        "tracked raw private-evidence label in public-report.md:3: ACCOUNT_NAME=Redacted Account",
        "tracked raw private-evidence label in public-report.md:5: TRANSACTION_AMOUNT=0.00",
    ]


def test_content_violations_reject_private_path_label_variants(tmp_path, monkeypatch):
    sample = tmp_path / "handoff.md"
    sample.write_text(
        "PRIVATE_PATH: /redacted\nORIGINAL_GNUCASH_PATH=/redacted\nONLY_COPY_GNUCASH_PATH=/redacted\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    problems = guard.content_violations([sample])

    assert problems == [
        "tracked raw private-evidence marker 'PRIVATE_PATH:' in: handoff.md",
        "tracked raw private-evidence marker 'ORIGINAL_GNUCASH_PATH=' in: handoff.md",
        "tracked raw private-evidence marker 'ONLY_COPY_GNUCASH_PATH=' in: handoff.md",
        "tracked raw private-evidence label in handoff.md:1: PRIVATE_PATH: /redacted",
        "tracked raw private-evidence label in handoff.md:2: ORIGINAL_GNUCASH_PATH=/redacted",
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
        "GnuCash path: /redacted\n"
        "Book path = /redacted\n"
        "Real account name: Redacted Account\n"
        "Account name: Redacted Account\n"
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
        "tracked raw private-evidence label in public-report.md:7: GnuCash path: /redacted",
        "tracked raw private-evidence label in public-report.md:8: Book path = /redacted",
        "tracked raw private-evidence label in public-report.md:9: Real account name: Redacted Account",
        "tracked raw private-evidence label in public-report.md:10: Account name: Redacted Account",
        "tracked raw private-evidence label in public-report.md:11: Memo: Redacted memo",
        "tracked raw private-evidence label in public-report.md:12: Amount: 0.00",
        "tracked raw private-evidence label in public-report.md:13: Balance: 0.00",
        "tracked raw private-evidence label in public-report.md:14: Account balance: 0.00",
        "tracked raw private-evidence label in public-report.md:15: Transaction amount: 0.00",
    ]


def test_content_violations_reject_markdown_private_evidence_labels(tmp_path, monkeypatch):
    sample = tmp_path / "public-report.md"
    sample.write_text(
        "- Private path: /redacted\n"
        "* Original GnuCash path = /redacted\n"
        "+ Real account name: Redacted Account\n"
        "> Transaction memo: Redacted memo\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    problems = guard.content_violations([sample])

    assert problems == [
        "tracked raw private-evidence label in public-report.md:1: - Private path: /redacted",
        "tracked raw private-evidence label in public-report.md:2: * Original GnuCash path = /redacted",
        "tracked raw private-evidence label in public-report.md:3: + Real account name: Redacted Account",
        "tracked raw private-evidence label in public-report.md:4: > Transaction memo: Redacted memo",
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
        "Write beta is production-ready.\n"
        "Real books are safe for writes.\n"
        "Private book writes are safe.\n"
        "Original books are safe for mutation.\n",
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
        "tracked unsafe affirmative wording in release.md:15: Write beta is production-ready.",
        "tracked unsafe affirmative wording in release.md:16: Real books are safe for writes.",
        "tracked unsafe affirmative wording in release.md:17: Private book writes are safe.",
        "tracked unsafe affirmative wording in release.md:18: Original books are safe for mutation.",
    ]


def test_content_violations_reject_compatibility_guarantee_wording(tmp_path, monkeypatch):
    sample = tmp_path / "compatibility.md"
    sample.write_text(
        "Fully compatible with GnuCash Desktop releases.\n"
        "Guaranteed compatible with GnuCash SQL books.\n"
        "Production-ready compatibility for write beta.\n"
        "All SQL backends are supported.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)

    problems = guard.content_violations([sample])

    assert problems == [
        "tracked unsafe affirmative wording in compatibility.md:1: Fully compatible with GnuCash Desktop releases.",
        "tracked unsafe affirmative wording in compatibility.md:2: Guaranteed compatible with GnuCash SQL books.",
        "tracked unsafe affirmative wording in compatibility.md:3: Production-ready compatibility for write beta.",
        "tracked unsafe affirmative wording in compatibility.md:4: All SQL backends are supported.",
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


def test_content_violations_allow_negative_safety_wording(tmp_path, monkeypatch):
    sample = tmp_path / "limits.md"
    sample.write_text(
        "No public write beta is ready.\n"
        "Do not claim broad GnuCash compatibility is supported.\n"
        "Only-copy books are not safe for writes.\n"
        "Even future closure must not mean:\n"
        "- real working-book writes are safe;\n",
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
