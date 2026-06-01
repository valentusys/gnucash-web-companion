# Issue #43 work package 5 — fresh copied-book preflight

- goal: Complete fresh copied-book preflight.
- scope: fresh copied/restorable owner-book copy only; PM-locked routed owner-writebeta/write-alpha flow.
- non-goals: no original/working/private/only-copy mutation; no public write beta; no release.
- acceptance criteria: preflight and locked operation/evidence gates pass for this package.
- safety checks: private paths, checksums, accounts, memos, descriptions, amounts, backup filenames, app DB rows, and screenshots remain out of committed artifacts.
- verification: redacted local evidence shows CREATE 2, PATCH 1, DELETE 1 overall; final DELETE verify-reset state `reset_required`; reset-disabled state `disabled`; disabled route probes CREATE/PATCH/DELETE returned 403; restore read probe passed.
- artifacts: redacted docs only; private evidence retained outside git.
- verdict: CONTINUE.
