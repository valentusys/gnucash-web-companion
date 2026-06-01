# Overnight cycle 1 — Issue #13 book management UI

Started: 2026-06-01T13:55:41+10:00
Completed: 2026-06-01T14:19:45+10:00
Repository: valentusys/gnucash-web-companion
Branch: main

## Analyst candidate selection

Candidate issue: #13 Book management UI.

Why this task: it is the highest-priority open product issue and can add user-facing value without GnuCash data mutation.

Expected product value:
- Read-only beta testers/admins get a clearer `/books` management path.
- Admins can register app metadata for an already-mounted copied/test SQLite book from the UI.
- Book list remains read-only and continues to avoid rendering private storage paths.

Safety risks:
- Mounted local paths are operationally sensitive.
- Book registration must not become upload/import/delete/edit-accounting-data functionality.
- Non-admin users must not be able to alter app metadata.

Recommended narrow scope:
- Add admin-only app-metadata registration for already-mounted local SQLite copied/test books.
- Keep the UI metadata-only: display name, optional base currency, mounted path, optional default fallback flag.
- Do not render raw private paths back in the book list.
- Add API and route tests for metadata-only registration and non-admin blocking.

Explicit non-goals:
- No uploads.
- No GnuCash accounting data mutation.
- No transaction/account fields or private accounting data collection.
- No collaborative/family-wallet scope.
- No real/original/private/working/only-copy book access or mutation.
- No release.

## PM scope lock

Goal: improve `/books` for #13 by adding a safe, admin-only metadata registration path for already-mounted copied/test SQLite books.

Scope:
- Backend `POST /books` endpoint registers a `Book` metadata row only.
- Endpoint validates admin role, local SQLite storage type, existing runtime file, and redacted error messages.
- Registered book is assigned owner access to the registering admin.
- Frontend `/books` page gets a localized metadata-registration form.
- Server action posts to the API without exposing raw path values in the rendered list.
- Static auth-route guard is updated to allow this safe form while still forbidding file upload/delete/collaborative framing.

Acceptance criteria:
- Admin can register an existing local SQLite copied/test file as app metadata only.
- Non-admin registration returns 403.
- Missing path errors do not echo private paths and do not create a row.
- `/books` source does not render `uri_or_path` or raw operator guidance message.
- Registration UI does not include file upload or accounting-data inputs.
- English and Russian i18n keys exist.
- Relevant API and web checks pass.

Safety checks:
- `GNUCASH_WRITES_ENABLED=false` default untouched.
- No GnuCash book files, app DBs, exports, screenshots, `.env`, secrets, or raw evidence committed.
- No original/private/working/only-copy book touched.
- GnuCash mutation counts: CREATE 0, PATCH 0, DELETE 0.

Verification commands run:
- `pytest -q apps/api/tests/test_multi_book_access.py` — passed, 39 tests.
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run check` — passed, 0 errors/warnings.
- `cd apps/web && npm run build` — passed.
- `cd apps/api && pytest -q` — passed, 611 tests.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `python3 scripts/check_public_status.py` — passed.
- `git diff --check` — passed.
- Added-lines static security scan for hardcoded secrets, shell injection, eval/exec, pickle, SQL format patterns — no findings.

## Programmer implementation summary

Changed files:
- `apps/api/app/routers/books.py`
  - Added `BookRegistrationRequest`.
  - Added admin guard and local SQLite metadata validation.
  - Added `POST /books` metadata-only registration endpoint.
- `apps/api/tests/test_multi_book_access.py`
  - Added admin fixture and tests for admin registration, non-admin denial, and redacted missing-path failure.
- `apps/web/src/routes/books/+page.server.ts`
  - Added `registerBook` action posting to API `POST /books`.
  - Added redacted API error handling.
- `apps/web/src/routes/books/+page.svelte`
  - Added localized admin metadata registration form using `mounted_path` field name.
  - Preserved no raw `uri_or_path` rendering in page source.
- `apps/web/src/lib/i18n/messages.ts`
  - Added English and Russian registration copy.
- `apps/web/scripts/test-auth-routes.mjs`
  - Added assertions for safe metadata-registration UI.
  - Updated old broad no-form assertion to keep upload/delete/collaborative prohibitions while permitting the scoped safe form.

## Auditor review

Acceptance criteria: met for the scoped #13 increment.

Scope creep check: one broader default/archive API experiment was removed before final verification because it was not required for the scoped UI and conflicted with existing unsupported-management-action posture.

Safety result:
- No GnuCash file was opened or mutated.
- No private paths or raw evidence were committed.
- Web UI uses `mounted_path` and does not render backend `uri_or_path` in the page source.
- API response serialization continues to omit `uri_or_path`.
- Default write-disabled posture and public status guard remain intact.

Issue status recommendation:
- #13 can be updated with evidence for this completed increment.
- Do not close #13 unless PM/Auditor accepts that metadata registration + current/default indicators satisfy the core issue; otherwise leave open with remaining tasks.

Release decision: NO_RELEASE for this cycle. User-facing value exists, but no release was requested and CI/push/issue update still need final post-commit verification.
