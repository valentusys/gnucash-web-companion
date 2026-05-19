# Write-alpha maintainer checklist

Status: experimental / pre-alpha review gate. This checklist is required before any maintainer considers broader write-alpha testing. Passing it does not make write mode production-ready and does not authorize real-book writes.

## Scope being reviewed

Record the exact operation and commit:

- Operation: `POST /books/{book_id}/transactions`, `PATCH /books/{book_id}/transactions/{transaction_id}`, or other explicitly authorized write-alpha route.
- Commit SHA:
- Test book provenance: synthetic/disposable/copy only:
- Reviewer:
- Date:

## Non-negotiable gate

Every item must be checked before proceeding:

- [ ] `GNUCASH_WRITES_ENABLED=false` remains the repository, `.env.example`, Docker/Compose, and documentation default.
- [ ] Enabled write route execution still requires `APP_ENV=test`.
- [ ] Tests use only `tmp_path`, committed synthetic fixtures copied to disposable paths, or other disposable generated data.
- [ ] No real/private GnuCash book, app DB, backup, `.env`, token, credential, cert, key, CSV export, screenshot/media, SQL dump, or private path is committed.
- [ ] Frontend write UI, if present, is hidden by default and requires explicit warning/acknowledgement before submission.
- [ ] GnuCash Desktop remains documented as the authoritative editor.
- [ ] The phase does not create a tag, GitHub release, package, upload, or production-readiness claim.

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
