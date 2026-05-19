# Read-only dogfood smoke check

Manual smoke checklist for Phase 38 personal dogfood readiness.

Use this together with `docs/dogfood/personal-readonly-dogfood.md`. This file stays manual/checklist-based. For the Phase 39 automated API smoke path, use `scripts/smoke/read-only-api-smoke.py`.

## Preconditions

- [ ] Running against a copied GnuCash SQL book under `data/books/`, not the authoritative/original book.
- [ ] `.env` exists locally and is not committed.
- [ ] `GNUCASH_DEFAULT_BOOK_PATH=/data/books/main.gnucash.sqlite` or another copied book path under `/data/books/`.
- [ ] `GNUCASH_WRITES_ENABLED=false` in `.env`.
- [ ] Docker Compose config resolves writes as disabled:

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep 'GNUCASH_WRITES_ENABLED=false'
```

- [ ] `git status --short` does not show real book files, app DB files, backups, screenshots, exports, `.env`, secrets, or keys staged/tracked.

## Startup

```bash
docker compose up --build
```

- [ ] API container becomes healthy.
- [ ] Web container starts.
- [ ] Proxy serves `http://localhost:8080`.

## Browser smoke path

- [ ] Login page opens.
- [ ] Invalid login fails safely.
- [ ] Valid admin login succeeds.
- [ ] Dashboard loads and shows read-only/safety wording.
- [ ] Accounts page loads.
- [ ] Account detail page loads for at least one account.
- [ ] Transactions page loads.
- [ ] Transaction search/filter controls do not crash.
- [ ] Transaction detail page loads for at least one transaction.
- [ ] CSV export downloads a file and respects current filters.
- [ ] Downloaded CSV is treated as sensitive local data and is not committed.

## Write-disabled smoke path

With `GNUCASH_WRITES_ENABLED=false`:

- [ ] Transactions page does not present a normal usable `New transaction` flow.
- [ ] Direct navigation to `/transactions/new` does not expose a usable create form.
- [ ] No frontend copy implies that writes are production-ready.
- [ ] No write test is performed against the personal copied book.

## Automated API smoke path

After the local Docker deployment is running with `GNUCASH_WRITES_ENABLED=false`, inspect script options if needed and run:

```bash
scripts/smoke/read-only-api-smoke.py --help
SMOKE_ADMIN_PASSWORD='<local-admin-password>' scripts/smoke/read-only-api-smoke.py
```

The script targets `http://localhost:8080/api` by default and checks API health, login, `/auth/me`, default book discovery, accounts, transactions, reports summary, and disabled-write 403 responses for validate/create/patch/delete endpoints. Override with `SMOKE_API_BASE_URL` only when testing a different local/LAN deployment.

## Shutdown / cleanup

```bash
docker compose down
```

Optional local cleanup after dogfood:

```bash
rm -f data/app/app.db
rm -f data/books/main.gnucash.sqlite
rm -rf data/backups/*
rm -f ~/Downloads/transactions*.csv
```

- [ ] Original GnuCash book and external backups were not deleted.
- [ ] Runtime data remains untracked by git.
- [ ] Any public issue/report avoids real account names, descriptions, balances, screenshots, book files, or CSV rows.
