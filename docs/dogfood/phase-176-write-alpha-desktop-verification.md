# Phase 176 — write-alpha GnuCash Desktop/tooling verification

Date: 2026-05-20
Status: PASS — disposable mutated copied book was accepted by GnuCash CLI tooling in a disposable container
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-roadmap.md` (Phase 5 only)

## Scope

This phase verified that a disposable synthetic copy, mutated once through the existing write-alpha create route, can be opened by GnuCash Desktop-adjacent tooling without committing the mutated book.

The run used only disposable paths and redacted evidence:

- source class: committed synthetic fixture copied to `/tmp` before use;
- source checksum: `sha256_12=c8f22b449c49`;
- mutation scope: exactly one balanced two-split transaction create through the write-alpha API route;
- mutated checksum: `sha256_12=c25172f9a44a`;
- Desktop/tooling environment: temporary `debian:12-slim` Docker container with `gnucash` and `gnucash-common` installed only inside the container;
- GnuCash tooling: `gnucash-cli --version` reported `GnuCash 4.13`;
- validation command class: `gnucash-cli --report show --name "Balance Sheet" <redacted disposable mutated SQLite book>`;
- result: command exited `0` and returned bounded report metadata only.

No host packages were installed. No private/real/only-copy book was opened. No screenshot, raw SQL dump, account names, descriptions, memos, amounts, private paths, app DB, backup, `.env`, token, key, cert, or mutated book is committed.

## Redacted command/result evidence

```text
source_preflight=status=ready; book=<redacted.gnucash.sqlite>; reason=write-alpha copied-book preflight passed without copying or mutation; source=external copied/disposable; runtime=ignored data/books; backups=ignored data/backups; size_bytes=212992; sha256_12=c8f22b449c49; dry_run=true
runtime=ignored disposable copy under data/books
app_env=test
writes_enabled=explicit local-only true
mutation=one balanced two-split create via write-alpha API route
mutation_audit=one transaction.create success row
backup_before_write=one ignored backup file observed before cleanup
lock_release=remaining lock file was present after write; Phase 175 helper noted this implementation detail, and cleanup removed it after runtime stop
mutated_book=temporary disposable copy outside git; size_bytes=212992; sha256_12=c25172f9a44a
desktop_tooling_container=debian:12-slim; temporary; no host package install
commands_available=gnucash:true, gnucash-cli:true
gnucash_cli_version=GnuCash 4.13
open_validation_command=gnucash-cli --report show --name "Balance Sheet" <redacted disposable mutated SQLite book>
open_validation_exit_code=0
open_validation_output_class=bounded report metadata only; no financial row data
read_only_api_reopen_after_desktop=PASS with GNUCASH_WRITES_ENABLED default false; validate/create/patch/delete returned 403
teardown=runtime book/app DB/backups/locks removed from ignored data paths
```

The bounded `gnucash-cli --report show` output was:

```text
* name: Balance Sheet
  guid: c4173ac99b2b448289bf4d11c731af13
```

## Result and compatibility boundary

PASS for this narrow disposable path only: GnuCash CLI 4.13 inside a temporary Debian 12 container accepted the disposable SQLite book after one write-alpha create mutation and could read report metadata from it.

This is not a broad GnuCash Desktop compatibility claim:

- the mutated book was a synthetic fixture copy, not a user/private book;
- the check used `gnucash-cli` in a disposable container, not a manual GUI session with screenshots;
- no Desktop-generated fixture was created;
- no PostgreSQL/MySQL/MariaDB/XML backend was tested;
- no real/private or only-copy write safety is claimed.

## Verification performed

```bash
python apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy <temporary external synthetic copy>
APP_ENV=test GNUCASH_WRITES_ENABLED=true JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose up --build -d
SMOKE_ADMIN_PASSWORD=<local dummy> python3 scripts/smoke/write-alpha-create-smoke.py
python apps/api/scripts/probe_gnucash_desktop_disposable_container.py --output <outside-git log path>
docker run --rm -v <temporary disposable directory>:/work:ro debian:12-slim sh -lc '<install GnuCash inside container>; gnucash-cli --logto stderr --report show --name "Balance Sheet" /work/mutated-disposable.gnucash.sqlite'
APP_ENV=test JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose up --build -d
SMOKE_ADMIN_PASSWORD=<local dummy> python3 scripts/smoke/read-only-api-smoke.py
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | <filter GNUCASH_WRITES_ENABLED>
```

Results:

- Phase 174 copied-book preflight passed with redacted source/runtime/backup classes.
- Exactly one `transaction.create` success audit row was observed for the mutation run.
- One ignored backup file was observed before cleanup.
- `gnucash-cli --report show --name "Balance Sheet"` exited `0` against the mutated disposable SQLite book.
- Read-only API smoke passed after the GnuCash CLI check, including disabled validate/create/PATCH/DELETE probes returning 403.
- Default Compose config still rendered `GNUCASH_WRITES_ENABLED: "false"` for API and web services.
- Ignored runtime book/app DB/backup/lock artifacts were removed after the run.

## Manual fallback if GUI evidence is required later

If a later phase requires real GUI Desktop evidence rather than CLI tooling, use only this disposable path:

1. Start a disposable VM/container with GnuCash Desktop installed; do not install host packages unless explicitly authorized.
2. Copy only the mutated disposable SQLite book into that environment.
3. Open the copy in GnuCash Desktop and close it without saving screenshots or exporting data.
4. Record only version, exit/status, checksum prefix, and whether the book opened.
5. Delete the disposable book and environment artifacts.

Do not open owner/private books, do not use an only-copy book, and do not publish screenshots or row data.
