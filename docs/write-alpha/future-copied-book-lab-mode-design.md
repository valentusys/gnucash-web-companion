# Phase 374 — Future copied-book lab mode design

Status: PASS.

Summary:
- Design only: a future non-APP_ENV=test copied-book lab mode would require a separate explicit lab flag, copied-book marker/manifest outside git, source-original exclusion proof, per-run backup/restore enforcement, owner acknowledgement, redacted evidence output, rate/operation limits, and hard default-disabled config. Current APP_ENV=test gate remains unchanged.

Safety:
- No original/private/only-copy book was mutated.
- No GnuCash book, backup, app DB, raw evidence, private path, account name, memo, amount, token, key, certificate, or .env file is committed.
- GNUCASH_WRITES_ENABLED=false remains default.
- Enabled write-alpha remains APP_ENV=test gated.

Verification:
- See redacted command/check summary in PROJECT_STATUS and handoff artifacts.
