# Phase 269 handoff — Owner dry-run request packet

Status: COMPLETE.

## Objective

Engineer objective: prepare a concise owner-facing copied-book dry-run request packet without running owner dogfood and without authorizing mutation.

## Scope

Created:

- `docs/write-alpha/owner-dry-run-request.md`

The packet includes:

- prerequisites for copied/restorable outside-git book use;
- the dry-run-only command;
- local redaction validation command;
- a redacted checklist for what the owner may paste back;
- stop conditions;
- explicit “do not run CREATE/PATCH/DELETE” wording.

## Safety review

- Original and only-copy books are forbidden.
- The packet asks only for redacted pass/fail/status evidence, not raw evidence files.
- Screenshots, CSV exports, raw paths, account names, memos, amounts, app DBs, books, backups, `.env` contents, tokens, keys, certs, and private financial artifacts are explicitly forbidden in shared output.
- `GNUCASH_WRITES_ENABLED=false` remains the default/reset posture.
- Explicit write-alpha dry-run inspection still requires `APP_ENV=test`.
- CREATE/PATCH/DELETE remain blocked.

## Verification

Commands/checks run:

```text
python3 scripts/check_public_status.py
pytest -q apps/api/tests/test_public_status_guard.py
git diff --check
```

## GitHub issue #36 evidence

Phase 269 is related to #36 because it prepares the owner dry-run request packet. Update #36 after commit/push with the packet path and safety summary.

## PM invocation

PM was not invoked. Phase 269 is a documentation/request-packet phase with no release/no-release decision, mutation authorization, write-mode relaxation, publication, private-data exception, or conflicting owner choice.

## Next phase

Phase 270 — Cycle 1 release/no-release decision. PM must be invoked by the phase definition.
