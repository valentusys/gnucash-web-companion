# Phase 173 — write-alpha copied-book dogfood design

Date: 2026-05-20
Status: COMPLETE — executable design and safe preflight interface only; no real write dogfood run
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-roadmap.md` (Phase 2 only)

## Goal

Prepare a safe executable design for future write-alpha dogfood on a copied/disposable GnuCash SQL book without risking a main/private/only-copy book.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-172.md`;
  - roadmap file named by the phase contract;
  - existing dogfood/write-alpha preflight and recovery files.
- Kept this as Phase 173 only; no Phase 174 preflight harness execution and no Phase 175 write dogfood were started.
- Added `docs/dogfood/write-alpha-copied-book-runbook.md` with a single local-only command path covering:
  - hard stop conditions for real/private/only-copy books;
  - source copied/disposable provenance outside git;
  - runtime copy under ignored `data/books/`;
  - local app DB under ignored `data/app/`;
  - backups under ignored `data/backups/` plus an operator backup outside git;
  - `APP_ENV=test` with explicit local-only `GNUCASH_WRITES_ENABLED=true` only for dogfood;
  - one minimal balanced two-split create transaction shape;
  - GnuCash Desktop verification after Docker shutdown;
  - restore and teardown/no-artifact checks;
  - redacted evidence template.
- Extended `apps/api/scripts/check_dogfood_book_candidate.py` with a `--write-alpha-plan` helper interface.
- Added tested helper logic in `apps/api/app/dogfood_preflight.py` to validate only path classes and disposable acknowledgement without opening/parsing/copying/writing a book.
- Added regression tests in `apps/api/tests/test_dogfood_preflight.py` for acknowledgement, source-inside-repo rejection, unsafe runtime/backup target rejection, and redacted metadata-only ready summaries.

## Files changed

- `apps/api/app/dogfood_preflight.py`
- `apps/api/scripts/check_dogfood_book_candidate.py`
- `apps/api/tests/test_dogfood_preflight.py`
- `docs/dogfood/write-alpha-copied-book-runbook.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-173.md`

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No write dogfood was run.
- No real/private/only-copy book was used.
- No runtime book, app DB, backup, `.env`, screenshot, CSV export, token, key, cert, or private data artifact was created for commit.
- The helper does not read financial content; it only checks file existence/stat size, repo containment, ignored runtime path classes, and explicit disposable acknowledgement.
- Helper/runbook evidence is intentionally redacted: no absolute private paths, account names, transaction descriptions, memos, or amounts.
- No release/tag/package was published.

## Verification

Commands run:

```bash
cd apps/api && pytest tests/test_dogfood_preflight.py -q
cd apps/api && pytest -q
git diff --check
python3 - <<'PY'
from pathlib import Path
runbook = Path('docs/dogfood/write-alpha-copied-book-runbook.md').read_text()
required = [
    'Hard stop conditions',
    'real/private/only-copy',
    'APP_ENV=test',
    'GNUCASH_WRITES_ENABLED=true',
    'data/books/',
    'data/backups/',
    'GnuCash Desktop',
    'Do not include private paths',
]
missing = [item for item in required if item not in runbook]
if missing:
    raise SystemExit(f'missing runbook terms: {missing}')
print('runbook static review passed')
PY
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# sensitive tracked-file hygiene scan
```

Results:

- Targeted dogfood preflight tests passed.
- Full backend suite passed.
- `git diff --check` passed.
- Static runbook review passed and confirmed required stop/default/test-mode/no-leak terms are present.
- Docker Compose config validation passed.
- Rendered Docker Compose config still keeps `GNUCASH_WRITES_ENABLED: "false"` by default.
- Sensitive tracked-file hygiene scan passed.

## Next

Continue only with the next explicitly requested phase. Phase 174 may turn this design into a stricter reproducible preflight harness. Do not run write-alpha dogfood on any copied book until a later phase explicitly authorizes it and the source passes disposable provenance checks.
