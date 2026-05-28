# Public read-only beta install

Status: v0.5.0-public-readonly-beta candidate. Read-only beta only; not production-ready, not security-audited, and not for direct public-internet exposure.

## Safe data rule
Use a copied/restorable GnuCash SQL book first. Do not mount an original, private, or only-copy book as the first test target. Keep backups outside the repository.

## Docker Compose quick start

1. Clone the repository and enter it.
2. Copy `.env.example` to `.env` locally; never commit `.env`.
3. Set strong local values for `JWT_SECRET` and `APP_ADMIN_PASSWORD`.
4. Keep `GNUCASH_WRITES_ENABLED=false`. This is the default and must remain the default.
5. Put a copied SQL book under the runtime books volume used by your deployment, not in git.
6. Run `docker compose config --quiet` before starting.
7. Start on a trusted LAN/VPN only; do not expose the service directly to the public internet.
8. Log in with the configured local admin password and verify dashboard/accounts/transactions/reports read-only views.

## First login
Use the configured admin password. Auth uses httpOnly cookies; do not share `.env` or browser session data.

## Backups and restore posture
This beta is read-only by default. Still keep independent backups of any copied book you mount. Do not treat this project as a disaster-recovery system.

## Troubleshooting
- If Docker config validation fails, fix `.env` locally and rerun validation.
- If the book does not open, test with a disposable/synthetic book and file a redacted issue.
- Do not upload financial books, screenshots, exports, account names, transaction descriptions, memos, amounts, tokens, or raw paths to public issues.
