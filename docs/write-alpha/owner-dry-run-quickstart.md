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

## Troubleshooting and abort conditions

Stop and do not proceed to CREATE if any of these happen. The safe action is to preserve only redacted
local notes, reset to `GNUCASH_WRITES_ENABLED=false`, and ask for review before trying again.

| Failure class | What it means | Safe action |
| --- | --- | --- |
| Missing copied book | The `--target` path does not exist or is unreadable. | Stop. Create a fresh outside-git restorable copy from the operator's normal backup workflow. Do not point the app at the original. |
| Unsafe path | The copied book or backup/evidence destination is inside the git checkout, production-looking, or would expose a raw private path. | Stop. Move the copied working book and backups outside git or to ignored local-only storage. Do not commit raw paths. |
| Original or only-copy selected | The selected target is the source/original book, or there is no independent restorable copy. | Stop completely. Do not run dry-run or CREATE. Make a restorable copy first and leave the original closed/untouched. |
| Backup preflight fails | The pre-step backup cannot be created, is not readable, or is not outside git/ignored storage. | Stop. Fix the backup location and verify a restore path before any further test. |
| Missing `APP_ENV=test` | The inspection is not running under the required write-alpha test gate. | Stop. Do not weaken the gate. Re-run only with `APP_ENV=test` for the local dry-run. |
| Write default appears enabled | Committed/default config or rendered Compose no longer shows `GNUCASH_WRITES_ENABLED=false`. | Stop and treat this as a write-gate blocker. Restore default-disabled config before continuing. |
| Docker/config check fails | Default-disabled reset verification cannot render Compose or reports an unsafe value. | Stop if it reports unsafe values. If Docker is unavailable, record it as blocked and review locally; do not proceed to CREATE from incomplete evidence. |
| Auth/health check fails | Optional local read-only browser/API smoke cannot authenticate or `/health` is unhealthy. | Stop dogfood. Fix the local read-only deployment first; do not test writes to debug auth/health. |
| Redaction checker fails | Evidence contains a raw path, amount, memo/account-like value, payload, token, key, screenshot, CSV row, app DB, book, or backup detail. | Stop. Do not paste or commit the evidence. Redact locally and re-run validation before sharing only bounded output. |
| Success output lacks no-mutation proof | The command does not explicitly show `mutation_requested=false` and `mutation_performed=false`, or evidence shows `create_command_status` other than `not-run`. | Stop and treat this as a mutation-risk blocker. Do not proceed to CREATE. |
| Any write endpoint succeeds during disabled smoke | validate/create/PATCH/DELETE returns success while writes should be disabled. | Stop immediately. This is a write-gate regression. Do not run further dogfood. |

After a clean dry-run, the next step is review of redacted dry-run evidence only. Do not proceed to
CREATE if dry-run is not clean. CREATE-one remains blocked until a later explicit phase accepts that
evidence and authorizes a separate plan.
