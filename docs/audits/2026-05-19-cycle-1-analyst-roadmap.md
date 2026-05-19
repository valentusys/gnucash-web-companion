# Cycle 1 Analyst Roadmap — 2026-05-19

## Резюме

Текущий baseline здоров для следующего инженерного цикла: Phase 151 завершена, `main` синхронизирован с `origin/main`, CI на последних коммитах зелёный, `v0.1.5-readonly` подготовлен, но не опубликован. Публичная read-only версия сейчас `v0.1.4-readonly`; `v0.1.5-readonly` можно публиковать только отдельной авторизованной release-фазой с повторной проверкой gate. Read-only/default safety сохраняется: `.env.example` и Docker Compose держат `GNUCASH_WRITES_ENABLED=false`, write-alpha остаётся post-MVP/test-fixture-only, production writes не заявлены. Основной риск цикла — не размыть v0.1 read-only ценность документационными/audit-only задачами и не уйти в v0.2 writes до усиления dogfood/compatibility/release evidence.

## Verdict

Ready for next engineering phase.

## Readiness

- Read-only MVP / maintenance-readiness: 90%.
- Prepared `v0.1.5-readonly` candidate readiness before publication: 95%, но publication всё ещё требует явной авторизации и повторного final gate.
- Production/security-audited readiness: 0%; проект честно остаётся pre-alpha, not production-ready, not security-audited.
- Write-alpha readiness for real/private books: 0%; controlled writes должны оставаться disabled by default и только synthetic/disposable `APP_ENV=test` scope.

## Baseline audit

### Repository state

- Branch: `main`.
- Local status: clean tracked tree, only untracked local `.hermes/` agent data.
- Latest commit: `a94a0a3 Phase 151 v0.1.5 readonly release readiness`.
- Last 10 commits are concrete release/dogfood/UX/localization work, not pure audit-loop churn:

| commit | type | user impact |
| --- | --- | --- |
| `a94a0a3` Phase 151 | release | prepared unpublished `v0.1.5-readonly` gate artifacts |
| `83a0a3f` Phase 150 | dogfood/tests | synthetic Docker/browser read-only dogfood passed |
| `c6eb9c1` Phase 149 | UX/localization | Russian coverage for recent read-only UX |
| `c69a1ac` Phase 148 | UX | `/books` self-hosting/read-only guidance |
| `5e75fed` Phase 147 | UX/accounting clarity | dashboard no-conversion/base-currency limitations clearer |
| `807ed1a` Phase 146 | UX/tests | transaction detail/split readability |
| `53e41af` Phase 145 | UX/docs/tests | transaction list/export confidence |
| `8b7a8ee` Phase 144 | UX/tests | local account-tree filtering |
| `649c566` Phase 143 | UX/tests | read-only/current-book status banner |
| `aa1477d` Phase 142 | release | published `v0.1.4-readonly` |

### Release state

- Current public read-only release: `v0.1.4-readonly`.
- Prepared but unpublished candidate: `v0.1.5-readonly`.
- GitHub releases list confirms no `v0.1.5-readonly` release exists yet.
- Recent GitHub Actions runs on `main` are successful, including Phase 151.
- Phase 151 final gate says `Ready for later authorized publish phase — prepared but unpublished`; publication must re-check clean tree, `HEAD == origin/main`, tag/release absence, green CI for release HEAD, local checks, write-disabled defaults, and sensitive hygiene.

### Safety boundary

- `.env.example` sets `GNUCASH_WRITES_ENABLED=false`.
- `docker-compose.yml` defaults API and web to `${GNUCASH_WRITES_ENABLED:-false}`.
- Phase 150 runtime dogfood verified `checks.writes_enabled=false`, hidden write UI, and disabled validate/create/patch probes returning 403.
- README/CHANGELOG/PROJECT_STATUS consistently describe controlled writes as experimental post-MVP/write-alpha, disabled by default, not production-safe, and not safe for real/private-book writes.
- Browser storage search found only theme preference in `localStorage`; no auth token storage evidence in `apps/web/src`.

### GitHub/backlog state

Open issues visible via `gh issue list`:

- #36 — remaining controlled-write v0.2 readiness gates. Keep out of this cycle unless using synthetic/disposable tests only; do not enable production writes.
- #29 — localization glossary; partially addressed by later localization phases but still open.
- #28 — markdown source readability; non-blocking, do not spend a whole cycle on docs-only cleanup.
- #22 — real GnuCash version compatibility fixtures; still meaningful read-only evidence gap.
- #17 — Russian documentation/UI localization; partially addressed, still open.
- #13 — book management UI; future/admin-only scope, must not add GnuCash data editing/upload/delete in MVP.

### Dogfood status

- Phase 150 synthetic/disposable Docker/Caddy API and headless browser dogfood passed with `GNUCASH_WRITES_ENABLED=false`.
- Latest dogfood is synthetic/disposable only; it does not establish production readiness or broad real-book readiness.
- Earlier personal copied-book dogfood exists in Phase 116, but current recent UX changes have only synthetic dogfood evidence.

### Security/auth notes

- README and release docs avoid security-audited claims.
- Auth cookie is documented as httpOnly; Phase 150 browser dogfood confirmed auth cookie not readable from `document.cookie`.
- No auth token localStorage/sessionStorage usage was found in current frontend source search; only theme storage uses localStorage.
- CORS wildcard remains development default with docs warning to narrow for LAN/VPN; this is acceptable for pre-alpha if not exposed publicly.

### Money/accounting notes

- Public docs continue to state no fake currency conversion and base-currency-only reporting.
- Recent phases improved dashboard limitation clarity and transaction split/reconciliation visibility.
- Future phases should preserve Decimal/string money handling and avoid frontend `Number()` money decisions.

## Top blockers

1. No safety blocker for the next engineering cycle.
2. `v0.1.5-readonly` publication is blocked until explicit release authorization plus fresh final gate; this is a release-process blocker, not a code blocker.
3. Broad compatibility remains narrow: no automated real GnuCash Desktop-version fixture evidence yet.

## Important non-blockers

1. Open #28/#29/#17 are useful but should not drive another docs-only/audit-only loop.
2. #36 write-alpha gates should remain post-MVP and disabled by default; do not prioritize production writes in this cycle.
3. Phase 150 dogfood is synthetic-only but enough to proceed with practical read-only engineering.

## PM escalation required

No.

Reason: priorities are narrow and non-conflicting if the cycle stays read-only-first: publish/preflight prepared release only with explicit authorization, improve read-only install/compatibility/UX/dogfood evidence, and reserve Phase 10 for a release gate. No unresolved product decision requires PM arbitration. Escalate to PM only if the programmer wants to change release scope, enable production writes, add book upload/delete/editing, expose public-internet deployment claims, or use private financial data.

## План на 10 фаз PM→программист

Этот план предназначен для прямой передачи программисту без отдельного ПМ. Все фазы должны сохранять `GNUCASH_WRITES_ENABLED=false` по умолчанию, не включать production writes, не коммитить `.env`, app DB, GnuCash books, backups, screenshots/exports with private data, tokens, keys, certs, or private paths. Документы обновлять только как поддержку фактических изменений.

## Phase 1 — v0.1.5-readonly publish gate or blocked evidence

- goal: Завершить уже подготовленный `v0.1.5-readonly` релизный шаг: либо опубликовать pre-release после явной авторизации Val и повторного gate, либо записать `BLOCKED — authorization absent` без публикации.
- scope: Проверить clean `main`, `HEAD == origin/main`, отсутствие tag/release `v0.1.5-readonly`, зелёный CI на текущем HEAD, backend/frontend/Docker checks, `GNUCASH_WRITES_ENABLED=false`, sensitive tracked-file hygiene; при наличии явной авторизации создать annotated tag и GitHub pre-release из существующих notes; синхронизировать release/status/handoff.
- non-goals: Не менять product code; не расширять release scope; не публиковать без явной авторизации; не публиковать package/image/binary; не трогать write-alpha.
- acceptance criteria: Есть один из двух исходов: опубликованный честный `v0.1.5-readonly` pre-release с publication evidence, либо документированный blocked gate без tag/release; README/PROJECT_STATUS/CHANGELOG отражают фактический исход.
- safety checks: `GNUCASH_WRITES_ENABLED=false`; no tracked private data; no production/security-audit claims; release notes keep pre-alpha/read-only wording.
- verification: `gh run list`, tag/release absence or presence according to outcome, backend targeted/full tests as needed, frontend check/auth-routes/build, Docker Compose config, `git diff --check`, sensitive scan.
- expected artifacts: `docs/release/v0.1.5-readonly-publication-evidence.md` or `docs/release/v0.1.5-readonly-blocked-gate.md`, updated `PROJECT_STATUS.md`, `README.md`, `CHANGELOG.md`, `docs/handoff/phase-152.md`.

## Phase 2 — Fresh-clone Docker install smoke

- goal: Prove a clean operator can run the read-only app from a fresh checkout with synthetic/disposable data and documented dummy secrets.
- scope: Add/adjust a reproducible smoke script or documented command path for clean clone/setup; run Docker Compose against copied synthetic fixture; verify login, health, books, dashboard, accounts, transactions, CSV export, scheduled page, hidden write UI, disabled write probes.
- non-goals: No production deployment hardening claim; no public internet exposure; no real/private book; no package/image publication.
- acceptance criteria: A clean-machine/fresh-clone smoke pass is documented with exact commands and redacted/safe outputs; failures become concrete bug fixes in the same phase, not docs-only excuses.
- safety checks: Use synthetic fixture only; keep `.env` untracked; keep writes disabled; no screenshots/raw CSV/app DB/book backups committed.
- verification: Docker Compose config, Docker startup, API smoke, browser dogfood, write-disabled probes, no-artifact check, clean tracked tree except intended docs/scripts/tests.
- expected artifacts: `docs/dogfood/phase-153-fresh-clone-docker-smoke.md`, optional smoke helper tests, `docs/handoff/phase-153.md`, status/changelog updates.

## Phase 3 — GnuCash compatibility fixture path v5

- goal: Move #22 forward with safe, automated compatibility evidence that does not rely on private books or unsupported claims.
- scope: If `gnucash`/`gnucash-cli` is available or can be installed safely in disposable CI/local environment, generate a synthetic Desktop-created SQLite fixture and validate read-only service paths; otherwise improve the tooling probe and record a precise blocked result. Update compatibility matrix honestly.
- non-goals: No broad all-version compatibility claim; no PostgreSQL/MySQL/MariaDB/XML support claim unless actually tested; no private book scanning; no Desktop write support.
- acceptance criteria: Either one new Desktop-generated synthetic fixture path is validated by tests, or a better reproducible blocker artifact explains exactly what tooling is missing and how to run it later.
- safety checks: Fixture must be synthetic/disposable; collector must redact paths and exclude account names/descriptions/amounts from metadata; writes disabled by default.
- verification: Fixture generation/probe tests, read-only integration tests over fixture if generated, checksum/no-mutation check, compatibility docs review.
- expected artifacts: `docs/gnucash-compatibility.md`, `docs/gnucash-version-fixture-plan.md`, optional synthetic fixture/tooling scripts/tests, `docs/handoff/phase-154.md`.

## Phase 4 — Multi-book read-only operator UX slice

- goal: Advance #13 without adding dangerous book management: make configured-book visibility and access problems clearer for self-hosted operators.
- scope: Improve `/books` and backend metadata for read-only diagnostics such as inaccessible/default/missing-file status, current/default explanation, and safe next actions; add tests for unauthorized/archived/missing/default states.
- non-goals: No upload, delete, registry edit, default-changing UI, direct GnuCash file browsing, collaborative/family-wallet flow, or GnuCash data writes.
- acceptance criteria: Users can understand why a configured book is unavailable or read-only without seeing private paths; unauthorized/archived books remain hidden/blocked; no management action is exposed.
- safety checks: Do not render raw `uri_or_path` or private filesystem paths; do not open GnuCash data merely to list app metadata unless already required by existing read-only route; writes disabled.
- verification: Backend metadata tests, frontend route/static checks, no local/session storage for book-sensitive state, Docker/API smoke subset.
- expected artifacts: Code/tests for read-only metadata UX, `docs/book-switcher-readonly-model.md` update if needed, `docs/handoff/phase-155.md`.

## Phase 5 — Dashboard drilldown and reporting evidence

- goal: Improve read-only usefulness by linking dashboard summary/report cards to the exact filtered transaction views behind them, while preserving accounting limitations.
- scope: Add safe drilldown links from income/expense/cashflow/recent dashboard sections to existing read-only transaction filters; ensure copy states base-currency-only/no conversion; tests pin URL parameters and no invented totals.
- non-goals: No new accounting engine, FX conversion, forecasting, write routes, or production correctness guarantee.
- acceptance criteria: Dashboard drilldowns use existing URL filters, preserve active book context, and explain limitations; transaction views and CSV export remain parity-compatible.
- safety checks: Decimal/string handling only; no frontend `Number()` money decisions for accounting logic; no fake conversion; no browser persistence of filters.
- verification: Backend report tests if API metadata changes, frontend route/static checks for links/copy, CSV parity checks where relevant.
- expected artifacts: UX/tests, `docs/money-model.md` or reports docs update if needed, `docs/handoff/phase-156.md`.

## Phase 6 — Scheduled transactions read-only clarity v2

- goal: Make scheduled/recurring transaction awareness more useful without pretending to edit or predict GnuCash schedules.
- scope: Improve `/scheduled` sorting/filtering/empty states and copy around enabled/template/auto-create metadata; add tests for safe fields and no template split leakage.
- non-goals: No scheduled transaction editing, no next-run prediction unless backed by tested GnuCash semantics, no template split amounts/accounts/memos exposure beyond current safe summary, no write paths.
- acceptance criteria: The scheduled page helps users inspect safe metadata and limitations; no private template details leak; GnuCash Desktop remains authoritative editor.
- safety checks: Safe DTO fields only; no raw SQL; no hidden write UI; no private data artifacts.
- verification: Backend tests for DTO redaction, frontend route/static checks, browser dogfood page coverage.
- expected artifacts: Scheduled route/UI/tests, `docs/scheduled-transactions.md` update, `docs/handoff/phase-157.md`.

## Phase 7 — Transaction/account mobile dogfood fix pass

- goal: Use current synthetic browser dogfood to find and fix one concrete mobile/narrow-width read-only UX pain point in account/transaction flows.
- scope: Run headless/browser checks at narrow viewport; fix overflow/touch/empty/error issue in accounts, account detail, transactions, or transaction detail; add regression checks.
- non-goals: No redesign, no heavy UI library, no screenshots with private data, no write-mode UI expansion.
- acceptance criteria: A specific mobile issue is fixed and pinned by tests; if no issue is found, add a durable narrow-viewport dogfood assertion instead of inventing a change.
- safety checks: Synthetic data only; no raw screenshots committed unless synthetic and intentionally small; writes disabled; auth remains cookie-based.
- verification: Frontend check, auth-route/static route checks, narrow-viewport browser dogfood, Docker smoke subset if UI change affects runtime.
- expected artifacts: UX/tests, `docs/dogfood/phase-158-mobile-readonly-dogfood.md`, `docs/handoff/phase-158.md`.

## Phase 8 — Russian localization completion slice for release-critical paths

- goal: Reduce partial-localization friction on the highest-value read-only paths without claiming full Russian translation.
- scope: Localize remaining visible strings for login/dashboard/accounts/transactions/books/scheduled/release-critical safety copy that were not covered by Phases 149 and earlier; update glossary only where needed.
- non-goals: No backend API localization rewrite; no full-app translation claim; no marketing copy; no docs-only phase without UI/tests.
- acceptance criteria: Key read-only paths have consistent English/Russian catalog coverage and tests; README.ru accurately says translation remains partial if any strings remain.
- safety checks: Preserve canonical English; safety terms translate consistently; do not soften pre-alpha/read-only/no-production/no-security-audit warnings.
- verification: Catalog/static route checks, frontend `npm run check`, Russian route smoke if supported, README.ru/docs consistency review.
- expected artifacts: Message catalog/UI/tests, `docs/localization.md`, `README.ru.md` if state changes, `docs/handoff/phase-159.md`.

## Phase 9 — Full release-candidate dogfood after phases 2–8

- goal: Re-run complete synthetic/disposable Docker+Caddy API and browser dogfood after all read-only changes in this cycle.
- scope: Run API smoke and browser dogfood through login, dashboard, accounts, books, scheduled, account detail, transaction filters, transaction detail, CSV export, hidden write UI, disabled write endpoints, no-artifact checks; optionally run copied-book dogfood only if Val explicitly provides a safe copied book path outside git.
- non-goals: No private directory search; no real/private data disclosure; no release publication; no write-alpha expansion.
- acceptance criteria: Dogfood PASS produces redacted evidence; if it fails, phase fixes concrete defects or records release-blocking failures for Phase 10.
- safety checks: `GNUCASH_WRITES_ENABLED=false`; only synthetic/disposable by default; copied-book optional requires explicit safe path and redacted evidence; no app DB/books/backups/screenshots/CSV exports committed.
- verification: Docker Compose config/startup, API smoke, browser dogfood, disabled write probes, no-artifact scan, sensitive tracked-file scan.
- expected artifacts: `docs/dogfood/phase-160-release-candidate-dogfood.md`, any bugfix tests, `docs/handoff/phase-160.md`.

## Phase 10 — Read-only maintenance release gate

- goal: Prepare and, only if safe and explicitly authorized, publish the next read-only maintenance pre-release after Phases 2–9; otherwise mark release `BLOCKED` with exact blockers.
- scope: Choose release tag based on actual Phase 1 outcome (`v0.1.6-readonly` if `v0.1.5-readonly` was published, or publish/refresh `v0.1.5-readonly` only if still unpublished and scope fits); prepare notes/checklist/final gate; run full local checks and GitHub CI gate; publish only with explicit Val authorization.
- non-goals: No production/stable release claim; no packages/images; no write-alpha promotion; no publishing with failed dogfood or dirty tree.
- acceptance criteria: If Phases 1–9 pass and authorization exists, GitHub pre-release is published with honest notes and evidence. If any gate fails or authorization is absent, release is not published and a `BLOCKED` gate artifact lists exact fixes.
- safety checks: `GNUCASH_WRITES_ENABLED=false`; clean tracked tree; `HEAD == origin/main`; no tag/release collision; sensitive tracked-file hygiene; no real/private data; conservative pre-alpha/read-only language.
- verification: backend full tests, frontend check/auth-routes/build, Docker Compose config, write-disabled tests, dogfood evidence review, `gh run list/watch`, tag/release checks, `git diff --check`, sensitive scan.
- expected artifacts: `docs/release/<tag>-notes.md`, `docs/release/<tag>-checklist.md`, `docs/release/<tag>-final-gate.md`, optional publication evidence or blocked gate, updated README/PROJECT_STATUS/CHANGELOG, `docs/handoff/phase-161.md`.

## Recommended next action

Give the programmer Phase 1 only first. If explicit publication authorization is not available, Phase 1 should produce a blocked release-gate artifact and then proceed to Phase 2 in the next implementation cycle; do not silently publish.

## What not to do next

- Do not run another audit-only phase.
- Do not enable `GNUCASH_WRITES_ENABLED=true` in normal/runtime deployment.
- Do not expand v0.2 write-alpha toward real/private books.
- Do not claim production readiness, audited security, broad GnuCash compatibility, or safe public-internet deployment.
- Do not create noisy GitHub issues just to show activity.
- Do not inspect private books, app DBs, backups, `.env`, screenshots, or exports.
