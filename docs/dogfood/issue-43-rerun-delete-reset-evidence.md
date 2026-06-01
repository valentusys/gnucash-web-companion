# Issue #43 rerun DELETE and reset evidence

Redacted result: exactly one DELETE succeeded on a write-alpha/state-machine-created disposable transaction. Read-back returned absent/404 for the deleted disposable transaction. The previously missing final DELETE owner-writebeta transition was captured: verify-reset returned `reset_required`; reset-disabled returned `disabled`. After restarting with writes disabled, CREATE/PATCH/DELETE probes returned 403.

Verdict: CONTINUE.
