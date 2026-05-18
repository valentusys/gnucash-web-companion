# Analyst Report — 2026-05-19

## Executive summary

Проект остаётся в целом безопасным по read-only границе: `GNUCASH_WRITES_ENABLED=false` стоит в `.env.example`, backend default — `False`, write endpoints проверяют feature flag до доступа к write service, и targeted disabled-write tests проходят. Существенных признаков включённого write-mode, frontend auth storage в local/sessionStorage или закоммиченных приватных данных в tracked paths не найдено. Главная проблема текущего состояния — release/docs drift вокруг уже опубликованного `v0.1.1-readonly`: GitHub release существует и tag указывает на текущий HEAD, но README всё ещё называет текущим публичным релизом `v0.1.0-readonly`, а опубликованные release notes для `v0.1.1-readonly` начинаются как draft/prep artifact and “does not authorize publication”. Это не safety blocker GnuCash-записи, но это release-facing blocker: публичные артефакты вводят в заблуждение о состоянии релиза.

## Verdict

Ready after blockers fixed

## Top blockers

1. `v0.1.1-readonly` уже опубликован как GitHub pre-release и локальный tag, но опубликованные release notes всё ещё являются draft notes: строка заголовка `# v0.1.1-readonly Draft Release Notes`, текст “does not create a git tag, publish a GitHub release, or authorize publication”, и раздел “Publication status: Not published yet”. Это публично неверно после фактической публикации.
2. README/публичная release-readiness секция устарела: `README.md` называет current public pre-alpha release `v0.1.0-readonly`, хотя `gh release list` показывает latest `v0.1.1-readonly`, а `git tag --list 'v0.1.1-readonly'` возвращает tag.
3. Scope релиза `v0.1.1-readonly` не синхронизирован с tag target: tag указывает на `a4d0415` после Phase 104, а `docs/release/v0.1.1-readonly-notes.md` описывает maintenance value в основном до Phase 96 и не отражает Phase 103/104 read-only transaction filter/search changes. Нужно либо честно обновить notes/README/status под фактический tag, либо явно зафиксировать, что Phase 103/104 included as extra read-only changes.

## Important non-blockers

1. Read-only safety boundary на проверенных путях intact: backend default false, `.env.example` false, Docker Compose default false, write routes gated before `_write_service_for()`.
2. Targeted disabled-write backend tests passed: `4 passed, 1 warning` for `tests/test_transaction_writes.py::TestWritesDisabledByDefault`.
3. Frontend auth/write-route static checks passed: `npm run test:auth-routes` returned `auth route checks passed`.
4. Docker Compose config validation passed with dummy safe env: `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`.
5. `localStorage` use found only for theme preference (`apps/web/src/lib/theme.ts`, `apps/web/src/app.html`), not auth token storage.
6. GitHub Actions latest 10 runs on `main` are `completed/success`.
7. GitHub #38 remains honestly open/blocked for personal copied-book dogfood; this is a known limitation, not a new regression.
8. Open-source hygiene files exist: `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, issue templates, funding metadata, and CI workflow.

## Last 10 commits classification

| commit | type | user impact |
| --- | --- | --- |
| `a4d0415` docs: record phase 104 push evidence | docs | No product behavior change; records pushed evidence for Phase 104. Also current `v0.1.1-readonly` tag target. |
| `28c2619` docs: record phase 104 commit evidence | docs | No product behavior change; handoff evidence update. |
| `0daca5b` feat: search split memos in transactions | code/tests/docs | Read-only transaction query now searches split memos as well as descriptions; tests and helper copy updated. |
| `c300f44` docs: plan phase 104 | docs | PM/phase planning only. |
| `aeb0cd9` docs: record phase 103 evidence | docs | No product behavior change; handoff evidence update. |
| `dcd9f83` feat: add transaction date presets | code/tests/docs | Read-only transaction UI adds date preset links preserving filters and CSV parity. |
| `10d8d1e` docs: plan phase 103 | docs | PM/phase planning only. |
| `bb335f8` docs: record phase 102 push evidence | docs | No product behavior change; handoff evidence update. |
| `7a8ed63` feat: refresh compatibility fixture provenance | code/tests/docs | Safe synthetic/disposable compatibility provenance improved; no broad compatibility claim. |
| `3dce768` docs: plan phase 102 | docs | PM/phase planning only. |

Recent work is mixed practical read-only engineering plus planning/evidence docs. It is not a pure audit loop, but release documentation is now stale after publication.

## Safety boundary

Findings:

- `.env.example` line 26 keeps `GNUCASH_WRITES_ENABLED=false`.
- `apps/api/app/config.py` sets `gnucash_writes_enabled: bool = False`.
- `docker-compose.yml` passes `GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}` to API and web services.
- `apps/api/app/routers/transactions.py` defines `_ensure_writes_enabled(settings)` and raises HTTP 403 when writes are disabled.
- The validate/create/patch controlled-write endpoints call `_ensure_writes_enabled(settings)` before `_resolve_viewable_book()`, `_require_book_edit_access()`, and `_write_service_for(book)`.
- `apps/api/tests/test_transaction_writes.py::TestWritesDisabledByDefault` asserts default false and proves validate/create/patch return 403 without constructing `_write_service_for`.
- Targeted verification run during this audit: `pytest -q tests/test_transaction_writes.py::TestWritesDisabledByDefault` passed with `4 passed, 1 warning`.
- No evidence was found that write mode is enabled by default.

No read-only safety blocker found.

## Release/docs consistency

Findings:

- Local branch: `main`; local and origin are in sync (`git rev-list --left-right --count main...origin/main` returned `0 0`).
- Working tree was clean before this audit report write (`git status --short --branch` showed `## main...origin/main`).
- GitHub releases list shows latest pre-release `v0.1.1-readonly` published at `2026-05-18T13:54:13Z`, followed by `v0.1.0-readonly`, `v0.0.2-prealpha`, and `v0.0.1-prealpha`.
- Local tag `v0.1.1-readonly` exists and points to commit `a4d0415` (`docs: record phase 104 push evidence`).
- GitHub release `v0.1.1-readonly` target commit is also `a4d04150c043ad4da3dea577b30ed7ffd2032df0`.
- `README.md` still says current public pre-alpha release is `v0.1.0-readonly`; this is stale.
- `docs/release/v0.1.1-readonly-notes.md` still says it is a draft and “Not published yet”; GitHub release body uses the same stale text.
- `PROJECT_STATUS.md` says completed through Phase 104 and records v0.1.1 preparation/gate/dry-run, but the section around Phase 99/100 also says publication remained unauthorized/absent. Current reality is publication exists; status should be updated.
- `CHANGELOG.md` has Unreleased entries through Phase 104 and historical release sections, but no `[0.1.1-readonly]` release section. That is not fatal by itself, but it contributes to release-state drift.

This is the main blocker category.

## GitHub project state

GitHub CLI is authenticated as `valentusys`. No issues were created or closed per task constraints.

Open issues listed by `gh issue list --state open --limit 50`:

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

- `v0.1.1-readonly` — Pre-release, published 2026-05-18, but notes are stale draft notes.
- `v0.1.0-readonly` — Pre-release.
- `v0.0.2-prealpha` — Pre-release.
- `v0.0.1-prealpha` — Pre-release.

Actions:

- Latest 10 `main` CI runs are all `completed/success`.

## Dogfood status

Findings:

- Phase 78 Docker/Caddy browser dogfood on copied/disposable synthetic data passed core UI/API read-only paths and disabled-write probes with `GNUCASH_WRITES_ENABLED=false`.
- Phase 100 synthetic/disposable local Docker API smoke passed on current `main`: health, login/auth, books/default book, accounts, transactions, transaction detail, CSV export, reports summary, and disabled validate/create/patch write probes.
- Phase 101 personal copied-book dogfood rerun is honestly blocked because no explicit safe copied/disposable book path was provided outside the repository. No private directories were searched, and no personal book pass is claimed.
- GitHub #38 remains open for this copied personal-book dogfood gap.

This is acceptable for pre-alpha/read-only claims if release notes remain honest. It is not acceptable to claim personal-book dogfood success or broad real-world readiness.

## Security/auth notes

Findings:

- JWT secret is not hardcoded as a usable default: `apps/api/app/config.py` defaults to empty string, and `apps/api/app/services/auth.py` rejects empty/change-me placeholder values via `require_configured_jwt_secret()`.
- Frontend login sets token in `access_token` cookie with `httpOnly: true`, `sameSite: 'lax'`, `path: '/'`, `maxAge`, and `secure` dependent on HTTPS protocol.
- Search for `localStorage|sessionStorage` under `apps/web/src` found only theme preference storage, not auth token/session storage.
- `SECURITY.md` and README explicitly say pre-alpha, not security-audited, not production-ready, do not expose directly to public internet, use copied/test data first.
- `.env.example` still has `CORS_ORIGINS=["*"]`; this is already tracked as GitHub #26 for LAN/VPN origin narrowing docs. It is not a release blocker by itself because current docs warn against direct public exposure, but it remains a deployment-safety non-blocker.
- `gh auth status` output masks token values; no token values were copied into this report.

No professional security audit is claimed or implied.

## Money/accounting notes

Findings:

- `docs/money-model.md` documents Decimal/string money rules, no float core money arithmetic, CSV decimal-string preservation, no fake currency conversion, and split transaction sign honesty.
- Backend schemas expose money amounts as strings in `apps/api/app/schemas/gnucash.py`.
- Transaction filters use `Decimal` query params for amount range validation.
- Reports explicitly document base-currency-only/no-conversion behavior and expose `includes_currency_conversion=false` in schemas.
- Multi-split transactions are represented as split details, and transaction-list counterparty language avoids pretending there is always one counter account.
- Previous Phase 83 frontend money-display hardening reduced `Number()` use for money display decisions; this audit did not find new backend float money arithmetic in the inspected core paths.

No money/accounting correctness blocker found in this pass.

## Recommended next action

Run one narrow release-docs correction phase: update README, PROJECT_STATUS, CHANGELOG, and `docs/release/v0.1.1-readonly-notes.md` / GitHub release notes so `v0.1.1-readonly` is honestly represented as already published at tag `a4d0415`, with scope including the actual Phase 103/104 read-only transaction-filter/search changes or an explicit explanation of why the tag target includes them.

## Suggested GitHub issues

No GitHub issues were created per task constraints. Suggested issue if you want to track the blocker instead of fixing immediately:

Title: Sync v0.1.1-readonly public release notes and README after publication

Labels: `documentation`, `release`, `audit`

Body:

```md
## Problem
`v0.1.1-readonly` is published as a GitHub pre-release and local tag, but public docs/release notes still describe it as a draft/not-published candidate.

Evidence:
- GitHub release `v0.1.1-readonly` exists and targets `a4d04150c043ad4da3dea577b30ed7ffd2032df0`.
- Published release body starts with `# v0.1.1-readonly Draft Release Notes` and says it does not publish/authorize publication.
- `README.md` still says the current public pre-alpha release is `v0.1.0-readonly`.
- Release notes do not cover Phase 103/104 changes even though the tag points after Phase 104.

## Acceptance criteria
- README current release section names `v0.1.1-readonly` as latest, while preserving pre-alpha/read-only/not-production/security warnings.
- `docs/release/v0.1.1-readonly-notes.md` no longer claims draft/not-published status.
- GitHub release notes are updated to match the corrected file.
- PROJECT_STATUS and CHANGELOG accurately reflect publication state and actual tag scope.
- No product code changes, no new release publication, no write-mode enablement.
```

## What not to do next

- Do not start v0.2 controlled writes or enable `GNUCASH_WRITES_ENABLED=true` by default.
- Do not publish another release/tag/package until the current `v0.1.1-readonly` public-docs drift is fixed.
- Do not claim production readiness, security-audited status, SaaS readiness, collaborative accounting, or safe write-mode for real books.
- Do not run personal-book dogfood unless Val provides an explicit safe copied/disposable GnuCash SQL book path outside the repository and confirms it is not the live authoritative book.
- Do not create noisy backlog issues for every non-blocker; either fix the release-docs drift directly or track exactly one meaningful issue.

## Checks run in this audit

- `git status --short --branch`
- `git log --oneline -20`
- `git log --oneline -10 --decorate --stat --no-renames`
- `git fetch --dry-run origin main`
- `git rev-list --left-right --count main...origin/main`
- `git tag --list 'v0.1.1-readonly'`
- `git show --no-patch --format=fuller v0.1.1-readonly`
- `gh auth status`
- `gh issue list --state open --limit 50`
- `gh release list --limit 10`
- `gh release view v0.1.1-readonly --json ...`
- `gh run list --limit 10`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- `pytest -q tests/test_transaction_writes.py::TestWritesDisabledByDefault`
- `npm run test:auth-routes`
- tracked sensitive-path scan via `git ls-files` with safe path-name filtering

Full heavy suites were not run because this was a read-only audit with a clear release-docs blocker, and recent CI already shows green full checks on `main`.
