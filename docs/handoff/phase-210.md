# Phase 210 — Bounded disposable write-alpha CRUD/restore refresh

Date: 2026-05-21
Status: COMPLETE — bounded write-alpha route-family dogfood passed and default read-only reset passed
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-1/roadmap-cycle-1.md` (Cycle 1, Phase 9 only)

## Goal

Collect one fresh bounded write-alpha evidence pass after cycle-1 hardening, using only ignored synthetic/disposable runtime copies and then returning to default false.

## Scope completed

- Read required context: `AGENTS.md`, `PROJECT_STATUS.md`, latest handoff `docs/handoff/phase-209.md`, and the cycle-1 roadmap file.
- Used only `apps/api/tests/fixtures/test-book.gnucash.sqlite` copied to a temporary external disposable source, then copied into ignored runtime storage as `data/books/main.gnucash.sqlite`.
- Ran the write-alpha copied-book preflight dry-run with explicit disposable acknowledgement; it passed with source/runtime/backup classes redacted and bounded.
- Started local Docker/Caddy only with explicit local `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true` and dummy local-only secrets.
- Prepared a fresh ignored runtime copy before each route-family smoke.
- Ran create smoke: validation failures failed safely, exactly one create succeeded, read-back passed, backup/audit increased once, and lock evidence was stale-released/not active.
- Ran PATCH smoke: missing transaction failed safely without backup, exactly one PATCH succeeded, read-back passed, amount fingerprint stayed unchanged, backup/audit evidence passed, and lock evidence was stale-released/not active.
- Ran DELETE+restore smoke: exactly one DELETE succeeded, absence checks passed, backup/audit evidence passed, host-readable restore proof and restored API read-back passed, and lock evidence was stale-released/not active.
- Reset runtime to default false, confirmed rendered Compose has `GNUCASH_WRITES_ENABLED: "false"` for API and web, and reran the read-only API smoke with validate/create/PATCH/DELETE returning 403.
- Cleaned ignored runtime book/backups/locks/generated smoke app DB; restored pre-existing ignored local `data/app/app.db` as untracked local state.
- Updated dogfood evidence, changelog, project status, and this handoff.

## Files changed

- `docs/dogfood/phase-210-write-alpha-cycle-1-dogfood.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-210.md`

No product code or write endpoint behavior changed in this phase.

## Verification summary

Commands/results:

```text
python3 apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy --runtime-book data/books/main.gnucash.sqlite --backup-dir data/backups/write-alpha-dogfood <external-disposable-source>
# passed: status=ready; source=external copied/disposable; runtime=ignored data/books; backups=ignored data/backups; dry_run=true

APP_ENV=test GNUCASH_WRITES_ENABLED=true docker compose up -d --build
# passed with dummy local-only secrets

SMOKE_ADMIN_PASSWORD=<dummy-local-password> SMOKE_API_BASE_URL=http://localhost:8080/api python3 scripts/smoke/write-alpha-create-smoke.py
# passed

SMOKE_ADMIN_PASSWORD=<dummy-local-password> SMOKE_API_BASE_URL=http://localhost:8080/api python3 scripts/smoke/write-alpha-patch-smoke.py
# passed

SMOKE_ADMIN_PASSWORD=<dummy-local-password> SMOKE_API_BASE_URL=http://localhost:8080/api python3 scripts/smoke/write-alpha-delete-restore-smoke.py
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
15:      GNUCASH_WRITES_ENABLED: "false"
65:      GNUCASH_WRITES_ENABLED: "false"

SMOKE_ADMIN_PASSWORD=<dummy-local-password> SMOKE_API_BASE_URL=http://localhost:8080/api python3 scripts/smoke/read-only-api-smoke.py
# passed: validate/create/PATCH/DELETE probes returned 403 under default false
```

Additional standard verification after docs/status updates is recorded in the final commit/report.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default.
- Write-alpha execution was explicit local `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true` only.
- Each create/PATCH/DELETE route family used a fresh prepared ignored runtime copy from a temporary external disposable source.
- No real/private/only-copy book, release/tag/package/image, enabled-by-default config, new write endpoint, `.env`, app DB, backup, screenshot, export, token, key, cert, raw private path, account name, memo, amount, runtime book, or private financial data was committed.
- The cleanup helper used `--via-compose` fallback for root-owned ignored backup artifacts and removed ignored runtime artifacts with redacted output.

## Risks / follow-up

- This is bounded synthetic/disposable write-alpha evidence only. It does not establish production safety, security audit coverage, broad compatibility, or safety for real/private/only-copy books.
- The restored ignored `data/app/app.db` predates this phase and remains untracked local state.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
