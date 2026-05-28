# Read-only deployment diagnostics and privacy guide

This guide supports public read-only beta operators. It does not claim production readiness or security audit completion.

## Configuration checks

Before shared LAN/VPN use:

- Replace placeholder `JWT_SECRET` with a long random value.
- Configure `APP_ADMIN_PASSWORD` or `APP_ADMIN_PASSWORD_HASH` locally; never commit it.
- Narrow `CORS_ORIGINS` to exact browser origins for non-local deployments.
- Keep cookies httpOnly and same-site defaults unless you understand the deployment tradeoff.
- Keep `GNUCASH_WRITES_ENABLED=false`.
- Keep GnuCash books mounted as files; do not upload books through issue reports or public channels.

## Diagnostics privacy rules

Safe diagnostics may include:

- boolean configured/exists/readable statuses;
- file names without parent directories;
- backend type for app DB;
- status labels such as `ok`, `warning`, `action_required`;
- redacted error class names.

Diagnostics must not include:

- full private paths;
- account names, descriptions, memos, or amounts;
- `.env` contents, tokens, JWT secrets, passwords, keys, certificates;
- app DB contents, GnuCash books, backups, CSV exports, screenshots with financial data.

## Backup expectations

- Back up the app metadata DB separately from the GnuCash book.
- Back up the GnuCash book using your normal accounting backup workflow.
- Writebeta backups are operation-scoped safety artifacts, not a replacement for independent backups.
- Public read-only beta testing should not produce writebeta backups.

## Upgrade rehearsal from v0.5.0

1. Save current tag/commit and local `.env` outside git.
2. Pull the target commit/tag.
3. Re-run `docker compose config --quiet` with dummy validation values or real local env values.
4. Start services against a synthetic/disposable or copied/restorable book first.
5. Confirm read-only pages and login before pointing at any important copied book.
6. If diagnostics mention missing config, fix local environment only; do not paste secrets into issues.
