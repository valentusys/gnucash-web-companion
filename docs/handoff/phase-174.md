# Phase 174 — write-alpha copied-book preflight harness

Date: 2026-05-20
Status: COMPLETE — reproducible synthetic dry-run preflight only; no write mutation run
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-roadmap.md` (Phase 3 only)

## Goal

Make write-alpha copied-book dogfood preflight reproducible before any mutation, accepting a candidate only when safety checks pass.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-173.md`;
  - roadmap file named by the phase contract;
  - existing write-alpha copied-book runbook/helper/tests.
- Kept this as the preflight-harness phase only; no Phase 4 write dogfood mutation was run.
- Extended `apps/api/app/dogfood_preflight.py` so write-alpha preflight now fails closed when:
  - candidate path is missing;
  - disposable-copy acknowledgement is absent;
  - source is inside the repo;
  - source looks like `.env`, app metadata DB, or backup artifact/directory;
  - runtime target is outside `data/books/` or is not ignored by git;
  - backup target is outside `data/backups/` or is not ignored by git.
- Added dry-run metadata evidence with redacted book class, source/runtime/backup classes, byte size, and short SHA-256 checksum.
- Updated CLI help/path for `--dry-run` and kept it copy-free/mutation-free.
- Expanded targeted pytest coverage for safe pass, unsafe failures, git-ignore fail-closed behavior, source-class rejection, redaction, and no-artifact guarantees.
- Added redacted synthetic evidence in `docs/dogfood/phase-174-write-alpha-preflight.md`.

## Files changed

- `apps/api/app/dogfood_preflight.py`
- `apps/api/scripts/check_dogfood_book_candidate.py`
- `apps/api/tests/test_dogfood_preflight.py`
- `docs/dogfood/phase-174-write-alpha-preflight.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-174.md`

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No write mutation was run.
- No real/private/only-copy book was used.
- No runtime book, app DB, backup, `.env`, screenshot, CSV export, token, key, cert, or private data artifact was created for commit.
- The helper does not parse with `piecash`, copy into runtime data, or mutate app/book state.
- Ready output is redacted: no absolute private paths, raw filenames, account names, transaction descriptions, memos, or amounts.
- No release/tag/package was published.

## Verification

Commands run:

```bash
cd apps/api && pytest tests/test_dogfood_preflight.py -q
python apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy <temporary external synthetic copy>
python apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run <temporary external synthetic copy> || true
python apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy apps/api/tests/fixtures/test-book.gnucash.sqlite || true
python apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy <missing temporary external synthetic copy> || true
git status --short -- data/books data/backups data/app
```

Results:

- Targeted dogfood preflight tests passed (`10 passed`).
- Full backend suite passed (`402 passed, 32 warnings`).
- Synthetic external dry-run passed with redacted file class, path classes, `size_bytes`, short checksum, and `dry_run=true`.
- Missing acknowledgement, source-inside-repo, and missing-file probes failed closed.
- Failed probes did not create runtime book, backup, or app DB artifacts.
- Redacted evidence scan passed for absolute private paths, raw filenames, account-like tokens, and amount-like tokens.
- `git diff --check` passed.
- Docker Compose config validation passed, and rendered config still keeps `GNUCASH_WRITES_ENABLED: "false"` by default.
- Sensitive tracked-file hygiene scan passed.

## Next

Continue only with the next explicitly requested phase. Do not run actual write-alpha dogfood until a later phase explicitly authorizes one disposable copied-book mutation and preflight passes immediately before the runtime copy step.
