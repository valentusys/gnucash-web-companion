# Autonomous long run — cycle 1

Issue: #13 Book management UI

PM scope:
- Add safe admin-only registry management actions for already-registered books.
- Implement set-default metadata action.
- Implement remove-from-registry metadata action that never deletes the underlying GnuCash file.
- Surface these actions on `/books` with EN/RU copy.

Non-goals:
- No upload.
- No GnuCash accounting data edits.
- No underlying file deletion.
- No private path rendering.

Implementation:
- API: `POST /books/{book_id}/default` sets the app metadata default book.
- API: `DELETE /books/{book_id}` archives/removes a book from the app registry only and returns `underlying_file_deleted=false`.
- API serialization exposes safe admin actions only to admins.
- Web: `/books` includes admin-only forms for set-default and remove-from-registry.
- Web: management success/error messages remain path-redacted.
- EN/RU i18n added for registry management actions.

Verification:
- `cd apps/api && pytest tests/test_multi_book_access.py -q` — 43 passed.
- `cd apps/web && npm run check` — passed, 0 errors/warnings.

Safety notes:
- No GnuCash book was opened or mutated by these actions.
- Remove-from-registry archives app metadata only; file deletion is not performed.
- Responses and UI do not expose `uri_or_path` or private paths.

Remaining #13 work after this cycle:
- Strengthen mounted path validation to reject non-SQLite / non-GnuCash-looking files safely.
- Update docs for local mounted book registration and registry management.
- Run full gates before deciding whether #13 closure criteria are satisfied.
