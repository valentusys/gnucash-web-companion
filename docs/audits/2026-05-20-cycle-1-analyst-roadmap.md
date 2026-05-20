# Цикл 1/3 — отчёт аналитика и 10-фазный roadmap

Дата: 2026-05-20
Репозиторий: `/home/val/gnucash-web-companion`
Режим: аналитик проекта, без изменения product code
Внешний roadmap: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-1/roadmap-cycle-1.md`

## Executive summary

Проект находится в здоровом pre-alpha состоянии для следующего инженерного цикла: последний опубликованный артефакт — `v0.2.3-writealpha` GitHub pre-release, CI по последним 10 пушам зелёный, read-only default сохранён. Релизные документы, README, CHANGELOG и PROJECT_STATUS синхронизированы до Phase 201 и честно удерживают границы: не production-ready, не security-audited, write-alpha только experimental/test/disposable. Блокера для следующей инженерной 10-фазной итерации нет. Блокеры для stable/production/public-safe claims остаются: нет real/private-book write safety, нет широкой Desktop/backend compatibility, нет security audit.

## Verdict

Ready for next engineering phase.

Не означает production/stable readiness. Означает, что можно безопасно запускать следующий узкий практический 10-фазный цикл с сохранением `GNUCASH_WRITES_ENABLED=false` по умолчанию и с публикацией только conservative pre-release в Phase 10, если фазы 1–9 дадут зелёные evidence.

## Top blockers

1. Для следующего engineering cycle: None.
2. Для production/stable claims: нет security audit и нельзя заявлять production readiness.
3. Для real/private write safety: write-alpha evidence остаётся synthetic/disposable only; реальные/private/only-copy книги запрещены.
4. Для broad compatibility claims: GitHub #22 остаётся открытым; нет достаточного набора Desktop-generated fixture coverage.

## Important non-blockers

1. `GNUCASH_WRITES_ENABLED=false` есть в `.env.example`, backend Settings default — `False`, Docker release gates проверяли rendered false.
2. Backend write routes вызывают feature gate и `APP_ENV=test` gate до создания write service.
3. Frontend write UI и write actions gated by `GNUCASH_WRITES_ENABLED === 'true'`; auth token хранится в httpOnly cookie, browser storage используется только для theme preference.
4. Последние Phase 199/200 dogfood artifacts дают свежую default-read-only regression evidence и отдельную bounded write-alpha CRUD/restore evidence на synthetic/disposable copies.
5. GitHub Actions последние 10 запусков по `main` завершились success.

## Проверенные области

- README.md: актуален до Phase 201, подчёркивает pre-alpha/read-only-first/not production/not security-audited.
- PROJECT_STATUS.md: актуален до Phase 201 и `v0.2.3-writealpha`.
- CHANGELOG.md: содержит `0.2.3-writealpha`, `Unreleased` пустой, что совпадает с clean baseline.
- .env.example: `GNUCASH_WRITES_ENABLED=false`, CORS wildcard снабжён предупреждением для development-only.
- docs/release: `v0.2.3-writealpha` notes/checklist/final-gate/publication-evidence присутствуют.
- docs/dogfood: Phase 200 write-alpha disposable dogfood записан, Phase 199 упомянут в release/status docs как default-read-only regression dogfood.
- apps/api: write gate расположен в backend, default false в Settings, write-alpha дополнительно ограничен `APP_ENV=test`.
- apps/web: auth-route tests закрепляют httpOnly cookie, no auth localStorage/sessionStorage, write UI gating.
- .github/workflows: CI проверяет required files, sensitive tracked files, frontend checks, backend pytest, Docker Compose config.
- GitHub: latest releases include `v0.2.3-writealpha`; open issues meaningful, no noisy backlog theater detected.

## Last 10 commits classification

| commit | type | user impact |
| --- | --- | --- |
| eb90a38 Phase 201 cycle-3 release gate | release | Published conservative `v0.2.3-writealpha` pre-release after green gate. |
| 3c306e6 Phase 200 write-alpha disposable dogfood | tests | Added bounded write-alpha CRUD/restore evidence on disposable copies. |
| 3aba57a Phase 199 default read-only regression dogfood | tests | Reconfirmed default read-only API/browser behavior and 403 write probes. |
| 530c068 Phase 198 multi-book diagnostics hardening | code | Safer multi-book diagnostics/recovery without exposing paths or management writes. |
| 1ec2ddc Phase 197 desktop fixture blocker refresh | tests | Improved compatibility blocker evidence without broad claims. |
| cddbf4a Phase 196 first-run diagnostics | code | Better redacted first-run/read-only diagnostics. |
| 56dbbd4 Phase 195 audit summary UX hardening | code | Safer read-only write-alpha audit-summary UX. |
| 65d783d Phase 194 write-alpha smoke helper resilience | tests | More reliable smoke evidence collection with root-owned artifact fallback. |
| f3e14e4 Phase 193 runtime cleanup helper | code | Safer stopped-runtime cleanup/recovery tooling. |
| ea590fe Phase 192 CI warning cleanup | tests | Removed non-blocking GitHub Actions Node 20 warnings; no runtime behavior change. |

Итог: последние 10 коммитов не являются audit-only loop; это практические code/tests/release изменения с release evidence.

## Safety boundary

- Default write posture сохранён: `.env.example` содержит `GNUCASH_WRITES_ENABLED=false`; `apps/api/app/config.py` содержит `gnucash_writes_enabled: bool = False`.
- Backend write endpoints имеют `_ensure_writes_enabled(settings)` и `_ensure_write_alpha_test_scope(settings)`; при disabled writes возвращают 403.
- Write-alpha execution допускается только при explicit enablement и `APP_ENV=test`; нормальный runtime должен оставаться false.
- Phase 200 evidence подтверждает default-false reset и 403 для validate/create/PATCH/DELETE probes.
- Нет evidence, что реальные/private книги использовались или коммитились; tracked sensitive-file scan локально не нашёл `.env`, secrets, private keys, runtime GnuCash DB/book/backups.

## Release/docs consistency

- README/CHANGELOG/PROJECT_STATUS совпадают по latest state: Phase 201 complete, `v0.2.3-writealpha` current write-alpha pre-release, `v0.1.7-readonly` current read-only pre-release.
- Release notes честно говорят: pre-alpha, experimental, disabled by default, no production/security/real-private-book write safety claims.
- `CHANGELOG.md` has `Unreleased: No unreleased changes yet`, что корректно до создания этих analyst artifacts.
- Новая 10-фазная дорожная карта должна привести к `v0.2.4-writealpha` только если будут практические изменения/evidence после `v0.2.3-writealpha`.

## GitHub project state

Open issues from `gh issue list`:

- #36 Track remaining controlled-write v0.2 readiness gates
- #29 Add localization glossary for accounting terms
- #28 Improve markdown source readability before wider announcement
- #22 Add compatibility fixtures from real GnuCash versions
- #17 Plan Russian documentation and UI localization
- #13 Book management UI

Latest releases from `gh release list`:

- `v0.2.3-writealpha` pre-release, 2026-05-20
- `v0.2.2-writealpha` pre-release
- `v0.2.1-writealpha` pre-release
- `v0.1.7-readonly` pre-release

Latest Actions from `gh run list`: последние 10 `main` CI runs — completed/success.

## Dogfood status

- Phase 199: default-read-only Docker/Caddy API/browser regression dogfood with disabled validate/create/PATCH/DELETE probes returning 403.
- Phase 200: bounded write-alpha create/PATCH/DELETE/restore dogfood on synthetic/disposable copies only, then reset to `GNUCASH_WRITES_ENABLED=false`.
- Нет real/private-book dogfood claim. Это правильно; следующий цикл не должен требовать или использовать real/private books.

## Security/auth notes

- JWT secret не захардкожен как рабочий secret; `.env.example` placeholder требует замены.
- Auth cookie закреплён как httpOnly в web tests; protected routes read cookie server-side.
- localStorage/sessionStorage в `apps/web/src` найден только для theme preference и bootstrap theme script, не для auth/session/financial state.
- CORS wildcard остаётся dev default, но `.env.example` предупреждает narrow exact origins for LAN/VPN and avoid wildcard outside single-machine development.
- SECURITY.md/CONTRIBUTING.md/CODE_OF_CONDUCT.md/LICENSE присутствуют.

## Money/accounting notes

- Core backend paths используют `Decimal` и string money DTO behavior; `format_money` rejects floats.
- CSV/export docs and UI keep decimal strings and no currency conversion claims.
- Multi-currency limitations documented as base-currency-only/no conversion; fake FX conversion не заявлена.
- Split transactions представлены честно; write-alpha CRUD remains experimental only.

## План на 10 фаз PM→программист

ПМ не нужен и не призывался: scope достаточно ясен, escalation criteria не сработали. Дорожная карта ниже практическая: каждая фаза должна дать behavior/test/UX/dogfood/release artifact, документация только поддерживает evidence.

1. Phase 1 — Read-only first-run health drill
2. Phase 2 — Disposable Desktop fixture capture path
3. Phase 3 — Compatibility matrix regression from fixture metadata
4. Phase 4 — Multi-book read-only recovery polish
5. Phase 5 — Transaction and scheduled read-only edge-case polish
6. Phase 6 — Write-alpha audit-summary redaction hardening
7. Phase 7 — Frontend safety/locale polish for operator flows
8. Phase 8 — Default-read-only full dogfood refresh
9. Phase 9 — Bounded disposable write-alpha CRUD/restore refresh
10. Phase 10 — `v0.2.4-writealpha` release gate/publication or explicit no-release verdict

Strict external roadmap written to:
`/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-1/roadmap-cycle-1.md`

## Recommended next action

Запустить программиста напрямую по внешнему roadmap cycle-1. Не запускать ПМ. Не начинать v0.2 write expansion beyond existing create/PATCH/DELETE; цель цикла — safety/evidence/read-only UX hardening и conservative pre-release gate.

## Suggested GitHub issues

Не создавать новые issues сейчас. Использовать существующие:

1. #22 для Desktop fixture/compatibility work.
2. #36 для controlled-write readiness gate tracking.
3. #13 для read-only multi-book UX slice only, без registry management writes.
4. #17/#29 для узкой localization/operator wording поддержки, если фазы требуют.

## What not to do next

- Не включать `GNUCASH_WRITES_ENABLED=true` по умолчанию.
- Не использовать real/private/only-copy books.
- Не ослаблять `APP_ENV=test` gate for write-alpha.
- Не публиковать stable/production/security-audited claims.
- Не расширять write scope до account/import/scheduled writes.
- Не запускать audit-only loop вместо практических фаз.
