# Phase 101 — Personal copied-book dogfood rerun gate

Date: 2026-05-18
Verdict: BLOCKED — safe copied book path not provided
Issue: GitHub #38

## Scope

Phase 101 was limited to rerunning or gating the copied personal-book dogfood attempt for GitHub #38.

The dogfood run was allowed only if a safe copied GnuCash SQL book path was explicitly provided by the controller, environment, or user context. The candidate also had to be outside `/home/val/gnucash-web-companion` and confirmed as a copied/disposable input, not the live authoritative GnuCash book.

## Candidate copied-book path check

Result: no safe candidate path was provided.

Evidence checked without printing or committing private paths:

- `GNUCASH_DOGFOOD_BOOK_PATH`: absent.
- `GNUCASH_DOGFOOD_BOOK_IS_COPY`: absent.
- The PM/controller message did not include an explicit copied-book path.
- No broad private-directory search was performed.

Because no explicit safe path was available, the personal copied-book dogfood smoke was not run. This is a blocked result, not a pass.

## Non-mutating verification performed

| Check | Result |
| --- | --- |
| `git status --short` before work | PASS — clean output. |
| `git rev-parse --abbrev-ref HEAD` | PASS — `main`. |
| `git rev-parse --short HEAD` | PASS — `80ccc96` before Phase 101 documentation changes. |
| `git tag --list 'v0.1.1-readonly'` | PASS — no tag output. |
| `gh auth status` | PASS — authenticated as `valentusys`. |
| `gh release view v0.1.1-readonly || true` | PASS — release not found. |
| `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` | PASS — no output. |
| `python3 scripts/smoke/read-only-api-smoke.py --help` | PASS. |
| `python3 -m py_compile scripts/smoke/read-only-api-smoke.py` | PASS. |

## Dogfood/smoke execution

Skipped by design because the safe copied-book path gate failed.

No GnuCash book was opened, copied, mounted, inspected, or committed during Phase 101. No browser screenshots or CSV exports were created.

## GitHub #38 state

GitHub #38 remains open because copied personal-book dogfood has not passed.

A non-sensitive issue update is allowed for this blocked result. The issue must not be closed unless a later run uses an explicitly provided safe copied/disposable book and passes the read-only smoke checks.

## Safety statement

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the required dogfood posture.
- Controlled writes remain post-MVP/experimental and disabled by default.
- GnuCash Desktop remains the authoritative editor.
- No tag, GitHub release, package, or release artifact was published.
- No real/private financial data, copied GnuCash book, app DB, backup, `.env`, screenshot, CSV export, secret, token, cert, key, private path, account name, transaction description, memo, or amount was committed.
- This phase does not claim personal-book dogfood success, production readiness, audited security, broad compatibility, family-wallet positioning, or collaborative accounting.

## Next requirement for #38

Provide an explicit safe copied/disposable GnuCash SQL book path outside the repository, plus confirmation that it is not the live authoritative book. Then rerun local-only read-only smoke with `GNUCASH_WRITES_ENABLED=false`, redacting all private evidence.
