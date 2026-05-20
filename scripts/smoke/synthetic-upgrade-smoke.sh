#!/usr/bin/env bash
# Synthetic local upgrade smoke for gnucash-web-companion.
#
# Starts a temporary checkout at the previous published write-alpha tag with only
# committed synthetic fixture data and a dummy app metadata DB, then checks out the
# current ref while preserving ignored runtime data. It verifies login, app
# metadata/default book access, selected-book recovery, read-only routes, audit
# summary, and disabled write probes. It never reads the operator's real
# data/app/app.db or real/private books.

set -Eeuo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/smoke/synthetic-upgrade-smoke.sh [options]

Options:
  --repo PATH_OR_URL       Repository to clone (default: current git top-level)
  --previous-ref REF       Starting published tag/ref (default: v0.2.4-writealpha)
  --current-ref REF        Ref to check out after preserving runtime data (default: HEAD)
  --workdir DIR            Existing parent directory for the temporary clone
  --port PORT              Host port for the Caddy proxy (default: 18083)
  --keep-workdir           Keep the temporary clone after the run
  -h, --help               Show this help

Environment overrides:
  SYNTHETIC_UPGRADE_REPO          Same as --repo
  SYNTHETIC_UPGRADE_PREVIOUS_REF  Same as --previous-ref
  SYNTHETIC_UPGRADE_CURRENT_REF   Same as --current-ref
  SYNTHETIC_UPGRADE_PORT          Same as --port

The smoke uses synthetic/disposable runtime data only, keeps
GNUCASH_WRITES_ENABLED=false throughout, and redacts dummy secret values from
output.
USAGE
}

log() {
  printf '[synthetic-upgrade-smoke] %s\n' "$*"
}

fail() {
  printf '[synthetic-upgrade-smoke] FAIL: %s\n' "$*" >&2
  exit 1
}

current_repo() {
  git rev-parse --show-toplevel 2>/dev/null || true
}

REPO="${SYNTHETIC_UPGRADE_REPO:-$(current_repo)}"
PREVIOUS_REF="${SYNTHETIC_UPGRADE_PREVIOUS_REF:-v0.2.4-writealpha}"
CURRENT_REF="${SYNTHETIC_UPGRADE_CURRENT_REF:-HEAD}"
PORT="${SYNTHETIC_UPGRADE_PORT:-18083}"
PARENT_WORKDIR=""
KEEP_WORKDIR=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO="${2:-}"
      shift 2
      ;;
    --previous-ref)
      PREVIOUS_REF="${2:-}"
      shift 2
      ;;
    --current-ref)
      CURRENT_REF="${2:-}"
      shift 2
      ;;
    --workdir)
      PARENT_WORKDIR="${2:-}"
      shift 2
      ;;
    --port)
      PORT="${2:-}"
      shift 2
      ;;
    --keep-workdir)
      KEEP_WORKDIR=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

[[ -n "$REPO" ]] || fail "repository path/URL is required"
[[ -n "$PREVIOUS_REF" ]] || fail "previous ref is required"
[[ -n "$CURRENT_REF" ]] || fail "current ref is required"
[[ "$PORT" =~ ^[0-9]+$ ]] || fail "port must be numeric"
command -v git >/dev/null || fail "git is required"
command -v docker >/dev/null || fail "docker is required"
command -v python3 >/dev/null || fail "python3 is required"

if [[ -n "$PARENT_WORKDIR" ]]; then
  mkdir -p "$PARENT_WORKDIR"
  WORKDIR="$(mktemp -d "$PARENT_WORKDIR/gwc-synthetic-upgrade.XXXXXX")"
else
  WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/gwc-synthetic-upgrade.XXXXXX")"
fi
CLONE_DIR="$WORKDIR/repo"
PROJECT_NAME="gwc_synthetic_upgrade_$$_$(date +%s)"
ADMIN_PASSWORD="dummy-synthetic-upgrade-password"
JWT_SECRET_VALUE="dummy-synthetic-upgrade-secret-value"
BASE_URL="http://127.0.0.1:${PORT}"
API_BASE_URL="${BASE_URL}/api"
FIXTURE_SOURCE="apps/api/tests/fixtures/test-book.gnucash.sqlite"
RUNTIME_FIXTURE="data/books/main.gnucash.sqlite"
APP_DB="data/app/app.db"
LEGACY_METADATA_JSON="$WORKDIR/legacy-metadata.json"

cleanup() {
  local exit_code=$?
  if [[ -d "$CLONE_DIR" ]]; then
    (
      cd "$CLONE_DIR"
      COMPOSE_PROJECT_NAME="$PROJECT_NAME" \
      JWT_SECRET="$JWT_SECRET_VALUE" \
      APP_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
      GNUCASH_WRITES_ENABLED=false \
      docker compose down --volumes --remove-orphans >/dev/null 2>&1 || true
    )
  fi
  if [[ "$KEEP_WORKDIR" -eq 0 ]]; then
    rm -rf "$WORKDIR"
  else
    log "kept temporary clone for inspection: $CLONE_DIR"
  fi
  exit "$exit_code"
}
trap cleanup EXIT

resolve_local_ref() {
  local repo="$1"
  local ref="$2"
  if [[ -d "$repo/.git" ]]; then
    git -C "$repo" rev-parse --verify "$ref" 2>/dev/null || printf '%s\n' "$ref"
  else
    printf '%s\n' "$ref"
  fi
}

CURRENT_CHECKOUT_REF="$(resolve_local_ref "$REPO" "$CURRENT_REF")"

write_runtime_env() {
  cat > .env <<EOF
JWT_SECRET=${JWT_SECRET_VALUE}
APP_ADMIN_USERNAME=admin
APP_ADMIN_PASSWORD=${ADMIN_PASSWORD}
GNUCASH_WRITES_ENABLED=false
API_INTERNAL_URL=http://api:8000
ORIGIN=${BASE_URL}
CORS_ORIGINS=["*"]
EOF
  chmod 0600 .env

  cat > docker-compose.override.yml <<EOF
services:
  proxy:
    ports:
      - "${PORT}:80"
EOF
}

validate_compose_false() {
  log "validate Docker Compose config keeps writes disabled"
  COMPOSE_PROJECT_NAME="$PROJECT_NAME" docker compose config --quiet
  if ! COMPOSE_PROJECT_NAME="$PROJECT_NAME" docker compose config | grep -q 'GNUCASH_WRITES_ENABLED: "false"'; then
    fail "rendered Docker Compose config did not keep GNUCASH_WRITES_ENABLED=false"
  fi
}

start_stack() {
  local label="$1"
  log "start Docker Compose for $label at $BASE_URL"
  COMPOSE_PROJECT_NAME="$PROJECT_NAME" docker compose up -d --build
}

stop_stack_preserve_runtime() {
  log "stop Docker Compose while preserving ignored runtime data"
  COMPOSE_PROJECT_NAME="$PROJECT_NAME" \
  JWT_SECRET="$JWT_SECRET_VALUE" \
  APP_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  GNUCASH_WRITES_ENABLED=false \
  docker compose down --remove-orphans
}

wait_for_health() {
  SMOKE_HEALTH_URL="${API_BASE_URL}/health" python3 - <<'PY'
import json, os, sys, time, urllib.error, urllib.request
url = os.environ['SMOKE_HEALTH_URL']
deadline = time.time() + 120
last = None
while time.time() < deadline:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
        if data.get('status') == 'ok':
            checks = data.get('checks') or {}
            if checks.get('writes_enabled') is not False:
                raise SystemExit('health did not report writes_enabled=false')
            print('ok: health status=ok writes_enabled=false')
            raise SystemExit(0)
        last = data
    except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        last = repr(exc)
    time.sleep(2)
print(f'health check timed out; last={last!r}', file=sys.stderr)
raise SystemExit(1)
PY
}

run_api_smoke() {
  log "run read-only API smoke"
  APP_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  SMOKE_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  SMOKE_API_BASE_URL="$API_BASE_URL" \
    python3 scripts/smoke/read-only-api-smoke.py
}

inject_legacy_metadata() {
  log "inject synthetic legacy app metadata into temporary app DB"
  COMPOSE_PROJECT_NAME="$PROJECT_NAME" docker compose exec -T api python - <<'PY' > "$LEGACY_METADATA_JSON"
import json, sqlite3

conn = sqlite3.connect('/data/app/app.db')
conn.row_factory = sqlite3.Row
try:
    admin = conn.execute("select id, username from users where username='admin'").fetchone()
    if admin is None:
        raise SystemExit('admin user missing in temporary app metadata DB')
    default_book = conn.execute("select id, name from books where is_default=1").fetchone()
    if default_book is None:
        raise SystemExit('default book missing in temporary app metadata DB')
    conn.execute(
        "insert into books (name, storage_type, uri_or_path, base_currency, is_default, is_archived, created_at) "
        "values (?, 'sqlite', '/data/books/phase-214-missing-synthetic.gnucash.sqlite', 'USD', 0, 0, CURRENT_TIMESTAMP)",
        ('Phase 214 unavailable synthetic book',),
    )
    legacy_book_id = int(conn.execute('select last_insert_rowid()').fetchone()[0])
    conn.execute(
        "insert into user_book_access (user_id, book_id, role) values (?, ?, 'editor')",
        (int(admin['id']), legacy_book_id),
    )
    conn.execute(
        "insert into audit_logs (user_id, book_id, action, payload_json, created_at) values (?, ?, ?, ?, CURRENT_TIMESTAMP)",
        (
            int(admin['id']),
            int(default_book['id']),
            'transaction.create',
            json.dumps({'result': 'success', 'transaction_id': 'phase-214-legacy-synthetic'}),
        ),
    )
    conn.commit()
    print(json.dumps(
        {
            'admin_id': int(admin['id']),
            'default_book_id': int(default_book['id']),
            'legacy_book_id': legacy_book_id,
            'default_book_name': default_book['name'],
        },
        sort_keys=True,
    ))
finally:
    conn.close()
PY
  log "ok: synthetic legacy app metadata inserted"
}

assert_metadata_db_preserved() {
  log "verify temporary app metadata DB remains readable after upgrade"
  local expected_json
  expected_json="$(tr -d '\n' < "$LEGACY_METADATA_JSON")"
  COMPOSE_PROJECT_NAME="$PROJECT_NAME" docker compose exec -T -e LEGACY_METADATA_JSON_CONTENT="$expected_json" api python - <<'PY'
import json, os, sqlite3

expected = json.loads(os.environ['LEGACY_METADATA_JSON_CONTENT'])
conn = sqlite3.connect('/data/app/app.db')
conn.row_factory = sqlite3.Row
try:
    default_book = conn.execute(
        'select id, name, is_default from books where id=?',
        (expected['default_book_id'],),
    ).fetchone()
    legacy_book = conn.execute(
        'select id, name, is_default from books where id=?',
        (expected['legacy_book_id'],),
    ).fetchone()
    audit_count = conn.execute(
        "select count(*) from audit_logs where book_id=? and action='transaction.create'",
        (expected['default_book_id'],),
    ).fetchone()[0]
    if default_book is None or int(default_book['is_default']) != 1:
        raise SystemExit('default book metadata was not preserved')
    if legacy_book is None or int(legacy_book['is_default']) != 0:
        raise SystemExit('synthetic secondary book metadata was not preserved')
    if int(audit_count) < 1:
        raise SystemExit('synthetic audit metadata was not preserved')
finally:
    conn.close()
print('ok: temporary app metadata DB preserved')
PY
}

verify_upgrade_routes() {
  log "verify upgraded API metadata, read-only routes, audit summary, disabled writes, and safe errors"
  SMOKE_API_BASE_URL="$API_BASE_URL" \
  SMOKE_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  LEGACY_METADATA_JSON="$LEGACY_METADATA_JSON" \
  python3 - <<'PY'
import json, os, urllib.error, urllib.parse, urllib.request

base_url = os.environ['SMOKE_API_BASE_URL'].rstrip('/')
password = os.environ['SMOKE_ADMIN_PASSWORD']
expected = json.loads(open(os.environ['LEGACY_METADATA_JSON'], encoding='utf-8').read())

def request(method, path, payload=None, token=None, expected_status=200):
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    headers = {'Accept': 'application/json'}
    if payload is not None:
        headers['Content-Type'] = 'application/json'
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(f'{base_url}{path}', data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read().decode('utf-8')
            status = response.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode('utf-8')
        status = exc.code
    if status != expected_status:
        raise SystemExit(f'{method} {path} returned HTTP {status}, expected {expected_status}; body={raw[:300]}')
    return json.loads(raw) if raw else None

login = request('POST', '/auth/login', {'username': 'admin', 'password': password})
token = login.get('access_token')
if not isinstance(token, str) or not token:
    raise SystemExit('login did not return an access token')
books = request('GET', '/books', token=token)
if not isinstance(books, list):
    raise SystemExit('/books did not return a list')
by_id = {book.get('id'): book for book in books if isinstance(book, dict)}
default_book = by_id.get(expected['default_book_id'])
legacy_book = by_id.get(expected['legacy_book_id'])
if default_book is None or default_book.get('is_default') is not True:
    raise SystemExit('upgraded /books did not expose preserved default book metadata')
if default_book.get('can_open_read_only_views') is not True:
    raise SystemExit('preserved default book is not openable after upgrade')
if legacy_book is None or legacy_book.get('status') != 'missing_file':
    raise SystemExit('upgraded /books did not expose safe unavailable synthetic book metadata')
if legacy_book.get('can_open_read_only_views') is not False:
    raise SystemExit('unavailable synthetic book advertised read-only data views')
raw_book = json.dumps(legacy_book, sort_keys=True)
if '/data/books/' in raw_book or 'phase-214-missing-synthetic.gnucash.sqlite' in raw_book:
    raise SystemExit('unavailable book metadata leaked a runtime path')
book_id = expected['default_book_id']
request('GET', f'/books/{book_id}', token=token)
request('GET', f'/books/{book_id}/accounts', token=token)
transactions = request('GET', f'/books/{book_id}/transactions?limit=5&offset=0', token=token)
if not isinstance(transactions, dict) or 'items' not in transactions:
    raise SystemExit('transactions response missing items')
request('GET', f'/books/{book_id}/reports/summary', token=token)
audit = request('GET', f'/books/{book_id}/write-alpha-audit-summary', token=token)
if audit.get('counts_by_action', {}).get('transaction.create', 0) < 1:
    raise SystemExit('audit summary did not include preserved synthetic audit metadata')
create_payload = {
    'date': '2026-05-21',
    'description': 'Upgrade smoke disabled-write probe',
    'splits': [
        {'account_id': 'synthetic-a', 'amount': '-1.00', 'currency': 'USD', 'memo': ''},
        {'account_id': 'synthetic-b', 'amount': '1.00', 'currency': 'USD', 'memo': ''},
    ],
}
for method, path, payload in [
    ('POST', f'/books/{book_id}/transactions/validate', create_payload),
    ('POST', f'/books/{book_id}/transactions', create_payload),
    ('PATCH', f'/books/{book_id}/transactions/smoke-nonexistent-transaction', {'description': 'probe'}),
    ('DELETE', f'/books/{book_id}/transactions/smoke-nonexistent-transaction', None),
]:
    body = request(method, path, payload=payload, token=token, expected_status=403)
    detail = str(body.get('detail', '')).lower()
    if 'writes are disabled' not in detail and 'read-only' not in detail:
        raise SystemExit(f'{method} disabled-write response was not explanatory')
    raw = json.dumps(body)
    if '/data/' in raw or '.gnucash' in raw or 'app.db' in raw:
        raise SystemExit(f'{method} disabled-write response leaked a path')
missing = request('GET', f'/books/{expected["legacy_book_id"]}/accounts', token=token, expected_status=503)
raw_missing = json.dumps(missing)
if '/data/' in raw_missing or '.gnucash' in raw_missing or 'app.db' in raw_missing:
    raise SystemExit('missing-book failure leaked a path')
print('ok: upgraded API route checks passed')
PY
}

verify_selected_book_recovery() {
  log "verify selected-book recovery through web route with unavailable synthetic book cookie"
  SMOKE_BASE_URL="$BASE_URL" \
  SMOKE_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  LEGACY_METADATA_JSON="$LEGACY_METADATA_JSON" \
  python3 - <<'PY'
import http.cookiejar, json, os, urllib.error, urllib.parse, urllib.request

base_url = os.environ['SMOKE_BASE_URL'].rstrip('/')
password = os.environ['SMOKE_ADMIN_PASSWORD']
expected = json.loads(open(os.environ['LEGACY_METADATA_JSON'], encoding='utf-8').read())
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar), urllib.request.HTTPRedirectHandler)
form = urllib.parse.urlencode({'username': 'admin', 'password': password}).encode('utf-8')
login = urllib.request.Request(
    f'{base_url}/login',
    data=form,
    headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': base_url,
    },
    method='POST',
)
try:
    opener.open(login, timeout=20).read()
except urllib.error.HTTPError as exc:
    if exc.code not in (302, 303):
        raise
if not any(cookie.name == 'access_token' for cookie in jar):
    raise SystemExit('web login did not set an auth cookie')
jar.set_cookie(
    http.cookiejar.Cookie(
        version=0,
        name='selected_book_id',
        value=str(expected['legacy_book_id']),
        port=None,
        port_specified=False,
        domain='127.0.0.1',
        domain_specified=False,
        domain_initial_dot=False,
        path='/',
        path_specified=True,
        secure=False,
        expires=None,
        discard=True,
        comment=None,
        comment_url=None,
        rest={'SameSite': 'Lax'},
        rfc2109=False,
    )
)
response = opener.open(f'{base_url}/accounts', timeout=20)
body = response.read().decode('utf-8', errors='replace')
if response.status != 200:
    raise SystemExit(f'/accounts returned HTTP {response.status}')
selected = [cookie.value for cookie in jar if cookie.name == 'selected_book_id']
if str(expected['default_book_id']) not in selected:
    raise SystemExit('selected_book_id cookie was not recovered to the preserved default book')
if '/data/' in body or '.gnucash.sqlite' in body or 'app.db' in body:
    raise SystemExit('selected-book recovery page leaked a path')
print('ok: selected-book recovery preserved default book and stayed path-safe')
PY
}

log "clone repo=$REPO previous_ref=$PREVIOUS_REF current_ref=$CURRENT_REF"
git clone --quiet "$REPO" "$CLONE_DIR"
(
  cd "$CLONE_DIR"
  git checkout --quiet "$PREVIOUS_REF"
  log "checked out previous tag $(git rev-parse --short HEAD)"
  [[ -f "$FIXTURE_SOURCE" ]] || fail "synthetic fixture missing in previous checkout"
  mkdir -p data/books data/app data/backups data/locks
  cp "$FIXTURE_SOURCE" "$RUNTIME_FIXTURE"
  fixture_sha="$(sha256sum "$RUNTIME_FIXTURE" | cut -d' ' -f1)"
  log "prepared synthetic runtime fixture filename=$(basename "$RUNTIME_FIXTURE") sha256=$fixture_sha"
  write_runtime_env
  validate_compose_false
  start_stack "$PREVIOUS_REF"
  wait_for_health
  run_api_smoke
  inject_legacy_metadata
  stop_stack_preserve_runtime

  git checkout --quiet "$CURRENT_CHECKOUT_REF"
  log "checked out current ref $(git rev-parse --short HEAD) with ignored runtime data preserved"
  write_runtime_env
  validate_compose_false
  start_stack "$CURRENT_REF"
  wait_for_health
  assert_metadata_db_preserved
  verify_upgrade_routes
  run_api_smoke
  verify_selected_book_recovery
  validate_compose_false
  log "PASS synthetic upgrade smoke previous=$(git rev-parse --short "$PREVIOUS_REF") current=$(git rev-parse --short HEAD)"
)
