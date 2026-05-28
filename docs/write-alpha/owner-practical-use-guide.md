# Owner practical use guide

- goal: summarize what the owner can do now.
- scope: read-only use, copied-book write-alpha dogfood, backup/restore, forbidden original-book use, stop conditions.
- non-goals: no production-readiness claim, no stable release, no original/private/only-copy support.
- acceptance criteria: guide is clear and conservative.
- safety checks: no private data.
- verification: final public-status and hygiene checks run later.
- expected artifacts: this guide and `docs/handoff/phase-422.md`.
- final verdict: CONTINUE.

Practical answer:
- Use the app as read-only by default.
- Write-alpha is experimental and copied-book-only.
- Never point write-alpha at the original book or the only copy of a book.
- For dogfood, use a copied/restorable SQL working book outside git, create an independent backup first, and keep raw evidence outside the repository.
- Current accepted copied-book write-alpha evidence is narrow: CREATE, metadata/memo-only PATCH, one disposable write-alpha-owned DELETE chain, and bounded small/realistic batches.
- Stop on any backup, read-back, audit, ownership, restore, compatibility, lock, redaction, or default-reset failure.
- `GNUCASH_WRITES_ENABLED=false` remains the default; enabled write-alpha remains `APP_ENV=test` gated.
