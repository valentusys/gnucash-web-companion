# Owner copied-book dry-run quickstart

Status: Phase 263 dry-run-only owner entrypoint.

This is the single recommended entrypoint for the next owner-facing copied-book step. It performs a
local dry-run only: redacted preflight, pre-step backup creation for rehearsal discipline, redacted
evidence writing, and default-disabled reset verification. It has no CREATE, PATCH, or DELETE mode.

## Safety boundary

Use only an outside-git copied/restorable working book. Never use:

- the original GnuCash book;
- the only existing copy of a book;
- a book inside this repository;
- a production/shared/public-internet deployment;
- any evidence containing raw paths, account names, memos, amounts, screenshots, CSV rows, app DBs,
  backups, tokens, keys, certs, or private financial artifacts.

This dry-run does not prove real/private-book write safety. It does not authorize CREATE, PATCH, or
DELETE. `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture, and any explicit
write-alpha inspection still requires `APP_ENV=test`.

## One command path

Run from the repository root with placeholders replaced locally only. Do not paste real private paths
into committed docs, GitHub issues, release notes, or chat reports.

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

The entrypoint intentionally rejects mutation by construction:

- no `--create-one` flag exists;
- no PATCH or DELETE path exists;
- the wrapper validates that `mutation_requested=false`, `mutation_performed=false`, and
  `create_command_status=not-run` before reporting success.

## Evidence review before sharing

Before sharing or committing evidence, run:

```bash
python3 scripts/redact_dogfood_evidence.py <redacted-evidence-json>
```

Then manually check that the evidence contains only bounded counts/statuses/placeholders. It must not
contain private paths, filenames, account names, descriptions, memos, amounts, balances, request or
response payloads, screenshots, CSV rows, app DBs, books, backups, `.env` contents, tokens, keys, or
certificates.

## Abort conditions

Stop and do not proceed to CREATE if any of these happen:

- the target is the original or only-copy book;
- the target or evidence would need to expose private paths or financial values;
- preflight rejects the copied book or backup destination;
- `APP_ENV=test` is absent during the inspection;
- committed/default config appears to enable writes;
- redaction validation fails;
- the success output does not explicitly show no mutation.

After a clean dry-run, the next step is review of redacted dry-run evidence only. CREATE-one remains
blocked until a later explicit phase accepts that evidence and authorizes a separate plan.
