# Issue #43 PM scope lock

Goal: lock the exact #43 slice under the project lead profile.

Scope:
- routed non-mutating preflight/status API;
- redacted CREATE/PATCH/DELETE preview;
- confirmation/arming token bound to preview hash;
- active-session mutation guard for existing write-alpha routes;
- verification/default-reset state visibility;
- conservative UI state-information shell;
- no real-book or original-book mutation.

Non-goals:
- no public write beta;
- no production/stable/security-audited claims;
- no amount/account/split-changing PATCH;
- no historical/manual transaction DELETE;
- no release unless all gates and copied-book dogfood pass.

PM decision: AUTHORIZE_NARROW_ROUTED_FOUNDATION. Copied-book dogfood may be attempted only if Phases C-H pass and the copied/restorable book is available outside git.

PM max dogfood operation counts if reached: 2 CREATE, 1 metadata/memo-only PATCH on a state-machine-created transaction, 1 DELETE of a state-machine-created disposable transaction. Historical/manual deletion is forbidden. Amount/account/split mutation is forbidden.

Safety checks: defaults remain write-disabled; APP_ENV=test gate remains; evidence must stay redacted.

Verification: scope recorded in this file.

Expected artifacts: this scope lock and `docs/handoff/issue-43-phase-b.md`.

Final verdict: CONTINUE.
