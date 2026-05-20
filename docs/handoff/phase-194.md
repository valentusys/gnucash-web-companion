# Phase 194 — Write-alpha smoke helper resilience

Date: 2026-05-20
Status: COMPLETE — helpers updated, tested, dogfooded on synthetic/disposable local runtime, committed/pushed
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-3-roadmap.md` (Phase 3 only)

## Goal

Make create/PATCH/DELETE write-alpha smoke helpers resilient to root-owned runtime artifacts so future dogfood does not stop after successful route execution without bounded backup/audit/lock evidence.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-193.md`;
  - roadmap file named by the phase contract;
  - write-alpha smoke helpers and smoke evidence tests.
- Added shared smoke evidence helper `scripts/smoke/write_alpha_smoke_evidence.py`:
  - host-side backup/audit/lock probes return bounded counts/statuses only;
  - if host-side runtime artifacts are unreadable, probes fall back to `docker compose exec -T api` and inspect from inside the API container;
  - compose interpolation receives dummy local-only defaults for `JWT_SECRET` and `APP_ADMIN_PASSWORD` when the smoke process itself did not export them;
  - container probe output is reduced JSON and does not expose raw paths, filenames, app DB rows, payloads, account names, memos, or amounts;
  - `/data/...` backup paths returned by API routes are mapped to ignored host `data/...` paths when host-side restore/inspection is possible.
- Updated smoke helpers:
  - `scripts/smoke/write-alpha-create-smoke.py` uses shared backup/audit/lock evidence collection;
  - `scripts/smoke/write-alpha-patch-smoke.py` uses shared backup/audit/lock evidence collection, including failed missing-transaction audit counts;
  - `scripts/smoke/write-alpha-delete-restore-smoke.py` uses shared backup/audit/lock evidence collection and emits restore proof only if a host-readable backup was actually copied back into the disposable runtime book.
- Preserved exactly-once mutation semantics:
  - route execution is not retried after a successful route response just because evidence collection needs container-side fallback;
  - during dogfood, an initial create evidence failure after successful route execution was inspected container-side and then cleaned up; the same runtime was not mutated again.
- Added tests in `apps/api/tests/test_write_alpha_smoke_lock_evidence.py` for:
  - lock evidence redaction;
  - unreadable-lock fallback guidance;
  - API-container fallback for unreadable lock evidence;
  - API-container fallback for unreadable backup count evidence;
  - path-safe DELETE restore-skip copy.
- Added dogfood evidence: `docs/dogfood/phase-194-write-alpha-smoke-helper-resilience.md`.
- Updated `PROJECT_STATUS.md`.

## Files changed

- `PROJECT_STATUS.md`
- `apps/api/tests/test_write_alpha_smoke_lock_evidence.py`
- `docs/dogfood/phase-194-write-alpha-smoke-helper-resilience.md`
- `docs/handoff/phase-194.md`
- `scripts/smoke/write_alpha_smoke_evidence.py`
- `scripts/smoke/write-alpha-create-smoke.py`
- `scripts/smoke/write-alpha-patch-smoke.py`
- `scripts/smoke/write-alpha-delete-restore-smoke.py`

No backend write route semantics, write scope, frontend write UI, Docker default, release/tag state, GitHub issue state, or product mutation behavior was changed.

## Verification summary

Commands/results:

```bash
cd apps/api && pytest tests/test_write_alpha_smoke_lock_evidence.py -q
# 7 passed

python3 -m py_compile \
  scripts/smoke/write_alpha_smoke_evidence.py \
  scripts/smoke/write-alpha-create-smoke.py \
  scripts/smoke/write-alpha-patch-smoke.py \
  scripts/smoke/write-alpha-delete-restore-smoke.py
# passed

cd apps/api && pytest tests/test_write_alpha_smoke_lock_evidence.py tests/test_transaction_writes.py -q
# 66 passed, 33 warnings

# local synthetic/disposable Docker/Caddy dogfood
SMOKE_ADMIN_PASSWORD=dummy python3 scripts/smoke/read-only-api-smoke.py
# PASS with validate/create/PATCH/DELETE disabled-write 403

SMOKE_ADMIN_PASSWORD=dummy python3 scripts/smoke/write-alpha-create-smoke.py
# PASS with one create, one backup increment, one success audit increment, non-active lock evidence

SMOKE_ADMIN_PASSWORD=dummy python3 scripts/smoke/write-alpha-patch-smoke.py
# PASS with missing-transaction 404/no-backup, one PATCH, audit evidence, non-active lock evidence

SMOKE_ADMIN_PASSWORD=dummy python3 scripts/smoke/write-alpha-delete-restore-smoke.py
# PASS with one DELETE, backup evidence, restore proof because restore was actually performed, non-active lock evidence

SMOKE_ADMIN_PASSWORD=dummy python3 scripts/smoke/read-only-api-smoke.py
# final PASS with validate/create/PATCH/DELETE disabled-write 403

python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED
# final dry-run: books=0, app=0, backups=0, locks=0

cd apps/api && pytest -q
# recorded in final report

cd apps/web && npm run build
# recorded in final report

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# recorded in final report; rendered default remains false

git diff --check
# recorded in final report

# sensitive tracked-file hygiene scan from phase execution playbook
# recorded in final report
```

## Dogfood evidence

`docs/dogfood/phase-194-write-alpha-smoke-helper-resilience.md` records the local synthetic/disposable run. Runtime data was created only under ignored `data/` classes and cleaned after verification. Output was redacted to statuses/counts and did not include raw artifact paths, filenames, account names, memos, amounts, payloads, secrets, or private data.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Mutating local dogfood used only explicit `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true` on fresh ignored synthetic runtime copies.
- No real/private/only-copy book was used.
- No `.env`, app DB, book, backup, screenshot, CSV export, token, key, cert, raw path, account name, transaction description, memo, amount, or private financial artifact was committed.
- No release, tag, package, Docker image, production-readiness claim, security-audit claim, or real/private-book write-safety claim was added.

## Risks / follow-up

- The helper relies on a running API container for container-side fallback evidence; if the stack is already stopped, operators should use the Phase 193 stopped-runtime cleanup helper instead.
- DELETE restore proof is conditional: it is emitted only when a restore copy actually succeeds. If host backup is unreadable and no restore is performed, the helper reports path-safe backup evidence and restore-skip status rather than claiming restore.
- Write-alpha remains experimental, disabled by default, `APP_ENV=test` gated when enabled, and unsafe for real/private or only-copy books.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
