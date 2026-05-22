# Owner copied-book dry-run request

Status: Phase 269 owner-facing request packet. Dry-run only. Do not run CREATE, PATCH, or DELETE.

## What this asks you to do

Run one local dry-run against a copied/restorable GnuCash SQL book, then share only the redacted pass/fail summary. This dry-run is a preflight/rehearsal step. It must not mutate the book.

## Hard requirements before you start

Use only a copied/restorable working book that is outside this git repository. Do not use:

- the original GnuCash book;
- the only existing copy of a book;
- a book stored inside this repository;
- a production/shared/public-internet deployment;
- any book that is not independently restorable from your normal backup process.

Keep the original closed and untouched. Keep all private paths, account names, memos, amounts, balances, screenshots, CSV exports, app DBs, books, backups, tokens, keys, certs, and `.env` contents out of chat, GitHub issues, commits, and release notes.

## Command

Run from the repository root. Replace placeholders locally only; do not paste real paths back.

```bash
GNUCASH_WRITES_ENABLED=true APP_ENV=test \
python3 scripts/write_alpha_owner_dry_run.py \
  --target <copied-book-path-outside-git> \
  --backup-dir <external-or-ignored-backup-dir> \
  --evidence-file <redacted-evidence-json> \
  --confirm-copied-disposable \
  --confirm-original-untouched \
  --confirm-outside-git
```

Expected success line:

```text
PASS: owner copied-book dry-run completed; mutation_requested=false; mutation_performed=false; ... paths=redacted
```

Then validate the redacted evidence file locally:

```bash
python3 scripts/redact_dogfood_evidence.py <redacted-evidence-json>
```

## What to paste back

Paste only this redacted checklist, filled with pass/fail/blocked values. Do not include raw file paths or private data.

```text
Owner copied-book dry-run evidence, redacted:
- command result: PASS/BLOCKED/FAIL
- redaction checker: PASS/BLOCKED/FAIL
- copied/restorable book used: yes/no
- original book untouched: yes/no
- target outside git: yes/no
- mutation_requested: false/other
- mutation_performed: false/other
- create_command_status: not-run/other
- patch_status: not-supported-by-default/other
- delete_status: not-supported-by-default/other
- pre-step backup created: yes/no
- default-disabled reset verified: verified-default-disabled/blocked/failed
- disabled validate/create/PATCH/DELETE probes, if run: all 403/not run/other
- any redaction concern: no/yes (describe without private data)
```

If the evidence file contains raw paths, account names, memos, amounts, balances, payloads, screenshots, CSV rows, app DBs, books, backups, `.env` contents, tokens, keys, certs, or other private financial artifacts, do not paste it. Stop and keep it local.

## Stop conditions

Stop and do not proceed to CREATE if any of these happen:

- the selected target is the original or only copy;
- the copied book is not restorable;
- the target, backup, or evidence path is unsafe or inside the git checkout;
- `APP_ENV=test` is missing;
- the command output does not explicitly show `mutation_requested=false` and `mutation_performed=false`;
- evidence shows `create_command_status` other than `not-run`;
- redaction validation fails;
- `GNUCASH_WRITES_ENABLED=false` no longer appears as the committed/default posture;
- any disabled write endpoint succeeds instead of returning 403;
- Docker/auth/health checks are unclear or fail in a way you cannot explain without private details.

Safe action on any stop condition: reset local config to `GNUCASH_WRITES_ENABLED=false`, preserve only local redacted notes, and ask for review before trying again.

## What this does not authorize

This request does not authorize CREATE, PATCH, DELETE, production use, original-book use, only-copy-book use, public-internet exposure, or real/private-book write-safety claims. The current allowed next step is dry-run evidence review only.
