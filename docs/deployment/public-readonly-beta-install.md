# Public read-only beta install guide

Status after Phase 480: draft, not yet release-ready.

Use only read-only mode:
1. Clone the repository.
2. Copy `.env.example` to `.env`.
3. Set a fresh `JWT_SECRET` and admin password/hash.
4. Point `GNUCASH_DEFAULT_BOOK_PATH` at a disposable/test SQL book first.
5. Keep `GNUCASH_WRITES_ENABLED=false`.
6. Render config: `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`.
7. Start on localhost/LAN/VPN only; do not expose directly to the public internet.

Do not share screenshots, CSV exports, paths, account names, transaction descriptions, memos or amounts in issues.
