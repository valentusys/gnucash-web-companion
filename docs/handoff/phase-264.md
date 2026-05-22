# Phase 264 — Owner dry-run evidence schema acceptance tests

Date: 2026-05-22

## Goal

Make dry-run evidence validation strict enough that owner evidence can be safely reviewed without
leaking private data.

## Scope

- Added acceptance tests for owner dry-run evidence redaction failure cases.
- Covered private path-like, amount-like, memo-like, account-name-like, and nested payload-like data.
- Hardened `scripts/redact_dogfood_evidence.py` so strings and numeric values nested below sensitive
  container keys such as `payload`/`splits` are rejected or redacted instead of passing through via
  neutral child key names.
- Added a positive redaction-mode test proving bounded evidence remains useful after private payload
  fields are redacted.
- Updated the evidence schema docs to describe nested sensitive-container handling.

## Non-goals

- No mutation.
- No release.
- No broad logging refactor.
- No owner/private/original/only-copy book use.

## Acceptance criteria

- Redaction/evidence tests cover accepted and rejected examples.
- Failure cases cover private paths, amounts, memos, account names, and nested payload data.
- Accepted/redacted evidence preserves useful bounded facts: phase, classification, counts, lock status,
  restore/default-reset status, and redacted command labels.
- Test fixtures contain only synthetic placeholder values.

## Safety checks

- No raw private strings were committed.
- No evidence schema bypass remains for nested free-form payload fields under sensitive container keys.
- Evidence remains counts/statuses/placeholders only.
- `GNUCASH_WRITES_ENABLED=false` remains default and `APP_ENV=test` gating is unchanged.

## Verification

- `pytest -q apps/api/tests/test_redact_dogfood_evidence.py`
  - Result: `7 passed`.

## Expected artifacts

- Updated `scripts/redact_dogfood_evidence.py`
- Updated `apps/api/tests/test_redact_dogfood_evidence.py`
- Updated `docs/write-alpha/dogfood-evidence-schema.md`
- `docs/handoff/phase-264.md`

## PM invocation

PM was not invoked. Phase 264 is a test/tooling hardening phase with no release decision, owner-risk
authorization, write-mode relaxation, publication, security exception, or conflicting owner choice.

## Result

Phase 264 is complete. The next roadmap phase is Phase 265 — dry-run troubleshooting and abort
conditions.
