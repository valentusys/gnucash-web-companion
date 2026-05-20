# Phase 219 handoff — accounting/safety localization glossary applied slice

Date: 2026-05-21

## Summary

Phase 219 added a small glossary-backed EN/RU operator-safety/accounting wording slice for visible release-critical flows. The frontend now has a typed safety glossary for canonical English and preferred partial Russian wording, and static route checks pin the release-critical catalog terms used by login/health/books/transactions/export/audit-summary warnings.

The only visible copy adjustment is narrow: `/books` now presents itself as book metadata instead of broad book management, preserving the existing no upload/delete/default-changing/registry-edit boundary.

## Files changed

- `apps/web/src/lib/i18n/safety-glossary.ts`
  - Added a typed glossary catalog for read-only default, `GNUCASH_WRITES_ENABLED=false`, write-alpha disposable/test-copy boundary, not production-ready, not security-audited, no currency conversion, and GnuCash Desktop authoritative-editor terms.
  - Maps each term to the relevant catalog message keys.
- `apps/web/src/lib/i18n/messages.ts`
  - Updated `/books` EN/RU title/subtitle from broad management wording to metadata-only wording.
- `apps/web/scripts/test-auth-routes.mjs`
  - Added glossary/static checks for EN/RU canonical terms.
  - Added checks that reject affirmative production/security-audited/safe-write claims in the localization slice.
  - Kept no-`localStorage`/`sessionStorage` coverage.
- `docs/localization.md`
  - Documented Phase 219 scope, English canonical status, partial Russian status, and glossary entries.
- `CHANGELOG.md`, `PROJECT_STATUS.md`, and this handoff
  - Status synchronized.

## Verification performed

Targeted/frontend and standard verification:

- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run check` — passed.
- `cd apps/api && pytest -q` — passed (`521 passed`, warnings only from existing dependencies/tests).
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `git diff --check` — passed.

Docs link check: no dedicated docs-link-check script or package entry was found in the repo; the docs update only references existing tracked paths.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- `APP_ENV=test` gate was not changed or weakened.
- No backend API localization overhaul, product behavior change, write route/default change, PM phase, release/tag/package/image, or marketing broadening was added.
- No real/private books, app DBs, backups, `.env`, screenshots, exports, tokens, keys, certs, raw private paths, account names, memos, or amounts were committed.
- The new checks reject unsafe softened wording and new browser storage use in the localization slice.

## Follow-up risks/blockers

None blocking Phase 219.

Russian remains partial/opt-in and manually reviewed; English remains canonical. This phase does not claim full translation, backend API localization, production readiness, security audit completion, safe writes for real/private or only-copy books, or currency conversion.
