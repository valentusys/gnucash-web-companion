# Write-alpha evidence matrix

Phase 480 summary:

| Area | Evidence | Status |
|---|---|---|
| Default read-only posture | `.env.example` and Docker Compose keep `GNUCASH_WRITES_ENABLED=false` | preserved |
| Existing copied-book write-alpha evidence | Prior narrow copied/restorable evidence remains historical only | unchanged |
| Owner write-session preflight | `scripts/owner_write_session_preflight.py` with redacted PASS/BLOCKED output | added |
| Backup/restore manifest | redacted manifest fields and tests | added |
| Owner warning UI | `WriteModeWarning.svelte` owner-writebeta gate prototype | added |
| New copied-book session mutation | CREATE 0 / PATCH 0 / DELETE 0 | absent |
| Real working-book mutation | CREATE 0 / PATCH 0 / DELETE 0 | blocked |
| Public write beta | none | blocked |

No production, security-audited, public-internet, broad compatibility, public write, real/private/only-copy safety claim.
