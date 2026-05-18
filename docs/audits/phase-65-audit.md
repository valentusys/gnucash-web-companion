# Phase 65 Audit — Test Coverage Audit

Date: 2026-05-18

## Executive summary

Phase 65 audited whether the current test suite supports the repository's maturity claims. The automated suite is credible for the current pre-alpha/read-only posture: backend tests cover authentication, app metadata, read-only GnuCash fixture access, reports, filters/export, multi-book access, compatibility fixture limits, disabled-write gating, and experimental write safety on disposable fixtures. Frontend coverage is intentionally lighter: Svelte type checks, build, and a static route/safety script cover auth-cookie, write-UI gating, localization, book-switcher, and filter/export wiring, but there is no committed browser E2E test for the full UI journey. That gap is already release-relevant through #25: v0.1 publication still needs copied/disposable-data runtime smoke/dogfood evidence.

## Verdict

Ready to continue pre-alpha; not enough evidence to publish `v0.1.0-readonly` yet.

The automated test coverage supports the current README/PROJECT_STATUS claim that this is pre-alpha / MVP in progress and read-only by default. It does not support any stronger claim such as production-ready, security-audited, broad GnuCash compatibility, or completed v0.1 runtime dogfood.

## Blockers

No new Phase 65 test-coverage blocker was found beyond the existing v0.1 publication blockers.

Carried-forward release blockers:

1. #24 — conservative `v0.1.0-readonly` release notes are still required before publication.
2. #25 — copied/disposable-data runtime smoke/dogfood evidence is still required before publication.

## Important non-blockers

1. Frontend has no committed browser E2E/screenshot/regression test for login → dashboard → accounts → transactions → CSV. This is acceptable for the current pre-alpha posture only because README does not claim production maturity and #25 requires runtime dogfood evidence before v0.1 publication.
2. CI runs the full backend suite, frontend check/auth-routes/build, sensitive-file checks, and Docker Compose config validation. It does not run a live Docker smoke deployment; that remains a manual/runtime gate tracked by #25.
3. Compatibility coverage remains limited to documented synthetic SQLite fixture paths and generated/disposable fixture coverage. This remains acceptable only while broad compatibility is not claimed and #22 stays open.
4. Experimental write-enabled tests exist and use disposable fixtures, but this must not be interpreted as safe write-mode approval. Writes remain post-MVP, experimental, and disabled by default.

## Audit scope and evidence inspected

Inspected:

- `AGENTS.md`
- `PROJECT_STATUS.md`
- `README.md`
- `CHANGELOG.md`
- `docs/release/v0.1.0-readonly-plan.md`
- `docs/release/v0.1.0-readonly-checklist.md`
- `docs/release/v0.0.2-prealpha-notes.md`
- `docs/release/v0.0.2-prealpha-checklist.md`
- latest handoff: `docs/handoff/phase-64.md`
- roadmap file: `/home/val/.hermes/cache/documents/doc_524e3283b5e8_auditor-roadmap-56-75.txt`
- `.github/workflows/ci.yml`
- `.env.example`
- `docker-compose.yml`
- `apps/api/app/config.py`
- `apps/api/tests/`
- `apps/web/package.json`
- `apps/web/scripts/test-auth-routes.mjs`
- `scripts/smoke/read-only-api-smoke.py`
- open GitHub issues via `gh issue list`

Observed test inventory:

- Backend collection: `282 tests collected`.
- Backend test files include auth, models, services, accounts, transactions, reports, health, fixture integration, multi-currency reports, multi-book access, transaction export, compatibility fixtures, write lock, disabled-write gating, write integration, and backup restore.
- Frontend scripts include `npm run check`, `npm run test:auth-routes`, and `npm run build`.
- CI has foundation/sensitive-file checks, frontend checks, backend tests, and Docker Compose config validation.

## Claim → Test coverage → Gap

| Claim | Test coverage | Gap / audit result |
| --- | --- | --- |
| MVP is read-only by default | `Settings.gnucash_writes_enabled` default is `False`; `.env.example` and `docker-compose.yml` default `GNUCASH_WRITES_ENABLED=false`; `tests/test_transaction_writes.py::TestWritesDisabledByDefault`; smoke script probes disabled write endpoints | OK for automated/backend coverage. Must keep release docs honest that write code exists but is disabled/experimental. |
| Write endpoints are disabled when writes are disabled | Backend tests cover validate/create/patch 403 responses and assert write service construction is not reached; smoke script also probes validate/create/patch against a running deployment | OK. This supports the current read-only-by-default safety claim. |
| Experimental write-enabled code uses disposable/test coverage | `tests/test_write_integration.py`, `tests/test_backup_restore.py`, `tests/test_write_lock.py`, and write tests use tmp/disposable fixtures and fakes | OK for post-MVP experimental coverage only. Does not justify safe write-mode or v0.1 write-scope claims. |
| Read-only GnuCash fixture access works | `tests/test_integration_fixture.py`, `tests/test_gnucash_book.py`, `tests/test_accounts.py`, `tests/test_transactions.py`, `tests/test_reports.py` | OK for synthetic fixture paths. Not proof for arbitrary real-world books. |
| CSV export is read-only and filter-aware | `tests/test_transaction_export.py`, transaction filter/export backend tests, frontend static route checks for preserving filters in export URLs | OK for API and static frontend wiring. No browser download E2E; acceptable as pre-alpha with #25 runtime gate. |
| Transaction search/filter behavior is conservative | Backend transaction tests and export tests cover invalid/inverted ranges; frontend static script checks date/amount client-side validation and URL preservation | Mostly OK. No browser E2E; keep #11 open for future improvements. |
| Multi-currency reporting avoids fake conversion | `tests/test_multicurrency_reports.py`; docs state limitations/no fake conversion | OK for tested fixture scenarios; limitations remain documented. |
| Multi-book foundation uses accessible independent books | `tests/test_multi_book_access.py`; frontend auth-route script checks accessible fallback/book switcher wording and no collaborative/family-wallet framing | OK for foundation. Full book-management UI remains out of v0.1 and tracked separately (#13). |
| Auth uses httpOnly cookies, not browser storage | Backend auth tests; frontend `test-auth-routes.mjs` asserts httpOnly cookie usage and rejects localStorage/sessionStorage for auth routes/source files | OK for current static/runtime unit coverage. This is not a professional security audit. |
| Frontend protected routes and write UI are safely gated by default | `npm run test:auth-routes` checks protected prefixes, redirects, `GNUCASH_WRITES_ENABLED` gating, `/transactions/new` redirect when disabled, and warning/acknowledgement when enabled | OK for static route checks. No browser E2E; #25 remains release blocker for runtime evidence. |
| Docker Compose config validates | `docker compose config --quiet` in CI and required local checks; `docker-compose.yml` defaults writes to false and requires JWT secret | OK for config syntax/default safety. Does not prove live deployment works. |
| CI validates core release gates | `.github/workflows/ci.yml` runs required-file/sensitive-file checks, backend pytest, frontend check/auth-routes/build, and Compose validation | OK for automated gates. CI does not perform live Docker smoke/dogfood, which is tracked by #25. |
| No real financial/secrets artifacts are tracked | CI foundation sensitive-file check, `.gitignore`, and manual audit scope | OK as an automated guard, but exact real-data detection remains pattern-based. Continue manual review before release. |
| Broad GnuCash compatibility is not claimed | Compatibility tests/docs exist, #22 remains open | OK because claims are conservative. Not proof of broad version/backend compatibility. |
| Project is production-ready/security-audited | No such claim should exist; tests are not sufficient for those claims | OK because README/release docs explicitly avoid those claims. |

## Product consistency

The test suite supports the current product positioning: pre-alpha, self-hosted, read-only-first, not a GnuCash replacement, not SaaS, and not collaborative accounting. Tests and static frontend checks specifically guard the default read-only posture and independent-book framing.

## Safety boundary

- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- `Settings.gnucash_writes_enabled: bool = False` remains the backend default.
- Disabled-write route tests cover validate/create/patch and assert the write service is not constructed while writes are disabled.
- Write-enabled tests are explicitly experimental/post-MVP and use disposable/fake/tmp fixtures.
- No Phase 65 evidence supports enabling writes by default or expanding write scope.

## Release/readme/docs consistency

README, PROJECT_STATUS, CHANGELOG, and release planning docs currently describe the maturity level more conservatively than the tests could overclaim. That is correct. The main release gap is not missing backend unit coverage; it is missing copied/disposable-data runtime smoke/dogfood evidence and conservative v0.1 notes, already tracked by #24/#25.

## GitHub project hygiene

Open issues reviewed:

- #24 — conservative `v0.1.0-readonly` release notes blocker.
- #25 — copied/disposable-data runtime smoke/dogfood gate blocker.
- #22 — real GnuCash version compatibility fixture coverage.
- #26 — CORS origin narrowing visibility.
- #11/#12/#13/#17 — non-blocking future/read-only/post-MVP backlog items.

No new issue is required for Phase 65. The frontend/no-live-smoke gap should be recorded on #25 instead of creating a duplicate noisy issue.

## Security notes

This was a test coverage audit, not a security audit. The suite has useful auth-cookie/static safety checks and sensitive-file CI checks, but that does not support any `security-audited` claim. Phase 66 is the dedicated security-posture audit.

## Test/CI notes

CI meaningfully covers the current pre-alpha claims:

- foundation file presence;
- tracked sensitive-file patterns;
- backend pytest suite;
- frontend Svelte check;
- frontend static auth-route/safety checks;
- frontend production build;
- Docker Compose config validation.

The local Phase 65 verification should run the full backend suite, frontend check/auth-routes/build, Compose config validation, and `git diff --check`.

## Recommended next actions

1. Keep #24 and #25 as blockers before any `v0.1.0-readonly` publication.
2. Update #25 with the Phase 65 finding that automated tests are credible but do not replace copied/disposable-data runtime smoke/dogfood evidence.
3. Do not create a duplicate issue for frontend E2E unless PM chooses to split it from #25 in a later phase.
4. In any future release notes, distinguish automated test coverage from live deployment/dogfood evidence.
5. Continue Phase 66 separately; do not start it from Phase 65.

## Suggested GitHub issues

Created: none.

Updated/suggested:

- Update #25 with the Phase 65 test-coverage audit result and keep it open as the release-blocking runtime evidence gate.

No noisy/fake issue should be created just to satisfy the audit phase.

## What not to do next

- Do not publish `v0.1.0-readonly` from this phase.
- Do not mark v0.1 ready merely because backend/frontend/Compose tests pass.
- Do not treat write-enabled disposable fixture tests as approval for real-book write mode.
- Do not add product features or expand write scope in this audit phase.
- Do not start Phase 66 automatically.
