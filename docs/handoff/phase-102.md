# Phase 102 — Compatibility fixture/version matrix v3 safe provenance refresh

## Status

Complete. Phase 102 implemented `docs/handoff/phase-102-pm-brief.md` as a narrow non-publishing compatibility evidence phase for GitHub #22.

Verdict: completed with environment blocker for a real GnuCash Desktop-generated fixture.

`gnucash --version` is unavailable in this environment (`gnucash: command not found`), so this phase does not claim a new real GnuCash Desktop version compatibility row. Instead it improves the generated/disposable compatibility path with tested safe runtime provenance.

No `v0.1.1-readonly` tag was created. No GitHub release was created or edited. No package or external release artifact was published.

## Implementation summary

Updated compatibility tooling:

- `apps/api/scripts/collect_gnucash_compatibility_metadata.py`
  - adds safe `runtime_context` metadata: `collector_version`, OS string, Python version, SQLite library version, and piecash package version;
  - keeps the book path redacted as `<redacted>`;
  - still records only schema/version markers and selected safe table counts, not row data.
- `apps/api/scripts/create_compatibility_fixture_v1.py`
  - adds safe generated-fixture `runtime_context` metadata: `generator_version`, OS string, Python version, SQLite library version, and piecash package version;
  - keeps generated SQLite fixtures in temp/ignored paths; no fixture binary was committed.

Updated tests:

- `apps/api/tests/test_gnucash_compatibility_metadata.py`
  - verifies safe runtime provenance exists;
  - continues proving private file paths, account names, and transaction descriptions are not serialized by the copied-book metadata collector.
- `apps/api/tests/test_compatibility_fixture_v1.py`
  - verifies generated fixture metadata includes safe runtime provenance.

Updated docs/status:

- `docs/gnucash-compatibility.md` — added a narrow Phase 102 generated/disposable provenance row and clarified remaining untested Desktop-version/backend scope.
- `docs/gnucash-version-fixture-plan.md` — documented the Phase 102 safe runtime-provenance fields and local environment evidence.
- `docs/gnucash-compatibility-fixture-v1.md` — documented the generated fixture metadata refresh.
- `CHANGELOG.md` — added the Phase 102 tooling/evidence entry.
- `PROJECT_STATUS.md` — baseline advanced through Phase 102 and next-step guidance updated.

## Compatibility evidence added

Local safe generated/disposable evidence:

- `gnucash --version`: unavailable (`gnucash: command not found`).
- Generated fixture path: temporary directory outside git.
- Fixture source: `apps/api/scripts/create_compatibility_fixture_v1.py`.
- Collector source: `apps/api/scripts/collect_gnucash_compatibility_metadata.py`.
- `piecash`: `1.2.1`.
- `python`: `3.11.15`.
- `sqlite`: `3.50.4`.
- SQLite `versions` markers observed on generated fixture include `Gnucash = 3000000` and `Gnucash-Resave = 19920`.
- Safe selected table counts observed by collector: `accounts`, `books`, `commodities`, `splits`, and `transactions`.

This is evidence for the generated/piecash disposable path only. It is not evidence for all GnuCash Desktop versions, PostgreSQL/MySQL/MariaDB backends, XML books, production readiness, or audited security.

## Verification summary

| Check | Result |
| --- | --- |
| `git status --short` before work | PASS — clean output. |
| `git rev-parse --abbrev-ref HEAD` | PASS — `main`. |
| `git rev-parse --short HEAD` | PASS — `3dce768` before Phase 102 changes. |
| `git tag --list 'v0.1.1-readonly'` | PASS — no tag output. |
| `gh auth status` | PASS — authenticated as `valentusys`; token output masked by `gh`. |
| `gh release view v0.1.1-readonly || true` | PASS — `release not found`. |
| `gnucash --version || true` | ENV BLOCKER — `gnucash: command not found`; no Desktop-generated fixture row claimed. |
| RED test for collector runtime provenance | PASS — first run failed with `KeyError: 'runtime_context'`. |
| GREEN collector targeted test | PASS — `pytest -q tests/test_gnucash_compatibility_metadata.py` → `2 passed`. |
| RED test for generated fixture runtime provenance | PASS — first run failed with `KeyError: 'runtime_context'`. |
| GREEN fixture targeted test | PASS — targeted generation test passed. |
| Temporary generated fixture + collector run | PASS — generated outside git and collected redacted metadata with safe runtime context. |

Final full verification before commit/push:

- `cd apps/api && pytest -q tests/test_gnucash_compatibility_metadata.py tests/test_compatibility_fixture_v1.py` — PASS, `9 passed`.
- `cd apps/api && pytest -q` — PASS, `329 passed, 27 warnings`.
- `cd apps/web && npm run check` — PASS, `svelte-check found 0 errors and 0 warnings`.
- `cd apps/web && npm run test:auth-routes` — PASS, `auth route checks passed`.
- `cd apps/web && npm run build` — PASS.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — PASS.
- `git diff --check` — PASS.

## Safety statement

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the required/default posture.
- Controlled writes remain post-MVP/experimental and disabled by default.
- GnuCash Desktop remains the authoritative editor.
- No write-mode scope was expanded or enabled.
- No tag, GitHub release, package, or external release artifact was published.
- No GnuCash book, binary real-book fixture, app DB, backup, `.env`, screenshot, private CSV export, secret, token, cert, key, private path, account name, transaction description, memo, amount, or real/private financial data was committed.
- Phase 102 does not claim broad GnuCash compatibility, production readiness, audited security, hosted SaaS readiness, family-wallet positioning, collaborative accounting, or personal-book dogfood success.

## GitHub / backlog note

- GitHub #22 was updated with non-sensitive Phase 102 evidence and left open: https://github.com/valentusys/gnucash-web-companion/issues/22#issuecomment-4478045716
- Remaining #22 gap: at least one fixture generated/saved by a real GnuCash Desktop version or another explicitly safe versioned disposable source is still needed before broadening compatibility evidence.
- GitHub #38 remains open/blocked until Val provides an explicit safe copied/disposable GnuCash SQL book path outside git and confirms it is not the live authoritative book.
- GitHub #39 remains closed; this phase found no CSV export regression.
- No new GitHub issue was created.

## Changed files

- `apps/api/scripts/collect_gnucash_compatibility_metadata.py`
- `apps/api/scripts/create_compatibility_fixture_v1.py`
- `apps/api/tests/test_gnucash_compatibility_metadata.py`
- `apps/api/tests/test_compatibility_fixture_v1.py`
- `docs/gnucash-compatibility.md`
- `docs/gnucash-version-fixture-plan.md`
- `docs/gnucash-compatibility-fixture-v1.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-102.md`

## Risks / follow-up

- Real GnuCash Desktop/version coverage is still missing in this environment because `gnucash` is not installed and no explicit safe copied/versioned disposable fixture path was provided.
- Keep compatibility claims narrow until a real Desktop-generated disposable fixture or reproducible versioned source is tested.
- If Val provides a safe copied/disposable GnuCash SQL book path outside git, rerun GitHub #38 dogfood as a separate local-only read-only phase.
- Publication remains unauthorized; do not publish `v0.1.1-readonly` without separate explicit Val authorization.

## Next recommended phase

Either add a real GnuCash Desktop/version disposable fixture source for GitHub #22 if one is safely available, or rerun GitHub #38 copied-book dogfood only if Val provides an explicit safe copied/disposable GnuCash SQL book path outside git.

## Commit / push

- Commit: `7a8ed63` (`feat: refresh compatibility fixture provenance`).
- Push: PASS — pushed `main` to `origin/main` (`3dce768..7a8ed63`).
