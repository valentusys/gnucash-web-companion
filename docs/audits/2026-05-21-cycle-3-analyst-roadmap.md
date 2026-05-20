# Цикл 3/3 — отчёт аналитика и 10-фазный roadmap

Дата: 2026-05-21
Репозиторий: `/home/val/gnucash-web-companion`
Режим: аналитик проекта, без изменения product code
Внешний roadmap: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-3/roadmap-cycle-3.md`

## Executive summary

Текущий `main` после cycle 2 находится в безопасном состоянии для следующего инженерного цикла, но не готов к новой write-alpha публикации. Последний опубликованный write-alpha release остаётся `v0.2.4-writealpha`; Phase 221 корректно отказалась публиковать `v0.2.5-writealpha` из-за Phase 220 DELETE backup-count anomaly. Read-only boundary сохранён: `.env.example` держит `GNUCASH_WRITES_ENABLED=false`, backend default `gnucash_writes_enabled=false`, write routes feature-gated, frontend write UI hidden unless explicitly enabled, auth token remains httpOnly cookie. GitHub Actions показывают последние 10 запусков mixed: последние два (`Phase 220`, `Phase 221`) зелёные, но Phase 216–219 имели failed runs на промежуточных commits; это не блокирует следующий engineering cycle, но Phase 10 release gate обязан проверять exact release/status commit CI. Следующий цикл должен быть практическим: сначала закрыть DELETE backup/audit artifact mismatch, затем собрать fresh evidence pack и только потом публиковать `v0.2.5-writealpha` или снова оформить no-release verdict.

## Verdict

Ready after blockers fixed.

Расшифровка: проект готов к следующему engineering cycle без ПМ, но не готов к релизу сейчас. Release blocker один и конкретный: Phase 220 write-alpha DELETE backup-count anomaly. Production/stable/security-audited readiness не заявляется.

## Top blockers

1. Release blocker for `v0.2.5-writealpha`: Phase 220 produced three successful backup-bearing write-alpha audit rows (create/PATCH/DELETE) but only two readable backup files after DELETE evidence collection.
2. Exact release-commit CI must be green before any Phase 10 publication; recent main history includes failed intermediate CI runs for Phases 216–219 even though later Phase 220/221 runs are green.
3. Real/private-book write safety remains blocked by design: all write-alpha evidence is synthetic/disposable only, `APP_ENV=test` gated, and unsafe for real/private/only-copy books.

## Important non-blockers

1. No runtime read-only safety blocker found: default read-only dogfood in Phase 220 passed with `GNUCASH_WRITES_ENABLED=false` and validate/create/PATCH/DELETE probes returning 403.
2. Phase 221 release gate failed safely: no `v0.2.5-writealpha` tag, GitHub release, package, image, or production deployment was published.
3. README/PROJECT_STATUS/CHANGELOG/docs/ROADMAP now consistently record completed Phase 221, current read-only release `v0.1.7-readonly`, current write-alpha release `v0.2.4-writealpha`, and the no-release verdict for `v0.2.5-writealpha`.
4. Frontend auth token storage remains httpOnly-cookie based; `localStorage` usage found is theme preference only.
5. GitHub open issues are meaningful and small: #36, #29, #28, #22, #17, #13; no noisy backlog theater needed.

## Проверенные области

- `README.md`: current status says Phase 0–221 complete, read-only by default, current read-only release `v0.1.7-readonly`, current write-alpha release `v0.2.4-writealpha`, and `v0.2.5-writealpha` no-release due to DELETE backup-count anomaly.
- `README.ru.md`: present and follows the same conservative positioning.
- `PROJECT_STATUS.md`: very large but current baseline says completed through Phase 221 and records the current release/no-release posture.
- `CHANGELOG.md`: Unreleased includes Phase 221 no-release gate and Phase 220 dogfood blocker; published section for `0.2.4-writealpha` remains latest write-alpha release.
- `.env.example`: `GNUCASH_WRITES_ENABLED=false`; `JWT_SECRET` placeholder requires replacement; CORS wildcard remains development default with exact-origin LAN/VPN guidance.
- `docs/release`: `v0.2.5-writealpha-*` artifacts include checklist/final-gate/no-release verdict; final gate says FAIL and no release published.
- `docs/dogfood`: Phase 220 records default-read-only PASS and bounded write-alpha CREATE/PATCH PASS, DELETE BLOCKED by backup-count anomaly.
- `docs/audits`: cycle-2 analyst report exists; this report supersedes it for cycle 3 and does not repeat completed/equivalent phases.
- `apps/api`: config default false; write routes call `_ensure_writes_enabled(settings)` before write service construction; money paths use `Decimal` and string schemas.
- `apps/web`: write UI gated by `data.writesEnabled` / `env.GNUCASH_WRITES_ENABLED === 'true'`; auth tokens are not in localStorage/sessionStorage; theme is the only localStorage use found.
- `.github/workflows`: recent runs inspected through `gh run list`; latest two main runs are success, earlier intermediate phase runs include failures.
- GitHub releases/actions/issues: latest GitHub release is `v0.2.4-writealpha`; no `v0.2.5-writealpha` release listed; open issue #36 remains the controlled-write readiness tracker.

## Last 10 commits classification

| commit | type | user impact |
| --- | --- | --- |
| f8e34cb Phase 221 cycle 2 no-release gate | release | Failed safely; recorded no-release verdict for `v0.2.5-writealpha`, no publication. |
| f2b2fd6 Phase 220 cycle-2 release-candidate dogfood | tests | Default read-only PASS; write-alpha DELETE backup-count blocker discovered. |
| bf62f59 Phase 219 cycle 2 accounting safety localization glossary | code | Added EN/RU safety/accounting wording guardrails. |
| 7e90419 Phase 218 cycle2 audit-summary pagination UX | code | Added bounded audit-summary pagination/operator UX. |
| 1430ff9 Phase 217 cycle 2 backup-failure safety drill | tests | Added write-alpha backup-failure/no-mutation coverage. |
| e1ea6fc Phase 216 cycle 2 CSV list export parity regressions | tests | Added read-only CSV/list parity and no-browser-storage/money-coercion guards. |
| f8c9cbc Phase 215 cycle 2 unavailable book recovery hardening | code | Hardened unavailable/missing/not-configured book contracts. |
| 713d8bf Phase 214 cycle 2 synthetic upgrade smoke | tests | Added synthetic upgrade smoke from `v0.2.4-writealpha`. |
| 9d12d07 Phase 213 cycle 2 tagged fresh-clone smoke | tests | Verified `v0.2.4-writealpha` fresh-clone default-disabled smoke. |
| fedc892 Phase 212 cycle 2 public status drift guard | tests | Added/updated public status drift guard. |

Итог: последние 10 commits — practical code/tests/dogfood/release changes, не audit-only loop.

## Safety boundary

- `GNUCASH_WRITES_ENABLED=false` remains default in `.env.example`.
- Backend `Settings` default is `gnucash_writes_enabled: bool = False`.
- Write routes in `apps/api/app/routers/transactions.py` call `_ensure_writes_enabled(settings)` before routed write behavior and keep the explicit test/disposable boundary copy.
- Phase 220 default-read-only smoke passed and disabled validate/create/PATCH/DELETE probes returned 403.
- Phase 221 did not change product code, write routes, gates, runtime defaults, package/image/release state, or any real/private data.
- No real/private books, app DBs, backups, `.env`, screenshots, exports, tokens, keys, certs, raw private paths, account names, memos, amounts, or private financial data were found in intended tracked changes.

## Release/docs consistency

- Current GitHub release list starts with `v0.2.4-writealpha`; `v0.2.5-writealpha` is absent.
- README/PROJECT_STATUS/CHANGELOG/docs/ROADMAP/release docs agree that Phase 221 completed and `v0.2.5-writealpha` was not published.
- Release docs correctly deny production readiness, security audit, broad compatibility, public-internet safety, and real/private-book write safety.
- `v0.2.5-writealpha` should only be attempted again after a practical remediation and fresh bounded evidence pack.

## GitHub project state

Open issues from `gh issue list`:

1. #36 — Track remaining controlled-write v0.2 readiness gates.
2. #29 — Add localization glossary for accounting terms.
3. #28 — Improve markdown source readability before wider announcement.
4. #22 — Add compatibility fixtures from real GnuCash versions.
5. #17 — Plan Russian documentation and UI localization.
6. #13 — Book management UI.

Latest releases from `gh release list`:

- `v0.2.4-writealpha` — latest write-alpha pre-release.
- `v0.2.3-writealpha`, `v0.2.2-writealpha`, `v0.2.1-writealpha` — previous write-alpha pre-releases.
- `v0.1.7-readonly` — current public read-only pre-release.

Latest Actions:

- `Phase 221 cycle 2 no-release gate` — success.
- `Phase 220 cycle-2 release-candidate dogfood` — success.
- Phase 216–219 runs listed as failure on their pushed commits; do not rely on “latest 10 all green” language. Phase 10 must verify exact release/status commit CI.

## Dogfood status

- Latest default-read-only dogfood: Phase 220, PASS. Docker/Caddy, synthetic fixture, `GNUCASH_WRITES_ENABLED=false`, API smoke, mobile/desktop browser dogfood, hidden write UI, 403 write probes, no raw artifacts.
- Latest write-alpha dogfood: Phase 220, PARTIAL/BLOCKED. CREATE and PATCH passed; DELETE route succeeded but backup file count did not increase by exactly one and backup-bearing audit rows outnumbered backup files.
- Next practical dogfood target: reproduce/remediate DELETE backup-count anomaly, then rerun DELETE restore proof, combined create/PATCH/DELETE evidence matrix, default-read-only regression, fresh-clone/upgrade smoke, and final release-candidate dogfood.

## Security/auth notes

- JWT secret is not hardcoded as a real secret; `.env.example` contains a placeholder and docs require replacement.
- Auth cookie remains httpOnly in the web login route model; no auth/session token localStorage/sessionStorage usage found.
- CORS wildcard remains a development default and is documented as unsafe outside single-machine development; exact LAN/VPN origins are recommended.
- SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, LICENSE, and README.ru.md exist.
- No professional security audit exists; docs correctly avoid claiming one.

## Money/accounting notes

- Backend transaction filters and write service use `Decimal`; schemas expose money as decimal strings.
- CSV/list parity got recent regression coverage in Phase 216; no fake currency conversion is claimed.
- Split transactions are handled in read-only UI and write-alpha evidence, but write-alpha remains synthetic/disposable only.
- The next cycle must not introduce float money arithmetic, raw amount leakage in reports, or account/import/scheduled write scope.

## ПМ escalation decision

ПМ не призывался.

Причина: критерии следующего цикла достаточно явные. Есть один конкретный engineering blocker (DELETE backup-count anomaly), понятные safety constraints, явный Phase 10 release/no-release gate, и нет необходимости менять product scope or owner policy. Эскалация к ПМ не обязательна по пользовательским критериям.

## План на 10 фаз PM→программист

ПМ не нужен и не призывался. План практический, не audit-only; каждая фаза обязана давать behavior/test/UX/dogfood/release artifact. Документация — только поддержка.

1. Phase 1 — DELETE backup artifact/accounting reconciliation
2. Phase 2 — Backup naming collision and monotonic evidence hardening
3. Phase 3 — Write-alpha DELETE restore proof v2
4. Phase 4 — Combined create/PATCH/DELETE backup-audit matrix
5. Phase 5 — Read-only regression after write-alpha remediation
6. Phase 6 — Operator-facing no-release blocker closure UX
7. Phase 7 — Fresh-clone and upgrade smoke after remediation
8. Phase 8 — Public status and release-doc drift guard refresh
9. Phase 9 — Final release-candidate dogfood pack
10. Phase 10 — v0.2.5-writealpha release gate/publication or no-release verdict

Strict external roadmap written to:
`/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-3/roadmap-cycle-3.md`

## Recommended next action

Запустить программиста напрямую по external roadmap cycle-3, начиная с Phase 1 DELETE backup artifact/accounting reconciliation. Не запускать ПМ. Не публиковать release до fresh green evidence pack and exact release/status commit CI.

## Suggested GitHub issues

Не создавать новые issues сейчас. Использовать существующий #36 для controlled-write readiness/release blocker tracking. Создавать новый issue только если Phase 1 обнаружит самостоятельный product defect, который не помещается в #36 and needs follow-up after the cycle.

## What not to do next

- Не включать `GNUCASH_WRITES_ENABLED=true` по умолчанию.
- Не использовать real/private/only-copy books.
- Не ослаблять `APP_ENV=test` gate for write-alpha.
- Не заявлять stable/production/security-audited/public-internet-safe status.
- Не расширять write scope до account/import/scheduled/import writes.
- Не публиковать `v0.2.5-writealpha`, если backup/audit/write-alpha evidence remains ambiguous.
- Не запускать audit-only loop вместо practical remediation and dogfood.
