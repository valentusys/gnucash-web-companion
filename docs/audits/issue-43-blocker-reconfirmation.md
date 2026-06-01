# Issue #43 blocker reconfirmation

Finding: the committed app model stores audit payload JSON in `AuditLog.payload_json`; there is no `AuditLog.payload` model field. The prior copied-book run already completed CREATE 2, PATCH 1, DELETE 1, but local evidence collection aborted after successful DELETE before capturing final owner-writebeta verify-reset/reset-disabled evidence.

Minimum fix: route local helper payload parsing through a small compatibility helper that prefers `payload_json`, falls back to older `payload` only if present, and degrades diagnostic parsing failures to redacted status instead of aborting after a successful mutation.

Safety: no private book data, paths, hashes, accounts, memos, descriptions, amounts, app DB rows, backups, or screenshots are included here.

Verdict: CONTINUE.
