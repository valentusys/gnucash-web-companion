# Phase 174 — write-alpha copied-book preflight harness

Date: 2026-05-20
Status: PASS — synthetic dry-run only; no write mutation run

## Scope

This evidence covers the reproducible preflight harness for a future local-only write-alpha dogfood run. It does not authorize or perform a write mutation.

The harness validates only safety metadata:

- source path exists and is outside the git checkout;
- source is explicitly acknowledged as a copied/disposable candidate, not a real/private/only-copy authoritative book;
- source is not `.env`, app metadata DB, or backup artifact/backup directory;
- runtime copy target is under `data/books/` and ignored by git;
- backup directory is under `data/backups/` and ignored by git;
- dry-run output is redacted and contains no absolute private path, account name, transaction description, memo, or amount.

## Command path

```bash
python apps/api/scripts/check_dogfood_book_candidate.py \
  --write-alpha-plan \
  --dry-run \
  --confirm-disposable-copy \
  "$WRITE_ALPHA_SOURCE_BOOK"
```

`--dry-run` is metadata-only. It does not parse with `piecash`, copy into runtime data, write to the book, create backups, or mutate any app state.

## Synthetic dry-run evidence

A committed synthetic fixture was copied to a temporary external scratch directory for preflight. The temporary copy was removed after the run. The exact scratch path is intentionally omitted.

Pass output:

```text
status=ready; book=<redacted.gnucash.sqlite>; reason=write-alpha copied-book preflight passed without copying or mutation; source=external copied/disposable; runtime=ignored data/books; backups=ignored data/backups; size_bytes=212992; sha256_12=c8f22b449c49; dry_run=true
```

Intentional failure checks:

```text
status=blocked; book=<redacted.gnucash.sqlite>; reason=disposable copied-book acknowledgement is required; source=unacknowledged; runtime=not checked; backups=not checked; dry_run=true
status=blocked; book=<redacted.gnucash.sqlite>; reason=source copied/disposable book must stay outside the git working tree; source=inside repo; runtime=not checked; backups=not checked; size_bytes=212992; dry_run=true
status=blocked; book=<redacted.gnucash.sqlite>; reason=source copied/disposable book file does not exist; source=missing; runtime=not checked; backups=not checked; dry_run=true
```

No runtime book, backup directory, app DB, `.env`, screenshot, export, token, key, or real/private data artifact was created for commit.

## Redaction review

The evidence above contains only:

- redacted file class: `<redacted.gnucash.sqlite>`;
- source/runtime/backup path classes;
- byte size;
- short checksum;
- dry-run status.

It intentionally omits absolute paths, raw filenames, account names, transaction descriptions, memos, amounts, screenshots, CSV exports, app DBs, book files, backups, cookies, tokens, and `.env` values.

## Boundary

This phase stops before write-alpha dogfood mutation. A later explicitly authorized phase must re-run preflight against its disposable source before copying into ignored runtime data or enabling `GNUCASH_WRITES_ENABLED=true` locally with `APP_ENV=test`.
