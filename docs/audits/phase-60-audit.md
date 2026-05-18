# Phase 60 Audit — Dogfood Readiness

## Executive summary

Phase 60 audited whether the maintainer can safely start read-only dogfood on a copied real GnuCash SQL book. The required dogfood instructions already exist and cover copied-book setup, the actual environment variable `GNUCASH_DEFAULT_BOOK_PATH`, disabled writes, Docker startup, dashboard/accounts/transactions checks, CSV export, shutdown, cleanup, and public-internet warnings.

This is readiness to perform dogfood, not evidence that dogfood has already passed and not approval to publish `v0.1.0-readonly`.

## Verdict

Ready for maintainer dogfood.

## Blockers

None for starting a cautious maintainer dogfood run on a copied real book.

Release blockers still carried forward from earlier phases:

1. `v0.1.0-readonly` release notes are still missing; GitHub #24 remains open.
2. A copied/disposable-data runtime smoke/dogfood pass is still not recorded; GitHub #25 remains open until actual dogfood evidence is captured.

## Non-blockers

1. The auditor roadmap says `DEFAULT_GNUCASH_BOOK_PATH`, but the repository’s implemented and documented variable is `GNUCASH_DEFAULT_BOOK_PATH`. The docs consistently use the actual variable, so this is not a repo blocker.
2. Dogfood docs are split between `docs/dogfood/personal-readonly-dogfood.md`, `scripts/smoke/read-only-smoke-check.md`, and `scripts/smoke/read-only-api-smoke.py`. This is acceptable; README and release-plan links point users toward the dogfood/smoke flow.

## Phase 60 audit checks

| Required dogfood readiness item | Evidence | Result |
| --- | --- | --- |
| Copying a GnuCash book | `docs/dogfood/personal-readonly-dogfood.md` section 1 instructs copying `/path/to/source-book.gnucash.sqlite` to `data/books/main.gnucash.sqlite` and verifying it is a copy. | Pass |
| Configuring default book path | `docs/dogfood/personal-readonly-dogfood.md` section 2 and `.env.example` use `GNUCASH_DEFAULT_BOOK_PATH=/data/books/main.gnucash.sqlite`. | Pass |
| Keeping writes disabled | Dogfood doc hard safety rules and section 3 require `GNUCASH_WRITES_ENABLED=false`; `.env.example` keeps it false; `Settings.gnucash_writes_enabled` defaults to `False`. | Pass |
| Starting Docker | Dogfood doc section 4 and smoke checklist startup section use `docker compose up --build`. | Pass |
| Checking dashboard/accounts/transactions | Dogfood doc section 5 covers login, dashboard, accounts, account detail, transactions, and transaction detail. | Pass |
| Exporting CSV | Dogfood doc section 5 covers CSV export and warns that exported CSV is sensitive and must not be committed. | Pass |
| Stopping services | Dogfood doc section 7 and smoke checklist use `docker compose down`. | Pass |
| Cleaning local data | Dogfood doc section 7 and smoke checklist list removal of local app DB, copied book, backups, and downloaded CSVs, with warning not to delete originals. | Pass |
| Not exposing to public internet | Dogfood doc hard safety rules and README warn not to expose pre-alpha deployments directly to the public internet. | Pass |

## Safety boundary

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented and configured default.
- Controlled writes remain experimental/post-MVP only.
- GnuCash Desktop remains the authoritative editor.
- The project is still positioned as not SaaS, not a GnuCash replacement, and not collaborative accounting.
- No release, production-readiness, security-audited, or safe-write-mode claim is accepted by this audit.
- No product code change is required for Phase 60.

## Release/readme/docs consistency

README and PROJECT_STATUS currently say Phase 59 is complete and `v0.1.0-readonly` is not published. Phase 60 should update them to record dogfood-readiness audit completion while keeping publication blocked until #24 and #25 are actually resolved.

The Phase 56 release plan already requires a clean dogfood/smoke pass before v0.1 publication. Phase 60 does not satisfy that pass; it only confirms that the maintainer has sufficient safe instructions to run it.

## GitHub project hygiene

Open issue review found existing meaningful issues:

- #24 — Prepare conservative v0.1.0-readonly release notes before publication.
- #25 — Complete v0.1 read-only runtime smoke/dogfood gate on copied or disposable data.
- #22, #17, #13, #12, #11 — non-blocking backlog as previously triaged for v0.1.

No new issue is needed. Phase 60 should comment on #25 that dogfood documentation is ready, but the issue remains open until actual dogfood/smoke evidence is recorded.

## Security notes

The dogfood docs explicitly prohibit committing `.env`, copied books, app DBs, backups, screenshots with real financial data, and CSV exports. They also instruct local/LAN/VPN-only style testing and warn against public-internet exposure.

No evidence of a changed auth-token storage model, changed write default, or new sensitive tracked file was found during this documentation audit.

## Test/CI notes

Because Phase 60 is a dogfood-readiness audit with release-gate implications, relevant full checks should be run before commit:

- `cd apps/api && pytest -q`
- `cd apps/web && npm run check`
- `cd apps/web && npm run test:auth-routes`
- `cd apps/web && npm run build`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- `git diff --check`

## Recommended next actions

1. Update README/PROJECT_STATUS/handoff to record Phase 60 completion and dogfood-ready status.
2. Comment on GitHub #25 that Phase 60 confirms docs are ready to execute dogfood, but the issue remains open until actual copied/disposable-data dogfood evidence is recorded.
3. Do not publish `v0.1.0-readonly` from Phase 60.
4. Do not start Phase 61 unless explicitly requested.

## Suggested GitHub issues

No new issues suggested. Existing #25 is the correct dogfood execution/evidence issue; creating a duplicate would be backlog noise.

## What not to do next

- Do not treat this audit as a completed dogfood run.
- Do not publish a `v0.1.0-readonly` tag or GitHub release.
- Do not enable or expand controlled writes.
- Do not test against the only/authoritative real GnuCash book.
- Do not commit `.env`, copied books, app DBs, backups, screenshots, CSV exports, secrets, keys, or certs.
