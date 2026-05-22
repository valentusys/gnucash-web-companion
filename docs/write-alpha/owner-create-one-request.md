# Owner copied-book CREATE-one request

Status: Phase 275 owner-facing request packet. This asks for one optional CREATE on a copied/restorable book only. It does not authorize PATCH or DELETE.

## What this asks you to do

If you choose to continue after the accepted copied-book dry-run, run exactly one minimal write-alpha CREATE test against a copied/restorable GnuCash SQL book, then share only the redacted pass/fail summary.

This is not a production-use instruction. It is one local write-alpha dogfood mutation on a copy, followed by compatibility check, restore verification, and reset to default disabled writes.

## Hard requirements before any CREATE run

Use only a copied/restorable working book outside this git repository. Do not use:

- the original GnuCash book;
- the only existing copy of a book;
- a book stored inside this repository;
- a production/shared/LAN/VPN/public-internet deployment;
- any book that is not independently restorable from a pre-mutation backup.

Keep the original closed and untouched. Keep all private paths, account names, memos, amounts, balances, screenshots, CSV exports, app DBs, books, backups, tokens, keys, certs, and `.env` contents out of chat, GitHub issues, commits, and release notes.

## Required explicit confirmation

Before the agent or operator runs owner copied-book CREATE, the owner must provide this confirmation in the same execution context:

```text
I want one CREATE test on a copied/restorable GnuCash book.
The original book is untouched and not used.
This is not my only copy.
The target, backups, and evidence are outside git.
I understand this is write-alpha, test-gated, and not production-safe.
```

Without that exact authorization, do not run owner copied-book CREATE.

## Command shape

Run from the repository root, with local placeholders replaced only on the local machine. Do not paste real paths back.

The local app stack must be configured for the copied working book, local-only access, `APP_ENV=test`, and explicit temporary `GNUCASH_WRITES_ENABLED=true` before the CREATE smoke command is run.

```bash
GNUCASH_WRITES_ENABLED=true APP_ENV=test python3 scripts/write_alpha_copied_book_dogfood.py   --create-one   --target <copied-book-path-outside-git>   --backup-dir <external-or-ignored-backup-dir>   --evidence-file <redacted-create-evidence-json>   --confirm-copied-disposable   --confirm-original-untouched   --confirm-outside-git   --confirm-create-one-mutation
```

Expected safe success shape:

```text
PASS: copied-book dogfood create-one completed; paths=redacted
```

Then validate the wrapper evidence locally:

```bash
python3 scripts/redact_dogfood_evidence.py <redacted-create-evidence-json>
```

## Required checks after CREATE

Run the compatibility harness before restore verification:

```bash
python3 scripts/write_alpha_compatibility_check.py   <copied-book-path-outside-git>   --output <redacted-compatibility-evidence-json>
```

Expected acceptable result for this owner CREATE-one packet is `pass` or a clearly explained `blocked` that does not hide a failure. A `fail` result stops the run.

Run restore verification against the copied working book from the pre-mutation backup:

```bash
python3 scripts/write_alpha_restore_verify.py   --target <copied-book-path-outside-git>   --backup <pre-mutation-backup-path>   --output <redacted-restore-evidence-json>   --confirm-copied-disposable   --confirm-original-untouched   --confirm-restore-over-copy   --confirm-backup-pre-mutation
```

Then reset the runtime/config back to `GNUCASH_WRITES_ENABLED=false` and verify disabled validate/create/PATCH/DELETE behavior. Do not continue to PATCH or DELETE.

## What to paste back

Paste only this redacted checklist. Do not include raw file paths, file names, account names, memos, amounts, balances, screenshots, CSV rows, app DBs, books, backups, `.env` contents, tokens, keys, certs, or Desktop stdout/stderr.

```text
Owner copied-book CREATE-one evidence, redacted:
- owner confirmation provided in execution context: yes/no
- copied/restorable book used: yes/no
- original book untouched: yes/no
- target/backups/evidence outside git: yes/no
- wrapper result: PASS/BLOCKED/FAIL
- redaction checker for wrapper evidence: PASS/BLOCKED/FAIL
- mutation_requested: true/other
- mutation_performed: true/other
- create_command_status: passed/other
- exactly one CREATE attempted: yes/no/unknown
- backup created before CREATE: yes/no
- read-back after CREATE: PASS/BLOCKED/FAIL
- audit evidence: one-success/blocked/fail
- lock evidence: released-or-stale-safe/blocked/fail
- compatibility check: PASS/BLOCKED/FAIL
- compatibility broad claim made: false/other
- restore verification: PASS/BLOCKED/FAIL
- default-disabled reset verified: verified-default-disabled/blocked/failed
- disabled validate/create/PATCH/DELETE probes after reset: all 403/not run/other
- PATCH run: no/other
- DELETE run: no/other
- any redaction concern: no/yes (describe without private data)
```

## Stop conditions

Stop immediately and do not retry mutation in the same session if any of these happen:

- selected target is the original or only copy;
- copied book is not restorable from a pre-mutation backup;
- target, backup, evidence, logs, or `.env` would be exposed in git or pasted to chat/GitHub;
- `APP_ENV=test` is missing during explicit write-alpha execution;
- committed/default config would enable writes;
- the app is exposed beyond local-only access;
- preflight, backup, routed CREATE, read-back, audit, lock, compatibility, restore, redaction, or reset evidence fails;
- more than one CREATE would be attempted;
- PATCH or DELETE is requested;
- any evidence contains private financial details.

Safe action on any stop condition: reset local config to `GNUCASH_WRITES_ENABLED=false`, preserve only local redacted notes, restore the copied working book from the pre-mutation backup if needed, and ask for review.

## What this does not authorize

This request does not authorize PATCH, DELETE, production use, original-book use, only-copy-book use, public-internet exposure, broad GnuCash compatibility claims, or real/private-book write-safety claims. One successful copied-book CREATE would be evidence for that one copied/restorable test only.
