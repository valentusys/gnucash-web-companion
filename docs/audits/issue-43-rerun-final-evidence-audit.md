# Issue #43 rerun final evidence audit

Verdict: ISSUE_43_EVIDENCE_ACCEPTED.

Accepted redacted evidence:
- Helper regression fixed and covered: `AuditLog.payload_json` is parsed without assuming obsolete `.payload`; malformed diagnostic payloads no longer abort redacted evidence summary.
- Synthetic/helper rehearsal passed before copied-book mutation.
- Fresh copied/restorable owner-book copy was staged by read-only copy from the authorized Windows source; source was not mutated.
- Routed owner-writebeta/write-alpha rerun completed locked counts: CREATE 2, metadata-only PATCH 1, DELETE 1.
- PATCH/DELETE targeted only write-alpha/state-machine-created disposable transaction refs.
- DELETE read-back returned absent/404.
- Final DELETE reset evidence captured: verify-reset `reset_required`, reset-disabled `disabled`.
- Audit rows: 2 create success, 1 patch success, 1 delete success; each had backup and transaction refs.
- Disabled runtime probes after reset: CREATE/PATCH/DELETE returned 403.
- Restore/read compatibility probe passed on a private restore copy.

Limits:
- This proves copied-book owner-writebeta dogfood only.
- It does not prove real working/private/original/only-copy safety.
- It does not launch public write beta.
- It does not publish a new release.

Private/raw evidence stayed outside git.
