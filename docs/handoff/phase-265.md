# Phase 265 — Dry-run troubleshooting and abort conditions

Date: 2026-05-22

## Goal

Ensure a non-expert owner knows when to stop and ask for review before any mutation.

## Scope

- Added a troubleshooting/abort table to `docs/write-alpha/owner-dry-run-quickstart.md`.
- Covered missing copied book, unsafe path, original/only-copy target, backup preflight failure,
  missing `APP_ENV=test`, unsafe write defaults, Docker/config failure, auth/health failure,
  redaction failure, missing no-mutation proof, and disabled-write endpoint success.
- Linked the broader maintainer copied-book dogfood packet back to the quickstart troubleshooting table
  for owner dry-run handling.

## Non-goals

- No automated release.
- No mutation.
- No UI feature work.
- No write-gate relaxation.
- No owner/private/original/only-copy book use.

## Acceptance criteria

- Every dry-run failure class has a safe recommended action.
- Docs explicitly say not to proceed to CREATE unless dry-run is clean.
- Docs do not recommend weakening safety gates or using an original/only-copy book.

## Safety checks

- Original and only-copy books remain forbidden.
- `APP_ENV=test` remains required for explicit write-alpha inspection.
- `GNUCASH_WRITES_ENABLED=false` remains the default/reset target.
- Redaction failure instructs stop/no share/no commit until bounded evidence passes validation.
- Disabled-write endpoint success is treated as a write-gate blocker.

## Verification

- Documentation-only phase; no scripts changed.
- `pytest -q apps/api/tests/test_public_status_guard.py`
  - Result: `27 passed`.
- `git diff --check`
  - Result: pass.

## Expected artifacts

- Updated `docs/write-alpha/owner-dry-run-quickstart.md`
- Updated `docs/write-alpha/maintainer-copied-book-dogfood-packet.md`
- `docs/handoff/phase-265.md`

## PM invocation

PM was not invoked. Phase 265 is documentation/troubleshooting work with no release decision,
owner-risk authorization, write-mode relaxation, publication, security exception, or conflicting owner
choice.

## Result

Phase 265 is complete. The next roadmap phase is Phase 266 — public docs drift guard update for the
v0.2.8 owner dry-run posture.
