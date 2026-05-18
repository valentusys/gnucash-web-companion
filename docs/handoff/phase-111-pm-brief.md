# Phase 111 PM brief — compatibility fixture v4 safe Desktop evidence

Date: 2026-05-19
Roadmap source: analyst Phase 6
Related GitHub issue: #22

## Decision

Run a narrow compatibility-evidence phase for GitHub #22. First check whether `gnucash` / `gnucash-cli` tooling is available in this execution environment. If it is available, collect only safe Desktop-generated SQLite fixture metadata from a synthetic/disposable book. If it is not available, do not fabricate Desktop evidence; instead add a tested safe tooling probe and improve reproducible generated/disposable fallback documentation and collector coverage.

## Goal

Move compatibility evidence forward without real/private books by distinguishing:

- committed/generated piecash fixture evidence;
- safe copied/disposable metadata evidence;
- real GnuCash Desktop-generated evidence, only when tooling is actually available.

## Non-goals

- No broad all-version compatibility claim.
- No real/private GnuCash book discovery or scanning.
- No committed binary fixture produced from a personal or unknown source.
- No write-mode enablement, fixture mutation, release/tag publication, or v0.2 scope.
- No account names, descriptions, amounts, memos, split rows, private paths, screenshots, exports, `.env`, app DBs, backups, tokens, keys, or certs in committed artifacts.

## Acceptance criteria

- Desktop tooling availability is checked safely with exact command/version evidence when present, or a clear unavailable result when absent.
- Compatibility docs distinguish generated/piecash evidence, copied/disposable metadata evidence, and Desktop-generated evidence.
- Metadata collector/probe regression tests prove private paths and row data are not serialized.
- Matrix row for this phase is narrow and does not claim broad Desktop compatibility if `gnucash` is unavailable.
- GitHub #22 receives a concise evidence update and remains open unless real Desktop-generated fixture coverage is actually complete.

## Safety checks

- Do not search user private directories.
- Do not commit real GnuCash books, app DBs, backups, `.env`, secrets, screenshots, or CSV exports.
- Keep `GNUCASH_WRITES_ENABLED=false` default unchanged.
- Keep all read-only fixture integrity/no-mutation coverage intact.
- Money logic remains Decimal/string; no float money changes.

## Verification

Required where relevant:

```bash
cd apps/api && pytest -q tests/test_gnucash_compatibility_metadata.py tests/test_compatibility_fixture_v1.py
cd apps/api && pytest -q
cd apps/web && npm run test:auth-routes
cd apps/web && npm run check
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
git diff --check
```

## Files/docs to update

- `apps/api/scripts/collect_gnucash_compatibility_metadata.py` or companion safe probe script
- `apps/api/tests/test_gnucash_compatibility_metadata.py`
- compatibility docs (`docs/gnucash-compatibility.md`, `docs/gnucash-version-fixture-plan.md`, and/or `docs/gnucash-compatibility-fixture-v1.md`)
- `docs/handoff/phase-111.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md` if user-visible behavior/docs warrant it

## GitHub/backlog

Update #22 with Phase 111 evidence. Keep it open if local Desktop tooling remains unavailable or if only generated/disposable evidence was improved.
