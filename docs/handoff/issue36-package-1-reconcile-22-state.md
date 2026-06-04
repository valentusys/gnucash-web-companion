# Package 1 — reconcile #22 state

Date: 2026-06-04

## Decision

`CLOSE_22_ON_GITHUB_NARROWLY` is already the correct reconciled state.

## Starting state checked

- Local `main` started clean at `bcae43e`.
- GitHub open issue list showed only #36.
- REST issue check showed #22 state is `closed`.
- The latest #22 comment closes the issue by `bcae43e` with narrow Desktop-generated synthetic SQLite fixture evidence only.
- `PROJECT_STATUS.md` already said #22 and #28 are closed.
- `docs/gnucash-compatibility.md` already described #22 as closed only for narrow Desktop-generated synthetic SQLite read-only fixture evidence.
- `README.md` still described #22/#28 as open, so it was stale.

## Evidence accepted for #22

The accepted evidence remains narrow:

- GnuCash 5.14 Desktop created one disposable synthetic SQLite book in isolated Xvfb.
- The raw SQLite fixture stayed outside git.
- Redacted metadata recorded safe schema/table-count evidence only.
- `scripts/preflight_desktop_fixture_candidate.py` accepted the candidate.
- Default-read-only validation passed with `GNUCASH_WRITES_ENABLED=false` and checksum unchanged.

## Reconciliation work

- Updated `README.md` so public docs agree that #22 and #28 are closed.
- Preserved narrow compatibility wording: no broad Desktop-version support, no PostgreSQL/MySQL/MariaDB/XML claim, no real-book safety claim, and no write-compatibility claim.

## Verification

To be completed in Package 6 full gate:

- `gh issue view 22` / REST state check.
- `gh issue list --state open`.
- `python3 scripts/check_public_status.py`.
- `git diff --check`.

## Safety

Mutation counts: CREATE 0 / PATCH 0 / DELETE 0.

No GnuCash book, app DB, backup, export, screenshot, private path, account name, transaction description, memo, amount, secret, key, token, or raw private evidence was opened, copied, mutated, committed, or posted.
