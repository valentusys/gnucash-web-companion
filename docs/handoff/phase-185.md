# Phase 185 — write-alpha DELETE disposable dogfood with restore proof

Date: 2026-05-20
Status: COMPLETE — synthetic/disposable DELETE dogfood and restore proof captured without write-scope expansion
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-2-roadmap.md` (Phase 4 only)

## Goal

Obtain bounded disposable evidence for the existing DELETE route and prove the restore path after delete, without claiming safe writes on real/private books.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-184.md`;
  - roadmap file named by the phase contract;
  - relevant transaction DELETE route/service/tests, frontend delete form, and smoke helpers.
- Added `scripts/smoke/write-alpha-delete-restore-smoke.py`, a redacted local smoke helper for one existing DELETE route run plus restore proof.
- Copied the committed synthetic fixture to a temporary external disposable source, preflighted source/runtime/backup path classes, then copied it into ignored runtime data.
- Ran exactly one successful DELETE under explicit local-only `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true`.
- Verified pre-delete detail read-back, post-delete API/runtime absence, exactly one backup, exactly one successful `transaction.delete` audit increment, backup transaction fingerprint, checksum-based backup/restore equality, restored runtime/API read-back, and non-active lock evidence.
- Restarted runtime in default write-disabled mode and ran read-only API smoke proving validate/create/PATCH/DELETE return 403.
- Removed ignored runtime book/app DB/backups/locks after verification.
- Added evidence artifact `docs/dogfood/phase-185-write-alpha-delete-restore-dogfood.md`.

## Files changed

- `scripts/smoke/write-alpha-delete-restore-smoke.py`
- `docs/dogfood/phase-185-write-alpha-delete-restore-dogfood.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-185.md`

## Verification summary

Commands/results recorded for this phase:

```bash
python3 -m py_compile scripts/smoke/write-alpha-delete-restore-smoke.py
python3 apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --confirm-disposable-copy --runtime-book data/books/main.gnucash.sqlite --backup-dir data/backups/phase185 <temp synthetic source>
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose up -d
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose exec -T api python - --api-base-url http://localhost:8000 --password dummy --app-db /data/app/app.db --backup-root /data/backups --lock-root /data/locks --runtime-book /data/books/main.gnucash.sqlite < scripts/smoke/write-alpha-delete-restore-smoke.py
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 docker compose up -d
SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-api-smoke.py
cd apps/api && pytest tests/test_transaction_writes.py::TestWriteAlphaDeleteRouteDisposableFixture -q
cd apps/web && npm run test:auth-routes
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
# sensitive tracked-file hygiene scan over git ls-files
```

Results:

- DELETE+restore smoke passed with redacted output.
- Preflight passed for external disposable source, ignored runtime book target, and ignored backup class.
- DELETE smoke confirmed one successful DELETE, API/runtime absence of the deleted transaction, exactly one backup, exactly one successful `transaction.delete` audit increment, checksum-based restore equality, restored API detail read-back, and non-active stale-released lock evidence from inside the API container.
- Read-only API smoke after default reset passed, including disabled validate/create/PATCH/DELETE probes returning 403.
- Runtime teardown removed ignored book/app DB/backups/locks; only tracked `.gitkeep` placeholders remained under `data/`.
- Targeted backend DELETE route tests passed.
- Frontend auth-route/static checks passed, including hidden-by-default delete UI coverage.
- Docker Compose config validation passed and rendered `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No new write endpoint or write feature was added.
- DELETE scope stayed limited to one existing synthetic transaction in one ignored disposable runtime copy.
- The write-enabled run was explicit local-only `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true`.
- Restore proof used the generated pre-write backup under ignored runtime backup storage and copied it back only over the ignored disposable runtime book.
- Runtime book/app DB/backups/locks were removed after verification.
- No real/private/only-copy book, `.env`, token, key, cert, screenshot, export, app DB, runtime book, backup, lock artifact, raw path, account name, original description, memo, amount, or private financial data was committed.
- No release, tag, package, or publication action was performed.

## Next

Proceed only to the next roadmap phase when explicitly requested. Do not start audit UI work, multi-book regression, release-candidate dogfood, or release-readiness work from this phase.
