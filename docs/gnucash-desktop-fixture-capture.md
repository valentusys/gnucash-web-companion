# Disposable Desktop fixture capture path

Status: safe helper path available; Desktop-generated fixture evidence is still blocked until a manually supplied synthetic SQLite book exists.

## Exact blocker for #22

Keep #22 open until an isolated disposable GUI/manual-safe environment produces a Desktop-generated
synthetic SQLite fixture and that fixture passes read-only validation with `GNUCASH_WRITES_ENABLED=false`.
Current helper/probe evidence is command/tooling evidence only and is not broad GnuCash Desktop compatibility.

Required environment/evidence before the blocker can clear:

1. No private home directory, private book, backup directory, app DB, `.env`, token, key, certificate,
   screenshot, export, or real account data is mounted or opened.
2. A human operator creates only synthetic accounts/transactions in GnuCash Desktop inside the isolated
   disposable GUI/manual-safe environment.
3. The resulting Desktop-generated synthetic SQLite fixture is handled outside git, then validated by
   the redacted metadata helper and default-read-only API checks.
4. Public evidence contains only redacted fixture class, Desktop version string, schema/table-count
   metadata, and pass/fail status; it contains no row values or private/raw financial data.

This runbook advances GitHub #22 without touching real/private books. It describes the only accepted path for a future Desktop-generated synthetic SQLite fixture and the deterministic rejection behavior used by the metadata helper.

## Current result

No Desktop-generated synthetic SQLite fixture is committed or claimed here.

The repository now has a stricter capture/metadata path in `apps/api/scripts/collect_gnucash_compatibility_metadata.py` for manually supplied `--fixture-origin desktop-generated-synthetic` inputs:

- accepts only regular SQLite/GnuCash SQLite files;
- requires an explicit GnuCash Desktop version string;
- requires a synthetic/disposable/test fixture marker in the filename;
- rejects non-disposable filename markers such as private, personal, real, production, prod, backup, or secret;
- rejects candidates inside repo `data/backups/`, repo `data/app/`, `secrets/`, `.env`, or path components named backup/backups/secrets;
- records only path-redacted candidate acceptance metadata plus schema versions/table counts;
- exits with path-redacted reasons for rejected candidates.

## Manual-safe creation requirement

A Desktop-generated fixture can be considered only after all of these are true:

1. GnuCash Desktop runs in an isolated disposable VM/container/GUI environment.
2. No private home directory, private book, backup directory, app DB, `.env`, token, key, certificate, screenshot, export, or real account data is mounted or opened.
3. The operator manually creates a synthetic SQLite book with synthetic accounts/transactions only.
4. The output is saved outside git, for example `/tmp/gwc-desktop-fixture/desktop-synthetic-fixture.gnucash.sqlite`.
5. `GNUCASH_WRITES_ENABLED=false` is used for any web/API validation.

The helper is not a Desktop automation tool and does not generate a fixture itself.

## Candidate acceptance command

Use a disposable path and a synthetic/disposable filename:

```bash
python apps/api/scripts/collect_gnucash_compatibility_metadata.py \
  /tmp/gwc-desktop-fixture/desktop-synthetic-fixture.gnucash.sqlite \
  --gnucash-version "GnuCash 4.13" \
  --fixture-origin desktop-generated-synthetic \
  --output /tmp/phase-203-desktop-synthetic-metadata.json
```

Accepted output remains bounded to:

- `book_path: "<redacted>"`;
- declared fixture origin and Desktop version;
- redacted `candidate_acceptance` path-class metadata;
- SQLite schema `versions` markers;
- selected table counts for `accounts`, `transactions`, `splits`, `commodities`, and `books`;
- safe runtime context for Python/SQLite/piecash/collector.

It intentionally excludes account names, account descriptions, transaction descriptions, split memos, split amounts, private paths, app DB data, backups, `.env`, secrets, keys, tokens, screenshots, exports, and row values.

## Rejection examples

These should fail safely and must not print raw candidate paths:

```bash
python apps/api/scripts/collect_gnucash_compatibility_metadata.py \
  /tmp/private-production-book.gnucash.sqlite \
  --gnucash-version "GnuCash 4.13" \
  --fixture-origin desktop-generated-synthetic
# rejected: filename contains forbidden non-disposable marker(s)

python apps/api/scripts/collect_gnucash_compatibility_metadata.py \
  data/backups/desktop-synthetic-fixture.gnucash.sqlite \
  --gnucash-version "GnuCash 4.13" \
  --fixture-origin desktop-generated-synthetic
# rejected: forbidden repo runtime/secrets class
```

## Validation after accepted metadata

After an accepted synthetic Desktop fixture exists, copy only that disposable file into ignored runtime storage and run read-only validation with writes disabled:

```bash
GNUCASH_WRITES_ENABLED=false SMOKE_ADMIN_PASSWORD=<dummy-local-password> \
  scripts/smoke/read-only-api-smoke.py
```

Do not commit the binary fixture, runtime copy, app DB, backups, `.env`, screenshots, exports, tokens, keys, certs, private paths, or raw row data.

## Suggested GitHub #22 update text

```text
Phase 203 advanced the Desktop-generated synthetic SQLite fixture path without claiming Desktop compatibility yet. The metadata helper now deterministically accepts/rejects manually supplied desktop-generated synthetic candidates: it requires a regular SQLite/GnuCash SQLite file, explicit GnuCash Desktop version, synthetic/disposable/test filename marker, rejects private/real/prod/backup/secret-like names and repo backup/app/secrets/.env path classes, and records only redacted candidate metadata plus schema versions/table counts. Rejected candidates return path-safe reasons. No Desktop-generated fixture was produced or committed; the remaining blocker is still a disposable GUI/manual-safe GnuCash Desktop session that creates the synthetic SQLite file, followed by this helper and default-read-only API validation with `GNUCASH_WRITES_ENABLED=false`.
```
