# Analyst Report — 2026-05-19

## Executive summary

Текущий `main` находится на `dac3252`, синхронизирован с `origin/main`; в рабочем дереве до этого задания был незакоммиченный черновик `docs/audits/2026-05-19-analyst-report.md`, он использован и обновлён как текущий audit/report artifact. После Phase 105 главный release/docs drift вокруг уже опубликованного `v0.1.1-readonly` исправлен: README, PROJECT_STATUS, CHANGELOG, локальные release notes и GitHub release state согласованы. Read-only safety boundary остаётся целым: `.env.example` и backend config держат `GNUCASH_WRITES_ENABLED=false`, write endpoints backend-gated до write service, targeted disabled-write tests проходят. Новых safety/release blockers в этом pass не найдено; проект готов к следующей практической read-only engineering phase, но не production-ready, не security-audited и не готов к включению write-mode. Следующие 10 фаз должны быть PM→программист, с практическими behavior/test/UX/dogfood/release artifacts, без audit-only фаз.

## Verdict

Ready for next engineering phase

Это значит: можно продолжать узкую read-only разработку после Phase 105. Это не означает production readiness, security-audited статус, broad compatibility или готовность включать `GNUCASH_WRITES_ENABLED=true`. Новый release/tag сейчас не нужен без отдельной команды Валентина.

## Top blockers

None.

## Important non-blockers

1. GitHub #38 остаётся open/blocked: copied personal-book dogfood не выполнен, потому что безопасный copied/disposable book path не предоставлен. Это evidence gap, не blocker для продолжения read-only pre-alpha engineering.
2. `.env.example` всё ещё содержит development-friendly `CORS_ORIGINS=["*"]`; это отслеживается #26 и должно стать практической deployment-safety phase, но текущие public-internet warnings достаточны для pre-alpha/LAN/VPN posture.
3. Compatibility evidence остаётся узкой: synthetic/disposable SQLite fixtures, generated metadata и safe collector procedures; broad PostgreSQL/MySQL/MariaDB/XML/all-version compatibility не заявляется.
4. Последние commits содержат много docs/planning/evidence, но это не чистая audit-only петля: внутри есть реальные read-only UX/search changes Phase 103/104, а Phase 105 была разовой correction phase.
5. Исторические release-gate/checklist artifacts до публикации `v0.1.1-readonly` могут сохранять pre-publication контекст; это допустимо, потому что текущие публичные status/notes синхронизированы.

## Last 10 commits classification

| commit | type | user impact |
| --- | --- | --- |
| `dac3252` docs: sync v0.1.1 readonly release state | release/docs | Исправляет публичную release-state правду после публикации `v0.1.1-readonly`; без product behavior change. |
| `3572adc` docs: plan phase 105 release docs correction | docs | PM/phase planning for correction; no product behavior change. |
| `a4d0415` docs: record phase 104 push evidence | docs/release | Evidence commit; also actual `v0.1.1-readonly` tag target. |
| `28c2619` docs: record phase 104 commit evidence | docs | Handoff evidence; no product behavior change. |
| `0daca5b` feat: search split memos in transactions | code/tests/docs | Read-only transaction query searches split memo text as well as descriptions; list/count/account-list/CSV parity covered. |
| `c300f44` docs: plan phase 104 | docs | PM/phase planning only. |
| `aeb0cd9` docs: record phase 103 evidence | docs | Handoff evidence; no product behavior change. |
| `dcd9f83` feat: add transaction date presets | code/tests/docs | Read-only transaction UI adds date preset links preserving active filters and CSV parity. |
| `10d8d1e` docs: plan phase 103 | docs | PM/phase planning only. |
| `bb335f8` docs: record phase 102 push evidence | docs | Handoff evidence; no product behavior change. |

## Safety boundary

Findings:

- `.env.example` keeps `GNUCASH_WRITES_ENABLED=false`.
- `apps/api/app/config.py` sets `gnucash_writes_enabled: bool = False`.
- `apps/api/app/routers/transactions.py` has `_ensure_writes_enabled(settings)` returning HTTP 403 when writes are disabled.
- Controlled write endpoints `validate_book_transaction`, `create_book_transaction`, and `patch_book_transaction` call `_ensure_writes_enabled(settings)` before `_resolve_viewable_book()`, `_require_book_edit_access()`, and `_write_service_for(book)`.
- `apps/api/tests/test_transaction_writes.py::TestWritesDisabledByDefault` asserts default false and verifies disabled validate/create/patch return 403 without constructing `_write_service_for`.
- Targeted verification in this audit: `pytest -q tests/test_transaction_writes.py::TestWritesDisabledByDefault` passed: `4 passed, 1 warning`.
- Docker Compose config validation with safe dummy env passed: `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`.
- Tracked sensitive-path scan found no suspicious tracked sensitive paths outside allowed synthetic fixtures.

No read-only safety blocker found.

## Release/docs consistency

Findings:

- README says current public pre-alpha release is `v0.1.1-readonly`, keeps pre-alpha/read-only/not-production/not-security-audited warnings, and instructs users to keep `GNUCASH_WRITES_ENABLED=false`.
- PROJECT_STATUS says “pre-alpha / v0.1.1 read-only published”, completed through Phase 105, and records the tag target `a4d04150c043ad4da3dea577b30ed7ffd2032df0`.
- CHANGELOG has `[0.1.1-readonly] - 2026-05-18`, includes Phase 103/104 read-only transaction changes, and keeps known limitations/non-claims.
- `docs/release/v0.1.1-readonly-notes.md` says the GitHub pre-release is published, states the same tag target, and keeps disabled-write/pre-alpha warnings.
- GitHub release `v0.1.1-readonly` is not draft, is prerelease, published at `2026-05-18T13:54:13Z`, and targets `a4d04150c043ad4da3dea577b30ed7ffd2032df0`.
- Current `HEAD` is `dac3252fb189bb5d742441afc733d7b3cd7d6a7b`; `origin/main` matches. `v0.1.1-readonly..HEAD` contains only Phase 105 docs/report correction commits.

Verdict on Phase 105 blocker: fixed.

## GitHub project state

GitHub CLI is available/authenticated enough for issue/release/run inspection. Per task constraints, no GitHub issues were created/closed and no releases were published.

Open issues from `gh issue list --state open --limit 50`:

- #38 — Run Phase 85 copied personal-book dogfood when safe book is available
- #36 — Track remaining controlled-write v0.2 readiness gates
- #29 — Add localization glossary for accounting terms
- #28 — Improve markdown source readability before wider announcement
- #26 — Document CORS origin narrowing for LAN/VPN deployments
- #22 — Add compatibility fixtures from real GnuCash versions
- #17 — Plan Russian documentation and UI localization
- #13 — Book management UI
- #12 — Scheduled/recurring transaction awareness
- #11 — Transaction search/filter improvements

Releases:

- `v0.1.1-readonly` — GitHub pre-release, published 2026-05-18, target `a4d04150c043ad4da3dea577b30ed7ffd2032df0`.
- `v0.1.0-readonly` — GitHub pre-release.
- `v0.0.2-prealpha` — GitHub pre-release.
- `v0.0.1-prealpha` — GitHub pre-release.

Actions:

- Latest 10 `main` CI runs listed by `gh run list --limit 10` were all `completed/success`, including `dac3252 docs: sync v0.1.1 readonly release state`.

Open-source hygiene:

- Present: `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/workflows/ci.yml`, issue templates, PR template, funding metadata.
- CI includes required-file checks, tracked sensitive-file guard, frontend checks/build, backend pytest, and Docker Compose validation.

## Dogfood status

Findings:

- Phase 78 Docker/Caddy browser dogfood on copied/disposable data passed core UI/API read-only paths and disabled-write probes with `GNUCASH_WRITES_ENABLED=false`.
- Phase 100 synthetic/disposable local Docker API smoke passed health, login/auth, books/default book, accounts, transactions, transaction detail, CSV export, reports summary, and disabled validate/create/patch probes.
- Phase 101 personal copied-book dogfood rerun remains blocked because no explicit safe copied/disposable book path was provided outside the repository. No private directories were searched and no personal-book success is claimed.
- GitHub #38 remains the correct tracker for that evidence gap.

This is acceptable for current conservative read-only pre-alpha claims. Do not convert it into broad real-book/production-readiness claims.

## Security/auth notes

Findings:

- JWT secret is not hardcoded as usable default: `Settings.jwt_secret` defaults to empty string; `.env.example` uses a placeholder and README says to replace it.
- Frontend auth route static check passed: `npm run test:auth-routes` returned `auth route checks passed`.
- The auth-route check asserts protected routes use `cookies.get('access_token')`, login sets the `access_token` cookie, `httpOnly: true` is present, logout deletes the cookie, and login does not use local/session storage.
- Search for `localStorage|sessionStorage` under `apps/web/src` found theme preference storage only (`theme.ts` and `app.html`), not auth token/session storage.
- README and SECURITY docs keep warnings: pre-alpha, not production-ready, not security-audited, test copied/disposable data first, do not expose directly to public internet.
- `CORS_ORIGINS=["*"]` remains a known development-friendly default/non-blocker with issue #26 for narrowing docs/diagnostics.
- No token values, secrets, private book paths, real screenshots, app DBs, backups, or financial exports were copied into this report.

No professional security audit is claimed.

## Money/accounting notes

Findings:

- Backend transaction filters use `Decimal` query params; core money paths use string/Decimal-style values.
- CSV export writes existing string amount fields and forwards metadata headers for limit/total/truncation.
- Reports expose base-currency-only/no-conversion limitations; no fake currency conversion claim was found in current release docs.
- Split transactions are represented honestly through split details; Phase 104 added split memo search without changing write scope.
- Phase 83 already hardened frontend money display decisions away from `Number()` on money strings; no new backend float money arithmetic was found in inspected core paths.

No money/accounting correctness blocker found in this pass.

## Recommended next action

Phase 106 — implement one narrow practical read-only backlog slice from GitHub #11, preferably reconciled/cleared transaction filtering if the underlying GnuCash metadata can be represented honestly; otherwise implement an equally narrow URL/filter UX improvement. Do not create tags/releases/packages, do not run personal-book dogfood without an explicit safe copied book path, and do not start v0.2/write-mode work.

## Suggested GitHub issues

None.

No new blocker needs an issue. Existing meaningful open issues already cover current work: #38 copied personal-book dogfood, #36 v0.2 write-readiness gates, #26 CORS origin narrowing, #22 compatibility fixtures, #17/#29 localization/glossary, #13 book management UI, #12 scheduled/recurring awareness, and #11 transaction search/filter improvements.

## What not to do next

- Do not start v0.2 controlled writes or enable `GNUCASH_WRITES_ENABLED=true` by default.
- Do not publish another release/tag/package without separate explicit Val authorization.
- Do not claim production readiness, security-audited status, hosted SaaS readiness, collaborative accounting, family-wallet positioning, broad compatibility, or safe production write mode.
- Do not run personal-book dogfood unless Val provides an explicit safe copied/disposable GnuCash SQL book path outside the repository and confirms it is not the live authoritative book.
- Do not continue audit-only churn; move to practical read-only engineering.

## План на 10 фаз PM→программист

Полный roadmap также записан отдельно: `/home/val/.hermes/logs/gnucash-web-companion/analyst-pm10-20260519-070631/analyst-10-phase-roadmap.md`.

## Phase 1 — Reconciled/cleared transaction filters
- Goal: Добавить практический read-only фильтр транзакций по состоянию split/transaction status, если доступные GnuCash поля позволяют это сделать честно без догадок.
- PM brief focus: Узко продолжить GitHub #11: только read-only state/reconciled filtering, без write-mode, импорта, локального хранения фильтров или нового release.
- Programmer work: Инвентаризировать доступные поля piecash для cleared/reconciled/void-подобного статуса; добавить backend query parameter, service-layer filtering/count/export parity и UI control только для подтверждённых значений.
- Acceptance criteria: List/count/account-list/CSV export используют один контракт; UI показывает фильтр/подсказку; unsupported values не фейкуются; существующие фильтры сохраняются.
- Safety checks: `GNUCASH_WRITES_ENABLED=false` не меняется; write endpoints не трогаются; реальные книги/экспорты/скриншоты не коммитятся.
- Verification: Backend tests, frontend route/static checks, targeted disabled-write tests, Docker Compose config validation.
- Expected artifacts: Code/tests, `docs/handoff/phase-106.md`, `PROJECT_STATUS.md`, optional #11 evidence update.

## Phase 2 — Filter URL presets and reset UX
- Goal: Улучшить UX поиска/фильтров транзакций через shareable URL presets/reset behavior без localStorage/sessionStorage.
- PM brief focus: Продолжить #11 через поведение в URL: clear all, predictable filter preservation, no browser storage.
- Programmer work: Добавить явную кнопку/ссылку “Clear filters”, улучшить preset URL construction, проверить сохранение параметров при навигации и CSV export.
- Acceptance criteria: Пользователь может сбросить фильтры одним действием; параметры не теряются неожиданно; CSV export получает тот же query string.
- Safety checks: Не хранить поисковые строки, account IDs или суммы в localStorage/sessionStorage; write UI behavior не менять.
- Verification: Frontend route/static checks, backend query validation where needed, auth-route checks, targeted disabled-write tests.
- Expected artifacts: UX code/tests, updated `docs/transactions-filters.md`, `docs/handoff/phase-107.md`, `PROJECT_STATUS.md`.

## Phase 3 — Account detail transaction filter parity
- Goal: Довести account detail transaction list до той же read-only filter/export семантики, что и общий transaction list.
- PM brief focus: Account page should filter/search its own transactions consistently, без новых write/import/admin workflows.
- Programmer work: Проверить текущую account detail страницу; добавить/синхронизировать filter controls; обеспечить count/list parity and links back to transaction detail.
- Acceptance criteria: Account detail supports approved filters; pagination/counts correct; empty states explain active filters; no cross-account leakage.
- Safety checks: Book access boundary remains enforced; archived/unauthorized books hidden/blocked; no direct GnuCash file access from frontend.
- Verification: Backend account transaction tests; frontend route/static checks; multi-book access-boundary targeted tests.
- Expected artifacts: Account detail UX/tests, `docs/handoff/phase-108.md`, `PROJECT_STATUS.md`, possible #11 evidence update.

## Phase 4 — Scheduled/recurring transaction awareness
- Goal: Добавить честное read-only awareness для scheduled/recurring transactions without editing, if safe metadata is available.
- PM brief focus: Address #12 as read-only visibility/limitation, not scheduling editor.
- Programmer work: Инвентаризировать metadata support; expose a conservative read-only endpoint/page or documented unsupported state; add UI copy that editing remains in GnuCash Desktop.
- Acceptance criteria: If supported, UI lists safe summary fields only; if unsupported, UI clearly says not available; no fake next-run calculations.
- Safety checks: Do not modify scheduled transaction tables; do not expose raw SQL/private data; no fake accounting predictions.
- Verification: Synthetic fixture or unsupported-path tests, frontend empty/limitation checks, disabled-write regression.
- Expected artifacts: Read-only scheduled/recurring awareness code/tests or explicit unsupported UX, `docs/handoff/phase-109.md`, docs limitation update, #12 evidence update.

## Phase 5 — Books metadata UX hardening
- Goal: Улучшить `/books` как read-only metadata/status page for accessible independent books.
- PM brief focus: Safe subset of #13: no upload, deletion, registry editing, or multi-user admin UI.
- Programmer work: Add clearer current/default markers, base currency/storage/read-only badges, inaccessible/empty states, and safe book-specific links.
- Acceptance criteria: `/books` useful on single-book and multi-book fixtures; safe links preserve book context; no management controls exposed.
- Safety checks: Access model remains authoritative; frontend never reads GnuCash directly; no family-wallet/collaborative framing.
- Verification: Multi-book API tests, frontend route/static checks, auth-route checks, unauthorized/archived route tests.
- Expected artifacts: `/books` UX/tests, `docs/book-switcher-readonly-model.md` update if needed, `docs/handoff/phase-110.md`, `PROJECT_STATUS.md`.

## Phase 6 — Compatibility fixture v4 safe Desktop evidence
- Goal: Получить следующий practical compatibility artifact without real/private books.
- PM brief focus: Move #22 forward with synthetic/disposable Desktop-generated SQLite fixture evidence if tools are available.
- Programmer work: Check `gnucash` tooling availability; generate or document disposable fixture; collect only redacted metadata; add collector/matrix tests.
- Acceptance criteria: Docs distinguish generated/piecash/Desktop evidence; no broad all-version claims; metadata excludes private/financial details.
- Safety checks: Do not search private directories; do not commit real books/backups; only synthetic fixture artifacts allowed.
- Verification: Collector tests, fixture integrity/no-mutation checks, safe tracked-file scan, read-only fixture tests if produced.
- Expected artifacts: Compatibility metadata/tests/docs, `docs/handoff/phase-111.md`, `PROJECT_STATUS.md`, #22 evidence update.

## Phase 7 — LAN/VPN deployment safety behavior
- Goal: Превратить CORS/public-exposure caveat into practical operator-facing behavior/tests, not just prose.
- PM brief focus: Address #26 with safe diagnostics/warnings while preserving local dev defaults.
- Programmer work: Add health/startup diagnostic warning when wildcard CORS is used outside development-like env; document LAN/VPN origin examples; add non-sensitive warning tests.
- Acceptance criteria: Operators see clear non-secret warning for risky posture; `.env.example` remains usable; docs provide exact examples.
- Safety checks: Do not log secrets/JWT/passwords/book full private paths; no public-internet readiness claim; writes remain disabled.
- Verification: Backend config/health tests, Docker Compose config validation, log redaction tests if logging changes, auth checks.
- Expected artifacts: Diagnostic behavior/tests, deployment doc update, `docs/handoff/phase-112.md`, `PROJECT_STATUS.md`, #26 evidence update.

## Phase 8 — Russian localization glossary and narrow UI slice
- Goal: Улучшить RU localization in a controlled way without making Russian canonical.
- PM brief focus: Combine #17/#29: glossary plus one visible UI slice, warnings preserved.
- Programmer work: Add accounting/safety glossary; localize one high-value read-only UI area such as transaction filters/export copy; ensure terminology consistency.
- Acceptance criteria: RU strings consistent; language toggle stable; docs state translation is partial; no mistranslated write-mode safety claims.
- Safety checks: Do not weaken Russian warnings; no new auth/session storage; no product-scope promises.
- Verification: Frontend route/static checks for catalog keys, docs link checks if available, auth-route checks.
- Expected artifacts: Glossary/doc update, localized UI strings/tests, `docs/handoff/phase-113.md`, `PROJECT_STATUS.md`, #17/#29 evidence update.

## Phase 9 — Synthetic browser dogfood refresh
- Goal: Rerun current browser/UI dogfood pass using synthetic/disposable data after UX/filter changes.
- PM brief focus: Dogfood artifact only on generated/synthetic data; no personal books unless Val separately provides explicit copied path.
- Programmer work: Start local Docker/Caddy with safe env; run browser/API smoke across login, dashboard, accounts, books, transactions filters, account detail, CSV export, disabled write probes; record redacted evidence.
- Acceptance criteria: Core read-only UI paths pass; write UI hidden/disabled; CSV export/filter parity checked; failures become concrete bugs.
- Safety checks: No real/private book data, screenshots, CSV exports, app DB, `.env`, secrets, tokens or private paths committed.
- Verification: Docker Compose config, smoke script, browser route checks, disabled validate/create/patch probes return 403.
- Expected artifacts: `docs/dogfood/phase-114-synthetic-browser-dogfood.md`, narrow bugfix/tests if needed, `docs/handoff/phase-114.md`, `PROJECT_STATUS.md`.

## Phase 10 — v0.1.2-readonly maintenance release prep, no publish
- Goal: Prepare a conservative release artifact for possible `v0.1.2-readonly` if Phases 1–9 produced meaningful read-only improvements.
- PM brief focus: Release-prep/gate artifact only; do not publish tag/release/package without separate explicit Val authorization.
- Programmer work: Summarize completed artifacts, update changelog/release notes/checklist, run appropriate checks, decide “ready for authorized publish” vs “more fixes required”.
- Acceptance criteria: Release notes honest: pre-alpha, read-only default, not production-ready, not security-audited, no personal-book dogfood claim unless explicitly done later.
- Safety checks: No tag, GitHub release, package publish, write-mode enablement, v0.2 scope, or private data; `GNUCASH_WRITES_ENABLED=false` remains posture.
- Verification: Backend tests, frontend check/auth-routes/build, Docker Compose config, GitHub Actions state, sensitive tracked-file scan, disabled-write targeted tests.
- Expected artifacts: `docs/release/v0.1.2-readonly-notes.md`, `docs/release/v0.1.2-readonly-checklist.md`, optional final-gate doc, `docs/handoff/phase-115.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`.

## Checks run in this audit

- `git status --short && git log --oneline -20`
- `gh issue list --state open --limit 50`
- `gh release list --limit 10`
- `gh run list --limit 10`
- Repo/docs/code searches for `GNUCASH_WRITES_ENABLED`, `gnucash_writes_enabled`, `localStorage`, `sessionStorage`, `httpOnly`, CORS, Decimal/money paths
- Read inspections: README, PROJECT_STATUS, CHANGELOG, `.env.example`, release notes, existing analyst report, API config/router/tests, docs/dogfood/release/audits/handoff listings
- `pytest -q tests/test_transaction_writes.py::TestWritesDisabledByDefault`
- `npm run test:auth-routes`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- `git status --short --branch; git rev-parse HEAD; git rev-parse origin/main; git rev-list -n 1 v0.1.1-readonly; git log --oneline v0.1.1-readonly..HEAD; git diff --stat v0.1.1-readonly..HEAD`
- `gh release view v0.1.1-readonly --json tagName,targetCommitish,isPrerelease,isDraft,publishedAt,name,url`
- tracked sensitive-path scan via `git ls-files` with safe path-name filtering

Full heavy suites were not rerun because this task is report/roadmap generation only, recent GitHub CI for current `main` is green, and targeted disabled-write/auth/compose checks cover the main audit risk areas.
