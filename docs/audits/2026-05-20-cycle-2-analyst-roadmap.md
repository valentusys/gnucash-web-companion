# Cycle 2 Analyst Roadmap — 2026-05-20

## Executive summary

Текущий baseline после предыдущего цикла сильный: `v0.1.6-readonly` опубликован как GitHub pre-release, `main` синхронизирован с `origin/main`, последние CI runs зелёные, tracked tree чистый кроме repo-local `.hermes/`. Read-only/default-write-disabled boundary сохраняется: `.env.example` держит `GNUCASH_WRITES_ENABLED=false`, release docs честно говорят pre-alpha/not production-ready/not security-audited, write-alpha остаётся experimental/test-disposable-only. Главный найденный drift: `docs/ROADMAP.md` заметно устарел относительно README/PROJECT_STATUS/CHANGELOG и всё ещё описывает старый release posture; это не runtime safety blocker, но должно стать поддерживающей частью следующей практической фазы. Следующий цикл не должен быть audit-only: нужны smoke/compatibility/UX/security/dogfood/release artifacts.

## Verdict

Ready for next engineering phase.

## Readiness

- Read-only MVP / next engineering readiness: 92%.
- Current public `v0.1.6-readonly` release confidence: 90% для pre-alpha read-only scope, с ограничением synthetic-only latest dogfood.
- Next maintenance release readiness: 0% сейчас, потому что после `v0.1.6-readonly` нет unreleased product changes; сначала нужны практические фазы и dogfood.
- Production/security-audited readiness: 0%; таких claims нет и быть не должно.
- Real/private-book write readiness: 0%; controlled writes остаются disabled by default, post-MVP/write-alpha, not safe for real/private books.

## Baseline audit

### Repository state

- Branch: `main`.
- Local status: `## main...origin/main` plus untracked `.hermes/`; `.hermes/` ignored as local agent telemetry per task.
- Latest commit: `6ea3cfb Phase 161 v0.1.6-readonly release gate`.
- Last 10 commits:

| commit | type | user impact |
| --- | --- | --- |
| `6ea3cfb` Phase 161 | release | published `v0.1.6-readonly` after final gate |
| `d56c335` Phase 160 | dogfood/tests | full synthetic release-candidate Docker/browser dogfood |
| `131d568` Phase 159 | UX/localization/tests | release-critical frontend localization |
| `84ac9e5` Phase 158 | UX/dogfood/tests | mobile touch-target/no-overflow pass |
| `aa34766` Phase 157 | UX/tests | scheduled transaction filters/read-only clarity |
| `14a9815` Phase 156 | UX/accounting clarity/tests | dashboard drilldowns to read-only filters |
| `616661e` Phase 155 | UX/API/tests | multi-book read-only operator diagnostics |
| `ae139e2` Phase 154 | compatibility/tests/docs | Desktop tooling blocker refresh |
| `111688a` Phase 153 | dogfood/tooling | fresh-clone Docker smoke helper |
| `d52d31b` Phase 152 | release | published `v0.1.5-readonly` |

Conclusion: recent work is practical release/dogfood/UX/test work, not an audit loop.

### Release state

- Current public read-only release: `v0.1.6-readonly`.
- Previous read-only release: `v0.1.5-readonly`.
- Published write-alpha pre-release: `v0.2.0-writealpha`, still experimental and disabled by default.
- GitHub release list confirms `v0.1.6-readonly` exists as pre-release.
- GitHub Actions list shows success for recent `main` commits from Phase 152 through Phase 161.
- `CHANGELOG.md` says no unreleased changes after `v0.1.6-readonly`.

### Product/docs consistency

- `README.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`, and `docs/release/v0.1.6-readonly-*` agree on current public release and safety posture.
- `docs/ROADMAP.md` is stale: it says completed through Phase 137/138 and current public read-only pre-release `v0.1.3-readonly`, while current state is Phase 161 and `v0.1.6-readonly`.
- Recommendation: fix `docs/ROADMAP.md` as a support artifact in the next practical phase, not as a standalone docs-only phase.

### Safety boundary

- `.env.example` line 27 sets `GNUCASH_WRITES_ENABLED=false`.
- Phase 160 dogfood verified runtime `checks.writes_enabled=false`, hidden write UI, disabled validate/create/patch probes, and an additional disabled DELETE probe returning 403.
- Phase 161 final gate verified rendered Compose config with `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- Search found browser storage usage only for theme (`localStorage` in theme code/app shell), not auth token storage.
- Controlled writes remain post-MVP/write-alpha, disabled by default, constrained to test/disposable scope when explicitly enabled.

### GitHub/backlog state

Open issues visible via `gh issue list`:

1. #36 — controlled-write v0.2 readiness gates. Keep out of this read-only cycle except disabled-write safety checks.
2. #29 — localization glossary. Partially addressed; useful only when tied to UI localization work.
3. #28 — markdown source readability. Non-blocking; avoid docs-only cleanup loop.
4. #22 — GnuCash Desktop compatibility fixtures. Still the best practical evidence gap for read-only confidence.
5. #17 — Russian documentation/UI localization. Partially addressed; useful as a narrow release-critical slice.
6. #13 — Book management UI. Only safe subset is read-only diagnostics/access/context clarity; no upload/delete/default-changing/editing.

No GitHub issues were created, closed, or modified by this analyst task.

### Dogfood status

- Latest dogfood: Phase 160 synthetic/disposable Docker/Caddy API + browser dogfood, PASS.
- Coverage included login, protected redirect, dashboard, accounts, books, scheduled, account detail, transaction filters, transaction detail, CSV export, mobile no-overflow, hidden write UI, disabled write probes, and no-artifact checks.
- Limitation: latest dogfood is synthetic/disposable only. Earlier copied-book dogfood exists from Phase 116, but current post-`v0.1.6` state should not claim broad real-book readiness.

### Security/auth notes

- README/release docs avoid security-audited and production-ready claims.
- Auth cookie is httpOnly by design/evidence; Phase 160 browser dogfood confirmed auth cookie not readable from `document.cookie`.
- No auth localStorage/sessionStorage usage found in frontend source search.
- CORS wildcard remains development default in `.env.example`, with comments warning LAN/VPN operators to use exact origins. Acceptable for pre-alpha if not exposed publicly.

### Money/accounting notes

- Docs and release notes continue to say no fake currency conversion and base-currency-only reporting limitations.
- Frontend `Number()` search shows uses for IDs/pagination/dates/sorting and comments that money display avoids `Number()`; no immediate blocker found from this quick baseline.
- Future phases must preserve Decimal/string money and CSV decimal-string behavior.

## Top blockers

1. No runtime safety blocker for the next engineering phase.
2. `docs/ROADMAP.md` is stale versus current release state; fix as support in Phase 1 with a tagged smoke, not as an audit-only/docs-only phase.
3. Broad compatibility remains narrow: no automated GnuCash Desktop-generated fixture evidence yet (#22).

## Important non-blockers

1. Open #28/#29/#17 should not become standalone docs-only phases.
2. #36 write-alpha work must not be used to justify enabling writes for real/private books.
3. Phase 160 synthetic-only dogfood is enough for engineering continuation, but not for production/broad real-book claims.

## PM escalation required

No.

Reason: roadmap is narrow and executable without product arbitration. Priorities are consistent: post-release smoke/status sync, compatibility evidence, read-only book/UX/export/auth/operator hardening, localization, dogfood, then release gate. Escalate to PM only if the programmer proposes production writes, book upload/delete/default-changing, public-internet readiness claims, private-data usage, or changing release scope.

## План на 10 фаз PM→программист

Этот план предназначен для прямой передачи программисту без отдельного ПМ. Все фазы должны сохранять `GNUCASH_WRITES_ENABLED=false` по умолчанию, не включать production writes, не коммитить `.env`, app DB, GnuCash books, backups, private screenshots/exports, tokens, keys, certs, private paths, or private financial data. Документы обновлять только как поддержку фактических behavior/test/UX/dogfood/release changes.

## Phase 1 — Post-release baseline sync + v0.1.6 tagged smoke
- goal: Синхронизировать фактический post-`v0.1.6-readonly` baseline и подтвердить, что опубликованный тег запускается по documented read-only path.
- scope: Исправить только фактический release/status drift в поддерживающих документах, особенно `docs/ROADMAP.md`, если он всё ещё говорит про старые фазы/релизы; выполнить fresh checkout/tag smoke для `v0.1.6-readonly` с synthetic fixture, dummy local `.env`, Docker Compose, API smoke и browser smoke; записать redacted evidence.
- non-goals: Не менять product behavior ради документации; не публиковать релиз; не трогать write-alpha; не использовать реальные книги; не добавлять новый backlog theater.
- acceptance criteria: Public docs больше не противоречат `README.md`/`PROJECT_STATUS.md` по current release/posture; tagged smoke `v0.1.6-readonly` проходит или даёт конкретный bugfix blocker; `GNUCASH_WRITES_ENABLED=false` подтверждён в rendered config/runtime.
- safety checks: Только synthetic/disposable fixture; `.env`, app DB, copied book, screenshots, CSV exports, backups не коммитятся; no production/security-audit claims; no public internet claim.
- verification: `git status --short --branch`; checkout/tag smoke script or documented command; `docker compose config --quiet`; API smoke; browser dogfood; disabled validate/create/patch/delete write probes; sensitive tracked-file scan.
- expected artifacts: `docs/dogfood/phase-162-v0.1.6-tagged-smoke.md`, updated `docs/ROADMAP.md`/status docs only if drift is confirmed, `docs/handoff/phase-162.md`, tests/scripts only if smoke tooling needs a real fix.

## Phase 2 — Disposable GnuCash Desktop compatibility fixture path
- goal: Двинуть #22 практическим compatibility evidence: получить Desktop-generated synthetic SQLite fixture в disposable окружении или зафиксировать воспроизводимый blocker без ложных claims.
- scope: Использовать контейнер/одноразовое окружение для `gnucash`/`gnucash-cli` tooling probe; если безопасно доступно — создать synthetic SQLite book, прогнать read-only service tests, checksum/no-mutation check, metadata collector; если нет — улучшить blocker artifact с точными install/runtime prerequisites.
- non-goals: Не устанавливать пакеты в небезопасное/shared окружение без изоляции; не открывать private books; не заявлять all-version/PostgreSQL/MySQL/MariaDB/XML support; не расширять writes.
- acceptance criteria: Есть либо tested Desktop-generated synthetic fixture evidence, либо clear BLOCKED artifact, который программист/оператор может повторить в disposable environment; compatibility matrix честно обновлена.
- safety checks: Fixture synthetic/disposable only; no account names/descriptions/amounts/memos/private paths in docs; writes disabled by default; metadata redaction tests pass.
- verification: Tooling probe tests; fixture generator tests if generated; read-only accounts/transactions/reports/CSV tests over generated fixture; checksum/no-mutation check; docs grep for overbroad compatibility claims.
- expected artifacts: `docs/gnucash-desktop-tooling-phase-163.md`, updated `docs/gnucash-compatibility.md`, `docs/gnucash-version-fixture-plan.md`, optional fixture generator/probe tests, `docs/handoff/phase-163.md`.

## Phase 3 — Book context and access edge-case hardening
- goal: Укрепить read-only multi-book foundation (#13) без management actions: меньше 403/404 confusion при invalid/stale selected-book cookie, archived/default mismatch, missing configured book.
- scope: Add/adjust backend/frontend behavior for stale selected-book cookie recovery, missing default guidance, archived/inaccessible book redirects/messages, safe current/default labels; pin route behavior with tests.
- non-goals: No upload/delete/default-changing/registry edit UI; no direct file browser; no collaborative/family-wallet workflow; no GnuCash data writes.
- acceptance criteria: Пользователь с invalid/stale selected book видит безопасное восстановление/переход на `/books`, а не confusing failure; unauthorized/archived books остаются hidden/blocked; raw `uri_or_path` не попадает в API/UI.
- safety checks: Do not expose private paths; do not open GnuCash data just for metadata listing beyond existing read-only routes; keep selected book state non-secret and cookie-scoped; no localStorage/sessionStorage for book-sensitive state.
- verification: Backend route tests for archived/unauthorized/missing/default cases; frontend route/static checks; browser dogfood on `/books`, dashboard redirect, account/transaction pages; search for `uri_or_path` rendering and browser storage.
- expected artifacts: Code/tests for read-only book-context UX, updated `docs/book-switcher-readonly-model.md` only if behavior changes, `docs/handoff/phase-164.md`.

## Phase 4 — Account tree large-hierarchy usability and benchmark
- goal: Улучшить read-only account-tree usability/performance evidence for large account hierarchies without inventing accounting semantics.
- scope: Generate synthetic large account hierarchy fixture/benchmark; measure `/accounts` and account filter UI; fix one concrete issue if benchmark or dogfood exposes slow/overflow/confusing behavior; add regression checks.
- non-goals: No cache layer unless measured need is clear; no account editing; no production scalability claim; no real account names.
- acceptance criteria: Large synthetic account hierarchy can be browsed/searched with documented local timings and no mobile/desktop overflow; if performance is still limited, docs say so honestly.
- safety checks: Synthetic account names only; Decimal/string money handling preserved; no private screenshots/export artifacts; writes disabled.
- verification: Backend benchmark/test helper; frontend account tree route checks; 320px and desktop browser dogfood for accounts/account detail; no-artifact and sensitive tracked-file scan.
- expected artifacts: `docs/performance/phase-165-large-account-tree-benchmark.md`, UX/tests if changed, `docs/handoff/phase-165.md`.

## Phase 5 — CSV export reliability and user feedback hardening
- goal: Сделать synchronous read-only CSV export safer and clearer under empty, filtered, capped, and timeout/error conditions.
- scope: Review/export endpoint and frontend proxy behavior for headers, empty result, cap/truncation copy, timeout/error display, account-scoped export parity; add tests and one UX improvement where evidence shows ambiguity.
- non-goals: No import; no background export queue unless explicitly justified later; no raw CSV artifact commits; no change to 10,000 cap without documented decision.
- acceptance criteria: Users see clear read-only/cap/filter/error state; backend/proxy headers remain consistent; account and transaction export parity is pinned by tests.
- safety checks: CSV amount strings remain strings; no fake conversion; no private CSV body in docs; writes disabled; no browser persistence of filters.
- verification: Backend CSV tests for empty/filtered/capped/error cases; frontend route/static checks; API smoke CSV export; browser dogfood CSV route; grep for raw committed CSV artifacts.
- expected artifacts: Code/tests for CSV reliability UX, updated `docs/transactions-filters.md` only as support, `docs/handoff/phase-166.md`.

## Phase 6 — Auth/session hardening for local/LAN pre-alpha
- goal: Укрепить auth/session defaults and operator feedback without claiming production security audit.
- scope: Review cookie flags, logout behavior, session expiry UX, CSRF/origin posture for state-changing app routes, and startup warnings; implement narrow hardening with tests if a gap is found.
- non-goals: No OAuth/SSO; no multi-user role expansion; no public-internet readiness claim; no security-audited claim.
- acceptance criteria: Auth token remains httpOnly cookie only; logout/session-expired paths are user-safe; state-changing routes have documented/testable protection appropriate for pre-alpha local/LAN use; warnings stay conservative.
- safety checks: No tokens/secrets in logs/docs; no localStorage/sessionStorage auth; placeholder JWT remains rejected; CORS wildcard remains warned against outside dev.
- verification: Backend auth/security tests; frontend auth-route checks; browser dogfood verifies cookie not readable from `document.cookie`; source search for storage/token leaks; Docker config validation.
- expected artifacts: Auth/session tests and any narrow code changes, updated security/deployment docs only if behavior changes, `docs/handoff/phase-167.md`.

## Phase 7 — First-run and broken-configuration operator UX
- goal: Сделать first-run failures actionable for self-hosted operators while preserving private-path redaction and pre-alpha warnings.
- scope: Improve health/startup/UI guidance for missing default book, unreadable book, rejected placeholder JWT, missing admin password/hash, app DB bootstrap issues; ensure `/login`, `/books`, and error page give safe next actions.
- non-goals: No setup wizard that writes config; no secrets display; no public hosting hardening; no book upload/management.
- acceptance criteria: Common broken local setup states produce clear safe messages and logs without leaking private paths/secrets; operator can fix `.env`/book placement from docs.
- safety checks: Redact paths/secrets; no `.env` commits; no private book probing; writes disabled; GnuCash Desktop remains authoritative editor.
- verification: Backend config/health tests; frontend error/login/books route checks; Docker Compose config with known bad dummy scenarios where safe; log redaction tests.
- expected artifacts: Code/tests for first-run diagnostics, updated `docs/operations/troubleshooting.md` or deployment docs as support, `docs/handoff/phase-168.md`.

## Phase 8 — Russian localization release-critical completion slice
- goal: Закрыть самый заметный RU/EN mismatch на release-critical read-only paths без заявления full localization.
- scope: Localize remaining visible safety/operator strings touched by phases 162–168: first-run errors, CSV export states, auth/session messages, book-context recovery, release-critical warnings; update glossary only where needed.
- non-goals: No backend API localization rewrite unless required by UI; no marketing rewrite; no full translation claim; no docs-only phase without UI/tests.
- acceptance criteria: RU locale covers current high-value read-only paths consistently; README.ru/docs честно говорят partial/opt-in если остаются gaps; safety language is not softened.
- safety checks: Canonical English preserved; terms for read-only, authoritative editor, not production-ready, not security-audited remain consistent; no private data in examples.
- verification: Catalog/static route checks; `npm run check`; browser smoke for RU locale if supported; docs consistency review for README.ru/localization.
- expected artifacts: Message catalog/UI/tests, updated `docs/localization.md` and `README.ru.md` if factual state changes, `docs/handoff/phase-169.md`.

## Phase 9 — Full synthetic + optional copied-book dogfood after cycle changes
- goal: Проверить весь cycle 2 read-only surface в runtime before any release gate.
- scope: Run Docker/Caddy API smoke and headless browser dogfood through login, dashboard, accounts, books, scheduled, account detail, transaction filters/detail, CSV export, auth/logout/session where applicable, hidden write UI, disabled write endpoints, no-artifact checks; optional copied-book pass only if Val explicitly provides safe copied book path outside git.
- non-goals: No private directory search; no release publication; no write-alpha expansion; no screenshots/raw CSV/private evidence commits.
- acceptance criteria: Synthetic dogfood PASS with redacted evidence, or concrete blockers fixed/recorded; optional copied-book evidence is redacted and local-only if provided.
- safety checks: `GNUCASH_WRITES_ENABLED=false`; synthetic/disposable default; copied-book optional requires explicit safe path and confirmation it is not authoritative live book; app DB/books/backups/exports/screenshots stay untracked.
- verification: Docker Compose config/startup; API smoke; browser dogfood at 320px and one desktop width if recent UX changed; disabled validate/create/patch/delete probes; no-artifact scan; sensitive tracked-file scan.
- expected artifacts: `docs/dogfood/phase-170-cycle-2-release-candidate-dogfood.md`, bugfix tests if needed, `docs/handoff/phase-170.md`.

## Phase 10 — v0.1.7-readonly release gate or BLOCKED artifact
- goal: Prepare the next read-only maintenance release artifact after phases 162–170 and publish only if gate is green and the user explicitly authorized publication in this task scope.
- scope: Choose candidate tag (`v0.1.7-readonly` unless actual release history dictates otherwise); prepare release notes/checklist/final gate; run full local checks, GitHub CI gate, tag/release collision checks, sensitive hygiene; publish GitHub pre-release only with explicit authorization and green gate, otherwise write `BLOCKED` gate artifact.
- non-goals: No stable/production/security-audited claim; no package/image/binary; no write-alpha promotion; no release with failed dogfood/dirty tree/no authorization.
- acceptance criteria: Either published honest pre-alpha read-only GitHub pre-release with publication evidence, or no publication and exact blockers documented; README/PROJECT_STATUS/CHANGELOG/release docs reflect actual outcome.
- safety checks: Clean tracked tree excluding repo-local `.hermes/`; `HEAD == origin/main`; `GNUCASH_WRITES_ENABLED=false`; no real/private data; no tag/release collision; conservative release language.
- verification: `cd apps/api && pytest -q`; `cd apps/web && npm run check && npm run test:auth-routes && npm run build`; Docker Compose config and write-disabled rendering; dogfood evidence review; `gh run list/watch`; `git diff --check`; sensitive tracked-file scan; tag/release checks.
- expected artifacts: `docs/release/v0.1.7-readonly-notes.md`, `docs/release/v0.1.7-readonly-checklist.md`, `docs/release/v0.1.7-readonly-final-gate.md`, optional publication evidence or blocked gate, updated README/PROJECT_STATUS/CHANGELOG, `docs/handoff/phase-171.md`.

## Recommended next action

Передать программисту Phase 1: post-release baseline sync + tagged `v0.1.6-readonly` smoke. Это исправит обнаруженный docs drift только как support artifact и сразу даст runtime evidence по опубликованному тегу.

## Suggested GitHub issues

No new issues recommended by this analyst pass. Existing #22/#13/#17/#29/#28/#36 are sufficient; avoid noisy duplicates.

## What not to do next

- Не запускать ещё один audit-only цикл.
- Не включать `GNUCASH_WRITES_ENABLED=true` в normal/runtime deployment.
- Не расширять write-alpha к real/private books.
- Не заявлять production readiness, audited security, broad GnuCash compatibility или safe public-internet deployment.
- Не создавать/закрывать GitHub issues ради видимости активности.
- Не читать private books, app DBs, backups, `.env`, private exports/screenshots, secrets, keys, certs.

## External roadmap

Strict 10-section roadmap written to:

`/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-resume-20260520-003549/cycle-2-roadmap.md`
