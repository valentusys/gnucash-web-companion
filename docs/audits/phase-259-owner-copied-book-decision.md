# Phase 259 — Owner copied-book decision gate

Date: 2026-05-21
Role: analyst
Scope: decide whether to ask the owner to run copied-book dogfood locally, outside git

## Verdict

READY TO ASK OWNER FOR DRY-RUN ONLY.

It is reasonable to ask the owner to run a local copied-book dry-run outside git, using only a copied/restorable book with the original untouched. It is not yet reasonable to ask for CREATE-one as the first owner action. CREATE-one can be considered only after the owner dry-run evidence is reviewed and confirms preflight, independent backup, redaction, local-only runtime, restore plan, and reset to `GNUCASH_WRITES_ENABLED=false`.

This verdict does not authorize real/private/original/only-copy book mutation, repository storage of private paths/data, release publication, default write enablement, `APP_ENV=test` gate weakening, PATCH/DELETE, production use, public-internet exposure, or any real/private-book write-safety claim.

## Inputs inspected

- `AGENTS.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-258.md`
- `docs/dogfood/phase-258-synthetic-copied-book-package.md`
- `docs/write-alpha/maintainer-copied-book-dogfood-packet.md`
- `docs/write-alpha/transaction-ownership.md`
- `docs/write-alpha/compatibility-check-harness.md`
- `docs/write-alpha/restore-verification-harness.md`
- Git status/log through Phase 258
- Safety greps for write defaults, backend write flag references, `APP_ENV=test`, and browser storage
- GitHub open issues via `gh issue list` attempted; GitHub API connection reset during this phase, so current issue state is based on the known strategic issues from Phase 252 and repository docs.

## Phase 258 evidence assessment

PASS for owner dry-run decision:

- Synthetic/disposable copied-book package rehearsal completed.
- Wrapper dry-run passed with redacted preflight, pre-step backup, no mutation, and default-disabled reset proof.
- Docker/Caddy create-one rehearsal passed on an ignored synthetic runtime copy, with one routed CREATE, read-back, backup/audit/lock evidence, and reset to disabled writes.
- Restore verification passed on synthetic/disposable evidence with checksum match and piecash read-back.
- Disabled write probes through Caddy returned 403 for validate/create/PATCH/DELETE after reset.
- Committed evidence is redacted to statuses, counts, checksum prefixes, and placeholders.
- No owner/private/original/only-copy book was used.

Limits that keep the owner ask to dry-run first:

- Phase 258 browser evidence is not claimed; the browser helper timed out in this environment after earlier route checks.
- Host `gnucash-cli` remained unavailable for the Phase 256 compatibility harness and is recorded as blocked, not compatibility evidence.
- A temporary Debian container `gnucash-cli` probe passed, but that is narrow one-run tooling evidence only and not broad Desktop/version compatibility.
- Synthetic evidence still does not prove real/private/copied owner-book mutation safety.

## Dogfood packet completeness

PASS for dry-run owner packet:

- `docs/write-alpha/maintainer-copied-book-dogfood-packet.md` defaults to dry-run first.
- It forbids original and only-copy books.
- It requires outside-git copied/restorable working books and independent pre-mutation backup.
- It requires local-only execution, explicit `GNUCASH_WRITES_ENABLED=true` plus `APP_ENV=test` only for bounded write-alpha testing, redacted evidence, cleanup, and reset to `GNUCASH_WRITES_ENABLED=false`.
- It limits optional mutation to one CREATE after dry-run review.
- It defers PATCH to later explicit review.
- It prohibits DELETE unless separately authorized for a write-alpha-created test transaction.

Missing for immediate CREATE-one ask:

- No owner dry-run evidence exists yet.
- No owner local backup/restore/redaction proof exists yet.
- No owner local compatibility harness result exists yet.

## Ownership guard assessment

PASS:

- CREATE records app metadata-only ownership markers.
- PATCH requires same-book app metadata write-alpha ownership after write-enabled/edit-access/`APP_ENV=test` gates and before constructing the write service.
- DELETE requires the same ownership condition before constructing the write service.
- Non-owned historical/imported/manual transactions remain read-only in this app.
- Frontend hiding is supporting UX only; backend guards are authoritative.

This reduces accidental PATCH/DELETE risk for copied-book dogfood, but it does not make real/private/original/only-copy books safe for write-alpha.

## Restore harness assessment

PASS for dry-run decision and conditional CREATE-one after dry-run review:

- `scripts/write_alpha_restore_verify.py` exists and is documented.
- It rejects target and backup files inside the git checkout.
- It requires explicit copied/disposable, original-untouched, restore-over-copy, and pre-mutation-backup confirmations.
- It restores only the copied working book from the pre-mutation backup.
- It verifies checksum/read-back state and writes redacted evidence.
- It verifies committed/default `GNUCASH_WRITES_ENABLED=false` posture when Docker Compose is available.

Restore proof remains local-run evidence only. It is not a production disaster-recovery claim.

## Compatibility harness assessment

PARTIAL / enough for dry-run, not enough for broad CREATE confidence:

- `scripts/write_alpha_compatibility_check.py` exists and is documented.
- It opens a copied/disposable target read-only with piecash.
- It optionally runs already-available `gnucash-cli` report probing.
- It records `pass`/`blocked`/`fail` and `broad_compatibility_claimed=false`.
- Phase 258 host run recorded missing host `gnucash-cli` as blocked, correctly avoiding a compatibility overclaim.
- Phase 258 separate temporary Debian CLI probe passed, but this is one-run bounded tooling evidence only.

Owner dry-run does not need mutation compatibility proof. Owner CREATE-one should not proceed until dry-run is reviewed and the owner accepts the compatibility-harness status for the local environment.

## Current open blockers / risks

No blocker prevents asking for dry-run only.

Blocking conditions for CREATE-one until dry-run review:

1. No owner dry-run evidence yet.
2. No owner independent backup/restore proof yet.
3. No owner local redaction proof yet.
4. Host/Desktop compatibility remains best-effort and may be `blocked` when `gnucash-cli` is unavailable.
5. Browser smoke was not claimed in Phase 258.

Known strategic non-blockers from the current roadmap:

- #36 — remaining controlled-write readiness gates.
- #22 — real GnuCash version compatibility fixtures.
- #28 — markdown readability before wider announcement.
- #17/#29 — Russian docs/UI localization and terminology.
- #13 — Book management UI.

These do not block a local dry-run ask because dry-run performs no mutation and does not require private data in the repository.

## Owner instruction boundary

If the owner is asked to run the next step, the ask should be limited to this:

1. Make a separate copied/restorable book outside git.
2. Keep the original untouched and closed.
3. Create an independent backup before any app run.
4. Run preflight/readiness/dry-run only.
5. Commit or share only redacted statuses/counts/placeholders, never paths, account names, memos, amounts, screenshots, CSV rows, app DBs, books, backups, tokens, keys, or certs.
6. Reset and verify `GNUCASH_WRITES_ENABLED=false` afterward.
7. Stop and report if any safety check fails.

Do not ask the owner for private paths in the repository or chat report. Do not ask the owner to run CREATE-one until dry-run evidence has been reviewed.

## Verification performed

```bash
git status --short
git log --oneline -8 --decorate --no-color
gh issue list --state open --limit 50 || true
# safety greps for GNUCASH_WRITES_ENABLED, gnucash_writes_enabled, APP_ENV=test, localStorage/sessionStorage
```

Results:

- Tracked tree was clean before this phase; untracked repo-local `.hermes/` exists and is excluded.
- `HEAD` and `origin/main` were both at Phase 258 before this phase.
- Safety grep confirmed `.env.example` keeps `GNUCASH_WRITES_ENABLED=false` and Docker Compose uses `${GNUCASH_WRITES_ENABLED:-false}`.
- Backend config still defaults `gnucash_writes_enabled` to false.
- `APP_ENV=test` write-alpha gate references remain present.
- Browser storage grep showed theme-only localStorage use in `apps/web/src`.
- GitHub issue list attempt failed with a transient API connection reset; no issue mutation was attempted.

## Decision

Owner copied-book dogfood is ready for DRY-RUN ONLY.

Owner CREATE-one is conditionally possible later, only after dry-run evidence is reviewed and passes. It is not authorized as the next immediate owner ask.

Owner PATCH/DELETE, real/private/original/only-copy book writes, release publication, production/security/public-internet/broad-compatibility claims, and default write enablement remain out of scope.
