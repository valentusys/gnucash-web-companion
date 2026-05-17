# Phase 35 — PM Brief: Audit-Driven Phase 34 Public Baseline and Controlled-Writes Docs Sync

## Status

Implemented by engineer in guarded background mission phase 12. Documentation/status synchronization is complete; final commit SHA and push status are recorded below.

## PM decision

Make the next engineer phase a narrowly scoped audit-driven documentation/status synchronization phase for the two accepted blockers from the immediately preceding independent audit:

1. synchronize public current-status wording through the Phase 34 baseline; and
2. remove/update the stale `docs/v0.2-controlled-writes.md` known-limitation line that says amount range filters are backend-only in the frontend.

Do not restore or change backend write-gating code: the phase 10 audit found no urgent write-gating blocker.

## Why

The immediately preceding audit (`/home/val/.hermes/logs/gnucash-web-companion/guarded-15-phases-20260517-215201/phase-10-audit.log`, addendum in `docs/audits/2026-05-17-audit.md`) concluded:

- backend disabled-write gating passed a real API-level check;
- `Settings.gnucash_writes_enabled: bool = False` remains the default;
- `_ensure_writes_enabled()` is present;
- validate/create/patch write endpoints call the gate before `_write_service_for()` / `GnuCashWriteService` construction;
- `pytest -q tests/test_transaction_writes.py::TestWritesDisabledByDefault` passed (`4 passed, 1 warning`);
- README still says Phase 0–33 complete while `PROJECT_STATUS.md` and latest handoff show Phase 34 complete;
- `docs/v0.2-controlled-writes.md` still says amount range filters are backend-only in the frontend, although Phase 30 added frontend amount range filters.

This documentation drift is higher priority than starting new release-value feature work because stale public baseline wording and stale controlled-writes limitations can mislead reviewers before `v0.0.2-prealpha` release preparation.

## Goal

Synchronize public documentation through the Phase 34 baseline and clean the stale controlled-writes limitation, while preserving conservative pre-alpha/read-only positioning and without publishing a release.

## Non-goals

- Do not implement product features.
- Do not enable writes by default.
- Do not change the write-gating route order unless a direct regression is discovered during verification.
- Do not add new write endpoints, write-mode UI, import/export write capability, banking integrations, recurring transactions, account editing, delete support, or collaborative editing.
- Do not publish `v0.0.2-prealpha`, create tags, create GitHub releases, publish packages, or claim production readiness.
- Do not close #18, #20, #21, or #22 unless a separate explicit PM/release decision says to do so.
- Do not commit real financial data, real GnuCash books, `.env`, app DBs, backups, secrets, tokens, keys, certs, or real screenshots.

## Acceptance criteria

1. `README.md` current status is advanced from Phase 0–33 to Phase 0–34 complete, or another explicitly honest current baseline that does not imply Phase 34 is missing.
2. README still clearly says:
   - pre-alpha / MVP in progress;
   - not production-ready;
   - not security-audited;
   - MVP v0.1 remains read-only by default;
   - controlled writes are experimental/post-MVP and disabled by default;
   - `v0.0.2-prealpha` has not been published unless Val explicitly requests release publication.
3. `docs/v0.2-controlled-writes.md` no longer contains the active stale limitation `amount range filters are backend-only in the frontend`. Replace it with accurate wording, or move it to resolved historical limitations with a Phase 30 note.
4. `CHANGELOG.md` Unreleased entries include a Phase 35 documentation/status sync entry only after implementation.
5. `docs/release/v0.0.2-prealpha-notes.md` and `docs/ROADMAP.md` are checked for stale `Phase 0–33`, `through Phase 33`, or related current-baseline wording and updated only if active wording is stale or misleading.
6. `PROJECT_STATUS.md` remains honest: Phase 34 is complete now; Phase 35 is only complete after engineer implementation finishes.
7. `docs/handoff/phase-35.md` is updated by the engineer with implementation summary, exact files changed, verification results, safety confirmation, commit SHA, push status, and GitHub issue outcome.
8. GitHub issue #19 is updated and may be closed only if README/PROJECT_STATUS/CHANGELOG/release docs are fully synchronized through Phase 34/35 and no stale active public status baseline remains.
9. #18, #20, #21, and #22 remain open unless explicitly handled outside this phase.

## Suggested implementation notes for engineer

- Treat this as documentation/status hygiene, not a feature phase.
- Start with README current status and `docs/v0.2-controlled-writes.md` known limitations.
- Search for active stale current-state claims such as `Phase 0–33`, `Phase 0-33`, `through Phase 33`, and `backend-only in the frontend`.
- Do not rewrite historical audit/PM text merely because it mentions earlier phases; historical records are acceptable when clearly historical.
- If #19 is closed, add a concise closing comment explaining exactly which files were synchronized and which commit did it.
- Keep release language conservative: `v0.0.2-prealpha` candidate notes may exist, but no tag/release should be created without explicit Val approval.

## Safety checks

Engineer must explicitly verify and report:

- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental, post-MVP, disabled by default, and not part of MVP v0.1.
- No production-readiness, audited-security, or broad GnuCash-version support claim was added.
- No code path was changed to construct/write with `GnuCashWriteService` when writes are disabled.
- No frontend auth token storage moved to localStorage/sessionStorage.
- No real financial data, GnuCash books, `.env`, app DBs, backups, secrets, tokens, keys, certs, or real screenshots were added.

## Verification commands

Required after implementation:

```bash
cd apps/api && pytest -q tests/test_transaction_writes.py::TestWritesDisabledByDefault
cd apps/api && pytest -q
cd apps/web && npm run check && npm run test:auth-routes && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

GitHub/status preflight:

```bash
git --version
gh --version || true
gh auth status || true
gh issue view 19 || true
gh issue view 18 || true
gh issue view 20 || true
gh issue view 21 || true
gh issue view 22 || true
```

Documentation consistency checks:

```bash
grep -R "Phase 0–33\|Phase 0-33\|through Phase 33\|backend-only in the frontend" README.md PROJECT_STATUS.md CHANGELOG.md docs/release docs/ROADMAP.md docs/v0.2-controlled-writes.md || true
```

Expected result: no active stale public current-state or controlled-writes limitation claim remains. Historical audit/PM references are acceptable only when clearly historical.

## Files/docs to update

Expected files:

- `README.md` — update current status to Phase 0–34 complete or another honest current baseline.
- `docs/v0.2-controlled-writes.md` — remove/update stale amount-range filter limitation.
- `CHANGELOG.md` — add Phase 35 docs/status sync entry after implementation.
- `PROJECT_STATUS.md` — after engineer completion, mark Phase 35 complete and record summary/results.
- `docs/handoff/phase-35.md` — update this PM brief with implementation summary, verification, commit, and GitHub issue outcome.

Potential files if stale wording is found:

- `docs/release/v0.0.2-prealpha-notes.md`.
- `docs/ROADMAP.md`.
- `docs/audits/2026-05-17-audit.md` only if the auditor explicitly requests an audit-report addendum; otherwise do not rewrite audit findings from this engineer phase.

## GitHub/backlog

- Primary issue: #19 “Sync README/PROJECT_STATUS/CHANGELOG after Phase 28”. It was reopened by the phase 10 audit because README was one phase behind.
- Keep #18 “Verify backend write feature flag cannot be bypassed” open unless PM/release triage explicitly closes it after confirming the mission no longer requires it open.
- Keep #20 `v0.0.2-prealpha` release preparation open; do not publish release artifacts in this phase.
- Keep #21 write-mode UI warning and #22 real GnuCash compatibility fixtures open for future phases.

## Handoff requirements for engineer

At completion, update this file with:

- implementation summary;
- exact docs changed;
- exact tests/checks run and results;
- safety confirmation;
- commit SHA;
- push status;
- GitHub issue #19/#18/#20/#21/#22 status.

## Engineer implementation results

### Implementation summary

- Synchronized public current-status wording so Phase 34 is no longer missing from the active public baseline.
- Updated controlled-writes documentation to remove the stale active limitation that described amount range filters as backend-only in the frontend; Phase 30 frontend amount filters are now recorded as completed historical work.
- Updated changelog, release candidate notes, roadmap, project status, and this handoff without publishing any tag or GitHub release.
- No product code or write-gating behavior was changed.

### Exact docs changed

- `README.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/v0.2-controlled-writes.md`
- `docs/release/v0.0.2-prealpha-notes.md`
- `docs/ROADMAP.md`
- `docs/handoff/phase-35.md`

### Verification results

- `cd apps/api && pytest -q tests/test_transaction_writes.py::TestWritesDisabledByDefault` — passed.
- `cd apps/api && pytest -q` — passed.
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- Documentation search for active stale `Phase 0–33`, `Phase 0-33`, `through Phase 33`, and `backend-only in the frontend` claims in README/status/changelog/release/roadmap/controlled-writes docs — no active stale public baseline or controlled-writes limitation remains; only historical Phase 34/PROJECT_STATUS references remain.

### Safety confirmation

- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental, post-MVP, disabled by default, and outside MVP v0.1.
- No production-readiness, audited-security, or broad GnuCash-version support claim was added.
- No code path was changed to construct/write with `GnuCashWriteService` when writes are disabled.
- No frontend auth token storage was moved to localStorage/sessionStorage.
- No real financial data, GnuCash books, `.env`, app DBs, backups, secrets, tokens, keys, certs, or real screenshots were added.

### GitHub issue status

- #19: closed after README/PROJECT_STATUS/CHANGELOG/release docs were synchronized through Phase 35 and stale controlled-writes limitation wording was removed.
- #18: left open as requested.
- #20: left open as requested.
- #21: left open as requested.
- #22: left open as requested.

### Commit and push

- Commit: `f50f407` (`docs: sync phase 35 audit status`).
- Push: pushed to `origin/main`.

## Blockers

None. The accepted audit documentation blockers for Phase 35 were resolved.
