# Phase 75 — v0.1.1 Maintenance Release Audit

## Status

Complete. Phase 75 performed the auditor-first v0.1.1 maintenance-release audit from the auditor roadmap, created the required audit artifact, synchronized durable status docs, ran full relevant checks because the phase makes a release/readiness decision, and pushed the phase commit.

This phase did not publish `v0.1.0-readonly`, did not prepare or publish `v0.1.1-readonly`, did not enable writes, did not expand write scope, did not implement product feature work, and did not start Phase 76.

## Auditor report

### Verdict

No release needed.

More precisely, a `v0.1.1-readonly` maintenance release is not applicable yet because `v0.1.0-readonly` does not exist as a git tag or GitHub release. GitHub releases list only `v0.0.1-prealpha` and `v0.0.2-prealpha`, and `gh release view v0.1.0-readonly` reports `release not found`.

This verdict is limited to Phase 75 maintenance-release audit. It is not approval to publish `v0.1.0-readonly`, not approval to plan/ship `v0.1.1-readonly`, not a production-readiness claim, and not a professional security audit.

### Blockers

No new Phase 75 blocker was found for the current pre-alpha/read-only posture.

Blocking conditions before any `v0.1.1-readonly` maintenance release can be considered:

1. `v0.1.0-readonly` does not exist as a git tag or GitHub release.
2. #24 — conservative `v0.1.0-readonly` release notes are still required before initial v0.1 publication.
3. #25 — copied/disposable-data runtime smoke/dogfood evidence is still required before initial v0.1 publication.
4. There is no completed post-v0.1 dogfood bugfix/docs/small read-only UX fix stream to package because the base v0.1 release has not happened.

### Audit report

- `docs/audits/phase-75-audit.md`

### Suggested / created GitHub issues

Created: none.

Suggested: none new. Existing #24 and #25 cover the meaningful release blockers. Creating a placeholder “v0.1.1 not applicable” issue would be noisy before `v0.1.0-readonly` exists.

### Auditor evidence summary

- AGENTS.md, PROJECT_STATUS.md, README.md, CHANGELOG.md, release docs, latest handoff, prior relevant audits, roadmap file, write-boundary code/docs, Git tags, GitHub releases, and open GitHub issues were inspected.
- `git tag -l 'v0.1*'` returned no tags.
- `gh release list --repo valentusys/gnucash-web-companion --limit 20` listed only `v0.0.2-prealpha` and `v0.0.1-prealpha`.
- `gh release view v0.1.0-readonly --repo valentusys/gnucash-web-companion` returned `release not found`.
- #24 and #25 are open.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state and no write-mode promotion was found.

## PM report

### Decision

Accept the auditor verdict. Phase 75 may safely record that `v0.1.1-readonly` is not applicable/no release needed, update durable audit/status/handoff docs, keep #24/#25 as the active release blockers, run verification, and commit/push the phase.

No product feature work, release publication, maintenance-release preparation, write enablement, write-scope expansion, new issue theater, or Phase 76 work is accepted in this phase.

### Why

The roadmap asks whether a maintenance release is needed if `v0.1.0-readonly` exists. It does not exist. The safe decision is to prevent misleading release sequencing: complete the audit artifact and status sync, but keep initial v0.1 work blocked by #24/#25 and avoid inventing a v0.1.1 backlog.

### Phase brief

- Goal: complete Phase 75 as a v0.1.1 maintenance-release audit; verify whether `v0.1.0-readonly` exists, whether post-v0.1 dogfood/docs/read-only UX fixes exist, and whether any maintenance release should be prepared.
- Non-goals: no Phase 76, no product feature work, no v0.1/v0.1.1 tag or GitHub release, no write enablement, no write-scope expansion, no real financial/secrets artifacts, no production/security-audited/safe-write claims.
- Acceptance criteria:
  - `docs/audits/phase-75-audit.md` exists.
  - `docs/handoff/phase-75.md` exists.
  - `PROJECT_STATUS.md` reflects completion through Phase 75 and explicit-only Phase 76.
  - README current-status/latest-audit references are synchronized.
  - CHANGELOG records the release-facing Phase 75 audit result.
  - GitHub issue hygiene is completed without noisy new issues.
  - Relevant checks pass.
  - A separate commit is created and pushed to `origin/main`.
- Safety checks:
  - Keep MVP read-only by default.
  - Keep `GNUCASH_WRITES_ENABLED=false` as the default.
  - Keep controlled writes experimental/post-MVP only.
  - Do not commit `.env`, real books, app DBs, backups, secrets, keys, certs, real screenshots, or real exports.
  - Do not claim production readiness, security audit, broad compatibility, SaaS readiness, GnuCash replacement, collaborative accounting, safe write mode, or family-wallet positioning.
- Verification:
  - Git/GitHub release/tag checks for `v0.1*` and `v0.1.0-readonly`.
  - Static release/docs/write-boundary checks.
  - `git diff --check`.
  - `cd apps/api && pytest -q`.
  - `cd apps/web && npm run check && npm run test:auth-routes && npm run build`.
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`.

### Risks

- The phrase “maintenance release” can imply `v0.1.0-readonly` already exists. Mitigation: audit/status/handoff explicitly state v0.1.0 is unpublished and v0.1.1 is not applicable.
- A new v0.1.1 placeholder issue could create backlog theater. Mitigation: no new issue; #24/#25 remain the meaningful blockers.
- Release readiness could be overclaimed from green checks. Mitigation: checks support the Phase 75 audit only; they do not unblock v0.1 publication without #24/#25.

### Files/docs to update

- `docs/audits/phase-75-audit.md`
- `docs/handoff/phase-75.md`
- `PROJECT_STATUS.md`
- `README.md`
- `CHANGELOG.md`

### GitHub/backlog

- No new issue created.
- #24 and #25 remain initial v0.1 publication blockers.
- #36 remains the controlled-write v0.2 readiness tracker.

## Engineer report

Implemented only PM-accepted Phase 75 docs/status/GitHub hygiene work:

- Created `docs/audits/phase-75-audit.md` with auditor verdict, blockers, non-blockers, Phase 75 roadmap checks, safety boundary, release/docs consistency, GitHub issue decision, and next actions.
- Updated `PROJECT_STATUS.md` to mark completion through Phase 75, add Phase 75 to completed phases, set Phase 76 as explicit-only future work, and add a Phase 75 status section.
- Updated `README.md` current status through Phase 75 and latest-audit link.
- Updated `CHANGELOG.md` with the release-facing Phase 75 maintenance-release audit entry.
- Created this handoff document.

No product code changed. No write behavior/default changed. No tag or GitHub release was published. No v0.1.1 release prep was started. No Phase 76 work was started.

## Checks

Run during Phase 75:

- `date +%F` — 2026-05-18.
- `git status --short --branch` — clean against `origin/main` before edits.
- `git log -1 --oneline` — starting HEAD `522d4c5 docs: add phase 74 controlled writes audit`.
- `~/.local/bin/gh auth status` — authenticated as `valentusys`.
- `git fetch --tags origin` and `git tag -l 'v0.1*'` — no `v0.1*` tags found.
- `~/.local/bin/gh release list --repo valentusys/gnucash-web-companion --limit 20` — only `v0.0.2-prealpha` and `v0.0.1-prealpha` listed.
- `~/.local/bin/gh release view v0.1.0-readonly --repo valentusys/gnucash-web-companion --json tagName,isPrerelease,name,url` — `release not found`.
- `~/.local/bin/gh issue list --state open --limit 100 --json number,title,labels,url` — reviewed open issues and avoided duplicates.
- `~/.local/bin/gh issue view 24` and `~/.local/bin/gh issue view 25` — both release blockers remain open.
- Static release/docs/write-boundary searches:
  - `docs/release/v0.1.0-readonly-notes.md` is absent, matching #24;
  - no dogfood results artifact exists, matching #25;
  - backend/default environment keeps writes disabled;
  - backend write routes are still feature-gated;
  - frontend write UI remains hidden unless explicitly enabled and warns/acknowledges experimental post-MVP write mode.
- `git diff --check` — passed.
- `cd apps/api && pytest -q` — passed, 282 passed, 27 warnings.
- `cd apps/web && npm run check` — passed, 0 errors and 0 warnings.
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.

Final check results:

- Required audit artifacts: passed.
- GitHub issue hygiene: passed (no new noisy issue; #24/#25 remain open blockers).
- Release/tag evidence: passed (`v0.1.0-readonly` missing, so v0.1.1 is not applicable).
- Backend/frontend/Docker checks: passed.
- Diff whitespace: passed.

## Safety confirmation

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental post-MVP and disabled by default.
- No write scope was expanded.
- No v0.1 or v0.1.1 release/tag was published.
- No Phase 75 result was represented as production readiness, release approval, security audit, broad compatibility, safe write-mode support, collaborative accounting, family-wallet support, or SaaS readiness.
- No GnuCash replacement, hosted SaaS, family-wallet baseline, collaborative accounting, banking integration, import/sync, or safe write-mode positioning was introduced.
- No real financial data, new GnuCash book, `.env`, app DB, backup, secret, key, token, cert, real screenshot, or real CSV export was added.

## Commit / push

- Phase commit message: `docs: add phase 75 maintenance release audit`.
- Phase commit: final pushed `origin/main` HEAD for Phase 75.
- Pushed to `origin/main`: yes.

## Blockers carried forward

1. Create and review conservative `docs/release/v0.1.0-readonly-notes.md` before any initial v0.1 publication (#24).
2. Complete and record copied/disposable-data Docker/runtime smoke and manual dogfood evidence before any initial v0.1 publication (#25).
3. Do not consider `v0.1.1-readonly` until after `v0.1.0-readonly` exists and there is an actual post-release maintenance change set.
4. Keep remaining controlled-write v0.2 readiness gates explicit and unresolved until an explicit write-readiness phase handles them (#36).
5. Continue real GnuCash Desktop version fixture coverage in #22 before broad compatibility/write-compatibility claims.
6. Redact/sanitize full default-book seed log path/URI output and add/adjust tests (#27).
7. Use #26 to make CORS origin narrowing visible in future release/checklist/deployment hardening work.
8. Continue gradual markdown source readability cleanup before broader announcement (#28).
9. Add a localization glossary for accounting/safety terms before the Russian translation surface grows (#29).
10. Implement generated/disposable read-only performance benchmark coverage for #30–#33 before claiming known large-book scalability.
11. Replace frontend display-only `Number()` money decisions with string/sign helpers or a decimal-safe utility in a later hardening phase (#34).
12. Add archived-book and full route-family multi-book access-boundary tests in a later hardening phase (#35).

Do not start Phase 76 until explicitly requested.
