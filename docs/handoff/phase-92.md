# Phase 92 — Compatibility fixture v2 / version matrix progress

## Status

Complete. Phase 92 was executed as a PM→Engineer phase with no analyst/auditor role. No audit-only phase and no `docs/audits/phase-92-audit.md` were created.

No new tag/release was published. No write-mode work was added or enabled. `GNUCASH_WRITES_ENABLED=false` remains the safe default. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DBs, backups, secrets, tokens, certs, keys, private screenshots, or CSV exports with real data were committed.

## PM report

### Decision

Implement the Phase 92 compatibility improvement as a safe copied/disposable SQLite metadata collection procedure plus tests and docs, rather than committing a new binary fixture or claiming a real GnuCash Desktop version pass.

### Why

The current environment does not have `gnucash` installed, so a desktop-generated fixture with a verified GnuCash Desktop version cannot be honestly produced here. The most useful safe Phase 92 result is to make future version-matrix evidence easier and less private-data-prone: a collector records redacted schema/version metadata from copied/test SQLite books and docs explain how to use it.

### Phase brief

- Goal: move compatibility evidence forward by improving the test-copy/version-matrix procedure and recording a narrow local generated-fixture metadata row.
- Non-goals: no broad GnuCash compatibility claim, no PostgreSQL/MySQL/MariaDB/XML support claim, no real/private book commit, no binary fixture commit, no write-mode work, no v0.2 work, no release/tag publication.
- Acceptance criteria:
  - `docs/gnucash-compatibility.md` includes a narrow Phase 92 matrix row and safe metadata procedure.
  - `docs/gnucash-version-fixture-plan.md` documents copied/test-book metadata collection instructions.
  - A tested script collects only non-sensitive metadata from copied/disposable SQLite books.
  - Tests prove private path/account/transaction row values are not serialized.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are updated.
  - Required checks pass or blockers are explicitly recorded.
  - Commit is pushed to `origin/main` and working tree is clean.
- Safety checks:
  - Collector opens SQLite in read-only mode.
  - Output uses `book_path: "<redacted>"`.
  - Output excludes account names, transaction descriptions, amounts, memos, split rows, private paths, screenshots, app DB data, backups, and secrets.
  - Compatibility docs explicitly state Phase 92 is procedure evidence, not a desktop-version compatibility claim.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check`
  - `cd apps/web && npm run test:auth-routes`
  - `cd apps/web && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`
  - GitHub issue/release/tag verification.

### GitHub/backlog

- GitHub #22 remains the compatibility-fixture tracking issue and should stay open until at least one real-version disposable fixture or reproducible desktop-generation path is implemented and tested.
- Phase 92 will update #22 with evidence if GitHub issue commenting succeeds; otherwise the local handoff records the blocker.
- No new release/tag publication.

## Engineer report

### Concrete result

Implemented a tested safe compatibility metadata path:

- `apps/api/scripts/collect_gnucash_compatibility_metadata.py` collects redacted compatibility metadata from copied/disposable GnuCash SQLite books:
  - `format`;
  - `book_path: "<redacted>"`;
  - declared GnuCash Desktop version, if provided;
  - SQLite backend;
  - `versions` markers;
  - selected safe table counts.
- `apps/api/tests/test_gnucash_compatibility_metadata.py` covers the script and proves it does not serialize the input path, account names, or transaction descriptions from a copied SQLite book.
- `apps/api/tests/test_gnucash_compatibility.py` now checks that compatibility docs document the Phase 92 collector path.
- `docs/gnucash-compatibility.md` now includes:
  - a narrow Phase 92 local metadata-procedure row;
  - explicit safe collector usage and privacy boundaries.
- `docs/gnucash-version-fixture-plan.md` now includes copied/test-book metadata collection steps and Phase 92 local procedure evidence.
- `README.md`, `PROJECT_STATUS.md`, and `CHANGELOG.md` were updated through Phase 92.

### Local Phase 92 evidence

```text
gnucash --version
BLOCKED/NOT AVAILABLE — gnucash: command not found

piecash
1.2.1

Generated disposable source
apps/api/scripts/create_compatibility_fixture_v1.py into a temporary directory outside git

Collector result summary
book_path=<redacted>
Gnucash=3000000
Gnucash-Resave=19920
table_counts include accounts=17, transactions=9, splits=20, commodities=1, books=1
```

Because GnuCash Desktop was not installed, no desktop-version compatibility pass is claimed.

### Required checks

```text
cd apps/api && pytest -q
PASS — 326 passed, 27 warnings

cd apps/web && npm run check
PASS — svelte-check found 0 errors and 0 warnings

cd apps/web && npm run test:auth-routes
PASS — auth route checks passed

cd apps/web && npm run build
PASS — production build completed

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
PASS

git diff --check
PASS
```

### Files changed

- `apps/api/scripts/collect_gnucash_compatibility_metadata.py`
- `apps/api/tests/test_gnucash_compatibility_metadata.py`
- `apps/api/tests/test_gnucash_compatibility.py`
- `docs/gnucash-compatibility.md`
- `docs/gnucash-version-fixture-plan.md`
- `PROJECT_STATUS.md`
- `README.md`
- `CHANGELOG.md`
- `docs/handoff/phase-92.md`

### GitHub/release

- Open issues were inspected; #22 remains open for real GnuCash version fixtures.
- GitHub #22 was updated with Phase 92 evidence and kept open: https://github.com/valentusys/gnucash-web-companion/issues/22#issuecomment-4476705049
- Existing tags/releases were verified as `v0.1.0-readonly`, `v0.0.2-prealpha`, and `v0.0.1-prealpha` only.
- No new tag or GitHub release was created.

### Commit/push

Pending until checks complete.
