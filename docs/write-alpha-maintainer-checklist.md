# Write-alpha maintainer checklist

Status: experimental / pre-alpha review gate. This checklist is required before any maintainer considers broader write-alpha or owner-writebeta testing. Passing it does not make write mode production-ready, does not authorize real-book writes, and does not justify a public write beta.

## Scope being reviewed

Record the exact operation and commit:

- Operation: `POST /books/{book_id}/transactions`, `PATCH /books/{book_id}/transactions/{transaction_id}`, `DELETE /books/{book_id}/transactions/{transaction_id}`, or a non-mutating #36 readiness audit.
- Commit SHA:
- Test book provenance: synthetic/disposable/copy only:
- Reviewer:
- Date:

## Issue #36 controlled-write readiness audit

Use this section for [issue #36](https://github.com/valentusys/gnucash-web-companion/issues/36) when reviewing whether remaining controlled-write readiness gates are complete. Current recommendation: keep #36 open unless every blocker below has accepted evidence and a maintainer/PM decision explicitly says the original issue scope is satisfied.

Evidence links already accepted narrowly:

- Default-disabled reset/probe invariant: `docs/handoff/overnight-2026-06-02-worker-02.md`.
- Backup/restore readiness evidence markers: `docs/handoff/overnight-2026-06-02-worker-07.md` and `docs/write-alpha/backup-restore-readiness-checklist.md`.
- Recovery/hard-stop expectations: `docs/handoff/overnight-2026-06-02-worker-09.md`.
- Concurrency/lock-contention readiness markers: `docs/handoff/overnight-2026-06-02-worker-10.md`.
- Default-disabled wording guard: `docs/handoff/overnight-2026-06-02-worker-14.md` and `scripts/check_write_safety_defaults.py`.
- Current evidence summary: `docs/write-alpha/evidence-matrix.md`.

Machine-checked wording required by `scripts/check_write_safety_defaults.py`:

- [ ] `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture.
- [ ] `APP_ENV=test` remains required before any enabled write-alpha/writebeta execution.
- [ ] The audit preserves the no-release/no-public-write posture.
- [ ] The audit states owner-input/real-book/copy-book constraints without private paths or raw private evidence.
- [ ] The audit lists exact next worker packages rather than broad phase planning.
- [ ] The audit says keep #36 open unless all blockers are accepted by maintainer/PM review.

Completed non-mutating gates with evidence:

- [ ] Default-disabled config/docs guard exists and passes.
- [ ] Reset/default-disabled disabled-probe wording is guarded.
- [ ] Backup/restore evidence checklist exists and rejects missing restore hash, row-count, schema marker, default-disabled posture, and private/raw evidence markers.
- [ ] Recovery/hard-stop markers are explicit: abort after failed restore/read-back/audit, preserve backups, no retry on the same copy without recovery, maintainer review or owner escalation, and default-disabled reset/probe.
- [ ] Concurrency/lock-contention markers are explicit: serialized per-book lock acquisition, active-lock contention blocked/rejected, no overlapping write execution, audit trail for contention/rejection, and default-disabled no-write probe.

Remaining blockers and exact next worker packages:

1. Maintainer review/recovery procedure packet:
   - Update or audit `docs/write-alpha-recovery-procedure.md` against the worker 07/09 markers.
   - Ensure it says failed restore/read-back/audit means hard stop, backup preservation, no retry on the same copy before recovery/regeneration, and owner/maintainer escalation.
   - Keep it non-mutating unless explicitly authorized.

2. Conservative compatibility wording packet:
   - Audit `docs/write-alpha/evidence-matrix.md`, `docs/v0.2-controlled-writes.md`, and release/status docs for GnuCash version/write compatibility claims.
   - Ensure claims remain tied to synthetic/disposable or copied/restorable evidence only.
   - Do not claim broad compatibility, public write beta readiness, stable readiness, production readiness, or security-audited status.

3. Future copied/restorable mutation evidence packet, only if explicitly authorized in the same execution context:
   - Require owner + PM authorization, Desktop closed, outside-git copied/restorable working book, independent backup, read-back, audit, lock, compatibility, restore, reset/default-disabled probe, and redaction gates.
   - Never use original/private/working/only-copy books.
   - Exact counts and route family must be specified before execution.

4. #36 closure decision packet:
   - Re-read #36, all linked handoffs, and latest CI.
   - Decide whether the original issue scope is truly satisfied.
   - Expected default is keep open until a maintainer/PM explicitly accepts the remaining blockers.

## Non-negotiable gate

Every item must be checked before proceeding:

- [ ] `GNUCASH_WRITES_ENABLED=false` remains the repository, `.env.example`, Docker/Compose, and documentation default.
- [ ] Enabled write route execution still requires `APP_ENV=test`.
- [ ] Tests use only `tmp_path`, committed synthetic fixtures copied to disposable paths, or other disposable generated data.
- [ ] No real/private GnuCash book, app DB, backup, `.env`, token, credential, cert, key, CSV export, screenshot/media, SQL dump, or private path is committed.
- [ ] Frontend write UI, if present, is hidden by default and requires explicit warning/acknowledgement before submission.
- [ ] GnuCash Desktop remains documented as the authoritative editor.
- [ ] The phase does not create a tag, GitHub release, package, upload, public write beta, or production-readiness claim.

## Lifecycle evidence

For each write route under review:

- [ ] Authorization/access checks happen before write-service construction for read-only/viewer users.
- [ ] Validation rejects invalid split count, non-zero-sum splits by currency, invalid decimal strings, missing accounts, placeholder accounts, invalid dates, and unsupported payloads.
- [ ] A per-book lock is acquired before mutation.
- [ ] Lock contention returns a controlled error and is audited when the request has entered the write route.
- [ ] A pre-write backup is created before mutation.
- [ ] Successful writes produce a successful audit row with non-sensitive metadata.
- [ ] Failed writes after route entry produce a failed audit row.
- [ ] Failures after backup record enough non-sensitive backup information for recovery.
- [ ] Locks are released after success, validation failure, lock contention, and synthetic post-backup failure.
- [ ] The disposable book can be reopened through read-only routes after the write/failure test.

## Recovery documentation gate

- [ ] `docs/write-alpha-recovery-procedure.md` exists and includes restore, integrity, lock, and damaged-book steps.
- [ ] The recovery procedure includes concrete commands.
- [ ] The recovery procedure says it is for synthetic/disposable/test copies only.
- [ ] The procedure forbids committing backups, real books, app DBs, `.env`, secrets, exports, screenshots, and private data.
- [ ] The procedure tells operators to return to `GNUCASH_WRITES_ENABLED=false` after recovery.

## Verification commands

Run from a clean working tree except for the intended phase changes:

```bash
python3 scripts/check_write_safety_defaults.py
python3 scripts/check_public_status.py
python3 scripts/check_tracked_hygiene.py
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
git diff --check
git ls-files | grep -E '(^|/)(\.env$|secrets?$|credentials?$)|data/books/.*\.(sqlite|sqlite3|gnucash|db)$|data/backups/.|.*\.(pem|key|crt|p12)$' && exit 1 || true
```

If frontend route/auth behavior changed, also run:

```bash
cd apps/web && npm run test:auth-routes
```

## Review outcome

Choose one:

- [ ] Pass for continued synthetic/disposable write-alpha testing only.
- [ ] Blocked: keep writes disabled and fix listed blockers.
- [ ] Not applicable: docs-only/read-only phase.

Blockers:

- [ ]

Notes:

- [ ]
