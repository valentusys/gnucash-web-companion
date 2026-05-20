# Phase 178 — write-alpha UX guardrails from dogfood findings

Date: 2026-05-20
Status: COMPLETE — narrow UX/safety guardrails updated from disposable dogfood friction
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-roadmap.md` (Phase 7 only)

## Dogfood finding used

Phase 175–177 copied-book write-alpha dogfood found no need to expand write features, but it did expose concrete operator friction around safe completion criteria:

- the write path must be run only in explicit `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true` against an ignored disposable runtime copy;
- the source/only copy must never be used as the runtime write target;
- a write-alpha run is not complete until backup, audit, and lock-release evidence is checked;
- released file locks can leave stale ignored lock files, so operator-facing error guidance must not expose raw paths and must point to local redacted logs/evidence.

## UX changes

- `WriteModeWarning.svelte` now says the form should be reachable only in an explicit `APP_ENV=test` disposable run.
- The warning now tells operators to use ignored runtime copies, never the source/only copy, and confirm backup/audit/lock-release evidence.
- `/transactions` write-enabled entry copy now repeats the `APP_ENV=test`, ignored disposable copy, backup/audit/lock-release boundary before the `New transaction` link.
- `/transactions/new` acknowledgement and final browser confirmation now mention ignored disposable copies, source/only-copy prohibition, and backup/audit/lock-release checks.
- Transaction-detail DELETE localized guardrails now mention ignored disposable copies in `APP_ENV=test` plus backup/audit/lock-release checks.
- Write-alpha create/delete form error rendering now avoids showing raw path-like backend `detail` strings; unsafe details are replaced with a safe operator message pointing to local redacted logs/evidence.

## Static/browser-dogfood evidence

- Frontend route/static checks pin the hidden-by-default write UI gate, write-enabled warning copy, explicit acknowledgement, final browser confirmation, localized DELETE guardrails, and no localStorage/sessionStorage beyond existing theme-only allowance.
- Browser dogfood with default `GNUCASH_WRITES_ENABLED=false` passed via `scripts/smoke/read-only-browser-dogfood.py`: hidden write UI remained hidden; no `New transaction` link appeared in the default read-only runtime.
- No write-enabled browser mutation was run in this phase; the phase only changed guardrail copy and safe frontend error handling based on earlier dogfood evidence.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No write feature was expanded.
- No `APP_ENV=test` gate was weakened.
- No account/import/recurring writes were added.
- No release/tag/package was published.
- No real/private/only-copy book, raw book, app DB, backup, `.env`, token, key, cert, screenshot, CSV export, account name, transaction description, memo, amount, private path, or private financial data was committed.
