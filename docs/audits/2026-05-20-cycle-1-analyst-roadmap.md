# Cycle 1 analyst roadmap artifact — 2026-05-20

This committed audit artifact records the Cycle 1 analyst verdict and pointers to the strict external roadmap requested by the owner.

Language note: user-facing conclusions are Russian because this artifact is intended for the current gnucash-web-companion analyst cycle.

## Executive summary

Проект технически здоров, но публичный статус снова частично разошёлся с release reality: `v0.1.7-readonly` и `v0.2.0-writealpha` уже опубликованы, а часть документов всё ещё выглядит как pre-publication state. Read-only/write-disabled boundary при инспекции сохранён: `GNUCASH_WRITES_ENABLED=false` остаётся default, backend write routes gated, frontend write UI hidden by default. Следующая фаза должна быть Phase 172 — короткая docs/status reconciliation, затем переход к write-alpha copied-book dogfood design.

## Verdict

Ready after blockers fixed.

## PM decision

SKIPPED — отдельный PM не нужен, потому что подготовлен narrow executable 10-phase roadmap без conflict/now-later ambiguity и без immediate publication decision.

## Current baseline/release state

- Branch: `main`.
- HEAD/origin at inspection: `c1341ad84c6da1ec4087c0af43f52d252309ea50`.
- GitHub releases observed: `v0.1.7-readonly` published pre-release; `v0.2.0-writealpha` published experimental pre-release.
- Recent GitHub Actions observed: green.
- Working tree before this artifact: only untracked `.hermes/` telemetry.

## Top blockers

1. `README.ru.md` is stale: Phase 0–169 and `v0.1.6-readonly` instead of Phase 0–171 and `v0.1.7-readonly`.
2. `docs/release/v0.2.0-writealpha-*` has mixed historical/current wording around prepared/unpublished/not authorized despite current published pre-release state.
3. Write-alpha copied/disposable-book dogfood has not yet been completed.

## План на 10 фаз

1. Phase 1 — Phase 172 public status reconciliation.
2. Phase 2 — Write-alpha copied-book dogfood design.
3. Phase 3 — Write-alpha copied-book preflight harness.
4. Phase 4 — Write-alpha controlled create dogfood on disposable copy.
5. Phase 5 — GnuCash Desktop open-and-integrity verification.
6. Phase 6 — Write-alpha backup and restore drill.
7. Phase 7 — Write-alpha UX guardrails from dogfood findings.
8. Phase 8 — Write-alpha API hardening from dogfood findings.
9. Phase 9 — Full read-only plus write-alpha regression dogfood.
10. Phase 10 — Final release-readiness gate and publication decision artifact.

## External requested artifacts

- Analyst report: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-analyst-report.md`
- Strict roadmap: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-roadmap.md`

## What not to do next

- Do not run another audit-only phase.
- Do not continue read-only maintenance unless it fixes a real bug.
- Do not enable writes by default.
- Do not relax `APP_ENV=test`.
- Do not run write-alpha on a real/private/only-copy book.
- Do not publish a release before Phase 172 reconciliation and a fresh gate.
