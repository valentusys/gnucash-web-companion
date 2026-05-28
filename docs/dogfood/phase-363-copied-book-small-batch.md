# Phase 363 — Executed small copied-book write batch

Status: PASS.

Summary:
- Executed the authorized small batch on the copied/restorable book outside git: exactly two CREATE attempts/successes and exactly one metadata/memo-only PATCH attempt/success; zero DELETE attempts. A pre-batch backup was created, route-level backups were created, ownership rows were recorded for the two created transactions, read-back confirmed created transactions present, audit summary returned successful create/patch counts, and reset disabled probes for create/patch returned 403. Raw evidence stayed outside git.

Safety:
- No original/private/only-copy book was mutated.
- No GnuCash book, backup, app DB, raw evidence, private path, account name, memo, amount, token, key, certificate, or .env file is committed.
- GNUCASH_WRITES_ENABLED=false remains default.
- Enabled write-alpha remains APP_ENV=test gated.

Verification:
- See redacted command/check summary in PROJECT_STATUS and handoff artifacts.
