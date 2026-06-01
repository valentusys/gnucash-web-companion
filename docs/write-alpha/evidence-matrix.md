# Write evidence matrix

| Area | Current evidence | Status |
|---|---|---|
| Public read-only beta | v0.5.0 public read-only beta | Published |
| Default write-disabled posture | `.env.example`, Compose render, disabled probes | Passed |
| Owner-writebeta state-machine routes | preflight, preview, confirm, verify-reset, reset-disabled | Passed in tests and copied-book dogfood |
| CREATE copied-book dogfood | 2 routed disposable creates | Passed |
| PATCH copied-book dogfood | 1 routed metadata-only patch of owned disposable target | Passed |
| DELETE copied-book dogfood | 1 routed delete of owned disposable target | Passed |
| Final DELETE reset evidence | verify-reset `reset_required`, reset-disabled `disabled` | Passed |
| Disabled route probes | CREATE/PATCH/DELETE -> 403 after reset | Passed |
| Real working/private/original book | Out of scope | Blocked |
| Public write beta | Out of scope | Blocked |
