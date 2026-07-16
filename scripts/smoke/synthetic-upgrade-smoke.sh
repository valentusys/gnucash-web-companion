#!/usr/bin/env bash
# Synthetic local upgrade smoke for gnucash-web-companion.
#
# Starts a temporary checkout at the supported public read-only baseline with
# only committed synthetic fixture data and a dummy app metadata DB, then checks
# out the current ref while preserving ignored runtime data. It verifies auth,
# app metadata, scoped book access, selected-book recovery, read-only routes,
# audit summary, cached health, fixture immutability, redaction, and disabled
# write probes. It never reads the operator's real data/app/app.db or
# real/private books.

set -Eeuo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/smoke/synthetic-upgrade-smoke.sh [options]

Options:
  --repo PATH_OR_URL       Repository to clone (default: current git top-level)
  --previous-ref REF       Starting published tag/ref (default: v0.5.0-public-readonly-beta)
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
PREVIOUS_REF="${SYNTHETIC_UPGRADE_PREVIOUS_REF:-v0.5.0-public-readonly-beta}"
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
NORMAL_USERNAME="analyst"
NORMAL_PASSWORD="dummy-synthetic-analyst-password"
DISABLED_USERNAME="disabled-user"
DISABLED_PASSWORD="dummy-synthetic-disabled-password"
BASE_URL="http://127.0.0.1:${PORT}"
API_BASE_URL="${BASE_URL}/api"
FIXTURE_SOURCE="apps/api/tests/fixtures/test-book.gnucash.sqlite"
RUNTIME_FIXTURE="data/books/main.gnucash.sqlite"
ASSIGNED_RUNTIME_FIXTURE="data/books/assigned.gnucash.sqlite"
MISSING_RUNTIME_FIXTURE="data/books/phase-58-private-path-sentinel.gnucash.sqlite"
APP_DB="data/app/app.db"
SYNTHETIC_METADATA_JSON="$WORKDIR/synthetic-metadata.json"
BASELINE_STATE_JSON="$WORKDIR/baseline-state.json"
UPGRADED_STATE_JSON="$WORKDIR/upgraded-state.json"
SOURCE_HASHES_JSON="$WORKDIR/source-hashes.json"

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
  if git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$repo" rev-parse --verify "${ref}^{commit}" 2>/dev/null || printf '%s\n' "$ref"
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
GNUCASH_DEFAULT_BOOK_PATH=/data/books/main.gnucash.sqlite
GNUCASH_BOOK_ALLOWED_ROOTS=["/data/books"]
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

  # Older supported tags hard-code the proxy host port in docker-compose.yml.
  # Compose merges port lists from override files instead of replacing them,
  # so rewrite only the temporary clone's base compose file to avoid binding
  # both 8080 and the requested unique smoke port.
  SMOKE_PROXY_PORT="$PORT" python3 - <<'PY'
import os
from pathlib import Path

path = Path('docker-compose.yml')
text = path.read_text(encoding='utf-8')
port = os.environ['SMOKE_PROXY_PORT']
replacements = {
    '      - "8080:80"': f'      - "{port}:80"',
    "      - '8080:80'": f'      - "{port}:80"',
    '      - 8080:80': f'      - "{port}:80"',
}
updated = text
for old, new in replacements.items():
    updated = updated.replace(old, new)
if updated != text:
    path.write_text(updated, encoding='utf-8')
PY
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

prepare_synthetic_app_metadata() {
  log "prepare synthetic app metadata baseline"
  COMPOSE_PROJECT_NAME="$PROJECT_NAME" docker compose exec -T \
    -e NORMAL_USERNAME="$NORMAL_USERNAME" \
    -e NORMAL_PASSWORD="$NORMAL_PASSWORD" \
    -e DISABLED_USERNAME="$DISABLED_USERNAME" \
    -e DISABLED_PASSWORD="$DISABLED_PASSWORD" \
    -e MISSING_RUNTIME_FIXTURE="$MISSING_RUNTIME_FIXTURE" \
    api python - <<'PY' > "$SYNTHETIC_METADATA_JSON"
import json
import os
import sqlite3

from app.services.auth import hash_password

DB = '/data/app/app.db'
NOW = '2026-07-16 00:00:00.000000'
DEFAULT_PATH = '/data/books/main.gnucash.sqlite'
ASSIGNED_PATH = '/data/books/assigned.gnucash.sqlite'
MISSING_PATH = '/' + os.environ['MISSING_RUNTIME_FIXTURE'].lstrip('/')


def columns(conn, table):
    return {str(row[1]) for row in conn.execute(f'pragma table_info({table})')}


def ensure_column(conn, table, name, ddl):
    if name not in columns(conn, table):
        conn.execute(f'alter table {table} add column {ddl}')


def ensure_forward_schema(conn):
    ensure_column(conn, 'users', 'username_normalized', "username_normalized varchar(64) not null default ''")
    ensure_column(conn, 'users', 'is_enabled', 'is_enabled boolean not null default 1')
    ensure_column(conn, 'users', 'auth_version', 'auth_version integer not null default 1')
    ensure_column(conn, 'users', 'updated_at', "updated_at datetime not null default '1970-01-01 00:00:00.000000'")
    ensure_column(conn, 'books', 'canonical_path', 'canonical_path varchar(1024)')
    ensure_column(conn, 'books', 'canonical_path_hash', 'canonical_path_hash varchar(64)')
    ensure_column(conn, 'books', 'is_enabled', 'is_enabled boolean not null default 1')
    ensure_column(conn, 'books', 'updated_at', 'updated_at datetime')
    conn.execute(
        "create table if not exists book_health_snapshots ("
        "book_id integer primary key, "
        "source_status varchar(64) not null default 'not_checked', "
        "open_status varchar(64) not null default 'not_checked', "
        "accounts_status varchar(64) not null default 'not_checked', "
        "transactions_status varchar(64) not null default 'not_checked', "
        "reports_status varchar(64) not null default 'not_checked', "
        "safe_code varchar(64) not null default 'not_checked', "
        "checked_at datetime null, "
        "last_successful_at datetime null, "
        "foreign key(book_id) references books(id) on delete cascade)"
    )
    conn.execute(
        "create table if not exists write_alpha_transaction_ownership ("
        "id integer primary key autoincrement, "
        "book_id integer not null, "
        "transaction_id varchar(64) not null, "
        "created_by_user_id integer, "
        "created_by_write_alpha boolean not null, "
        "created_at datetime not null, "
        "last_mutated_at datetime not null, "
        "foreign key(book_id) references books(id) on delete cascade, "
        "foreign key(created_by_user_id) references users(id) on delete set null, "
        "unique(book_id, transaction_id))"
    )


def normalize(username):
    return str(username).strip().casefold()


def ensure_user(conn, *, username, password, display_name, is_admin, is_enabled, auth_version):
    username_key = normalize(username)
    existing = conn.execute('select id, password_hash from users where username=?', (username_key,)).fetchone()
    if existing is None:
        conn.execute(
            "insert into users "
            "(username, username_normalized, display_name, password_hash, is_admin, is_enabled, auth_version, created_at, updated_at) "
            "values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                username_key,
                username_key,
                display_name,
                hash_password(password),
                1 if is_admin else 0,
                1 if is_enabled else 0,
                int(auth_version),
                NOW,
                NOW,
            ),
        )
        return int(conn.execute('select last_insert_rowid()').fetchone()[0])
    user_id = int(existing['id'])
    conn.execute(
        "update users set username_normalized=?, display_name=?, is_admin=?, is_enabled=?, auth_version=?, updated_at=? where id=?",
        (username_key, display_name, 1 if is_admin else 0, 1 if is_enabled else 0, int(auth_version), NOW, user_id),
    )
    return user_id


def ensure_book(conn, *, name, path, is_default, is_enabled):
    existing = conn.execute('select id from books where name=?', (name,)).fetchone()
    if existing is None:
        existing = conn.execute(
            'select id from books where uri_or_path=? and is_archived=0 order by id limit 1',
            (path,),
        ).fetchone()
    if existing is None:
        conn.execute(
            "insert into books "
            "(name, storage_type, uri_or_path, canonical_path, canonical_path_hash, base_currency, is_default, is_archived, is_enabled, created_at, updated_at) "
            "values (?, 'sqlite', ?, null, null, 'USD', ?, 0, ?, ?, ?)",
            (name, path, 1 if is_default else 0, 1 if is_enabled else 0, NOW, NOW),
        )
        return int(conn.execute('select last_insert_rowid()').fetchone()[0])
    book_id = int(existing['id'])
    conn.execute(
        "update books set name=?, storage_type='sqlite', uri_or_path=?, base_currency='USD', is_default=?, is_archived=0, is_enabled=?, updated_at=? where id=?",
        (name, path, 1 if is_default else 0, 1 if is_enabled else 0, NOW, book_id),
    )
    return book_id


def upsert_access(conn, user_id, book_id, role):
    conn.execute(
        'insert or replace into user_book_access (user_id, book_id, role) values (?, ?, ?)',
        (int(user_id), int(book_id), role),
    )


def upsert_health(conn, book_id, safe_code):
    if safe_code == 'ready':
        values = ('ready', 'ready', 'ready', 'ready', 'ready', 'ready', NOW, NOW)
    else:
        values = (safe_code, 'blocked', 'blocked', 'blocked', 'blocked', safe_code, NOW, None)
    conn.execute(
        "insert or replace into book_health_snapshots "
        "(book_id, source_status, open_status, accounts_status, transactions_status, reports_status, safe_code, checked_at, last_successful_at) "
        "values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (int(book_id), *values),
    )


conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
try:
    ensure_forward_schema(conn)
    admin = conn.execute("select id from users where username='admin'").fetchone()
    if admin is None:
        raise SystemExit('admin user missing in temporary app metadata DB')
    admin_id = int(admin['id'])
    conn.execute(
        "update users set username_normalized='admin', is_enabled=1, auth_version=7, updated_at=? where id=?",
        (NOW, admin_id),
    )
    conn.execute('update books set is_default=0 where is_default=1')
    default_book_id = ensure_book(
        conn,
        name='Synthetic Main Book',
        path=DEFAULT_PATH,
        is_default=True,
        is_enabled=True,
    )
    assigned_book_id = ensure_book(
        conn,
        name='Synthetic Assigned Book',
        path=ASSIGNED_PATH,
        is_default=False,
        is_enabled=True,
    )
    missing_book_id = ensure_book(
        conn,
        name='Synthetic Unavailable Book',
        path=MISSING_PATH,
        is_default=False,
        is_enabled=False,
    )
    normal_user_id = ensure_user(
        conn,
        username=os.environ['NORMAL_USERNAME'],
        password=os.environ['NORMAL_PASSWORD'],
        display_name='Synthetic Analyst',
        is_admin=False,
        is_enabled=True,
        auth_version=3,
    )
    disabled_user_id = ensure_user(
        conn,
        username=os.environ['DISABLED_USERNAME'],
        password=os.environ['DISABLED_PASSWORD'],
        display_name='Synthetic Disabled User',
        is_admin=False,
        is_enabled=False,
        auth_version=5,
    )
    for book_id in (default_book_id, assigned_book_id, missing_book_id):
        upsert_access(conn, admin_id, book_id, 'owner')
    upsert_access(conn, normal_user_id, assigned_book_id, 'viewer')
    upsert_access(conn, disabled_user_id, assigned_book_id, 'viewer')
    upsert_health(conn, default_book_id, 'ready')
    upsert_health(conn, assigned_book_id, 'ready')
    upsert_health(conn, missing_book_id, 'missing_file')
    conn.execute(
        "insert into audit_logs (user_id, book_id, action, payload_json, created_at) values (?, ?, ?, ?, ?)",
        (admin_id, default_book_id, 'transaction.create', json.dumps({'result': 'success', 'transaction_id': 'upgrade-smoke-synthetic'}), NOW),
    )
    conn.execute(
        "insert into audit_logs (user_id, book_id, action, payload_json, created_at) values (?, ?, ?, ?, ?)",
        (admin_id, assigned_book_id, 'metadata.health.cached', json.dumps({'result': 'success'}), NOW),
    )
    conn.commit()
    print(json.dumps(
        {
            'admin_id': admin_id,
            'normal_user_id': normal_user_id,
            'disabled_user_id': disabled_user_id,
            'default_book_id': default_book_id,
            'assigned_book_id': assigned_book_id,
            'missing_book_id': missing_book_id,
        },
        sort_keys=True,
    ))
finally:
    conn.close()
PY
  log "ok: synthetic users, books, access, audit, and cached health prepared"
}

capture_metadata_state() {
  local label="$1"
  local output_json="$2"
  log "capture app metadata state: $label"
  COMPOSE_PROJECT_NAME="$PROJECT_NAME" docker compose exec -T -e STATE_LABEL="$label" api python - <<'PY' > "$output_json"
import hashlib
import json
import os
import sqlite3

TABLES = [
    'users',
    'books',
    'user_book_access',
    'book_health_snapshots',
    'audit_logs',
    'write_alpha_transaction_ownership',
]


def table_exists(conn, table):
    return conn.execute("select 1 from sqlite_master where type='table' and name=?", (table,)).fetchone() is not None


def columns(conn, table):
    return {str(row[1]) for row in conn.execute(f'pragma table_info({table})')}


def hash_text(value):
    return hashlib.sha256(str(value or '').encode('utf-8')).hexdigest()


conn = sqlite3.connect('/data/app/app.db')
conn.row_factory = sqlite3.Row
try:
    user_cols = columns(conn, 'users')
    book_cols = columns(conn, 'books')
    users = []
    for row in conn.execute('select * from users order by id'):
        username = str(row['username'])
        users.append({
            'id': int(row['id']),
            'username': username,
            'username_normalized': str(row['username_normalized']) if 'username_normalized' in user_cols else username.strip().casefold(),
            'display_name': str(row['display_name']),
            'password_hash_sha256': hash_text(row['password_hash']),
            'is_admin': bool(row['is_admin']),
            'is_enabled': bool(row['is_enabled']) if 'is_enabled' in user_cols else True,
            'auth_version': int(row['auth_version']) if 'auth_version' in user_cols else 1,
        })
    books = []
    for row in conn.execute('select * from books order by id'):
        books.append({
            'id': int(row['id']),
            'name': str(row['name']),
            'storage_type': str(row['storage_type']),
            'uri_fingerprint': hash_text(row['uri_or_path']),
            'base_currency': row['base_currency'],
            'is_default': bool(row['is_default']),
            'is_archived': bool(row['is_archived']),
            'is_enabled': bool(row['is_enabled']) if 'is_enabled' in book_cols else True,
        })
    access = [
        {'user_id': int(row['user_id']), 'book_id': int(row['book_id']), 'role': str(row['role'])}
        for row in conn.execute('select user_id, book_id, role from user_book_access order by user_id, book_id')
    ]
    health = []
    if table_exists(conn, 'book_health_snapshots'):
        health = [
            {
                'book_id': int(row['book_id']),
                'source_status': str(row['source_status']),
                'open_status': str(row['open_status']),
                'accounts_status': str(row['accounts_status']),
                'transactions_status': str(row['transactions_status']),
                'reports_status': str(row['reports_status']),
                'safe_code': str(row['safe_code']),
            }
            for row in conn.execute('select * from book_health_snapshots order by book_id')
        ]
    audit_counts = {
        str(row['action']): int(row['count'])
        for row in conn.execute('select action, count(*) as count from audit_logs group by action order by action')
    }
    row_counts = {
        table: int(conn.execute(f'select count(*) from {table}').fetchone()[0])
        for table in TABLES
        if table_exists(conn, table)
    }
    user_version = int(conn.execute('pragma user_version').fetchone()[0])
    print(json.dumps(
        {
            'label': os.environ['STATE_LABEL'],
            'user_version': user_version,
            'row_counts': row_counts,
            'users': users,
            'books': books,
            'user_book_access': access,
            'book_health_snapshots': health,
            'audit_counts_by_action': audit_counts,
        },
        sort_keys=True,
    ))
finally:
    conn.close()
PY
}

compare_metadata_state() {
  log "verify app metadata semantic state preserved"
  BASELINE_STATE_JSON="$BASELINE_STATE_JSON" UPGRADED_STATE_JSON="$UPGRADED_STATE_JSON" python3 - <<'PY'
import json
import os

baseline = json.loads(open(os.environ['BASELINE_STATE_JSON'], encoding='utf-8').read())
upgraded = json.loads(open(os.environ['UPGRADED_STATE_JSON'], encoding='utf-8').read())
keys = [
    'row_counts',
    'users',
    'books',
    'user_book_access',
    'book_health_snapshots',
    'audit_counts_by_action',
]
for key in keys:
    if baseline.get(key) != upgraded.get(key):
        raise SystemExit(f'{key} changed across upgrade: baseline={baseline.get(key)!r} upgraded={upgraded.get(key)!r}')
print(
    'ok: app metadata state preserved '
    f"users={len(upgraded['users'])} books={len(upgraded['books'])} "
    f"access={len(upgraded['user_book_access'])} audit_actions={len(upgraded['audit_counts_by_action'])} "
    f"user_version={upgraded['user_version']}"
)
PY
}

write_fixture_hashes_before() {
  DEFAULT_FIXTURE="$RUNTIME_FIXTURE" ASSIGNED_FIXTURE="$ASSIGNED_RUNTIME_FIXTURE" SOURCE_HASHES_JSON="$SOURCE_HASHES_JSON" python3 - <<'PY'
import hashlib
import json
import os


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


paths = {
    'default': os.environ['DEFAULT_FIXTURE'],
    'assigned': os.environ['ASSIGNED_FIXTURE'],
}
with open(os.environ['SOURCE_HASHES_JSON'], 'w', encoding='utf-8') as handle:
    json.dump({key: sha256(path) for key, path in paths.items()}, handle, sort_keys=True)
    handle.write('\n')
PY
}

verify_fixture_hashes_unchanged() {
  log "verify synthetic GnuCash fixtures unchanged"
  DEFAULT_FIXTURE="$RUNTIME_FIXTURE" ASSIGNED_FIXTURE="$ASSIGNED_RUNTIME_FIXTURE" SOURCE_HASHES_JSON="$SOURCE_HASHES_JSON" python3 - <<'PY'
import hashlib
import json
import os


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


expected = json.loads(open(os.environ['SOURCE_HASHES_JSON'], encoding='utf-8').read())
actual = {
    'default': sha256(os.environ['DEFAULT_FIXTURE']),
    'assigned': sha256(os.environ['ASSIGNED_FIXTURE']),
}
if actual != expected:
    raise SystemExit(f'synthetic fixture hashes changed: before={expected!r} after={actual!r}')
print('ok: synthetic fixture hashes unchanged default_sha={default} assigned_sha={assigned}'.format(**actual))
PY
}

verify_upgrade_routes() {
  log "verify upgraded API metadata, read-only routes, audit summary, disabled writes, and safe errors"
  SMOKE_API_BASE_URL="$API_BASE_URL" \
  SMOKE_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  SMOKE_NORMAL_USERNAME="$NORMAL_USERNAME" \
  SMOKE_NORMAL_PASSWORD="$NORMAL_PASSWORD" \
  SMOKE_DISABLED_USERNAME="$DISABLED_USERNAME" \
  SMOKE_DISABLED_PASSWORD="$DISABLED_PASSWORD" \
  SMOKE_JWT_SECRET="$JWT_SECRET_VALUE" \
  SYNTHETIC_METADATA_JSON="$SYNTHETIC_METADATA_JSON" \
  python3 - <<'PY'
import json, os, urllib.error, urllib.parse, urllib.request

base_url = os.environ['SMOKE_API_BASE_URL'].rstrip('/')
admin_password = os.environ['SMOKE_ADMIN_PASSWORD']
normal_username = os.environ['SMOKE_NORMAL_USERNAME']
normal_password = os.environ['SMOKE_NORMAL_PASSWORD']
disabled_username = os.environ['SMOKE_DISABLED_USERNAME']
disabled_password = os.environ['SMOKE_DISABLED_PASSWORD']
expected = json.loads(open(os.environ['SYNTHETIC_METADATA_JSON'], encoding='utf-8').read())
unsafe_fragments = [
    '/data/',
    'phase-58-private-path-sentinel',
    os.environ['SMOKE_ADMIN_PASSWORD'],
    os.environ['SMOKE_NORMAL_PASSWORD'],
    os.environ['SMOKE_DISABLED_PASSWORD'],
    os.environ['SMOKE_JWT_SECRET'],
]


def assert_no_private(label, value):
    raw = value if isinstance(value, str) else json.dumps(value, sort_keys=True)
    for fragment in unsafe_fragments:
        if fragment and fragment in raw:
            raise SystemExit(f'{label} leaked a private fragment')


def redacted(raw):
    text = raw if isinstance(raw, str) else str(raw)
    for fragment in unsafe_fragments:
        if fragment:
            text = text.replace(fragment, '[redacted]')
    return text

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
    expected_statuses = (expected_status,) if isinstance(expected_status, int) else tuple(expected_status)
    if status not in expected_statuses:
        raise SystemExit(f'{method} {path} returned HTTP {status}, expected {expected_status}; body={redacted(raw)[:300]}')
    assert_no_private(f'{method} {path}', raw)
    return json.loads(raw) if raw else None


def login(username, password, expected_status=200):
    body = request('POST', '/auth/login', {'username': username, 'password': password}, expected_status=expected_status)
    if expected_status != 200:
        return None
    token = body.get('access_token') if isinstance(body, dict) else None
    if not isinstance(token, str) or not token:
        raise SystemExit(f'login for {username} did not return an access token')
    return token


health = request('GET', '/health')
if health.get('checks', {}).get('writes_enabled') is not False:
    raise SystemExit('/health did not report writes_enabled=false after upgrade')

admin_token = login('admin', admin_password)
normal_token = login(normal_username, normal_password)
login(disabled_username, disabled_password, expected_status=401)

books = request('GET', '/books', token=admin_token)
if not isinstance(books, list):
    raise SystemExit('/books did not return a list')
by_id = {book.get('id'): book for book in books if isinstance(book, dict)}
default_book = by_id.get(expected['default_book_id'])
assigned_book = by_id.get(expected['assigned_book_id'])
if default_book is None or default_book.get('is_default') is not True:
    raise SystemExit('upgraded /books did not expose preserved default book metadata')
if default_book.get('can_open_read_only_views') is not True:
    raise SystemExit('preserved default book is not openable after upgrade')
if default_book.get('health', {}).get('safe_code') != 'ready':
    raise SystemExit('preserved default book cached health was not ready')
if assigned_book is None or assigned_book.get('is_default') is not False:
    raise SystemExit('upgraded /books did not expose preserved assigned book metadata')
if assigned_book.get('can_open_read_only_views') is not True:
    raise SystemExit('preserved assigned book is not openable after upgrade')
if assigned_book.get('health', {}).get('safe_code') != 'ready':
    raise SystemExit('preserved assigned book cached health was not ready')

missing_detail = request('GET', f'/books/{expected["missing_book_id"]}', token=admin_token)
if missing_detail.get('is_enabled') is not False or missing_detail.get('can_open_read_only_views') is not False:
    raise SystemExit('unavailable synthetic book was not preserved as disabled/non-openable')

normal_books = request('GET', '/books', token=normal_token)
if not isinstance(normal_books, list):
    raise SystemExit('normal-user /books did not return a list')
normal_ids = {book.get('id') for book in normal_books if isinstance(book, dict)}
if normal_ids != {expected['assigned_book_id']}:
    raise SystemExit(f'normal user saw unexpected book ids: {sorted(normal_ids)!r}')
request('GET', f'/books/{expected["default_book_id"]}', token=normal_token, expected_status=403)

book_id = expected['default_book_id']
assigned_id = expected['assigned_book_id']
request('GET', f'/books/{book_id}', token=admin_token)
request('GET', f'/books/{book_id}/accounts', token=admin_token)
request('GET', f'/books/{assigned_id}/accounts', token=normal_token)
transactions = request('GET', f'/books/{book_id}/transactions?limit=5&offset=0', token=admin_token)
if not isinstance(transactions, dict) or 'items' not in transactions:
    raise SystemExit('transactions response missing items')
request('GET', f'/books/{assigned_id}/transactions?limit=5&offset=0', token=normal_token)
request('GET', f'/books/{book_id}/reports/summary', token=admin_token)
request('GET', f'/books/{assigned_id}/reports/summary', token=normal_token)

admin_users = request('GET', '/admin/users?limit=50&offset=0', token=admin_token)
if admin_users.get('total_count', 0) < 3:
    raise SystemExit('admin users endpoint did not expose preserved synthetic users')
users_by_name = {item.get('username'): item for item in admin_users.get('items', []) if isinstance(item, dict)}
if users_by_name.get(disabled_username, {}).get('is_enabled') is not False:
    raise SystemExit('admin users endpoint did not preserve disabled user state')
if users_by_name.get(normal_username, {}).get('assignment_count') != 1:
    raise SystemExit('admin users endpoint did not preserve normal-user assignment count')

book_options = request('GET', '/admin/book-access/books?limit=50&offset=0', token=admin_token)
option_ids = {item.get('id') for item in book_options.get('items', []) if isinstance(item, dict)}
if expected['default_book_id'] not in option_ids or expected['assigned_book_id'] not in option_ids:
    raise SystemExit('admin book-access options did not include active preserved books')
if expected['missing_book_id'] in option_ids:
    raise SystemExit('admin book-access options exposed disabled unavailable book')

audit = request('GET', f'/books/{book_id}/write-alpha-audit-summary', token=admin_token)
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
    body = request(method, path, payload=payload, token=admin_token, expected_status=403)
    detail = str(body.get('detail', '')).lower()
    if 'writes are disabled' not in detail and 'read-only' not in detail:
        raise SystemExit(f'{method} disabled-write response was not explanatory')
request('GET', f'/books/{expected["missing_book_id"]}/accounts', token=admin_token, expected_status=503)
print(
    'ok: upgraded API route checks passed '
    'admin_login=1 normal_login=1 disabled_denied=1 scoped_access=1 '
    'readonly_sections=4 disabled_write_probes=4 leak_checks=all'
)
PY
}

verify_selected_book_recovery() {
  log "verify selected-book recovery through web route with unavailable synthetic book cookie"
  SMOKE_BASE_URL="$BASE_URL" \
  SMOKE_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  SYNTHETIC_METADATA_JSON="$SYNTHETIC_METADATA_JSON" \
  python3 - <<'PY'
import http.cookiejar, json, os, urllib.error, urllib.parse, urllib.request

base_url = os.environ['SMOKE_BASE_URL'].rstrip('/')
password = os.environ['SMOKE_ADMIN_PASSWORD']
expected = json.loads(open(os.environ['SYNTHETIC_METADATA_JSON'], encoding='utf-8').read())
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
        value=str(expected['missing_book_id']),
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

log "clone fresh temporary checkout previous_ref=$PREVIOUS_REF current_ref=$CURRENT_REF"
git clone --quiet "$REPO" "$CLONE_DIR"
(
  cd "$CLONE_DIR"
  git checkout --quiet "$PREVIOUS_REF"
  previous_sha="$(git rev-parse --short HEAD)"
  log "checked out supported baseline $previous_sha"
  [[ -f "$FIXTURE_SOURCE" ]] || fail "synthetic fixture missing in previous checkout"
  mkdir -p data/books data/app data/backups data/locks
  cp "$FIXTURE_SOURCE" "$RUNTIME_FIXTURE"
  cp "$FIXTURE_SOURCE" "$ASSIGNED_RUNTIME_FIXTURE"
  write_fixture_hashes_before
  log "prepared synthetic runtime fixtures default=$(basename "$RUNTIME_FIXTURE") assigned=$(basename "$ASSIGNED_RUNTIME_FIXTURE")"
  write_runtime_env
  validate_compose_false
  start_stack "$PREVIOUS_REF"
  wait_for_health
  prepare_synthetic_app_metadata
  capture_metadata_state "baseline" "$BASELINE_STATE_JSON"
  run_api_smoke
  stop_stack_preserve_runtime

  git checkout --quiet -- docker-compose.yml
  git checkout --quiet "$CURRENT_CHECKOUT_REF"
  current_sha="$(git rev-parse --short HEAD)"
  log "checked out current ref $current_sha with ignored runtime data preserved"
  write_runtime_env
  validate_compose_false
  start_stack "$CURRENT_REF"
  wait_for_health
  capture_metadata_state "upgraded" "$UPGRADED_STATE_JSON"
  compare_metadata_state
  verify_fixture_hashes_unchanged
  verify_upgrade_routes
  run_api_smoke
  verify_selected_book_recovery
  validate_compose_false
  log "PASS synthetic upgrade smoke previous=$previous_sha current=$current_sha baseline=v0.5.0-public-readonly-beta writes_enabled=false"
)
