# Phase 249 — Write-alpha ownership documentation and operator warnings

Date: 2026-05-21

## Summary

Phase 249 documented the write-alpha ownership boundary so operators do not treat write-alpha as a general editor for historical GnuCash transactions.

The operator-facing docs now state that:

- CREATE creates transactions owned by this app's write-alpha flow.
- PATCH and DELETE are limited to write-alpha-owned transactions for the same app metadata book record.
- Historical, imported, or manually created GnuCash transactions remain read-only in this app.
- Frontend hiding is supporting UX only; backend ownership guards remain authoritative.
- The ownership boundary does not make real/private, original, production, shared, or only-copy books safe for write-alpha.

## Changes

- Updated `docs/write-alpha/transaction-ownership.md` with an explicit operator rule, CREATE marker behavior, safety-boundary wording, and operator warning section.
- Updated `docs/write-alpha/copied-book-dogfood-runbook.md` with a PATCH/DELETE ownership boundary for copied/disposable dogfood.
- Updated `docs/write-alpha/environment.md` with concise ownership-boundary guidance for local write-alpha environments.
- Updated `docs/write-alpha/dogfood-evidence-schema.md` with redacted ownership-summary evidence expectations for PATCH/DELETE scenarios.
- Updated README/README.ru, CHANGELOG, PROJECT_STATUS, docs/ROADMAP, and the public-status guard baseline to Phase 249.

## Safety posture

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- The backend `APP_ENV=test` write-alpha gate remains intact.
- No release, tag, product-code behavior change, write default change, or gate weakening was added.
- No real/private book, only-copy book, app DB, backup, `.env`, CSV/export, screenshot, token, key, cert, raw private path, account name, memo, amount, or private financial artifact was used or committed.
- Docs continue to avoid production/security/public-internet/broad-compatibility and real/private-book write-safety claims.

## Verification

```bash
python3 scripts/check_public_status.py
cd apps/api && pytest tests/test_public_status_guard.py -q
python3 - <<'PY'
from pathlib import Path
paths = [
    Path('README.md'),
    Path('README.ru.md'),
    Path('CHANGELOG.md'),
    Path('PROJECT_STATUS.md'),
    Path('docs/ROADMAP.md'),
    Path('docs/write-alpha/transaction-ownership.md'),
    Path('docs/write-alpha/copied-book-dogfood-runbook.md'),
    Path('docs/write-alpha/environment.md'),
    Path('docs/write-alpha/dogfood-evidence-schema.md'),
    Path('docs/handoff/phase-249.md'),
]
errors = []
for path in paths:
    text = path.read_text(encoding='utf-8')
    if '\t' in text:
        errors.append(f'{path}: tab character')
    if not text.endswith('\n'):
        errors.append(f'{path}: missing trailing newline')
if errors:
    print('\n'.join(errors))
    raise SystemExit(1)
print('markdown structural check: ok')
PY
git diff --check
python3 - <<'PY'
import subprocess, re
files = subprocess.check_output(['git','ls-files'], text=True).splitlines()
patterns = [
    ('.env tracked', re.compile(r'(^|/)\\.env($|\\.)')),
    ('app db/runtime db', re.compile(r'(^|/)(app\\.db|.*\\.sqlite3?|.*\\.db)$', re.I)),
    ('backup artifact', re.compile(r'(^|/)(backups?|.*\\.bak|.*\\.backup)(/|$)', re.I)),
    ('secret/key/cert/token', re.compile(r'(^|/)(id_rsa|id_ed25519|.*\\.(pem|key|crt|p12|pfx)|.*token.*|.*secret.*)$', re.I)),
    ('csv export', re.compile(r'(^|/).*\\.csv$', re.I)),
]
allow_prefixes = ('apps/api/tests/fixtures/', 'tests/fixtures/', 'docs/images/')
allow_exact = {'.env.example','.env.writealpha.example','apps/api/tests/test_config.py','apps/api/tests/test_backup_restore.py','apps/api/tests/test_transaction_writes.py','docs/security/auth-cookie-deployment.md'}
issues=[]
for f in files:
    if f in allow_exact or f.startswith(allow_prefixes):
        continue
    for label, pat in patterns:
        if pat.search(f):
            issues.append((label,f))
if issues:
    for label,f in issues:
        print(f'{label}: {f}')
    raise SystemExit(1)
print('sensitive tracked-file hygiene scan passed')
PY
```

Results:

- Public status guard: PASS.
- Targeted public-status guard tests: PASS (`19 passed`).
- Markdown structural check: PASS.
- Git diff whitespace check: PASS.
- Sensitive tracked-file hygiene scan: PASS.

## Result

Phase 249 is complete. The ownership boundary is now documented for operators without expanding write-alpha scope or claiming that write-alpha is safe for real/private or only-copy books.
