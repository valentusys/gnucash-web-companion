# План на 10 фаз

## Phase 1 — Публикация prepared v0.2.1-writealpha под свежим gate

goal:
Опубликовать уже подготовленный `v0.2.1-writealpha`, только если свежий pre-publish gate на текущем `main` зелёный и подтверждает отсутствие tag/GitHub release; если gate не зелёный — остановиться с no-release artifact.

scope:
Проверить clean tracked tree с игнорированием `.hermes/`, `HEAD == origin/main`, отсутствие локального/remote tag и GitHub release `v0.2.1-writealpha`, актуальность `docs/release/v0.2.1-writealpha-*`, rendered Compose `GNUCASH_WRITES_ENABLED=false`, sensitive tracked-file hygiene, GitHub Actions на exact commit; при PASS создать annotated tag и GitHub pre-release из prepared notes, затем записать publication evidence и handoff/status/changelog sync.

non-goals:
Не менять product code, не расширять write-alpha scope, не включать writes by default, не публиковать package/image, не читать real/private books, не создавать/закрывать issues.

acceptance criteria:
Либо `v0.2.1-writealpha` опубликован как GitHub pre-release с честными experimental/write-alpha/non-production claims и evidence file, либо создан честный no-release artifact с конкретным blocker list; `GNUCASH_WRITES_ENABLED=false` подтверждён до и после.

safety checks:
Default false в `.env.example`, Docker Compose API/web render; backend write routes всё ещё требуют `GNUCASH_WRITES_ENABLED=true` и `APP_ENV=test`; no real/private/only-copy data; no committed `.env`, app DB, books, backups, exports, screenshots, secrets.

verification:
`git status --short`, `git rev-parse HEAD origin/main`, `git tag -l v0.2.1-writealpha`, `gh release view v0.2.1-writealpha || true`, `gh run list --limit 10`, `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`, rendered config grep, backend/frontend checks as needed for exact release commit, `git diff --check`, sensitive tracked-file scan.

expected artifacts:
`docs/release/v0.2.1-writealpha-publication-evidence.md` or `docs/release/v0.2.1-writealpha-no-release.md`, updated `PROJECT_STATUS.md`, `CHANGELOG.md`, README status if factual release state changes, `docs/handoff/phase-182.md`, commit and push.

## Phase 2 — Write-alpha restore UX/API evidence tightening

goal:
Закрыть практический риск из Phase 177/180: stale lock file после released flock и root-owned lock readability должны иметь безопасный operator workflow и тестовое покрытие без изменения write scope.

scope:
Добавить/уточнить backend helper или script-level check для различения active lock hold vs stale lock file в ignored runtime path, безопасные user-facing/operator messages без private paths, тесты на stale-lock cleanup guidance, и UI/docs support для recovery после disposable write-alpha dogfood.

non-goals:
Не добавлять lock management UI для production, не удалять lock files автоматически без явного operator action в runtime, не расширять create/PATCH/DELETE, не использовать private books.

acceptance criteria:
Disposable/test workflow может доказать: active lock блокирует write с 409, stale released lock не маскируется как active hold в evidence path, recovery guidance не раскрывает paths и не предлагает использовать real/private books.

safety checks:
Writes remain disabled by default; any write smoke uses only `APP_ENV=test` plus explicit local-only `GNUCASH_WRITES_ENABLED=true` on synthetic/disposable copy; no raw lock/book path rendered to frontend/API errors.

verification:
Targeted backend tests for lock contention/stale lock messaging, frontend static/auth-route checks if UI copy changes, rendered Compose default false, `git diff --check`, sensitive tracked-file scan.

expected artifacts:
Code/tests if needed, updated recovery/runbook docs as support, dogfood evidence with redacted metadata, `PROJECT_STATUS.md`, `docs/handoff/phase-183.md`, commit and push.

## Phase 3 — Write-alpha PATCH disposable dogfood

goal:
Получить реальное synthetic/disposable dogfood evidence для existing PATCH transaction metadata/split-memo route, сопоставимое с create evidence, без расширения функциональности.

scope:
На committed synthetic fixture copied into ignored runtime data выполнить один explicit local-only PATCH under `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=true`; проверить validate/read-back, backup, audit row, lock release, safe error behavior, return to default false, disabled validate/create/PATCH/DELETE probes.

non-goals:
Не PATCH amounts/accounts, не использовать real/private/only-copy book, не публиковать release, не добавлять new write endpoints.

acceptance criteria:
Один PATCH dogfood pass documented with bounded/redacted evidence; backup and audit exist; read-only smoke after default false passes; no runtime artifacts committed.

safety checks:
Preflight source/runtime/backup classes; `APP_ENV=test`; explicit local-only enablement only for the PATCH run; teardown removes ignored book/app DB/backups/locks; no descriptions/memos/amounts from private data.

verification:
Existing/new smoke helper output, API read-back for patched synthetic marker only, disabled-write probes return 403 after reset, Docker Compose default false, no-artifact check.

expected artifacts:
`docs/dogfood/phase-184-write-alpha-patch-dogfood.md`, optional smoke helper/tests if needed, status/handoff updates, commit and push.

## Phase 4 — Write-alpha DELETE disposable dogfood with restore proof

goal:
Получить bounded disposable evidence для existing DELETE route и доказать restore path after delete, без claim безопасной записи на real/private books.

scope:
На synthetic/disposable runtime copy выполнить один DELETE существующей synthetic transaction under explicit write-alpha gates; проверить pre-write backup, audit, transaction absence after delete, restore from backup, read-only smoke on restored copy, return to default disabled writes.

non-goals:
Не делать bulk delete, account delete, recurring delete, UI redesign, private-data dogfood, release publication.

acceptance criteria:
DELETE dogfood artifact показывает success audit, one backup, transaction absent in mutated copy, restored copy passes read-only smoke and disabled write probes; no private/raw artifacts committed.

safety checks:
Only ignored runtime copy; explicit `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=true` for one run; backup/restore under ignored paths; teardown verified; frontend delete remains hidden unless writes enabled and acknowledgement present.

verification:
API smoke before/after, DELETE route response/read-back absence, restore checksum or bounded metadata, disabled validate/create/PATCH/DELETE probes with 403, frontend route check for hidden-by-default delete UI.

expected artifacts:
`docs/dogfood/phase-185-write-alpha-delete-restore-dogfood.md`, tests/helper updates if gaps are found, status/handoff updates, commit and push.

## Phase 5 — Write-alpha audit trail review UI for disposable runs

goal:
Сделать audit evidence для write-alpha runs operator-visible в безопасной форме, не показывая private paths/raw amounts и не превращая это в production audit feature.

scope:
Добавить narrow read-only audit summary endpoint/UI or CLI report for current app DB synthetic/disposable runs: action, result, timestamp, redacted backup presence, bounded transaction id prefix, safe error text; tests verify redaction and access control.

non-goals:
Не строить полноценный audit log product, не показывать backup paths/private file paths, не добавлять multi-user admin console, не читать GnuCash book directly from frontend.

acceptance criteria:
Operator can confirm create/PATCH/DELETE write-alpha audit outcomes through safe summary; viewer/unauthorized access blocked; no secrets/paths/raw request payload leakage.

safety checks:
Endpoint is read-only app metadata only; no GnuCash mutation; no private paths in DTO/UI; auth required; writes default false unchanged.

verification:
Backend tests for auth/redaction/access, frontend checks if UI is added, dogfood with synthetic app DB only, localStorage/sessionStorage scan for no audit persistence.

expected artifacts:
Backend/frontend behavior + tests, safe UX copy, dogfood evidence, status/handoff updates, commit and push.

## Phase 6 — Multi-book read-only access regression and UX hardening

goal:
Вернуться к practical read-only MVP hardening: проверить и усилить independent-book access boundaries after write-alpha work, чтобы write-alpha не размывал read-only baseline.

scope:
Добавить regression tests/UI checks for active book selection, archived/unauthorized/missing/not-configured books, selected-book cookie recovery, transaction/account/report route families, and no write UI exposure under default false across multiple accessible independent books.

non-goals:
Не добавлять upload/delete/default-changing/registry-edit UI, не строить collaborative/family-wallet flows, не включать writes.

acceptance criteria:
Route families consistently hide/block unauthorized/archived books, recover stale selected-book cookie safely, show only redacted storage diagnostics, and keep write controls hidden by default.

safety checks:
No real book paths returned; no frontend direct file access; no localStorage/sessionStorage for selected book/auth; `GNUCASH_WRITES_ENABLED=false` remains default.

verification:
Backend route tests, frontend route/static checks, browser dogfood over synthetic multi-book fixture if feasible, storage scan for local/session storage sensitive state.

expected artifacts:
Tests/UX hardening, dogfood or route evidence, updated docs support if behavior wording changes, status/handoff updates, commit and push.

## Phase 7 — Read-only reporting correctness edge cases

goal:
Усилить money/accounting correctness для read-only dashboard/reporting before any next release claim.

scope:
Add synthetic fixture/tests for mixed-currency excluded splits, unknown `XXX` base currency, zero-balance fallback, negative/contra accounts, and drilldown link parity; UI copy must keep base-currency-only/no-conversion limitations visible.

non-goals:
Не добавлять FX conversion, forecasting, accounting engine rewrite, write behavior, external rates, or production accounting guarantee.

acceptance criteria:
Reports remain Decimal/string based, limitations are explicit, drilldowns preserve URL-filter parity, and edge-case tests prevent misleading zero/mixed-currency summaries.

safety checks:
No float money arithmetic in core paths; JSON amounts remain strings; no fake currency conversion; no private financial data.

verification:
Backend report tests, frontend route/static checks, optional synthetic benchmark smoke, grep/search for `Number(` on money-sensitive frontend paths if changed.

expected artifacts:
Code/tests/UX copy where needed, `docs/money-model.md` support update if semantics change, status/handoff updates, commit and push.

## Phase 8 — Fresh-clone install smoke v2 with published/current tags

goal:
Проверить install/upgrade confidence for current published releases and current main without reading private data.

scope:
Run/extend fresh-clone Docker smoke to cover current public read-only release, current write-alpha release/candidate state, and `main` with synthetic fixture, dummy local-only secrets, default `GNUCASH_WRITES_ENABLED=false`, API/browser dogfood, disabled write probes, and no-artifact teardown.

non-goals:
Не публиковать Docker images/packages, не test real deployments, не expose public internet, не enable writes except explicit separate disposable smoke if documented.

acceptance criteria:
Fresh clone starts, health/login/books/accounts/transactions/reports/CSV/browser flows pass; default disabled write probes return 403; no runtime artifacts survive; failures create narrow blocker artifact.

safety checks:
Only committed synthetic fixture; generated `.env` stays temp/ignored; teardown removes temp clone/runtime; no screenshots/exports/backups committed.

verification:
Smoke helper logs with redacted output, Docker Compose config default false, API/browser dogfood results, no-artifact scan.

expected artifacts:
`docs/dogfood/phase-189-fresh-clone-smoke-v2.md`, script/test updates if needed, status/handoff updates, commit and push.

## Phase 9 — Combined release-candidate dogfood after cycle-2 changes

goal:
Собрать финальное практическое evidence после фаз 2–8: default read-only regression plus explicit disposable write-alpha smoke for touched routes only.

scope:
Run Docker/Caddy default read-only API/browser dogfood with `GNUCASH_WRITES_ENABLED=false`; run separate explicit local-only write-alpha smoke for create/PATCH/DELETE only if prior phases changed or need final evidence; verify return to default false and teardown.

non-goals:
Не читать real/private books, не создавать release/tag, не expand writes, не claim production/security audit.

acceptance criteria:
Default read-only API/browser flows pass; validate/create/PATCH/DELETE probes return 403 under default false; write-alpha smoke evidence is synthetic/disposable and bounded; no runtime artifacts committed.

safety checks:
Separate read-only and write-enabled runs; `APP_ENV=test` for write smoke; explicit local `GNUCASH_WRITES_ENABLED=true` only during write smoke; default false before/after; no raw book/app DB/backup/export/screenshot.

verification:
API smoke, browser dogfood mobile+desktop if feasible, rendered config grep before/after, audit/backup/lock redacted inspection, no-artifact scan, sensitive tracked-file scan.

expected artifacts:
`docs/dogfood/phase-190-cycle-2-release-candidate-dogfood.md`, status/handoff updates, commit and push.

## Phase 10 — Cycle-2 release-readiness gate and publication/no-release artifact

goal:
Выполнить финальный release-readiness gate for cycle 2 and publish only if evidence warrants it and the exact release commit is green; otherwise produce honest no-release artifact with blockers.

scope:
Compare README/README.ru/PROJECT_STATUS/CHANGELOG/release docs/dogfood evidence/GitHub releases/actions/open issues against actual `main`; decide target release name based on changes since published release (`v0.2.2-writealpha` if cycle-2 write-alpha changes warrant maintenance pre-release, or read-only maintenance tag only if scope is read-only); verify clean tracked tree, `HEAD == origin/main`, tag/release absence, local checks, CI success, default false, sensitive hygiene; publish authorized pre-release only on PASS.

non-goals:
Не публиковать if blockers exist, не overclaim production/security/real-private-book write safety, не enable writes by default, не create/close issues, не publish packages/images.

acceptance criteria:
Either a GitHub pre-release is published with conservative notes/checklist/final gate/publication evidence, or a no-release artifact lists exact blockers and next phase; docs/status are synchronized to the factual outcome.

safety checks:
`GNUCASH_WRITES_ENABLED=false` default in `.env.example`, config, Compose render; backend gates still require explicit enablement plus `APP_ENV=test`; no real/private/only-copy data; no public-internet/security-audit/production-safe write claims.

verification:
Full backend suite or targeted plus release-critical tests as appropriate, frontend check/auth-routes/build, Docker Compose config validation, GitHub Actions on exact release commit, tag/release absence before publish, sensitive tracked-file scan, `git diff --check`.

expected artifacts:
Release notes/checklist/final-gate/publication evidence or no-release blocker artifact under `docs/release/`, updated README/README.ru/PROJECT_STATUS/CHANGELOG, `docs/handoff/phase-191.md`, tag/GitHub pre-release only if PASS, commit and push.
