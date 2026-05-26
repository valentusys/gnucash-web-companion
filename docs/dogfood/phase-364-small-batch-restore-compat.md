# Phase 364 — Small batch restore and compatibility

Status: PASS.

Summary:
- Restore and compatibility passed for the small batch. The pre-batch backup was restored to an outside-git target with checksum match and piecash read-back pass. The mutated copied book passed piecash read-only compatibility and gnucash-cli/Desktop report probe via the compatibility harness. This remains copied-book dogfood evidence only.

Safety:
- No original/private/only-copy book was mutated.
- No GnuCash book, backup, app DB, raw evidence, private path, account name, memo, amount, token, key, certificate, or .env file is committed.
- GNUCASH_WRITES_ENABLED=false remains default.
- Enabled write-alpha remains APP_ENV=test gated.

Verification:
- See redacted command/check summary in PROJECT_STATUS and handoff artifacts.
