# Owner recovery runbook

If a writebeta session reaches failed_hard_stop or reset_required, stop all mutation. Do not restore over a working book by default. Restore only to a separate copy first, keep `GNUCASH_WRITES_ENABLED=false`, verify read-back/compatibility, and record only redacted opaque evidence.
