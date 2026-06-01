# Issue #43 work package 4 — PM fresh copied-book rerun authorization

- goal: Record PM decision for rerun on a fresh copied/restorable owner book.
- scope: PM authorized the same locked operation counts: CREATE 2, metadata/memo-only PATCH 1, DELETE 1 of a state-machine/write-alpha-created disposable transaction.
- non-goals: no real working/original/only-copy mutation; no release.
- acceptance criteria: decision recorded as AUTHORIZE_FRESH_COPIED_BOOK_RERUN.
- safety checks: source Windows file was only read/copied; mutation target was a fresh local copied/restorable copy; private paths and checksums are not committed.
- verification: VAL-PC WinRM reachable; copy staged locally; source was not mutated by this run.
- artifacts: this file.
- verdict: CONTINUE.
