# Phase 36 — PM Brief: Write-Mode UI Warning and Explicit Confirmation

## Status

Planned by Project Lead in guarded background mission phase 14. This is a PM brief for the next engineer phase; implementation is not complete yet.

## PM decision

Make the next engineer phase a narrowly scoped safety/release-readiness fix for the highest-risk accepted blocker from the immediately preceding independent audit: GitHub #21, “Add UI warning before write mode”.

Do not publish `v0.0.2-prealpha` in this phase. Do not expand write capabilities. Do not change backend write-gating unless verification finds a regression.

## Why

The phase 13 audit addendum in `docs/audits/2026-05-17-audit.md` found no urgent backend write-gating blocker:

- `Settings.gnucash_writes_enabled: bool = False` remains the default.
- `_ensure_writes_enabled()` gates validate/create/patch endpoints before write-service construction.
- `pytest -q tests/test_transaction_writes.py::TestWritesDisabledByDefault` passed (`4 passed, 1 warning`).

The remaining active blockers are release preparation (#20), write-mode UI warning/confirmation (#21), and real-version compatibility fixtures (#22). The UI warning is the highest-risk engineer task to address next because write-mode UI already exists behind `GNUCASH_WRITES_ENABLED=true`, and the current confirmation text is too light for an experimental post-MVP financial write path.

## Goal

Add an explicit, hard-to-miss frontend warning and confirmation flow for controlled write mode so users cannot reach or submit the transaction write form without being told that:

- controlled writes are experimental post-MVP functionality;
- MVP v0.1 remains read-only by default;
- `GNUCASH_WRITES_ENABLED=false` remains the safe default;
- GnuCash Desktop remains the authoritative editor;
- users must use disposable/test copies and backups, never their only real book.

## Non-goals

- Do not enable writes by default.
- Do not add new write endpoints or broaden existing write capabilities.
- Do not change the backend write model except to preserve/verify the existing disabled-write gate.
- Do not add CSV/OFX import, banking integrations, recurring transactions, account editing, delete support, split amount editing, or collaborative editing.
- Do not publish `v0.0.2-prealpha`, create tags, create GitHub releases, publish packages, or claim production readiness.
- Do not claim write mode is safe for real financial data.
- Do not close #18, #20, or #22 in this phase.
- Do not commit real financial data, real GnuCash books, `.env`, app DBs, backups, secrets, tokens, keys, certs, or real screenshots.

## Acceptance criteria

1. The transactions page still hides the `New transaction` entry point unless frontend `GNUCASH_WRITES_ENABLED === 'true'`.
2. When writes are enabled, the `New transaction` entry point is accompanied by explicit warning text, not just a neutral button.
3. The `/transactions/new` page displays a prominent warning panel before or above the form with conservative write-mode language covering the goal bullets above.
4. Final create submission requires an explicit user acknowledgement beyond a generic browser confirm. Acceptable options include a required checkbox plus confirm dialog, or a typed acknowledgement phrase. Keep it simple and accessible.
5. Validation-only action may remain available for form validation, but final create must be blocked unless the acknowledgement is present.
6. Existing server-side disabled-write guards remain in place for both `validate` and `create` actions when frontend writes are disabled.
7. Add or update frontend route checks so the warning/acknowledgement behavior is covered by automation where practical. At minimum, extend `npm run test:auth-routes` or an equivalent existing script to prove the disabled-write redirect still works and the write page contains the warning/acknowledgement when enabled.
8. Update public docs/status after implementation:
   - `CHANGELOG.md` Unreleased entry for Phase 36.
   - `docs/v0.2-controlled-writes.md` safety checklist noting UI warning/confirmation coverage.
   - `docs/release/v0.0.2-prealpha-notes.md` if it tracks the controlled-write safety backlog.
   - `PROJECT_STATUS.md` marking Phase 36 complete only after implementation and checks pass.
   - this handoff with implementation summary, verification, commit, push, and issue status.
9. GitHub #21 is updated and may be closed only if the implemented UI warning/confirmation and checks satisfy this brief.
10. #18, #20, and #22 remain open unless explicitly handled by a separate PM/release decision.

## Suggested implementation notes for engineer

- Inspect current write UI first:
  - `apps/web/src/routes/transactions/+page.svelte`
  - `apps/web/src/routes/transactions/new/+page.svelte`
  - `apps/web/src/routes/transactions/new/+page.server.ts`
  - `apps/web/src/lib/components/ReadOnlyStatusBanner.svelte`
- Prefer a small reusable component such as `WriteModeWarning.svelte` if it keeps the page readable.
- Keep all write-warning copy conservative and unambiguous: experimental, post-MVP, disabled by default, test/disposable copies only, backups required, GnuCash Desktop authoritative.
- Avoid localStorage/sessionStorage for acknowledgement state. A per-submit checkbox or form field is safer and easier to audit.
- Do not weaken backend API 403 behavior for disabled writes.
- Do not make screenshots with real data.

## Safety checks

Engineer must explicitly verify and report:

- `GNUCASH_WRITES_ENABLED=false` remains the default documented state.
- Backend disabled-write API gating still returns 403 for validate/create/patch before write-service construction.
- The frontend write page is unreachable/redirected when frontend writes are disabled.
- When frontend writes are enabled, users see explicit warning text before final write submission.
- Final create submission cannot proceed without explicit acknowledgement.
- Controlled writes remain experimental, post-MVP, disabled by default, and outside MVP v0.1.
- No production-readiness, audited-security, or broad GnuCash-version support claim was added.
- Auth tokens remain in httpOnly cookies; no localStorage/sessionStorage auth path was introduced.
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
gh issue view 18 || true
gh issue view 20 || true
gh issue view 21 || true
gh issue view 22 || true
```

Documentation/code consistency checks:

```bash
grep -R "GNUCASH_WRITES_ENABLED=false\|experimental post-MVP\|GnuCash Desktop remains" README.md docs apps/web/src || true
grep -R "localStorage\|sessionStorage" apps/web/src || true
```

Expected result: write-mode warning language is visible in the write UI/docs, and no auth-token storage path is introduced.

## Files/docs to update

Expected implementation files:

- `apps/web/src/routes/transactions/+page.svelte` — warning near the write entry point when writes are enabled.
- `apps/web/src/routes/transactions/new/+page.svelte` — prominent warning and explicit acknowledgement before final create.
- `apps/web/src/routes/transactions/new/+page.server.ts` — validate acknowledgement for final create if using a submitted form field.
- Existing frontend auth/route check script or related tests — cover disabled redirect and enabled warning/acknowledgement where practical.

Potential component file:

- `apps/web/src/lib/components/WriteModeWarning.svelte`

Expected docs/status files after implementation:

- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/v0.2-controlled-writes.md`
- `docs/release/v0.0.2-prealpha-notes.md` if the safety checklist is mentioned there
- `docs/handoff/phase-36.md`

## GitHub/backlog

- Primary issue: #21 “Add UI warning before write mode”. Update and close only if the warning/confirmation is implemented and verified.
- Keep #18 “Verify backend write feature flag cannot be bypassed” open unless a separate audit/release decision accepts closure.
- Keep #20 `v0.0.2-prealpha` release preparation open; do not publish release artifacts in this phase.
- Keep #22 real GnuCash compatibility fixtures open for a future phase.

## Handoff requirements for engineer

At completion, update this file with:

- implementation summary;
- exact files changed;
- exact tests/checks run and results;
- safety confirmation;
- commit SHA;
- push status;
- GitHub issue #21/#18/#20/#22 status.

## Project Lead report

### Decision

Plan Phase 36 as the write-mode UI warning/explicit confirmation phase for GitHub #21.

### Why

The preceding audit found backend write-gating intact and documentation synchronized through Phase 35. The next highest-risk accepted blocker is preventing users from treating the hidden experimental write UI as safe for real books if they explicitly enable it.

### Risks

- A weak warning may be treated as permission to use real financial data.
- A client-only acknowledgement must not replace backend write-gating.
- Over-scoping into new write features would weaken the pre-alpha/release-readiness cadence.

### Files/docs to update

See the expected files list above.

### GitHub/backlog

Work against #21; leave #18, #20, and #22 open unless separately decided.
