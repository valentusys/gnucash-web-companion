# Owner next steps for write-alpha

Status: Phase 303 practical guidance. This page is an operator-facing summary, not a release note and not an authorization to mutate any book.

## Current short answer

Use read-only mode for practical work. Keep `GNUCASH_WRITES_ENABLED=false`.

Write-alpha remains experimental, local/test-only, disabled by default, and allowed only against synthetic/disposable fixtures or copied/restorable test books. It is not safe for original, private, production, shared, or only-copy books.

## What is accepted now

| Area | Status | Meaning |
| --- | --- | --- |
| Read-only Docker/Caddy use | Accepted practical path | Phase 301 passed API/browser regression with writes disabled. |
| Owner copied-book dry-run | Accepted as dry-run-only evidence | Dry-run can inspect local preconditions without mutation. |
| Owner copied-book CREATE-one | Accepted as one bounded evidence class | Phase 276 accepted exactly one CREATE on a copied/restorable working book; this is not general write safety. |
| Owner copied-book CREATE-to-PATCH chain | Accepted narrowly | Phases 294–295 accepted exactly one CREATE followed by exactly one metadata/memo-only PATCH on the same write-alpha-created transaction in one fresh copied/restorable working book. |
| Owner copied-book DELETE | Blocked/not run | No owner DELETE evidence exists, no DELETE request packet is prepared, and Phase 302 kept DELETE blocked. |

## What you can do now

1. Run the app in read-only mode for browsing accounts, transactions, dashboards, reports, scheduled transaction metadata, and CSV export.
2. If you need write-alpha investigation, start with dry-run-only checks against a copied/restorable test book, not the original.
3. Keep the original GnuCash book untouched and independently backed up.
4. Keep all write-alpha evidence redacted: no private paths, account names, memos, descriptions, amounts, screenshots, CSV exports, tokens, keys, or raw payloads in public artifacts.
5. Treat GnuCash Desktop as the authoritative editor.

## What is still forbidden

- Do not run write-alpha on an original book.
- Do not run write-alpha on an only-copy book.
- Do not run write-alpha on a production/private book that is not a disposable/restorable test copy.
- Do not enable writes by default.
- Do not weaken the `APP_ENV=test` gate for enabled write-alpha routes.
- Do not edit amounts, accounts, currency, split count, reconciliation state, scheduled transactions, imports, or account data through write-alpha.
- Do not run owner DELETE.
- Do not prepare or execute a DELETE request packet unless a later explicit PM/owner decision changes scope.
- Do not claim production readiness, security audit status, broad GnuCash compatibility, public-internet safety, or general real/private-book write safety.

## If you only want practical use

Recommended path:

1. Keep `GNUCASH_WRITES_ENABLED=false`.
2. Use a copied GnuCash SQL book under `data/books/` for local testing.
3. Use GnuCash Desktop for all edits.
4. Re-copy or refresh the web app's read-only book after Desktop edits if needed.
5. Do not use write-alpha.

Relevant docs:

- `docs/deployment/local-secure-deployment.md`
- `scripts/smoke/read-only-smoke-check.md`
- `scripts/smoke/read-only-api-smoke.py`

## If you need dry-run-only write-alpha investigation

Dry-run is the only owner-facing write-alpha step that does not mutate the target book.

Relevant docs:

- `docs/write-alpha/owner-dry-run-quickstart.md`
- `docs/write-alpha/owner-dry-run-request.md`
- `docs/write-alpha/maintainer-copied-book-dogfood-packet.md`
- `docs/write-alpha/dogfood-evidence-schema.md`

Dry-run evidence can support planning, but it does not authorize CREATE, PATCH, or DELETE by itself.

## If considering CREATE/PATCH evidence

The current accepted evidence is narrow:

- Phase 276: exactly one owner copied-book CREATE-one evidence run.
- Phases 294–295: exactly one fresh copied-book CREATE-to-PATCH chain, where PATCH was metadata/memo-only and targeted the same write-alpha-created transaction.

Relevant docs:

- `docs/write-alpha/create-one-copied-book-plan.md`
- `docs/write-alpha/owner-create-one-request.md`
- `docs/write-alpha/patch-one-copied-book-plan.md`
- `docs/write-alpha/owner-patch-one-request.md`
- `docs/write-alpha/owner-create-patch-chain-request.md`
- `docs/write-alpha/transaction-ownership.md`
- `docs/write-alpha/copied-book-write-alpha-posture.md`
- `docs/write-alpha/evidence-matrix.md`

Do not reuse old authorization text for a new mutation scope. Any future mutation scope needs explicit same-context authorization and must remain copied/restorable-test-book only.

## DELETE status

DELETE remains blocked.

Reasons:

- It is destructive.
- It has no owner copied-book evidence.
- It has no owner request packet.
- Existing CREATE/PATCH evidence does not prove DELETE safety.
- Historical/imported/manual transactions must remain read-only in this app.

Phase 302 verdict: keep owner DELETE blocked. Planning-only documentation may explain the block; it must not include executable owner DELETE instructions.

## Current release state

- Current public read-only pre-alpha release: `v0.1.7-readonly`.
- Current public experimental write-alpha pre-release: `v0.2.8-writealpha`.
- `v0.2.9-writealpha` was not released.
- No release, tag, package, image, stable release, or production deployment is authorized by this page.
