# Phase 193 — Root-owned runtime cleanup and lock recovery UX

Date: 2026-05-20
Status: COMPLETE — stopped-runtime-only cleanup helper added, tested, dogfooded on synthetic ignored files, committed/pushed
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-3-roadmap.md` (Phase 2 only)

## Goal

Close the Phase 190 operator pain where root-owned ignored runtime files, locks, and backups can block host-side smoke helpers, while keeping cleanup safe, stopped-runtime-only, and path-redacted.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-192.md`;
  - relevant Phase 190/183 handoffs and lock evidence docs;
  - roadmap file named by the phase contract;
  - write-lock tests/helpers and operations runbook.
- Added `apps/api/app/runtime_cleanup.py` service logic for ignored runtime cleanup:
  - allowlist only `data/books`, `data/app`, `data/backups`, and `data/locks` under the repository `data` root;
  - requires exact stopped-runtime acknowledgement token `I_CONFIRM_RUNTIME_STOPPED`;
  - dry-run by default;
  - cleanup only with `--execute`;
  - reports path classes/counts/statuses only;
  - detects active flock-held locks and preserves them;
  - removes stale lock files when explicitly executing after acknowledgement;
  - handles unreadable lock files only after stopped-runtime acknowledgement within the allowed `data/locks` class;
  - skips unsupported lock-directory children;
  - fails closed for non-repository data roots.
- Added `scripts/ops/runtime-cleanup.py` operator CLI:
  - default host-side dry-run/execute;
  - optional `--via-compose` re-executes through the API service with the repository mounted for root-owned/container-readable artifacts.
- Added tests in `apps/api/tests/test_runtime_cleanup.py` for acknowledgement, allowlist, redaction, active/stale/unreadable lock handling, cleanup, and fail-closed cases.
- Updated `.gitignore` and added `data/locks/.gitkeep` so `data/locks/*` is explicitly ignored while the runtime directory placeholder can be tracked.
- Updated `docs/operations/backup-and-recovery.md` with stopped-runtime cleanup procedure and safety boundaries.
- Added redacted dogfood note `docs/dogfood/phase-193-runtime-cleanup.md` from synthetic ignored placeholder files only.
- Updated `PROJECT_STATUS.md`.

## Files changed

- `.gitignore`
- `PROJECT_STATUS.md`
- `apps/api/app/runtime_cleanup.py`
- `apps/api/tests/test_runtime_cleanup.py`
- `data/locks/.gitkeep`
- `docs/dogfood/phase-193-runtime-cleanup.md`
- `docs/handoff/phase-193.md`
- `docs/operations/backup-and-recovery.md`
- `scripts/ops/runtime-cleanup.py`

No write routes, product write behavior, Docker runtime defaults, release/tag state, GitHub issue state, or frontend UI were changed.

## Verification summary

Commands/results:

```bash
cd apps/api && pytest tests/test_runtime_cleanup.py tests/test_write_lock.py tests/test_write_alpha_smoke_lock_evidence.py -q
# 25 passed

# manual synthetic ignored-runtime dry-run and cleanup
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED --execute
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED
# redacted class/count/status output; final counts zero

cd apps/api && pytest tests/test_transaction_writes.py tests/test_write_lock.py tests/test_runtime_cleanup.py -q
# 80 passed

cd apps/api && pytest -q
# 464 passed, 33 warnings

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# rendered false for API and web

git diff --check
# passed

# sensitive tracked-file hygiene scan from phase execution playbook
# passed
```

## Dogfood evidence

Manual dogfood created only synthetic placeholder files under ignored `data/books`, `data/app`, `data/backups`, and `data/locks`. The helper dry-run reported one artifact in each class, cleanup removed four eligible synthetic artifacts, and a final dry-run reported zero artifacts. Output did not include raw paths, names, account data, memos, amounts, backup filenames, app DB rows, `.env`, or secrets.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Helper refuses to work without stopped-runtime acknowledgement.
- Active locks are preserved.
- Cleanup is constrained to ignored runtime path classes under repository `data/`.
- No real/private/only-copy book, app DB, backup, `.env`, token, key, cert, screenshot, export, raw path, account name, transaction description, memo, amount, or private financial artifact was committed.
- No release, tag, package, Docker image, production-readiness claim, security-audit claim, or real/private-book write-safety claim was added.

## Risks / follow-up

- The helper is an operator recovery utility, not a production lock-management UI.
- `--via-compose` depends on Docker Compose being available and the API image being buildable locally.
- Write-alpha remains experimental, disabled by default, `APP_ENV=test` gated when enabled, and unsafe for real/private or only-copy books.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
