# Cycle 3 analyst roadmap artifact — 2026-05-20

Canonical external report: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-3-analyst-report.md`

Canonical strict roadmap: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-3-roadmap.md`

## Executive summary

Репозиторий после cycle 2 находится в здоровом pre-alpha состоянии: `v0.2.2-writealpha` опубликован как conservative GitHub pre-release, exact-commit CI зелёный, docs/status синхронизированы до Phase 191. Read-only boundary сохранён: `GNUCASH_WRITES_ENABLED=false` default, write-alpha дополнительно gated через `APP_ENV=test`, production/security/real-private-book write safety не заявляется. Следующий цикл должен быть практическим maintenance/safety/dogfood циклом, не audit-only loop.

## Verdict

Ready for next engineering phase.

Не production-ready. Не security-audited. Write-alpha остаётся unsafe для real/private/only-copy books.

## PM decision: SKIPPED, reason

PM decision: SKIPPED.

Reason: аналитик дал narrow executable roadmap ровно на 10 фаз; отсутствующего roadmap нет; конфликтующих приоритетов нет; release/no-release decision вынесен в gated Phase 10; private-data/write-mode/security/publication risks ограничены safety checks каждой фазы.

## Current baseline/release state

- Branch: `main`.
- Inspected HEAD: `8ca6be4 Phase 191 cycle-2 release gate`.
- Current write-alpha pre-release: `v0.2.2-writealpha`.
- Current read-only pre-release: `v0.1.7-readonly`.
- Latest 10 GitHub Actions runs: success.
- Open issues inspected via `gh`: #36, #29, #28, #22, #17, #13.
- Tracked tree before this artifact: clean except untracked `.hermes/` telemetry.

## Top blockers

1. No current release blocker for the conservative pre-alpha baseline.
2. Write-alpha remains unsafe for real/private/only-copy books.
3. Root-owned ignored runtime files can still limit host-side write-alpha helper finalization; fix before the next write-alpha release claim.
4. GitHub Actions Node.js 20 deprecation warning should be cleaned early in cycle 3.
5. Broad GnuCash Desktop/version/backend compatibility remains unproven.

## План на 10 фаз

1. Phase 1 — CI/toolchain warning cleanup.
2. Phase 2 — Root-owned runtime cleanup and lock recovery UX.
3. Phase 3 — Write-alpha smoke helper resilience.
4. Phase 4 — Write-alpha audit summary operator UX hardening.
5. Phase 5 — First-run/read-only deployment confidence pass.
6. Phase 6 — Disposable GnuCash Desktop fixture compatibility evidence.
7. Phase 7 — Multi-book read-only registry diagnostics hardening.
8. Phase 8 — Full default-read-only regression dogfood.
9. Phase 9 — Bounded write-alpha disposable CRUD/restore dogfood.
10. Phase 10 — Cycle-3 release-readiness gate and publication/no-release artifact.

## What not to do next

- Do not start another audit-only cycle.
- Do not enable `GNUCASH_WRITES_ENABLED=true` by default.
- Do not run write-alpha on real/private/only-copy books.
- Do not claim production readiness, security audit, hosted SaaS readiness, public-internet safety, broad GnuCash compatibility, or real/private-book write safety.
- Do not publish release/package/image before Phase 10 gate.
- Do not stage `.hermes/` telemetry.

## Inspection evidence

- `.env.example`: `GNUCASH_WRITES_ENABLED=false`.
- `apps/api/app/config.py`: `gnucash_writes_enabled: bool = False`.
- `apps/api/app/routers/transactions.py`: write routes call backend gates before write service construction.
- Frontend storage search found theme localStorage only, not auth token storage.
- Phase 190 dogfood: default read-only API/browser passed; validate/create/PATCH/DELETE returned 403; explicit write-alpha was local-only synthetic/disposable and reset to default false.
- Phase 191: `v0.2.2-writealpha` published only after green local checks, rendered false defaults, sensitive hygiene, and exact-commit GitHub Actions.

## Recommended next action

Start Phase 1 from the external strict roadmap.
