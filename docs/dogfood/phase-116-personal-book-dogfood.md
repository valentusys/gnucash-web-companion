# Phase 116 — copied personal-book dogfood for GitHub #38

Date: 2026-05-19
Status: PASS
Related issue: GitHub #38

## Scope

A safe copied personal GnuCash SQL book archive provided by Val was used for a local-only read-only dogfood pass. The source archive remained untouched. The copied book was unpacked into a private temporary directory outside the repository and mounted read-only into the Docker/Caddy deployment.

This artifact is intentionally redacted. It does not include private filesystem paths, account names, transaction descriptions, memos, amounts, raw SQL dumps, screenshots, CSV bodies, tokens, credentials, cookies, or app DB contents.

## Safety posture

| Check | Result |
| --- | --- |
| Source archive modified | PASS — no |
| Unpacked outside git | PASS |
| Runtime app DB outside git | PASS |
| Runtime backups/locks outside git | PASS |
| `GNUCASH_WRITES_ENABLED=false` | PASS |
| Docker/Caddy local-only target | PASS |
| Screenshots/downloaded CSV files created | PASS — none |
| Tag/release/package published | PASS — none |

## Minimal copied-book preflight

| Check | Result |
| --- | --- |
| Expected filename present | PASS |
| SQLite read-only open | PASS |
| `PRAGMA integrity_check` | PASS |
| Required GnuCash SQL tables present | PASS |

No table dumps, row dumps, account names, descriptions, memos, or amounts were printed or recorded.

## API dogfood

Target route family count checked: 11.

| Route type | Result |
| --- | --- |
| `GET /api/health` | PASS — 200 |
| `POST /api/auth/login` | PASS — 200 |
| `GET /api/auth/me` | PASS — 200 |
| `GET /api/books` and `GET /api/books/{id}` | PASS — 200 |
| `GET /api/books/{id}/accounts` | PASS — 200 |
| `GET /api/books/{id}/transactions` | PASS — 200 |
| `GET /api/books/{id}/transactions/{transaction_id}` | PASS — 200 |
| `GET /api/books/{id}/transactions/export` | PASS — 200; CSV header and metadata headers checked without saving the body |
| `GET /api/books/{id}/reports/summary` | PASS — 200 |
| `POST /api/books/{id}/transactions/validate` | PASS — 403 while writes disabled |
| `POST /api/books/{id}/transactions` and `PATCH /api/books/{id}/transactions/{transaction_id}` | PASS — 403 while writes disabled |

## Browser/UI dogfood

Target route/action count checked: 12.

| Route/action | Result |
| --- | --- |
| `/login` | PASS |
| Protected `/dashboard` redirect to login | PASS |
| Login flow | PASS |
| Auth cookie not readable from `document.cookie` | PASS |
| `/dashboard` | PASS; write UI hidden |
| `/accounts` | PASS; write UI hidden |
| `/books` | PASS; write UI hidden |
| `/scheduled` | PASS; write UI hidden |
| First account detail route | PASS |
| Filtered `/transactions` route | PASS |
| CSV export link preserves active filters | PASS |
| First transaction detail route | PASS |
| Authenticated CSV export fetch | PASS — 200; headers checked; no file saved |
| Browser temp artifacts | PASS — no screenshots/downloads/CSV files written |

## Limitation / note

A first browser attempt using a different loopback hostname hit the framework's cross-site form-origin guard and was rerun with the configured local origin. The passing browser evidence above used the configured origin and did not require product-code changes.

## Verdict

PASS — GitHub #38 acceptance evidence is complete for this copied personal-book dogfood pass, with read-only mode enforced and redacted evidence recorded.
