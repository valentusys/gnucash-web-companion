# Phase 234 handoff — Copied-book write-alpha dogfood runbook v1

Date: 2026-05-21
Status: COMPLETE — conservative copied/disposable write-alpha dogfood runbook added; no dogfood executed.

## Summary

Phase 234 stayed within the documentation-only runbook contract. It added a maintainer-facing runbook for future copied-book write-alpha dogfood that requires copied/disposable books outside git, an independent backup before any mutation, local-only Docker, explicit `GNUCASH_WRITES_ENABLED=true` plus `APP_ENV=test`, one mutation at a time, strict stop conditions, redacted evidence, restore verification, and reset back to `GNUCASH_WRITES_ENABLED=false`.

No real/private copied-book dogfood was run. No UI feature, product code, release, tag, write-mode default, `APP_ENV=test` gate, or real/private/only-copy book safety claim was changed.

## Files changed

- `docs/write-alpha/copied-book-dogfood-runbook.md` — new conservative copied/disposable write-alpha dogfood runbook.
- `README.md` and `README.ru.md` — current phase summary synchronized to Phase 234 and linked to the runbook without expanding write-safety claims.
- `CHANGELOG.md` — Phase 234 entry added under Unreleased.
- `PROJECT_STATUS.md` — current completed phase advanced to Phase 234 and Phase 234 status section added.
- `docs/ROADMAP.md` — current posture and recent phase list synchronized to Phase 234.
- `scripts/check_public_status.py` and `apps/api/tests/test_public_status_guard.py` — public-status guard expectations advanced to Phase 234.
- `docs/handoff/phase-234.md` — this handoff.

## Verification performed

- Documentation review — passed: the runbook forbids original/only-copy books, requires outside-git copied/disposable working books, backup before mutation, explicit `APP_ENV=test`, explicit write enablement only for the local run, one mutation at a time, stop conditions, redaction, restore, and reset to default false.
- `python3 scripts/check_public_status.py` — passed.
- `cd apps/api && pytest tests/test_public_status_guard.py -q` — passed.
- `git diff --check` — passed.
- `.env.example` grep confirmed `GNUCASH_WRITES_ENABLED=false`.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default.
- `APP_ENV=test` write-alpha gate remains intact and was not weakened.
- The new runbook explicitly rejects original and only-copy books.
- The new runbook instructs maintainers not to commit evidence with private paths, account names, memos, amounts, CSV rows, screenshots, books, backups, app DBs, `.env`, tokens, keys, certs, or private financial data.
- No production readiness, stable release, security audit, public-internet safety, broad compatibility, or real/private-book write-safety claim was added.

## Risks / blockers

No Phase 234 blocker remains. The runbook is preparatory documentation only; it does not itself prove copied-book write safety.

## Next

Do not continue to Phase 235 from this session.
