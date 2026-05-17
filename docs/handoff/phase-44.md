# Phase 44 — Backup and Recovery Runbook

## Status

Complete. Backup/recovery documentation was added, status/docs were synchronized, required checks passed, and the phase commit was pushed.

## PM report

### Decision

Execute exactly Phase 44 from the roadmap: add a conservative backup and recovery runbook for read-only deployments and future experimental controlled-write testing.

### Why

After publishing `v0.0.2-prealpha` and adding local deployment guidance in Phase 43, the next release-value step is operational safety documentation. Users need clear manual backup/restore expectations before dogfood or private self-host testing. This phase is documentation-only and deliberately avoids expanding write scope.

### Phase brief

- Goal: create `docs/operations/backup-and-recovery.md` covering app metadata DB backups, GnuCash copied-book backups, Docker data paths, backup frequency, restore dry-runs, controlled-write pre-write backup expectations, restored-book verification, and explicit non-guarantees.
- Non-goals: no product code changes, no release/tag publication, no write-mode enablement, no write-scope expansion, no restore UI/API, no automated backup system, no real financial/secrets artifacts committed.
- Acceptance criteria:
  - Conservative language.
  - No claim that backup system is production-grade.
  - Manual recovery procedure included.
  - App metadata DB backup covered.
  - GnuCash book backup covered.
  - Docker volume paths covered.
  - Backup frequency covered.
  - Restore dry-run covered.
  - Controlled-write pre-write backup behavior covered as experimental post-MVP.
  - Restored-book read verification covered.
  - Non-guarantees explicitly listed.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are synchronized.
- Safety checks:
  - `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
  - Controlled writes remain experimental post-MVP and disabled by default.
  - No real GnuCash files, `.env`, app DBs, backups, secrets, keys, tokens, screenshots, or exports are committed.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check && npm run test:auth-routes && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`

### Risks

- Backup docs could imply production-grade disaster recovery. Mitigation: explicit pre-alpha/no-guarantee language and non-guarantees section.
- Controlled-write backup wording could normalize write mode. Mitigation: repeated `GNUCASH_WRITES_ENABLED=false` and experimental post-MVP framing.
- Manual restore instructions could be destructive. Mitigation: stop containers first, restore dry-run first, move current `data/` aside instead of deleting it.

### Files/docs to update

- `docs/operations/backup-and-recovery.md`
- `README.md`
- `docs/deployment/local-secure-deployment.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-44.md`

### GitHub/backlog

- No Phase 44-specific open GitHub issue was found.
- Existing open issues #22, #17, #13, #12, and #11 remain for later roadmap phases.

## Engineer report

Implemented Phase 44 documentation-only scope:

- Created `docs/operations/backup-and-recovery.md`.
- Covered app metadata DB backup, copied GnuCash book backup, Docker data paths, backup frequency, restore dry-run, manual recovery, restored-book read verification, controlled-write pre-write backup expectations, and explicit non-guarantees.
- Updated `README.md` current status to Phase 0–44 complete and linked the backup/recovery runbook from Quick start.
- Updated `docs/deployment/local-secure-deployment.md` so the Phase 43 backup placeholder now links to the Phase 44 runbook.
- Updated `CHANGELOG.md` with a Phase 44 Unreleased entry.
- Updated `PROJECT_STATUS.md` through Phase 44 and set Phase 45 as next planned phase.
- Created this handoff file.

No product code changed. No release/tag was published. No write behavior changed.

## Verification

Passed:

- `cd apps/api && pytest -q` — passed (`269 passed`, 27 existing warnings).
- `cd apps/web && npm run check` — passed.
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `git diff --check` — passed.

## Safety confirmation

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental post-MVP and disabled by default.
- No write scope was expanded.
- No auth localStorage/sessionStorage path was introduced.
- No real financial data, GnuCash books, `.env`, app DBs, backups, secrets, keys, tokens, certs, real screenshots, or real CSV exports were added.

## Commit / push

- Commit message: `docs: add backup and recovery runbook`.
- Final commit SHA: see `git log -1 --oneline` for this phase commit.
- Push: pushed to `origin/main`.

## GitHub issue status

- No Phase 44-specific open GitHub issue found or updated.
- GitHub #22, #17, #13, #12, and #11 remain open for later roadmap work.

## Blockers

None.
