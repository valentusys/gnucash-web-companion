# Issue #22 package 5: PM/Auditor decision

Date: 2026-06-04

## Decision

KEEP_22_OPEN_WITH_EXACT_EXTERNAL_BLOCKER_AND_NEXT_MANUAL_STEPS

## Rationale

The #22 blocker is not resolved in this environment. The host has GnuCash tooling available, but it does not have a safe disposable Desktop GUI/Xvfb automation environment for creating and saving a new synthetic SQLite book.

Observed environment:

- `gnucash-cli --version` reports GnuCash 5.14 / Build ID 5.14+(2025-12-20).
- `gnucash` is installed, but cannot initialize without a display.
- `DISPLAY` and `WAYLAND_DISPLAY` are unset.
- `xvfb-run`, `Xvfb`, and `xdotool` are missing from PATH.
- No safe noninteractive `gnucash-cli` path was found to create and save a new SQLite fixture.

CLI availability and version metadata are useful environment evidence, but they are not Desktop-generated synthetic SQLite fixture evidence.

## Issue #22 outcome

Issue #22 must remain open. Closing it now would overclaim compatibility because the Desktop-generated synthetic SQLite fixture evidence still does not exist.

The exact external blocker is:

> A disposable isolated GnuCash Desktop GUI/Xvfb/manual-safe environment must create and save a minimal synthetic SQLite GnuCash book outside git, after which only redacted metadata/manifests and validator output may be committed.

## Manual next steps

Use `docs/compatibility/desktop-synthetic-fixture-runbook.md`.

Required high-level steps:

1. Use an isolated disposable environment with GnuCash Desktop GUI access.
2. Create a new SQLite book using only generic synthetic accounts and trivial synthetic transactions.
3. Keep the raw SQLite file outside git.
4. Run redacted metadata collection.
5. Run `scripts/preflight_desktop_fixture_candidate.py`.
6. Run read-only/default fail-closed validation with `GNUCASH_WRITES_ENABLED=false`.
7. Update #22 with redacted evidence output only.

## Safety/privacy decision

No raw fixture was generated in this session.
No GnuCash book was opened, copied, committed, or mutated.
No owner/private/source-only book was used.
No raw DB/app DB/backup/export/screenshot/.env/token/key/cert/account/description/memo/amount evidence was committed or posted.

## Release impact

- #36 remains open.
- v0.4.0-owner-writebeta remains not prepared and not published.
- v0.5.1-public-readonly-beta remains not published and must not be claimed.
- Public read-only beta remains v0.5.0-public-readonly-beta.
- The #22 compatibility-confidence gap remains a blocker for broad write-readiness/release-confidence claims.
