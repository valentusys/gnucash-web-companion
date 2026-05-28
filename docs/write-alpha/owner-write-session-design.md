# Owner write session design

Lifecycle: preflight -> arm -> independent backup -> exact operation preview -> exact confirmation -> mutation -> read-back -> compatibility check -> restore-ready proof -> default-disabled reset -> redacted audit summary.

API/UI boundary:
- API owns gates, backup/restore checks, audit and mutation serialization.
- UI displays dangerous-mode warnings, blocked states, operation preview and reset status.
- Frontend warnings are advisory only; backend gates remain authoritative.

Failure states stop the session: wrong target, target inside git, missing backup readiness, Desktop lock hint, runtime writes enabled during preflight, APP_ENV not test/approved stronger gate, failed read-back, failed restore readiness, failed reset, redaction failure.

Evidence model: opaque refs and fingerprint prefixes only; no raw paths, account names, descriptions, memos, amounts, exports, screenshots, backups, books or app DBs committed.
