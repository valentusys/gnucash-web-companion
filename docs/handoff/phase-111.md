# Phase 111 — compatibility fixture v4 safe Desktop-tooling evidence

Date: 2026-05-19
Status: complete
Related GitHub issue: #22
PM brief: `docs/handoff/phase-111-pm-brief.md`

## Summary

Phase 111 implemented the analyst roadmap Phase 6 slice for compatibility evidence without real/private books. The phase checked whether local GnuCash Desktop/CLI tooling is available and, because it is not available in this environment, added a tested safe tooling probe plus documentation that keeps Desktop-generated compatibility claims explicitly blocked until a disposable Desktop environment exists.

## PM decision

Move #22 forward only with honest evidence. Do not fabricate a Desktop-generated fixture when `gnucash` / `gnucash-cli` are unavailable. Keep the matrix split between generated/piecash evidence, copied/disposable metadata evidence, and future real Desktop-generated evidence.

## Implementation

Added:

- `apps/api/scripts/probe_gnucash_desktop_tooling.py`
  - probes only fixed command names: `gnucash` and `gnucash-cli`;
  - records command availability;
  - redacts executable paths;
  - records bounded `--version` output only when a command exists;
  - opens no GnuCash book;
  - searches no user/private directories.

Updated tests:

- `apps/api/tests/test_gnucash_compatibility_metadata.py`
  - verifies available-tool metadata redacts executable paths;
  - verifies unavailable-tool metadata stays safe;
  - keeps collector path/redaction tests for copied/disposable SQLite metadata.

Updated docs:

- `docs/gnucash-compatibility.md`
  - added a narrow Phase 111 matrix row;
  - states local Desktop tooling is unavailable;
  - states no Desktop-generated fixture or Desktop-version compatibility row is claimed.
- `docs/gnucash-version-fixture-plan.md`
  - documents the Desktop-tooling probe;
  - records Phase 111 local evidence (`desktop_tooling_available=false`);
  - keeps next-step instructions for future disposable Desktop-generated fixtures.
- `docs/gnucash-compatibility-fixture-v1.md`
  - adds the Phase 111 safety note for Desktop-tooling availability.
- `CHANGELOG.md` and `PROJECT_STATUS.md` updated for Phase 111.

## Local probe result

Command run:

```bash
python apps/api/scripts/probe_gnucash_desktop_tooling.py --output /tmp/phase-111-gnucash-tooling-probe.json
python apps/api/scripts/probe_gnucash_desktop_tooling.py
```

Result:

- `desktop_tooling_available=false`
- `gnucash`: not found
- `gnucash-cli`: not found
- no book opened
- no private directories searched
- no fixture binary produced or committed

## Safety

- `GNUCASH_WRITES_ENABLED=false` default was not changed.
- No backend write endpoints/services were changed.
- No GnuCash Desktop-generated fixture was claimed because tooling is unavailable.
- No broad all-version, PostgreSQL/MySQL/MariaDB, XML, arbitrary real-book, production-ready, or security-audited compatibility claim was added.
- No tag, release, or package was published.
- No real/private GnuCash books, app DBs, backups, `.env`, screenshots, CSV exports, secrets, tokens, certs, keys, private paths, account names, transaction descriptions, memos, amounts, or personal financial data were committed.
- Money logic was not changed; no float money logic was added.

## Verification

Passed:

```bash
cd apps/api && pytest -q tests/test_gnucash_compatibility_metadata.py tests/test_compatibility_fixture_v1.py
# 11 passed, 21 warnings

cd apps/api && pytest -q
# 346 passed, 27 warnings

cd apps/web && npm run test:auth-routes
# auth route checks passed

cd apps/web && npm run check
# svelte-check found 0 errors and 0 warnings

cd apps/web && npm run build
# passed

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
# passed

git diff --check
# passed
```

## Files changed

- `apps/api/scripts/probe_gnucash_desktop_tooling.py`
- `apps/api/tests/test_gnucash_compatibility_metadata.py`
- `docs/gnucash-compatibility.md`
- `docs/gnucash-version-fixture-plan.md`
- `docs/gnucash-compatibility-fixture-v1.md`
- `docs/handoff/phase-111-pm-brief.md`
- `docs/handoff/phase-111.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`

## GitHub

- Updated #22 with Phase 111 evidence: https://github.com/valentusys/gnucash-web-companion/issues/22#issuecomment-4482832804
- Kept #22 open because real Desktop-generated disposable fixture coverage is still absent.

## Commit/push

- Commit: this commit (`Add safe GnuCash desktop tooling probe`); final SHA is recorded in controller stdout.
- Push: pending at handoff creation time; expected target `origin/main`.
