# Owner-writebeta operating guide

Use copied/restorable books only after explicit PM authorization, preflight, independent backup,
restore-to-copy plan, state-machine readiness, and redacted evidence. Real working-book mutation
remains blocked until a future exact same-context owner confirmation and PM authorization.

## Current state for #36

- #43 is closed after routed copied-book dogfood evidence was accepted narrowly.
- Routed copied/restorable evidence exists for controlled write readiness, but it is not a public write
  beta and not a real working-book safety claim.
- `v0.4.0-owner-writebeta` is not published unless a future release gate proves otherwise.
- `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture.
- Enabled write-alpha/writebeta paths remain `APP_ENV=test` gated.
- Real/private/original/only-copy books remain blocked as write targets.

## Owner and PM confirmation checklist before any real working-book trial

A real working-book trial is blocked unless all items below are true in the same execution context:

1. Owner explicitly names the target scope and confirms it is not an original, only-copy, or unbacked
   book.
2. PM explicitly authorizes the exact trial package and mutation count.
3. Desktop is closed for the target book and any app runtime lock/preflight checks pass.
4. An independent restorable backup exists before the trial, with restore steps documented.
5. The trial remains local/test-gated with `APP_ENV=test` and temporary explicit write enablement only.
6. The route preflight, preview, confirmation, audit, backup, read-back, compatibility, reset, and
   disabled-probe evidence is captured in redacted form.
7. No account names, transaction descriptions, memos, amounts, private paths, screenshots, app DBs,
   backups, books, tokens, or `.env` files are committed or posted.

If any item is missing, mark the subtask blocked and continue with non-mutating readiness work.

## Future copied/restorable authorization format

A future copied/restorable dogfood package is allowed only when the owner and PM authorization is in
same execution context as the operation. The authorization must state:

1. copied/restorable target class and outside-git staging location class, without printing a private path;
2. route family and operation counts;
3. backup/read-back/audit/lock/restore/reset expectations;
4. redaction and evidence-publication limits;
5. No original/private/real-working/only-copy book is the target.

If authorization is absent, run non-mutating guards/docs/tests only and keep #36 open.

## Phase 778 addendum

Operating guide refreshed conservatively.

Defaults remain disabled; APP_ENV=test write gate remains; no private/raw evidence or real-book
mutation is authorized.
