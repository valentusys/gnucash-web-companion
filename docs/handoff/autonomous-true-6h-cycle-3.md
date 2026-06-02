# Autonomous true 6h cycle 3 — #22 Desktop tooling probe hardening

## Analyst queue scan

#22 remains active. After report and matrix vocabulary hardening, the next safe work package is Desktop tooling probe hardening and current blocked/manual documentation. This work is non-mutating and does not open books.

## PM work package

Goal: harden the safe `gnucash`/`gnucash-cli` availability probe against unexpected private-looking command output and document current local tooling status as blocker evidence only.

Scope:
- `apps/api/scripts/probe_gnucash_desktop_tooling.py`
- `apps/api/tests/test_gnucash_compatibility_metadata.py`
- `docs/gnucash-desktop-tooling-autonomous-cycle-3.md`

Non-goals:
- no book opening;
- no fixture generation;
- no user-directory search;
- no package installation;
- no Desktop-version support claim.

Acceptance criteria:
- mocked version output containing path/account/memo/amount-like text is redacted;
- probe still records only availability/version status;
- local observation documents that `gnucash-cli` exists but fixture generation remains blocked/manual.

Tests:
- `python -m pytest apps/api/tests/test_gnucash_compatibility_metadata.py -q`
- actual non-mutating probe command.

Stop conditions:
- any book open/search/mutation would be required;
- probe output leaks private-looking data.

## Programmer implementation

Added redaction to the Desktop tooling probe's bounded version output and a regression test for unexpected path/account/memo/amount-like command output. Added a short cycle-3 tooling evidence doc.

## Auditor verification

Focused test output:

```text
........                                                                 [100%]
8 passed in 0.05s
```

Actual probe excerpt:

```text
"gnucash": available true; version_command_succeeded false; no DISPLAY/headless GUI error
"gnucash-cli": available true; version_command_succeeded true; version_output "GnuCash 5.14\nBuild ID: 5.14+(2025-12-20)"
"desktop_generated_fixture_possible_now": false
```

Safety/privacy check:
- no book opened;
- no private directory searched;
- executable paths are redacted;
- version-output redaction is covered by tests;
- writes remain disabled by default;
- no release was published.

## PM decision

Cycle accepted. Continue #22; Desktop-generated fixture remains blocked on isolated disposable GUI/manual-safe fixture creation and read-only validation.
