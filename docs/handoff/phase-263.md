# Phase 263 — Owner dry-run packet cleanup and single entrypoint

Date: 2026-05-22

## Goal

Make the owner copied-book dry-run path easy to run without mutation and without leaking private data.

## Scope

- Reviewed the existing copied-book dogfood packet, dry-run wrapper, preflight/readiness path, and
  evidence redaction helper.
- Added one owner-facing dry-run-only entrypoint:
  `python3 scripts/write_alpha_owner_dry_run.py`.
- Added `docs/write-alpha/owner-dry-run-quickstart.md` as the single dry-run command path.
- Updated the maintainer copied-book dogfood packet to point dry-run users to that entrypoint.
- Added targeted tests proving the entrypoint has no CREATE mode and records no mutation evidence.
- Ran the entrypoint against a synthetic disposable fixture copy outside the git checkout and committed
  only redacted evidence.

## Non-goals

- No CREATE-one execution.
- No PATCH.
- No DELETE.
- No owner/private/original/only-copy book use.
- No release.
- No write default change or `APP_ENV=test` gate relaxation.

## Acceptance criteria

- One obvious command/document path exists for owner dry-run only:
  `docs/write-alpha/owner-dry-run-quickstart.md` → `scripts/write_alpha_owner_dry_run.py`.
- The command defaults to no mutation and exposes no mutation CLI mode.
- The docs explicitly forbid original and only-copy books.
- Synthetic dry-run evidence records `mutation_requested=false`, `mutation_performed=false`, and
  `create_command_status=not-run`.

## Safety checks

- Dry-run path does not call mutation endpoints and has no CREATE/PATCH/DELETE mode.
- Evidence output passed `scripts/redact_dogfood_evidence.py` before commit.
- Evidence uses redacted placeholders and counts/statuses only.
- `GNUCASH_WRITES_ENABLED=false` remains committed/default; dry-run inspection still requires
  `APP_ENV=test`.
- Original/only-copy book use remains forbidden.

## Verification

- `pytest -q apps/api/tests/test_write_alpha_owner_dry_run.py apps/api/tests/test_write_alpha_copied_book_dogfood.py apps/api/tests/test_redact_dogfood_evidence.py`
  - Result: `13 passed`.
- Synthetic disposable dry-run from an outside-git temp copy:
  - Command: `GNUCASH_WRITES_ENABLED=true APP_ENV=test python3 scripts/write_alpha_owner_dry_run.py ...`
  - Result: pass; no mutation requested/performed; default-disabled reset verified.
- Redaction validation:
  - `python3 scripts/redact_dogfood_evidence.py docs/dogfood/phase-263-owner-dry-run-synthetic-evidence.json`
  - Result: pass.

## Expected artifacts

- `scripts/write_alpha_owner_dry_run.py`
- `apps/api/tests/test_write_alpha_owner_dry_run.py`
- `docs/write-alpha/owner-dry-run-quickstart.md`
- Updated `docs/write-alpha/maintainer-copied-book-dogfood-packet.md`
- `docs/dogfood/phase-263-owner-dry-run-synthetic-evidence.json`
- `docs/handoff/phase-263.md`

## PM invocation

PM was not invoked. Phase 263 is an engineering dry-run-only cleanup phase with no release decision,
owner-risk authorization, write-mode relaxation, publication, security exception, or conflicting owner
choice.

## Result

Phase 263 is complete. The next roadmap phase is Phase 264 — owner dry-run evidence schema acceptance
tests.
