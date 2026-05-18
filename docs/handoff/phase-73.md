# Phase 73 — Multi-book Access Model Audit

## Status

Complete. Phase 73 performed the auditor-first multi-book access model audit from the auditor roadmap, created the required audit artifact, created one meaningful GitHub follow-up issue, synchronized durable status docs, ran relevant checks, and pushed the phase commit.

This phase did not publish `v0.1.0-readonly`, did not expand write scope, did not enable writes, did not add collaborative/family-wallet framing, and did not start Phase 74.

## Auditor report

### Verdict

No new Phase 73 blocker for the current pre-alpha/read-only posture.

The multi-book foundation remains scoped to explicit `UserBookAccess` metadata, unauthorized book-aware routes are blocked before GnuCash data is opened, the frontend switcher renders only books returned by authenticated `GET /books`, and docs/UI frame multi-book as independent read-only books.

This verdict is limited to Phase 73 multi-book access model review. It is not a `v0.1.0-readonly` release approval, not a production-readiness claim, and not a professional security audit.

### Blockers

No new Phase 73 blocker was found.

Carried-forward blockers before any `v0.1.0-readonly` publication:

1. #24 — conservative `v0.1.0-readonly` release notes are still required before publication.
2. #25 — copied/disposable-data runtime smoke/dogfood evidence is still required before publication.

### Audit report

- `docs/audits/phase-73-audit.md`

### Suggested / created GitHub issues

Created:

- #35 — Expand multi-book access boundary tests for archived books and all read-only routes.

Not created separately:

- Book switcher UX clarification — existing UI/doc/static checks already frame books as independent read-only books.
- Book archive/visibility docs — fixed directly in `docs/book-switcher-readonly-model.md` and covered by #35 for regression coverage.

### Auditor evidence summary

- AGENTS.md, PROJECT_STATUS.md, README.md, CHANGELOG.md, release docs, latest handoff, roadmap file, relevant backend/frontend code, tests, docs, and open GitHub issues were inspected.
- `BookAccessService` requires explicit `UserBookAccess` roles for book view/edit decisions.
- `BookRegistryService.list_books_for_user()` joins through `UserBookAccess` and filters archived books.
- `resolve_viewable_book()` rejects missing/archived books and enforces view access before account/transaction/report/export service use.
- Existing backend tests cover visible-book filtering and unauthorized access for major route families.
- `getActiveBookContext()` uses the authenticated accessible book list and replaces stale/malicious selected-book cookies with accessible fallbacks.
- `BookSwitcher.svelte` renders only the accessible `books` prop and says “independent read-only books”.
- Test-hardening gap: archived-book visibility and every report route family need explicit regression tests before multi-book/admin scope grows.

## PM report

### Decision

Accept the auditor verdict. Phase 73 may safely record the audit, create one meaningful GitHub issue for multi-book access-boundary test hardening, clarify archive/visibility semantics in the existing book-switcher model doc, update README/PROJECT_STATUS/CHANGELOG/handoff, and run verification.

No product feature work, write expansion, book-management UI, archive controls, release publication, or Phase 74 work is accepted in this phase.

### Why

The roadmap asks for a multi-book access model audit, not implementation of new multi-book administration. The current boundary is safe enough for the pre-alpha/read-only posture, while the meaningful gap is future regression coverage around archived books and all route families. The safest accepted work is durable audit/status/docs synchronization plus issue hygiene.

### Phase brief

- Goal: complete Phase 73 as a multi-book access model audit; inspect explicit user-book access, unauthorized access blocking, book switcher visibility, independent-books wording, no family-wallet/collaborative implication, and default-book alias safety.
- Non-goals: no Phase 74, no product feature work, no book-management/archive UI, no write-scope expansion, no release/tag publication, no real financial/secrets artifacts, no production/security-audited claims.
- Acceptance criteria:
  - `docs/audits/phase-73-audit.md` exists.
  - `docs/handoff/phase-73.md` exists.
  - `PROJECT_STATUS.md` reflects completion through Phase 73 and next explicit-only Phase 74.
  - README latest-audit/current-status references are synchronized.
  - CHANGELOG records the release-facing Phase 73 audit/docs result.
  - Meaningful GitHub issue hygiene is completed without noisy issues.
  - Relevant checks pass.
  - A separate commit is created and pushed to `origin/main`.
- Safety checks:
  - Keep MVP read-only by default.
  - Keep `GNUCASH_WRITES_ENABLED=false` as the default.
  - Keep controlled writes experimental/post-MVP only.
  - Do not commit `.env`, real books, app DBs, backups, secrets, keys, certs, real screenshots, or real exports.
  - Do not claim production readiness, security audit, broad compatibility, SaaS readiness, GnuCash replacement, collaborative accounting, safe write mode, or family-wallet positioning.
- Verification:
  - Static multi-book access/code/docs searches.
  - `git diff --check`.
  - `cd apps/api && pytest -q`.
  - `cd apps/web && npm run check && npm run test:auth-routes && npm run build`.
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`.
  - GitHub issue verification via `gh`.

### Risks

- The phrase “shared access” in tests can be misread as collaborative accounting. Mitigation: audit/handoff/docs keep the product language to “multiple independent books with scoped access”; no collaborative editing semantics were added.
- Missing archived-book tests could become a future bug if book-management UI is added. Mitigation: #35 tracks explicit regression coverage before that surface grows.
- The audit could be overread as v0.1 approval. Mitigation: README/PROJECT_STATUS/handoff keep #24/#25 as publication blockers.

### Files/docs to update

- `docs/audits/phase-73-audit.md`
- `docs/handoff/phase-73.md`
- `docs/book-switcher-readonly-model.md`
- `PROJECT_STATUS.md`
- `README.md`
- `CHANGELOG.md`

### GitHub/backlog

- Created #35 for archived-book/full route-family multi-book access-boundary test hardening.
- #24 and #25 remain v0.1 publication blockers.

## Engineer report

Implemented only PM-accepted Phase 73 docs/status/GitHub hygiene work:

- Created `docs/audits/phase-73-audit.md` with auditor verdict, blockers, non-blockers, multi-book access findings, GitHub issue decisions, safety notes, and next actions.
- Clarified archived-book visibility and future archive/visibility-management expectations in `docs/book-switcher-readonly-model.md`.
- Created GitHub issue #35 for archived-book/full route-family multi-book access-boundary test hardening.
- Updated `PROJECT_STATUS.md` to mark completion through Phase 73, add Phase 73 to completed phases, set Phase 74 as the next explicit-only roadmap phase, and add a Phase 73 status section.
- Updated `README.md` current status through Phase 73 and latest-audit link.
- Updated `CHANGELOG.md` with the release-facing Phase 73 multi-book access audit entry.
- Created this handoff document.

No product code changed. No write behavior/default changed. No tag or GitHub release was published. No Phase 74 work was started.

## Checks

Run during Phase 73:

- `git status --short --branch` — clean against `origin/main` before edits.
- `~/.local/bin/gh issue list --state open --limit 100 --json number,title,labels,url` — reviewed open issues and avoided duplicates.
- `~/.local/bin/gh issue create ...` — created #35.
- Static multi-book access/code/docs searches:
  - `BookAccessService` requires explicit `UserBookAccess` roles;
  - `BookRegistryService.list_books_for_user()` scopes by user access and non-archived books;
  - book-aware account/transaction/report/export routes resolve viewable books before service use;
  - backend tests cover major unauthorized route families;
  - frontend active-book context resolves only accessible books and replaces stale cookies;
  - book-switcher UI copy says independent read-only books and static checks reject upload/collaborative/family-wallet framing.
- `git diff --check` — passed.
- `cd apps/api && pytest -q` — passed, 282 passed, 27 warnings.
- `cd apps/web && npm run check` — passed, 0 errors and 0 warnings.
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.

Final check results:

- Required audit artifacts: passed.
- GitHub issue hygiene: passed (#35 created; no noisy duplicate issue created).
- Static multi-book access assertions: passed.
- Backend/frontend/Docker checks: passed.
- Diff whitespace: passed.

## Safety confirmation

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental post-MVP and disabled by default.
- No write scope was expanded.
- No v0.1 release/tag was published.
- No Phase 73 result was represented as production readiness, release approval, security audit, broad compatibility, safe write-mode support, collaborative accounting, family-wallet support, or SaaS readiness.
- No GnuCash replacement, hosted SaaS, family-wallet baseline, collaborative accounting, banking integration, import/sync, book-management UI, archive UI, or safe write-mode positioning was introduced.
- No real financial data, new GnuCash book, `.env`, app DB, backup, secret, key, token, cert, real screenshot, or real CSV export was added.

## Commit / push

- Phase commit message: `docs: add phase 73 multi-book access audit`.
- Phase commit: final pushed `origin/main` HEAD for Phase 73; pre-handoff self-reference push was `a00dab0`.
- Pushed to `origin/main`: yes.

## Blockers carried forward

1. Create and review conservative `docs/release/v0.1.0-readonly-notes.md` before any release publication (#24).
2. Complete and record copied/disposable-data Docker/runtime smoke and manual dogfood evidence before any release publication (#25).
3. Redact/sanitize full default-book seed log path/URI output and add/adjust tests (#27).
4. Continue gradual markdown source readability cleanup before broader announcement (#28).
5. Add a localization glossary for accounting/safety terms before the Russian translation surface grows (#29).
6. Continue real GnuCash Desktop version fixture coverage in #22 when an explicit compatibility implementation phase is requested.
7. Use #26 to make CORS origin narrowing visible in future release/checklist/deployment hardening work.
8. Implement generated/disposable read-only performance benchmark coverage for #30–#33 before claiming known large-book scalability.
9. Replace frontend display-only `Number()` money decisions with string/sign helpers or a decimal-safe utility in a later hardening phase (#34).
10. Add archived-book and full route-family multi-book access-boundary tests in a later hardening phase (#35).

Do not start Phase 74 until explicitly requested.
