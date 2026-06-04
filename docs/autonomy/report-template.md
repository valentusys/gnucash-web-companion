# Autonomous supervisor report template

Status: TEMPLATE
Mode: dry-run | live
Queue: docs/autonomy/queues/example.md
Run root: .hermes/autonomy/runs/YYYYMMDDTHHMMSSZ

## Summary

- Tasks attempted:
- Tasks completed/simulated:
- Stop reason:
- GitHub state snapshot:

## Task results

| Task | Status | Attempts | Verification summary |
| --- | --- | ---: | --- |
| example-task | SIMULATED | 1 | dry-run prompt rendered |

## Gates run

Paste exact command output summaries only. Do not include private logs, local
private paths, account names, transaction descriptions, memos, amounts, raw DB
rows, screenshots, `.env`, tokens, keys, or certs.

## Safety/privacy summary

- No original/private/working/only-copy GnuCash book touched.
- No GnuCash book, app DB, backup, export, screenshot, `.env`, token, key, cert,
  private path, account name, transaction description, memo, amount, or raw
  private evidence committed.
- `GNUCASH_WRITES_ENABLED=false` remained default.
- Enabled writes remained `APP_ENV=test` gated.
- No release, tag, package, or image published.

## Limitations / follow-ups

- None recorded in this template.
