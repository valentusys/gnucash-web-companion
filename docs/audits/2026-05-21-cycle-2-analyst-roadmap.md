# Цикл 2/3 — отчёт аналитика и 10-фазный roadmap

Дата: 2026-05-21
Репозиторий: `/home/val/gnucash-web-companion`
Режим: аналитик проекта, без изменения product code
Внешний roadmap: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-2/roadmap-cycle-2.md`

## Executive summary

Текущий `main` после cycle 1 находится в рабочем pre-alpha состоянии для следующего инженерного цикла. Последний опубликованный артефакт — `v0.2.4-writealpha` GitHub pre-release; последние 10 CI запусков по `main` зелёные; `HEAD == origin/main` до создания этого аналитического артефакта. Read-only boundary сохранён: `.env.example`, backend defaults и rendered Docker Compose держат `GNUCASH_WRITES_ENABLED=false`, write-alpha остаётся experimental, explicit `APP_ENV=test` + disposable/synthetic only. Главная находка аудита: `docs/ROADMAP.md` заметно отстал и всё ещё описывает Phase 172 / `v0.2.0-writealpha` как current posture; это не runtime safety blocker, но это release/docs drift, который должен быть первой практической фазой cycle 2 с автоматическим guard, а не очередным audit-only loop.

## Verdict

Ready for next engineering phase.

Не означает production/stable readiness. Означает: можно запускать прямой 10-фазный engineering cycle без ПМ, если фазы сохранят `GNUCASH_WRITES_ENABLED=false` по умолчанию, не используют real/private books и доведут Phase 10 до conservative pre-release gate или явного no-release verdict.

## Top blockers

1. Для следующего engineering cycle: нет runtime blocker.
2. Для следующего релиза: `docs/ROADMAP.md` stale и должен быть синхронизирован/закреплён automated status guard до release gate.
3. Для production/stable/public-safe claims: нет security audit, broad compatibility evidence и real/private-book write safety.
4. Для real/private write safety: write-alpha evidence остаётся synthetic/disposable only; реальные/private/only-copy книги запрещены.

## Important non-blockers

1. `GNUCASH_WRITES_ENABLED=false` присутствует в `.env.example`; `apps/api/app/config.py` default — `gnucash_writes_enabled: bool = False`.
2. Backend write routes содержат `_ensure_writes_enabled(settings)` and `_ensure_write_alpha_test_scope(settings)` before write service construction.
3. Frontend write UI/actions gated by `env.GNUCASH_WRITES_ENABLED === 'true'`; auth token хранится в httpOnly cookie; найденный `localStorage` — theme preference only.
4. Phase 209/210 dogfood evidence свежая: default-read-only API/browser dogfood с 403 write probes и отдельная bounded write-alpha create/PATCH/DELETE+restore evidence на synthetic/disposable copies.
5. GitHub issues осмысленные, без backlog theater: #36, #29, #28, #22, #17, #13.

## Проверенные области

- `README.md`: актуален до Phase 211, честно говорит pre-alpha/read-only-first/not production/not security-audited; current release links include `v0.2.4-writealpha`.
- `PROJECT_STATUS.md`: актуален до Phase 211 and `v0.2.4-writealpha`, но очень большой и требует не расширять audit churn без необходимости.
- `CHANGELOG.md`: содержит `0.2.4-writealpha` section; `Unreleased` пустой до новых артефактов, что корректно.
- `.env.example`: default `GNUCASH_WRITES_ENABLED=false`, CORS wildcard помечен как development default with LAN/VPN exact-origin guidance.
- `docs/release`: `v0.2.4-writealpha` notes/checklist/final-gate/publication-evidence присутствуют.
- `docs/dogfood`: Phase 209 default-readonly and Phase 210 bounded write-alpha evidence present, redacted, synthetic/disposable only.
- `docs/ROADMAP.md`: stale current posture says completed through Phase 172 and current write-alpha `v0.2.0-writealpha`; это docs/release consistency defect for cycle 2.
- `apps/api`: write-gating and Decimal/string money paths remain visible; write-alpha tests assert defaults and disabled endpoints.
- `apps/web`: httpOnly auth cookie set on login; no auth localStorage/sessionStorage found; write UI gated.
- `.github/workflows`: recent GitHub Actions on main are successful.
- GitHub releases/actions/issues: latest release list starts with `v0.2.4-writealpha`; latest 10 CI runs successful.

## Last 10 commits classification

| commit | type | user impact |
| --- | --- | --- |
| 8b6412b Phase 211 cycle1 v0.2.4-writealpha release gate | release | Published conservative `v0.2.4-writealpha` pre-release after green gate. |
| f578a1a Phase 210 cycle-1 write-alpha CRUD restore dogfood | tests | Fresh bounded write-alpha create/PATCH/DELETE+restore evidence on disposable copies. |
| aec7926 Phase 209 cycle1 default readonly dogfood refresh | tests | Reconfirmed default read-only API/browser behavior and 403 write probes. |
| f0d798d Phase 208 cycle1 frontend safety locale polish | code | Safer EN/RU operator safety copy without full-localization claim. |
| cb0f5e0 Phase 207 cycle1 audit-summary redaction hardening | code | Hardened redacted audit-summary endpoint/UI. |
| 4a166b7 Phase 206 cycle1 transaction scheduled readonly polish | code | Read-only transaction/scheduled edge-case UX/test hardening. |
| 7e972b1 Phase 205 cycle1 multi-book read-only recovery polish | code | Improved safe multi-book recovery for unavailable/inaccessible contexts. |
| b8d2845 Phase 204 cycle1 compatibility matrix regression | tests | Better compatibility-matrix regression and evidence boundaries. |
| 5db657f Phase 203 cycle 1 desktop fixture capture path | tests | Advanced Desktop fixture blocker/provenance path without broad claims. |
| b044a3d Phase 202 cycle 1 read-only first-run health drill | code | Better redacted first-run/read-only diagnostics. |

Итог: это не audit-only loop; последние 10 commits — практические code/tests/dogfood/release changes.

## Safety boundary

- Default write posture сохранён: `.env.example` line 27 has `GNUCASH_WRITES_ENABLED=false`; rendered Compose shows API and web `GNUCASH_WRITES_ENABLED: "false"`.
- Backend Settings default false; write routes call feature gate before write operations.
- Write-alpha execution remains explicitly local/test/disposable: `APP_ENV=test` gate documented and enforced in route guard.
- Phase 209 verified default false read-only API/browser flow and 403 validate/create/PATCH/DELETE probes.
- Phase 210 verified bounded write-alpha route-family evidence under explicit `APP_ENV=test` + `GNUCASH_WRITES_ENABLED=true`, then reset to default false.
- No evidence of real/private books, committed runtime book/app DB/backups, `.env`, secrets, screenshots, exports, tokens, keys, certs.

## Release/docs consistency

- README/PROJECT_STATUS/CHANGELOG/release docs agree on `v0.2.4-writealpha` and Phase 211.
- Release docs deny production readiness, security audit, broad compatibility, public-internet safety, and real/private write safety.
- GitHub release list confirms `v0.2.4-writealpha` as latest pre-release.
- Defect: `docs/ROADMAP.md` still says completed through Phase 172 and current write-alpha `v0.2.0-writealpha`. This should be fixed in Phase 1 of cycle 2 with a status consistency guard.

## GitHub project state

Open issues from `gh issue list`:

1. #36 — Track remaining controlled-write v0.2 readiness gates.
2. #29 — Add localization glossary for accounting terms.
3. #28 — Improve markdown source readability before wider announcement.
4. #22 — Add compatibility fixtures from real GnuCash versions.
5. #17 — Plan Russian documentation and UI localization.
6. #13 — Book management UI.

Latest releases:

- `v0.2.4-writealpha` — pre-release, 2026-05-20/21 boundary in local docs, latest listed by GitHub.
- `v0.2.3-writealpha`, `v0.2.2-writealpha`, `v0.2.1-writealpha`.
- `v0.1.7-readonly` remains current read-only pre-release.

Latest Actions:

- Last 10 `main` CI runs completed successfully, including Phase 211 release gate and cycle-1 dogfood phases.

## Dogfood status

- Latest default read-only dogfood: Phase 209, PASS. Docker/Caddy, synthetic fixture, `GNUCASH_WRITES_ENABLED=false`, API smoke, browser dogfood at mobile/desktop, hidden write UI, 403 write probes, no artifacts.
- Latest write-alpha dogfood: Phase 210, PASS. Synthetic/disposable copied fixture, explicit `APP_ENV=test` + `GNUCASH_WRITES_ENABLED=true`, create/PATCH/DELETE+restore evidence, backup/audit/lock evidence, default false reset.
- No real/private-book write safety is claimed. This is correct.
- Next cycle should add post-release tagged fresh-clone smoke for `v0.2.4-writealpha` and an upgrade/app-metadata preservation smoke rather than repeat the exact cycle-1 phases.

## Security/auth notes

- JWT secret is not hardcoded as a real secret; `.env.example` uses a placeholder that docs require replacing.
- Auth cookie is set `httpOnly: true` in web login server route.
- No auth/session token storage in `localStorage` or `sessionStorage` found; theme preference uses localStorage only.
- CORS wildcard remains development default with explicit warning to narrow for LAN/VPN.
- SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, LICENSE exist.
- No security audit has been performed; docs correctly do not claim one.

## Money/accounting notes

- Backend money paths use `Decimal` and string DTOs; schemas document decimal strings.
- CSV/export paths preserve decimal-string posture and documented caps/limitations.
- No fake FX conversion is claimed; base-currency-only/no-conversion limitations remain documented.
- Split transactions are handled in read-only UI and write-alpha evidence without claiming production-safe writes.

## ПМ escalation decision

ПМ не призывался.

Причина: scope and release criteria are explicit enough from the user prompt and repository evidence. No escalation criteria triggered: no safety blocker requiring product decision, no unclear owner preference, no irreversible action beyond committing intended analyst artifacts, and no need to alter product scope. Roadmap prepared directly for programmer.

## План на 10 фаз PM→программист

ПМ не нужен и не призывался. План практический, не audit-only; каждая фаза обязана давать behavior/test/UX/dogfood/release artifact. Документация — только поддержка.

1. Phase 1 — Public status drift guard
2. Phase 2 — v0.2.4 tagged fresh-clone smoke
3. Phase 3 — Synthetic upgrade and app-metadata preservation smoke
4. Phase 4 — Read-only unavailable-book error contract hardening
5. Phase 5 — Read-only CSV/export and list parity regression pack
6. Phase 6 — Write-alpha backup-failure and no-mutation drill
7. Phase 7 — Write-alpha audit-summary pagination and operator review UX
8. Phase 8 — Accounting/safety localization glossary applied slice
9. Phase 9 — Cycle-2 full default-readonly and bounded write-alpha dogfood
10. Phase 10 — v0.2.5-writealpha release gate/publication or explicit no-release verdict

Strict external roadmap written to:
`/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-2/roadmap-cycle-2.md`

## Recommended next action

Запустить программиста напрямую по external roadmap cycle-2, starting with Phase 1 public status drift guard. Не запускать ПМ. Не начинать account/import/scheduled write expansion; keep write-alpha create/PATCH/DELETE only, default false, `APP_ENV=test` gate, synthetic/disposable evidence.

## Suggested GitHub issues

Не создавать новые issues сейчас. Использовать существующие:

1. #36 for controlled-write readiness gate tracking.
2. #22 for Desktop fixture/compatibility work if Phase 2/3 touches compatibility evidence.
3. #13 for read-only multi-book unavailable-book UX only, without registry management writes.
4. #17/#29 for the narrow localization glossary applied slice.
5. #28 only if markdown source readability becomes a real release/publication blocker.

## What not to do next

- Не включать `GNUCASH_WRITES_ENABLED=true` по умолчанию.
- Не использовать real/private/only-copy books.
- Не ослаблять `APP_ENV=test` gate for write-alpha.
- Не заявлять stable/production/security-audited/public-internet-safe status.
- Не расширять write scope до account/import/scheduled writes.
- Не публиковать release в Phase 10, если Phases 1–9 не дали safe meaningful evidence.
- Не запускать audit-only loop вместо practical engineering phases.
