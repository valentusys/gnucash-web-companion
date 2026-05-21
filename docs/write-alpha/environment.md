# Write-alpha environment guidance

Status: operator reference for local synthetic/disposable or copied-test-book write-alpha testing only.

Write-alpha remains experimental, pre-alpha, disabled by default, and not safe for real/private books
or the only copy of any book. GnuCash Desktop remains the authoritative editor.

## Safe default

The normal deployment path is still read-only:

- `.env.example` keeps `GNUCASH_WRITES_ENABLED=false`.
- `docker-compose.yml` renders `GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}`.
- Do not change those defaults for regular read-only use.

## Do not copy blindly

`.env.writealpha.example` is a reference, not a drop-in default configuration.

Do not copy it blindly to `.env`. If you prepare a local write-alpha test environment, review every
line first and replace placeholders with local disposable values. Never commit the resulting `.env`.

## Required write-alpha gates

A routed write-alpha test requires both explicit gates:

```env
GNUCASH_WRITES_ENABLED=true
APP_ENV=test
```

If either gate is missing, normal behavior is to keep write routes blocked. Do not weaken the
`APP_ENV=test` guard and do not make writes easy to enable in default deployment files.

## Allowed books only

Use only:

- synthetic books generated for testing;
- disposable books that can be deleted;
- copied-test books made specifically for the run and kept outside git.

Never use:

- the original book;
- the only copy of any book;
- a real/private operational book mounted directly into the app;
- a copied book whose backup/restore path has not been verified.

The original book must never be mounted, referenced, opened, backed up, or mutated by write-alpha
runs.

## Ownership boundary

Enabling write-alpha does not make existing GnuCash history editable:

- CREATE creates app-metadata ownership markers for transactions created by this app's write-alpha
  flow.
- PATCH and DELETE require that same write-alpha-owned marker for the same book record.
- Historical, imported, or manually created GnuCash transactions remain read-only in this app.
- Non-owned transaction edit/delete hiding in the frontend is supporting UX only; backend guards are
  authoritative.
- This boundary does not make real/private, original, production, shared, or only-copy books safe for
  write-alpha.

## Exposure boundary

Write-alpha testing is local-only:

- bind to localhost or a trusted single-machine test setup;
- keep `ORIGIN` and `CORS_ORIGINS` narrow and exact;
- do not expose a write-alpha environment to the public internet;
- do not share it on an untrusted LAN/VPN;
- use fresh local-only credentials and secrets for the disposable run.

This project is not production-ready, not security-audited, not public-internet safe, and does not
claim real/private-book write safety.

## Minimum operator checklist

Before enabling write-alpha for a local test:

1. Confirm the target is synthetic/disposable/copied-test only.
2. Confirm the original book is not mounted or referenced.
3. Keep the copied target outside git and do not commit runtime evidence with private data.
4. Verify an independent backup and restore path before any mutation.
5. Set `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=true` only for the test run.
6. Keep the deployment local-only with exact origins.
7. Run one bounded scenario at a time.
8. Record only redacted evidence.
9. Reset to `GNUCASH_WRITES_ENABLED=false` after the run.
10. Re-render Docker Compose and confirm the normal default is false before returning to read-only use.

## Verification commands

Default read-only posture check:

```bash
JWT_SECRET=dummy-local-secret APP_ADMIN_PASSWORD=dummy-local-password docker compose config --quiet
JWT_SECRET=dummy-local-secret APP_ADMIN_PASSWORD=dummy-local-password docker compose config \
  | grep -n 'GNUCASH_WRITES_ENABLED=false'
python3 scripts/check_public_status.py
```

These checks prove only that the default configuration is still read-only and public status docs are
synchronized. They do not prove write-alpha safety for real/private books.
