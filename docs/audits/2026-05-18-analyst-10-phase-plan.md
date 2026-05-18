# Analyst 10-Phase PM→Engineer Roadmap — 2026-05-18

## Executive summary

Текущий `main` находится после Phase 94: `v0.1.0-readonly` уже опубликован как pre-release, read-only/default-write boundary в коде и документации в целом сохранён, CI на последних push зелёный. Главный практический блокер перед `v0.1.1-readonly` — GitHub #39: CSV export фактически ограничен 500 строками при документации/headers про 10,000 и `truncated=false`. Второй блокер — #38: нет безопасной скопированной личной GnuCash SQL книги вне git, поэтому нельзя заявлять персональный real-book dogfood pass. Следующие 10 фаз должны быть инженерными/dogfood/release-value, а не очередным audit-loop; документы должны обновляться только как evidence/handoff вокруг выполненной работы.

## Verdict

Ready after blockers fixed.

Проект готов к следующей практической инженерной фазе, но не готов к `v0.1.1-readonly` maintenance release до исправления #39 и подтверждения release checks. Controlled writes нельзя продвигать в MVP: `GNUCASH_WRITES_ENABLED=false` остаётся обязательным default, write code — только post-MVP/experimental.

## Top blockers

1. GitHub #39 — CSV export row-count/header mismatch. Для read-only user-facing export это release blocker перед `v0.1.1-readonly`.
2. GitHub #38 — copied personal-book dogfood rerun заблокирован отсутствием безопасной скопированной SQL книги вне git. Не блокирует синтетический maintenance fix, но блокирует любые claims о personal-book dogfood pass.
3. GitHub #22 — compatibility evidence всё ещё узкое: есть synthetic/metadata procedure, но нет широкой real-version матрицы GnuCash Desktop versions. Не блокирует pre-alpha, но блокирует broad compatibility claims.

## Important non-blockers

1. `CORS_ORIGINS=["*"]` остаётся дефолтом в `.env.example` и `Settings`; это допустимо только с текущими LAN/local/VPN warnings и tracked issue #26, не как production-safe posture.
2. Russian localization неполная и честно описана как limited slice; это не blocker для read-only maintenance.
3. `/books` UI сейчас metadata-only и read-only; registry editing/upload/delete/default management остаются future work по #13.
4. Open controlled-write code существует, но backend routes feature-gated before write service construction; это допустимо только при continued disabled default and tests.
5. Theme preference uses `localStorage`; auth token не хранится в `localStorage/sessionStorage`, хранится в httpOnly cookie.

## Inspection performed

- Read `AGENTS.md`, `PROJECT_STATUS.md`, `README.md`, `README.ru.md`, `CHANGELOG.md`, `.env.example`, `SECURITY.md`.
- Inspected `docs/audits/`, `docs/dogfood/`, `docs/release/` state.
- Inspected backend settings/write routes in `apps/api/app/config.py` and `apps/api/app/routers/transactions.py`.
- Inspected frontend auth/write route behavior in `apps/web/src/routes/login/+page.server.ts` and `apps/web/src/routes/transactions/new/+page.server.ts`.
- Searched for `GNUCASH_WRITES_ENABLED`, `gnucash_writes_enabled`, `localStorage`, `sessionStorage`, `document.cookie`, `Decimal`, money-related code.
- Checked GitHub state with `gh issue list`, `gh release list`, `gh run list`.
- Checked local git history/status on `main`.

## Last 10 commits classification

| Commit | Type | User impact |
| --- | --- | --- |
| `34cd194 docs: record phase 94 push evidence` | docs/release | Records push evidence; no product change. |
| `f578ebf docs: record phase 94 maintenance decision` | docs/release | Documents no `v0.1.1` until #39 fixed. |
| `4613d33 docs: record phase 93 github evidence` | docs | Records GitHub evidence; no product change. |
| `165ed13 feat: extend russian localization slice` | code/docs | Adds limited RU `/books`/nav localization value. |
| `01b78aa docs: record phase 92 push evidence` | docs | Records push evidence; no product change. |
| `7eb5fa7 feat: add safe gnucash compatibility metadata collector` | code/tests/docs | Adds safe metadata collection procedure for copied/disposable books. |
| `3e294e5 docs: record phase 91 handoff evidence` | docs | Records phase evidence; no product change. |
| `631ffe0 feat: add read-only books metadata page` | code/tests/docs | Adds safe read-only `/books` metadata UI. |
| `7052d0d docs: record phase 90 push evidence` | docs | Records push evidence; no product change. |
| `a943720 feat: summarize active transaction filters` | code/tests/docs | Improves transaction filter/CSV parity UX. |

Recent work is mixed: useful code phases exist, but there is enough docs/evidence churn that the next step must be practical engineering, not another analyst/audit-only phase.

## Safety / read-only boundary

Findings:

- `.env.example` keeps `GNUCASH_WRITES_ENABLED=false`.
- Backend `Settings.gnucash_writes_enabled` default is `False`.
- Backend write routes call `_ensure_writes_enabled(settings)` before resolving edit access and before constructing `GnuCashWriteService`.
- Disabled write route behavior is covered in `apps/api/tests/test_transaction_writes.py` per inspected search results.
- Frontend `/transactions/new` load/actions redirect/return disabled-write errors unless private env `GNUCASH_WRITES_ENABLED === 'true'`.
- README/README.ru/PROJECT_STATUS consistently state read-only by default and controlled writes experimental/post-MVP.
- No evidence found that MVP write mode is enabled by default.

Conclusion: no safety blocker found in the read-only boundary during this inspection. Continue treating write-mode code as post-MVP and never release-market it as production-safe.

## Release/docs consistency notes

- Current GitHub release list shows `v0.1.0-readonly` as latest pre-release; docs agree.
- `PROJECT_STATUS.md`, README, CHANGELOG, and `docs/release/v0.1.1-readonly-decision.md` agree that `v0.1.1-readonly` should not be prepared before #39 is fixed.
- The repository still contains many historical audit phases; the next roadmap should deliberately avoid audit-only loops.
- README’s historical current-status list is long but not materially false; cleanup is non-blocking and tracked by #28.

## GitHub project state

Open issues observed:

- #39 — CSV export row count/header mismatch; primary maintenance-release blocker.
- #38 — copied personal-book dogfood rerun pending safe copied SQL book.
- #36 — controlled-write v0.2 readiness gates; keep out of MVP.
- #29/#28/#26/#22/#17/#13/#12/#11 — meaningful non-blocker roadmap/backlog items.

Releases observed:

- `v0.1.0-readonly` — Pre-release, latest.
- `v0.0.2-prealpha` — Pre-release.
- `v0.0.1-prealpha` — Pre-release.

Actions observed:

- Last 10 workflow runs shown by `gh run list` are completed/success on `main`.

## Dogfood status

- Phase 77/78 copied/disposable Docker/API/browser dogfood passed for v0.1 publication with writes disabled.
- Phase 85 personal copied-book dogfood is blocked, not passed: no safe copied personal GnuCash SQL book was available outside git.
- #38 correctly tracks the rerun. Do not manufacture or imply personal-book success until a safe copied book is mounted outside the repository.
- Future dogfood must not commit real book files, app DB, backups, screenshots, CSV exports, private account names, amounts, `.env`, secrets, or private paths.

## Security/auth notes

- `SECURITY.md` clearly says pre-alpha, no production guarantee, not security audited, do not expose early versions directly to the public internet.
- Login sets `access_token` as `httpOnly`, `sameSite: 'lax'`, `secure` only on HTTPS.
- Search found `localStorage` used for theme only; no auth token storage in `localStorage/sessionStorage` was found.
- `selected_book_id` is set via `document.cookie` client-side and is not auth-sensitive.
- `CORS_ORIGINS=["*"]` remains a conservative-docs risk; keep #26 open until origin narrowing guidance/defaults improve.
- No secrets or real financial data were intentionally inspected/created in this analyst phase.

## Money/accounting notes

- Backend transaction filters use `Decimal` for amount bounds.
- CSV rows preserve amount fields as strings from DTOs.
- Docs and dashboard copy now state base-currency-only/no-conversion limitations; no fake currency conversion should be added.
- Phase 83 replaced frontend money-display decisions based on `Number()` for money strings; remaining Number usage appears route/pagination/id oriented from current status.
- Split/multi-currency correctness remains an area for practical tests, not release marketing claims.

## Recommended next action

Exactly one recommended next phase: Phase 95 — fix GitHub #39 with regression coverage and targeted export verification, then update only handoff/status evidence.

## 10 sequential PM→Engineer phases

### Phase 95 — Fix CSV export row-count/header mismatch (#39)

Goal:
- Make CSV export body row count, `X-CSV-Export-Limit`, `X-CSV-Export-Total`, and `X-CSV-Export-Truncated` consistent for exports above 500 rows and up to the documented 10,000-row cap.

Non-goals:
- No write-mode work.
- No new export formats.
- No async export system.
- No real/private book data.

PM brief expectations:
- PM gives engineer a narrow #39 brief: read-only export correctness only, use synthetic/disposable data, preserve current API/frontend proxy contract where possible.
- PM requires proof that list pagination defaults do not silently cap CSV export rows.

Engineer acceptance criteria:
- Backend test fails before fix or clearly targets the mismatch path: >500 synthetic/fake rows export produces body rows matching headers.
- CSV export endpoint returns consistent `limit`, `total`, `truncated` semantics.
- Frontend SvelteKit export proxy forwards corrected headers unchanged.
- GitHub #39 is updated with evidence and closed only if the fix is proven.

Required checks:
- `cd apps/api && pytest -q`
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- Targeted synthetic CSV export smoke/benchmark for >500 rows.

Report expectations:
- Update `PROJECT_STATUS.md` and `docs/handoff/phase-95.md`.
- Include row counts, header values, truncation flag, test commands, GitHub #39 state.
- Explicitly state writes remain disabled by default.

### Phase 96 — Synthetic large-export benchmark and UX confirmation

Goal:
- Re-run/extend the synthetic large-book benchmark focused on CSV export after #39, including user-visible export copy consistency.

Non-goals:
- No performance overclaim.
- No real-book dogfood.
- No new CSV customization features.

PM brief expectations:
- PM asks for evidence that the fixed export behavior holds in the existing synthetic benchmark path and UI copy no longer misleads users.

Engineer acceptance criteria:
- Benchmark output records CSV export total/body/header consistency for a synthetic book above 500 transactions.
- Docs/performance artifact explains synchronous cap/timeout/truncation honestly.
- UI text remains clear that exports are read-only, filtered, synchronous, and capped.

Required checks:
- Targeted benchmark command used by existing performance tooling.
- `cd apps/api && pytest -q`
- Frontend route/auth checks if UI copy changes.

Report expectations:
- Add/update a `docs/performance/phase-96-...` artifact.
- Update `docs/handoff/phase-96.md` and `PROJECT_STATUS.md`.
- Report no real/private data committed.

### Phase 97 — v0.1.1-readonly release-prep checklist and notes

Goal:
- Prepare conservative `v0.1.1-readonly` release notes/checklist after #39 is fixed and verified.

Non-goals:
- Do not publish tag/release in this phase.
- Do not claim production readiness, security audit, broad GnuCash compatibility, or personal-book dogfood pass.
- Do not start v0.2 writes.

PM brief expectations:
- PM gives release-prep-only brief: summarize post-v0.1 maintenance changes, known limitations, checks required before publication.

Engineer acceptance criteria:
- `docs/release/v0.1.1-readonly-notes.md` exists and is conservative.
- `docs/release/v0.1.1-readonly-checklist.md` exists with explicit blockers/checks and no false claims.
- README/PROJECT_STATUS/CHANGELOG updated only as needed for candidate state.

Required checks:
- Markdown/link sanity by inspection.
- `git diff --check`.
- No product test suite required unless docs changes touch commands or claims needing verification.

Report expectations:
- Handoff lists release candidate status as prepared, not published.
- Include exact open blockers/non-blockers and #38 limitation.

### Phase 98 — v0.1.1-readonly release-gate verification

Goal:
- Run final release-gate checks for `v0.1.1-readonly` candidate and produce a gate artifact.

Non-goals:
- Do not publish tag/release.
- Do not fix unrelated product issues unless gate fails on them; if it fails, stop and report blocker.

PM brief expectations:
- PM requires full release gate: backend/frontend/Docker config/GitHub Actions state/read-only write-probe evidence.

Engineer acceptance criteria:
- `docs/release/v0.1.1-readonly-final-gate.md` records verdict.
- Disabled write endpoint tests/probes are represented by automated tests or targeted smoke.
- GitHub Actions on `main` are checked and recorded.
- Verdict is honest: ready to publish or blocked.

Required checks:
- `cd apps/api && pytest -q`
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- `gh run list --limit 10` if gh authenticated.
- Optional targeted API smoke for disabled write endpoints with `GNUCASH_WRITES_ENABLED=false`.

Report expectations:
- Handoff includes command outputs summary, not full logs unless relevant.
- Explicitly state no real/private data and no release published.

### Phase 99 — Publish v0.1.1-readonly only if explicitly authorized by PM/controller

Goal:
- Publish the maintenance pre-release only after Phase 98 says ready and PM/controller explicitly authorizes publication.

Non-goals:
- No code changes.
- No release if any gate is blocked.
- No package publishing beyond git tag/GitHub pre-release.

PM brief expectations:
- PM must include explicit publish authorization and target tag `v0.1.1-readonly`.
- PM must tell engineer to verify tag/release absence before creating them.

Engineer acceptance criteria:
- Annotated git tag `v0.1.1-readonly` created on the approved commit.
- GitHub pre-release created using prepared notes.
- Tag/release URLs recorded.
- No source files changed except release evidence/status docs if needed.

Required checks:
- `git status --short`
- `git tag --list 'v0.1.1-readonly'`
- `gh release view v0.1.1-readonly || true`
- `gh release create ... --prerelease --notes-file docs/release/v0.1.1-readonly-notes.md` only after authorization.
- `gh run list --limit 10` before/after as evidence.

Report expectations:
- Handoff says published or blocked, with exact commit/tag/release URL.
- If authorization is absent, phase must stop with “not published”.

### Phase 100 — Post-release install/upgrade smoke on synthetic fixture

Goal:
- Validate a fresh local install/upgrade path for `v0.1.1-readonly` using synthetic/disposable fixture data.

Non-goals:
- No personal-book dogfood unless #38 safe copied book is provided.
- No write-mode testing beyond disabled probes.
- No production deployment claims.

PM brief expectations:
- PM asks for operator-facing smoke: clone/checkout tag or current main, `.env.example` path, Docker Compose, login, core screens/API, disabled writes.

Engineer acceptance criteria:
- Fresh/upgrade smoke evidence recorded against synthetic fixture.
- Login/dashboard/accounts/transactions/CSV export tested.
- Disabled write endpoints return 403 or automated equivalent passes.
- Any docs drift in quick start is corrected narrowly.

Required checks:
- Docker Compose config validation.
- Targeted local Docker/API smoke script if available.
- Browser smoke only with synthetic data and no private screenshots unless synthetic-only.

Report expectations:
- `docs/handoff/phase-100.md` plus optional dogfood/smoke artifact.
- Include exact data safety statement.

### Phase 101 — Copied personal-book dogfood rerun (#38) if safe book is available

Goal:
- Rerun #38 with a safe copied personal GnuCash SQL book outside git, or explicitly record blocked status again if unavailable.

Non-goals:
- Do not search private directories beyond PM-approved path.
- Do not commit book, app DB, backups, screenshots, CSV exports, private paths, account names, or amounts.
- Do not enable writes.

PM brief expectations:
- PM must provide or confirm a safe copied SQL book path outside the repository and authorize local-only read-only dogfood.
- If no book is provided, PM should accept a blocked handoff rather than fake success.

Engineer acceptance criteria:
- Preflight helper classifies candidate safely with redacted output.
- If ready: API/browser read-only core paths pass locally with `GNUCASH_WRITES_ENABLED=false`.
- If blocked: GitHub #38 remains open with redacted reason.
- If passed: #38 updated/closed only with non-sensitive evidence.

Required checks:
- Dogfood preflight CLI.
- Local-only API/browser smoke with redacted notes.
- Disabled write probes return 403.

Report expectations:
- `docs/dogfood/phase-101-personal-copied-book-results.md` with redacted evidence only.
- Handoff includes pass/blocked and exact safety exclusions.

### Phase 102 — Compatibility fixture/version matrix v3 (#22)

Goal:
- Expand safe compatibility evidence using disposable/generated or manually provided copied test books from known GnuCash Desktop versions.

Non-goals:
- No broad “all GnuCash versions supported” claim.
- No PostgreSQL/MySQL/XML claims unless actually tested.
- No private data.

PM brief expectations:
- PM asks engineer to gather only safe metadata and read-only smoke evidence for versioned disposable fixtures.

Engineer acceptance criteria:
- Compatibility matrix gains at least one meaningful new version/backend row or records environment blocker honestly.
- Metadata collector output remains redacted: no paths/account names/descriptions/amounts.
- Read-only service smoke passes for added fixture(s) where possible.

Required checks:
- Existing compatibility metadata collector tests.
- Targeted read-only fixture tests.
- `cd apps/api && pytest -q` if code/tests change.

Report expectations:
- Update `docs/gnucash-compatibility.md`, `docs/handoff/phase-102.md`, `PROJECT_STATUS.md`.
- Update #22 with evidence; close only if acceptance scope is genuinely met.

### Phase 103 — Read-only transaction/search UX polish from #11/#12 subset

Goal:
- Deliver one practical read-only UX improvement around transaction search/filtering or scheduled/recurring transaction awareness, chosen by PM as highest user value.

Non-goals:
- No CSV/OFX import.
- No writes.
- No recurring transaction editing.
- No family-wallet/collaborative framing.

PM brief expectations:
- PM selects one narrow user story, e.g. saved query URL clarity, better empty states, recurring/scheduled transaction read-only indication if safely inspectable.

Engineer acceptance criteria:
- User-facing read-only behavior improves and has tests.
- API/service logic remains behind read-only service layer.
- Docs mention limitations honestly.

Required checks:
- Relevant backend tests if API/service changed.
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build` for frontend changes.
- Docker config validation if deployment/docs touched.

Report expectations:
- Handoff includes screenshots only if synthetic fixture data is used.
- GitHub issue #11 or #12 updated with exact scope/evidence.

### Phase 104 — Maintenance roadmap consolidation and next practical PM brief

Goal:
- Consolidate the previous practical results into `PROJECT_STATUS.md`, handoff, and one next PM brief without creating a new audit loop.

Non-goals:
- No broad audit report.
- No new noisy GitHub issues.
- No v0.2 write planning unless read-only maintenance/dogfood is stable and PM explicitly asks.

PM brief expectations:
- PM asks for a concise release/readiness consolidation: what shipped, what remains, what one practical phase is next.

Engineer acceptance criteria:
- `PROJECT_STATUS.md` accurately reflects phases 95–104.
- Open issues are updated only where evidence exists.
- Next recommended phase is one concrete engineering/dogfood/release-value task.
- No docs-only churn beyond status/handoff/evidence.

Required checks:
- `git diff --check`.
- `gh issue list --state open --limit 50` if gh available.
- Test suites only if product code changed in this phase.

Report expectations:
- `docs/handoff/phase-104.md` includes one next PM-ready brief.
- Final message explicitly says whether to stop, release, dogfood, or engineer next.

## Suggested GitHub issues

No new issues recommended from this analyst phase. Existing issues #39 and #38 cover the real blockers. Avoid creating backlog theater.

## What not to do next

- Do not run another audit-only phase immediately after this report.
- Do not start v0.2 controlled-write planning before read-only maintenance/dogfood evidence is stable.
- Do not publish `v0.1.1-readonly` before #39 is fixed and a release gate passes.
- Do not claim personal-book dogfood success while #38 is blocked.
- Do not enable `GNUCASH_WRITES_ENABLED=true` by default.
- Do not commit real financial data, `.env`, app DBs, backups, screenshots, CSV exports with private data, secrets, tokens, or private paths.
