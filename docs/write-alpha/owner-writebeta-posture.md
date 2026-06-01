# Owner-writebeta posture

Current posture after issue #43:

- Public/default product remains read-only.
- `GNUCASH_WRITES_ENABLED=false` remains the default in `.env.example` and Docker Compose rendering.
- Write execution remains gated to explicit local/test/dogfood contexts.
- Owner-writebeta routed state-machine evidence has passed on a fresh copied/restorable owner-book copy: CREATE 2, metadata-only PATCH 1, DELETE 1.
- Final DELETE verify-reset/reset-disabled evidence was captured in the rerun.
- Disabled CREATE/PATCH/DELETE route probes returned 403 after reset.

Allowed claim:
- Internal owner-only copied-book dogfood evidence for the routed owner-writebeta/write-alpha path is accepted.

Not allowed claims:
- No production safety claim.
- No stable write support claim.
- No public write beta claim.
- No real working/private/original/only-copy mutation safety claim.

Operational rule:
- Use only copied/restorable books for any future writebeta dogfood unless a separate owner decision explicitly changes scope.
