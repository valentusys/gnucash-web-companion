# Cycle 2 analyst report — 2026-05-20

## Executive summary

Текущий baseline после Phase 181 здоровый для следующего практического цикла: read-only default сохранён, write-alpha остаётся experimental/post-MVP, backend gates требуют `GNUCASH_WRITES_ENABLED=true` и `APP_ENV=test`, а последние CI runs на `main` зелёные. Главный фактический release-state gap: `v0.2.1-writealpha` уже подготовлен как unpublished candidate и был остановлен только из-за отсутствия явной owner authorization в Phase 181; текущий запрос эту авторизацию даёт, но публикация всё равно должна идти через свежий pre-publish gate. PM не нужен: ниже дан narrow executable roadmap на 10 фаз, с практическими behavior/test/UX/dogfood/release artifacts и без audit-only phases. Риск, который нельзя размывать: write-alpha dogfood только на synthetic/disposable/copied test books; real/private/only-copy books, `.env`, app DB, backups, exports/screenshots и secrets не трогать.

## Verdict

Ready for next engineering phase.

Уточнение: проект не production-ready и не security-audited. `v0.2.1-writealpha` готов к отдельной публикации только после свежего gate на exact commit; дальнейший cycle-2 release в Phase 10 должен быть publish-or-no-release по evidence.

## PM decision: SKIPPED, reason

PM decision: SKIPPED.

Reason: roadmap ниже достаточно узкий и executable для прямой передачи программисту. Конфликтующих приоритетов нет: текущий baseline уже показывает следующий безопасный путь — сначала свежий gate/publish prepared `v0.2.1-writealpha` при PASS, затем practical hardening/dogfood, затем Phase 10 release-readiness gate/publication-or-no-release. Риски private data/write-mode/security/publication явно зафиксированы как safety checks внутри каждой фазы; отдельный PM нужен только если gate провалится, появится новый release/no-release спор, потребуется real/private data, или владелец изменит приоритеты.

## Current baseline/release state

- Local path: `/home/val/gnucash-web-companion`.
- Branch: `main`.
- Current HEAD during inspection: `30d6222 Phase 181 release readiness gate`.
- Working tree before analyst artifacts: only untracked `.hermes/`, ignored as telemetry.
- README/README.ru/PROJECT_STATUS/CHANGELOG say Phase 0–181 complete.
- Current public read-only pre-release: `v0.1.7-readonly`.
- Current public write-alpha pre-release: `v0.2.0-writealpha`.
- Prepared unpublished candidate: `v0.2.1-writealpha`.
- `docs/release/v0.2.1-writealpha-final-gate.md` verdict: ready for release after explicit owner authorization — prepared but unpublished.
- `gh release list --limit 10` returned releases through `v0.1.7-readonly` and `v0.2.0-writealpha`; no `v0.2.1-writealpha` release shown.
- `gh run list --limit 10` showed latest ten `main` CI runs completed/success, through Phase 181.
- `gh auth status` reports invalid stored token for account `valentusys`, but release/run/issue reads still returned data in this environment. Publication/push may still need working git/GitHub auth at execution time.
- Open issues listed by `gh issue list`: #36 controlled-write v0.2 readiness gates, #29 localization glossary, #28 markdown readability, #22 GnuCash compatibility fixtures, #17 Russian docs/UI localization, #13 book management UI.

## Safety/read-only boundary findings

- `.env.example` line 27 keeps `GNUCASH_WRITES_ENABLED=false`.
- `docker-compose.yml` uses `${GNUCASH_WRITES_ENABLED:-false}` for API and web.
- `apps/api/app/config.py` default is `gnucash_writes_enabled: bool = False`.
- Write routes in `apps/api/app/routers/transactions.py` call `_ensure_writes_enabled(settings)` and then `_ensure_write_alpha_test_scope(settings)` before write service construction for validate/create/PATCH/DELETE paths.
- `_ensure_write_alpha_test_scope` blocks enabled write-alpha routes unless `APP_ENV=test`.
- Frontend write UI is gated by `env.GNUCASH_WRITES_ENABLED === 'true'`; `/transactions/new` redirects back to `/transactions` when disabled.
- `localStorage` usage found only for theme (`apps/web/src/lib/theme.ts` and `app.html`), not auth/session/book/write state.
- Phase 180 dogfood confirms default read-only API/browser flows pass and validate/create/PATCH/DELETE probes return 403 under default false.

## Top blockers

1. No release blocker for next engineering phase.
2. Publication blocker for `v0.2.1-writealpha`: must run a fresh pre-publish gate on exact current release commit; Phase 181 gate was prepared before this analyst artifact and before explicit authorization.
3. Operational blocker for GitHub write operations may appear: `gh auth status` reports invalid token, even though read commands worked. If tag/release/push fail, stop with no-release/auth-blocked artifact instead of guessing credentials.

## Important non-blockers

1. `v0.2.1-writealpha` being unpublished is not a safety blocker; it is a controlled publication-state gap with prepared artifacts.
2. Open issues #13/#17/#22/#28/#29/#36 are meaningful backlog/state items, but none blocks the next practical cycle if scope stays narrow and evidence-bound.
3. Theme `localStorage` is acceptable; no auth/session token storage in localStorage/sessionStorage was found by the inspected search.
4. CORS wildcard remains documented as development default with warnings; do not claim production security readiness.

## План на 10 фаз

1. Phase 1 — Публикация prepared v0.2.1-writealpha под свежим gate
   - Практический результат: fresh gate, publication evidence или no-release artifact.
   - Release/safety: publish only if exact commit is green; no packages/images; writes default false.

2. Phase 2 — Write-alpha restore UX/API evidence tightening
   - Практический результат: stale lock vs active lock behavior/tests/operator evidence.
   - Safety: no automatic unsafe cleanup, no raw paths, synthetic/disposable only.

3. Phase 3 — Write-alpha PATCH disposable dogfood
   - Практический результат: one bounded PATCH dogfood pass with backup/audit/read-back/default-false reset.
   - Safety: no amounts/accounts PATCH expansion, no private books.

4. Phase 4 — Write-alpha DELETE disposable dogfood with restore proof
   - Практический результат: DELETE dogfood plus restore-from-backup proof.
   - Safety: one synthetic/disposable transaction only, teardown/no-artifacts.

5. Phase 5 — Write-alpha audit trail review UI for disposable runs
   - Практический результат: safe read-only audit summary behavior/tests/UX.
   - Safety: app metadata only, redacted backup/path details, auth/access control.

6. Phase 6 — Multi-book read-only access regression and UX hardening
   - Практический результат: route-family regression and UX hardening for independent books.
   - Safety: no management/write UI, no raw `uri_or_path`, no browser-sensitive storage.

7. Phase 7 — Read-only reporting correctness edge cases
   - Практический результат: synthetic accounting/reporting edge-case tests and UX copy.
   - Safety: Decimal/string money, no FX conversion, no production accounting guarantee.

8. Phase 8 — Fresh-clone install smoke v2 with published/current tags
   - Практический результат: reproducible fresh-clone Docker smoke evidence with synthetic fixture.
   - Safety: temp dummy `.env`, default false, no screenshots/exports/backups committed.

9. Phase 9 — Combined release-candidate dogfood after cycle-2 changes
   - Практический результат: default read-only API/browser dogfood plus explicit disposable write-alpha smoke if needed.
   - Safety: separate read-only/write-enabled runs; default false before/after; no private artifacts.

10. Phase 10 — Cycle-2 release-readiness gate and publication/no-release artifact
   - Практический результат: final gate and either conservative pre-release publication or honest no-release blockers.
   - Safety: no publish on blocker, no production/security/real-private-book write-safety claims, default false preserved.

Strict machine-readable roadmap with exactly ten `## Phase N — ...` sections is written separately to `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-2-roadmap.md`.

## What not to do next

- Do not run another audit-only cycle before doing practical gate/dogfood/hardening work.
- Do not enable `GNUCASH_WRITES_ENABLED=true` by default.
- Do not use real/private/only-copy GnuCash books for write-alpha dogfood.
- Do not claim production readiness, security audit, public-internet safety, broad GnuCash compatibility, or real/private-book write safety.
- Do not create/close GitHub issues in this analyst phase.
- Do not publish packages, Docker images, or broad marketing announcements.
- Do not read or commit `.env`, app DBs, real books, backups, screenshots, CSV exports, tokens, certs, keys, or private paths.
- Do not let frontend-only write gating substitute for backend gates.
- Do not treat `v0.2.1-writealpha` as published until the tag/GitHub release and publication evidence exist.
