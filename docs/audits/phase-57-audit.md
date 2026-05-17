# Phase 57 Audit — v0.1.0-readonly Release Gate

Date: 2026-05-18

## Executive summary

Phase 57 audited whether the repository is ready to publish `v0.1.0-readonly`.

Verdict: Not ready for `v0.1.0-readonly` yet.

The core safety boundary is intact: `GNUCASH_WRITES_ENABLED=false` remains the backend and documented default, backend validate/create/patch write routes are gated before constructing the write service, and the frontend hides/blocks write UI unless the explicit write flag is enabled. README/status/release-plan language remains conservative: pre-alpha, read-only by default, GnuCash Desktop authoritative, not production-ready, not security-audited, not SaaS, not a GnuCash replacement, and not collaborative accounting.

The release is blocked by release-process gaps, not by a discovered read-only boundary break: conservative `v0.1.0-readonly` release notes do not exist yet, and there is no recorded clean runtime smoke/dogfood pass on copied or disposable data after the Phase 56 release plan.

## Verdict

Not ready for v0.1.0-readonly.

## Top blockers

1. `docs/release/v0.1.0-readonly-notes.md` does not exist. The Phase 56 checklist requires conservative release notes before tag/GitHub release publication.
2. The runtime smoke/dogfood gate is not complete or recorded. The release plan requires a Docker/runtime smoke pass and manual read-only checks on copied/disposable data, or an explicit accepted exception.
3. The v0.1 checklist is still intentionally unchecked; it has not been converted into a completed release-gate checklist with evidence.

## Important non-blockers

1. Existing open issues #22, #17, #13, #12, and #11 are not automatic release blockers if release notes clearly document v0.1 scope and limitations.
2. Compatibility is conservative and limited to validated synthetic/disposable SQLite fixture paths; this is acceptable only if the future release notes repeat the limitation.
3. Backend tests and frontend static/build checks can support a later gate, but they do not replace runtime smoke/dogfood evidence.

## Product consistency

Checked files:

- `README.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/ROADMAP.md`
- `docs/release/v0.1.0-readonly-plan.md`
- `docs/release/v0.1.0-readonly-checklist.md`
- `docs/handoff/phase-56.md`
- auditor roadmap file for Phase 57

Findings:

- README correctly says Phase 0–56 are complete before this Phase 57 work, and says v0.1 planning exists but no v0.1 tag/release has been published.
- PROJECT_STATUS correctly records completion through Phase 56 and identifies the next direction as a dedicated v0.1 release-gate audit.
- CHANGELOG includes release-facing entries through Phase 56.
- Docs consistently preserve the MVP model: one installation, one local admin user, one default book, read-only access by default.
- Docs consistently reject SaaS, GnuCash replacement, collaborative accounting, family-wallet baseline, production-readiness, and audited-security claims.

## Safety boundary

Findings:

- `.env.example` keeps `GNUCASH_WRITES_ENABLED=false`.
- `apps/api/app/config.py` keeps `gnucash_writes_enabled: bool = False`.
- `apps/api/app/routers/transactions.py` calls `_ensure_writes_enabled(settings)` before resolving book edit access or constructing `_write_service_for(book)` in validate/create/patch write routes.
- Disabled-write regression tests exist in `apps/api/tests/test_transaction_writes.py::TestWritesDisabledByDefault` and assert 403 responses and no `_write_service_for` construction.
- Frontend `transactions/new` redirects to `/transactions` when `env.GNUCASH_WRITES_ENABLED !== 'true'`.
- Transaction list shows the write entry point only behind `data.writesEnabled`.
- Experimental write UI copy requires an explicit acknowledgement and keeps post-MVP/disposable-data warnings.

No read-only boundary blocker was found.

## Release/readme/docs consistency

Findings:

- The current public release remains `v0.0.2-prealpha`; no `v0.1.0-readonly` tag or GitHub release exists.
- The release plan and checklist exist and are realistic about scope, checks, dogfood, compatibility, blockers, and rollback.
- Missing release notes are a blocker for publication.
- Missing recorded runtime smoke/dogfood evidence is a blocker for publication.
- README and release docs do not currently claim v0.1 is ready or published.

## GitHub project hygiene

Open issues reviewed via `gh issue list`:

- #22 — Add compatibility fixtures from real GnuCash versions
- #17 — Plan Russian documentation and UI localization
- #13 — Book management UI
- #12 — Scheduled/recurring transaction awareness
- #11 — Transaction search/filter improvements

Phase 57 created release-gate blocker issues:

- #24 — Prepare conservative v0.1.0-readonly release notes before publication
- #25 — Complete v0.1 read-only runtime smoke/dogfood gate on copied or disposable data

## Security notes

- No new hardcoded JWT secret was found in inspected release/config docs.
- `.env.example` uses a placeholder JWT secret and warns it must be replaced.
- README and security/deployment language continue to say not production-ready and not security-audited.
- Auth storage static checks cover httpOnly cookie usage and absence of browser local/session storage in auth paths.
- Sensitive tracked-file scan found no tracked `.env`, app DB, real GnuCash book outside the historical synthetic test-fixture allowlist, backups, keys, certs, or real CSV exports.

## Test/CI notes

Local checks run during Phase 57:

- `cd apps/api && pytest -q tests/test_transaction_writes.py::TestWritesDisabledByDefault && pytest -q` — passed; full backend result: 282 passed, 27 warnings.
- `cd apps/web && npm run check` — passed; `svelte-check found 0 errors and 0 warnings`.
- `cd apps/web && npm run test:auth-routes` — passed; `auth route checks passed`.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `git diff --check` — passed.

CI status for the final pushed Phase 57 commit must be checked separately if release publication is considered later.

## Recommended next actions

1. Do not publish `v0.1.0-readonly` in Phase 57.
2. Prepare conservative `docs/release/v0.1.0-readonly-notes.md` and review it against this audit, the release plan, and the checklist.
3. Complete and record a clean Docker/runtime smoke and manual dogfood pass using only copied or disposable data.
4. Re-run the release gate after blockers #24 and #25 are resolved.
5. Keep open backlog issues #22, #17, #13, #12, and #11 out of v0.1 unless explicitly accepted as in-scope read-only work.

## Suggested GitHub issues

Created:

1. #24 — Prepare conservative v0.1.0-readonly release notes before publication — labels: `release`, `documentation`, `audit`.
2. #25 — Complete v0.1 read-only runtime smoke/dogfood gate on copied or disposable data — labels: `release`, `read-only`, `safety`, `audit`.

No additional issues are suggested from this audit.

## What not to do next

- Do not publish a `v0.1.0-readonly` tag or GitHub release until blockers #24 and #25 are resolved or explicitly accepted by a later release gate.
- Do not mark the project production-ready or security-audited.
- Do not expand controlled writes or make write mode part of v0.1.
- Do not use real financial screenshots, exports, `.env`, app DBs, backups, keys, certs, or real GnuCash books in release artifacts.
- Do not start Phase 58 from this phase.
