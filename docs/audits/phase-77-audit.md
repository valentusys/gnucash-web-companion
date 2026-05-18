# Phase 77 Audit — Real Read-only Dogfood on Copied/Disposable GnuCash Book

Date: 2026-05-18

## Executive summary

Phase 77 finally produced runtime dogfood evidence instead of another audit-only phase. The API-level read-only deployment worked against a copied/disposable SQL book and runtime writes were disabled. The release gate is still not passed because the Docker web UI cannot render `/login`; it redirects `/login` to itself and blocks browser dogfood. The phase used a synthetic/disposable fixture because no safe real copied personal book was discoverable.

## Verdict

Not ready for `v0.1.0-readonly`.

The project is ready after fixes only if #37 is fixed and the browser dogfood pass is rerun successfully with writes disabled. The API evidence is useful but not enough for a user-facing web release.

## Top blockers

1. #37 — Docker web UI redirects `/login` to itself, leaving the web container unhealthy and preventing browser/UI dogfood.
2. #25 cannot be closed from this phase alone because the dogfood pass is API-only plus failed browser attempt; browser-level evidence remains missing.
3. No safe real copied personal GnuCash SQL book was found locally, so this phase used the committed synthetic/disposable SQL fixture. That is safe, but weaker than a copied real-book pass.

## Important non-blockers

1. API health was `ok` and the default copied/disposable book was present/readable.
2. `GNUCASH_WRITES_ENABLED=false` was verified in Compose-resolved runtime config and `/api/health`.
3. Validate/create/patch write endpoints returned read-only/write-disabled 403 responses.
4. Accounts, account detail, transactions, transaction detail, reports summary, search/filter, and CSV export worked through the API.
5. No evidence indicates that Phase 77 wrote to the GnuCash book.

## Product consistency

The Phase 77 evidence preserves the intended product model:

- read-only by default;
- GnuCash Desktop remains the authoritative editor;
- no SaaS, production-readiness, security-audited, collaborative-accounting, or GnuCash-replacement claim;
- controlled writes remain experimental/post-MVP and disabled by default.

The failed web UI is a release-readiness problem, not a reason to expand scope or add features.

## Safety boundary

Safety boundary passed at API/runtime level:

- Compose config resolved `GNUCASH_WRITES_ENABLED: "false"` for both API and web services.
- `/api/health` returned `writes_enabled: false`.
- Write probes returned 403 with explicit disabled-write wording:
  - `POST /books/1/transactions/validate`;
  - `POST /books/1/transactions`;
  - `PATCH /books/1/transactions/nonexistent`.
- Runtime data lived under `/tmp/gnucash-web-companion-phase77`, outside git.
- No `.env`, app DB, backup, real book, secret, screenshot, token, or raw CSV export was committed.

Safety caveat: because the book was a synthetic fixture rather than a real copied personal book, this does not prove behavior on a real user book. It does prove the local Docker/API/read-only path on a disposable SQL book.

## Release/readme/docs consistency

The repository previously stated that copied/disposable-data runtime dogfood evidence was missing and blocked `v0.1.0-readonly`. Phase 77 changes that from “missing” to “attempted and partially successful”: API/runtime evidence exists, but browser dogfood failed. Release docs/status should therefore continue to block v0.1 publication until #37 is fixed and browser evidence is recorded.

`CHANGELOG.md` and `PROJECT_STATUS.md` should describe Phase 77 as a real dogfood result, not an audit-only phase.

## GitHub project hygiene

Created:

- #37 — Docker web UI redirects `/login` to itself and prevents browser dogfood.

Existing issue #25 should remain open. Phase 77 should be treated as progress toward #25, not closure, because browser/UI dogfood failed.

## Security notes

No new security issue was found beyond the existing pre-alpha limitations. The dogfood command outputs were sanitized:

- token value was not recorded;
- admin password was redacted in docs;
- no real financial screenshots or exports were committed;
- only synthetic fixture account names/descriptions were recorded;
- full real personal paths were not applicable because no real copied book was used.

The login redirect loop is availability/usability/release-readiness, not currently a data exposure finding.

## Test/CI notes

Phase 77 runtime evidence:

- Docker Compose config validation passed.
- Docker API service became healthy.
- API smoke script passed.
- Manual API dogfood checks passed.
- Browser navigation timed out due to `/login` redirect loop.

Standard checks should be recorded in the handoff after doc/status updates:

- `cd apps/api && pytest -q`
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- `git diff --check`

## Recommended next actions

1. Fix #37 with a narrow tested bugfix; do not add features.
2. Rerun the same Docker copied/disposable-book dogfood and confirm browser login/dashboard/accounts/transactions/search/export work.
3. Update #25 only after browser dogfood is successful and PM accepts the source class of dogfood book evidence.
4. If a safe real copied SQL book is available later, rerun dogfood using a redacted copied-book source outside git.
5. Keep controlled writes disabled and do not start v0.2 write planning from this phase.

## Suggested GitHub issues

Created:

- #37 — Docker web UI redirects `/login` to itself and prevents browser dogfood. Labels: `bug`, `release`, `read-only`.

Suggested but not created:

- No duplicate dogfood blocker issue. #25 remains the correct umbrella tracker.

## What not to do next

- Do not publish `v0.1.0-readonly` with the web UI login redirect loop unresolved.
- Do not close #25 based on API-only evidence.
- Do not enable `GNUCASH_WRITES_ENABLED=true` to work around dogfood issues.
- Do not expand controlled-write scope.
- Do not commit real GnuCash books, app DBs, backups, screenshots with real financial data, `.env`, tokens, secrets, or raw CSV exports.
- Do not create more audit-only phases unless explicitly requested.
