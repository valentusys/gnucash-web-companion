# Public read-only beta feedback packet

Use this for `v0.5.0-public-readonly-beta` feedback.

## Current public beta boundary

- `v0.5.0-public-readonly-beta` is the current public read-only beta.
- `v0.5.1-public-readonly-beta` is not published.
- Read-only feedback only: accounts, transactions, dashboards, reports, install flow, and diagnostics.
- No public write beta, stable release, production-ready claim, or security-audited claim.
- Do not test against an original/private/real-working/only-copy book; use synthetic/disposable or
  copied/restorable test books only.

## Good reports

- App version/tag and commit if known.
- Operating system and browser.
- Whether the book is synthetic/disposable or a copied/restorable test book.
- Redacted steps to reproduce.
- Error message text after removing private paths, names, amounts, memos, and descriptions.

## Do not upload

GnuCash books, SQLite DBs, app DBs, backups, CSV exports, screenshots containing finances, `.env`,
tokens, keys, certificates, private paths, account names, transaction descriptions, memos, or amounts.

## Scope

Read-only beta feedback only. Do not request or attempt public write-mode testing through this beta.
