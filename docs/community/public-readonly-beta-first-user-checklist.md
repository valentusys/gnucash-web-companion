# Public read-only beta first-user checklist

Use this checklist for v0.5.x public read-only beta testers.

## Before starting

- Use a synthetic/disposable GnuCash SQL book first.
- If you later use your own data, use a copy/restorable book and keep the original managed by GnuCash Desktop.
- Do not expose the app directly to the public internet.
- Keep `GNUCASH_WRITES_ENABLED=false` unless you are following a separately authorized owner/trusted writebeta drill.
- Set a long random `JWT_SECRET` and a local admin password before first login.

## Install smoke

1. Clone the repository and check out the intended tag/commit.
2. Copy `.env.example` to a local `.env`; do not commit it.
3. Set `JWT_SECRET`, `APP_ADMIN_PASSWORD`, and a container-visible `GNUCASH_DEFAULT_BOOK_PATH`.
4. Run: `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`.
5. Start the stack locally or on a LAN/VPN host.
6. Confirm login works and the dashboard loads.
7. Confirm account, transaction, scheduled, and book pages render without write prompts.

## Safe feedback

Include only:

- version/tag/commit;
- OS/browser/Docker versions;
- whether the book is synthetic, disposable, or copied/restorable;
- redacted steps and safe error text.

Do not include GnuCash books, app DBs, backups, CSV exports, screenshots with financial data, `.env`, tokens, keys, certificates, private paths, account names, transaction descriptions, memos, or amounts.

## Stop conditions

Stop testing and open a redacted issue if:

- write controls appear while `GNUCASH_WRITES_ENABLED=false`;
- login requires sharing secrets publicly;
- diagnostics expose full private paths or financial data;
- the app claims stable/production/security-audited/public-write safety.
