# Personal read-only dogfood checklist

This checklist is for a cautious personal dogfood test of gnucash-web-companion against a copy of a GnuCash SQL book.

Status: pre-alpha. Not production-ready. Not security-audited. Keep GnuCash Desktop as the authoritative editor.

## Hard safety rules

- Use only a copy of a GnuCash SQL book.
- Do not point the app at your only/authoritative book.
- Keep `GNUCASH_WRITES_ENABLED=false`.
- Do not expose this pre-alpha deployment directly to the public internet.
- Keep a separate backup of the source book outside this repository.
- Do not commit copied books, `.env`, app DB files, backups, screenshots with real financial data, or exported CSVs.

## 1. Prepare a copy of the book

From the repository root:

```bash
mkdir -p data/books data/app data/backups
cp /path/to/source-book.gnucash.sqlite data/books/main.gnucash.sqlite
```

Before continuing, confirm that `data/books/main.gnucash.sqlite` is a copy. If unsure, stop and make a new copy from GnuCash Desktop or from a backup.

The `data/` directory is local runtime data and must stay out of git.

## 2. Create local environment config

Copy the example config and fill in local-only secrets:

```bash
cp .env.example .env
```

Required values for a local dogfood run:

```dotenv
JWT_SECRET=<long random local value>
APP_ADMIN_USERNAME=admin
APP_ADMIN_PASSWORD=<local test password>
GNUCASH_DEFAULT_BOOK_PATH=/data/books/main.gnucash.sqlite
GNUCASH_WRITES_ENABLED=false
ORIGIN=http://localhost:8080
```

Generate a local JWT secret if needed:

```bash
openssl rand -hex 32
```

Do not commit `.env`.

## 3. Verify writes are disabled before startup

Check both the local env file and the resolved Docker Compose config:

```bash
grep '^GNUCASH_WRITES_ENABLED=false$' .env
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep 'GNUCASH_WRITES_ENABLED=false'
```

If either check does not show `false`, stop. Do not start dogfood against a personal copy until writes are disabled.

## 4. Start Docker

```bash
docker compose up --build
```

Open the app locally:

```text
http://localhost:8080
```

Log in with the admin username/password from `.env`.

## 5. Screens to verify

Use the copied book only. Do not upload or commit screenshots if they show real financial data.

- Login:
  - Login form loads.
  - Invalid credentials fail without revealing sensitive details.
  - Valid admin credentials enter the app.
- Dashboard:
  - Summary cards render.
  - Currency and amount display looks plausible for the copied book.
  - Read-only/safety wording is visible in the authenticated shell.
- Accounts:
  - Account tree loads.
  - Account names and hierarchy look plausible.
  - Placeholder/parent accounts are not presented as editable.
- Account detail:
  - Opening an account shows account metadata and related transactions.
  - Pagination/empty states are understandable.
- Transactions:
  - Transaction list loads.
  - Search/date/account/amount filters do not crash.
  - Pagination works on the copied dataset.
- Transaction detail:
  - Opening a transaction shows splits and balancing details.
  - Amounts are displayed as strings/decimals, not rounded unexpectedly.
- CSV export:
  - Export from the transactions screen downloads a CSV.
  - Filters are preserved in the export.
  - Treat the CSV as sensitive local financial data; do not commit it.

## 6. Confirm write UI is hidden

With `GNUCASH_WRITES_ENABLED=false`:

- The transactions screen must not show a normal "New transaction" write entry point.
- Directly opening `/transactions/new` should redirect away or otherwise block the create form.
- Any visible write-mode warning or acknowledgement UI should appear only when write mode is explicitly enabled for disposable post-MVP testing, not during this read-only dogfood run.

Optional API-level check while Docker is running:

```bash
curl -i http://localhost:8080/transactions/new
```

Expected result: no usable transaction-create flow in the browser while writes are disabled.

## 7. Stop and clean local runtime data

Stop containers:

```bash
docker compose down
```

To remove only local app runtime state and the copied book from this checkout after dogfood:

```bash
rm -f data/app/app.db
rm -f data/books/main.gnucash.sqlite
rm -rf data/backups/*
```

Do not delete your original GnuCash book or external backups.

If you created CSV exports or screenshots during testing, store them outside the repository or delete them:

```bash
rm -f ~/Downloads/transactions*.csv
```

## 8. Dogfood notes to record

Record findings without attaching real data:

- App commit SHA.
- GnuCash desktop version used to create the copied book.
- Book backend/type, for example SQLite.
- Whether login/dashboard/accounts/account detail/transactions/transaction detail/CSV export passed.
- Any confusing UI, missing error copy, slow queries, or display mismatch.
- Confirmation that write UI stayed hidden with `GNUCASH_WRITES_ENABLED=false`.

Do not paste real account names, transaction descriptions, balances, exported CSV rows, screenshots, or book files into public issues.
