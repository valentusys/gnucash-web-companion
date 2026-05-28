# Owner recovery runbook

If a writebeta session reaches failed_hard_stop or reset_required, stop all mutation. Do not restore over a working book by default. Restore only to a separate copy first, keep `GNUCASH_WRITES_ENABLED=false`, verify read-back/compatibility, and record only redacted opaque evidence.

## Phase 768 addendum

Runbook updated for routed writebeta hard-stop/reset

Defaults remain disabled; APP_ENV=test write gate remains; no private/raw evidence or real-book mutation is authorized.
