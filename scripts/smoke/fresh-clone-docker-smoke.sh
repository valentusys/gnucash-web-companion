#!/usr/bin/env bash
# Run a fresh-clone Docker smoke test for gnucash-web-companion.
#
# The script clones the repository into a temporary directory, prepares only the
# committed synthetic fixture as runtime data, starts Docker Compose with dummy
# local-only secrets and GNUCASH_WRITES_ENABLED=false, then runs the existing API
# smoke and headless browser dogfood helpers. Runtime .env/app DB/book copies stay
# inside the temporary clone and are removed unless --keep-workdir is passed.

set -Eeuo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/smoke/fresh-clone-docker-smoke.sh [options]

Options:
  --repo PATH_OR_URL       Repository to clone (default: current git top-level)
  --ref REF               Git ref to checkout in the clone (default: HEAD)
  --workdir DIR           Existing parent directory for the temporary clone
  --port PORT             Host port for the Caddy proxy (default: 18080)
  --keep-workdir          Keep the temporary clone after the run
  -h, --help              Show this help

Environment overrides:
  FRESH_CLONE_REPO        Same as --repo
  FRESH_CLONE_REF         Same as --ref
  FRESH_CLONE_PORT        Same as --port
  CHROMIUM_BIN            Optional Chromium/Chrome binary for browser dogfood

The script intentionally uses synthetic/disposable data only and does not print
secret values. It creates an untracked .env only inside the temporary clone.
USAGE
}

log() {
  printf '[fresh-clone-smoke] %s\n' "$*"
}

fail() {
  printf '[fresh-clone-smoke] FAIL: %s\n' "$*" >&2
  exit 1
}

current_repo() {
  git rev-parse --show-toplevel 2>/dev/null || true
}

REPO="${FRESH_CLONE_REPO:-$(current_repo)}"
REF="${FRESH_CLONE_REF:-HEAD}"
PORT="${FRESH_CLONE_PORT:-18080}"
PARENT_WORKDIR=""
KEEP_WORKDIR=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO="${2:-}"
      shift 2
      ;;
    --ref)
      REF="${2:-}"
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
[[ -n "$REF" ]] || fail "git ref is required"
[[ "$PORT" =~ ^[0-9]+$ ]] || fail "port must be numeric"
command -v git >/dev/null || fail "git is required"
command -v docker >/dev/null || fail "docker is required"
command -v python3 >/dev/null || fail "python3 is required"

if [[ -n "$PARENT_WORKDIR" ]]; then
  mkdir -p "$PARENT_WORKDIR"
  WORKDIR="$(mktemp -d "$PARENT_WORKDIR/gwc-fresh-clone-smoke.XXXXXX")"
else
  WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/gwc-fresh-clone-smoke.XXXXXX")"
fi
CLONE_DIR="$WORKDIR/repo"
PROJECT_NAME="gwc_fresh_clone_$$_$(date +%s)"
ADMIN_PASSWORD="dummy-fresh-clone-smoke"
BASE_URL="http://127.0.0.1:${PORT}"
FIXTURE_SOURCE="apps/api/tests/fixtures/test-book.gnucash.sqlite"
RUNTIME_FIXTURE="data/books/main.gnucash.sqlite"

cleanup() {
  local exit_code=$?
  if [[ -d "$CLONE_DIR" ]]; then
    (
      cd "$CLONE_DIR"
      COMPOSE_PROJECT_NAME="$PROJECT_NAME" \
      JWT_SECRET=dummy-fresh-clone-validation-secret \
      APP_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
      GNUCASH_WRITES_ENABLED=false \
      docker compose down --volumes --remove-orphans >/dev/null 2>&1 || true
    )
  fi
  if [[ "$KEEP_WORKDIR" -eq 0 ]]; then
    rm -rf "$WORKDIR"
  else
    log "kept temporary clone: $CLONE_DIR"
  fi
  exit "$exit_code"
}
trap cleanup EXIT

log "clone repo=$REPO ref=$REF into $CLONE_DIR"
git clone --quiet "$REPO" "$CLONE_DIR"
(
  cd "$CLONE_DIR"
  git checkout --quiet "$REF"
  log "checked out $(git rev-parse --short HEAD)"

  [[ -f "$FIXTURE_SOURCE" ]] || fail "synthetic fixture missing in clone: $FIXTURE_SOURCE"
  mkdir -p data/books data/app data/backups
  cp "$FIXTURE_SOURCE" "$RUNTIME_FIXTURE"
  fixture_sha="$(sha256sum "$RUNTIME_FIXTURE" | awk '{print $1}')"
  log "prepared synthetic runtime fixture filename=$(basename "$RUNTIME_FIXTURE") sha256=$fixture_sha"

  cat > .env <<EOF
JWT_SECRET=dummy-fresh-clone-validation-secret
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

  log "validate Docker Compose config with writes disabled"
  COMPOSE_PROJECT_NAME="$PROJECT_NAME" docker compose config --quiet
  if ! COMPOSE_PROJECT_NAME="$PROJECT_NAME" docker compose config | grep -q 'GNUCASH_WRITES_ENABLED: "false"'; then
    fail "rendered Docker Compose config did not keep GNUCASH_WRITES_ENABLED=false"
  fi

  log "start Docker Compose at $BASE_URL"
  COMPOSE_PROJECT_NAME="$PROJECT_NAME" docker compose up -d --build

  log "wait for /api/health"
  SMOKE_HEALTH_URL="${BASE_URL}/api/health" python3 - <<'PY'
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

  log "run API smoke"
  APP_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  SMOKE_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  SMOKE_API_BASE_URL="${BASE_URL}/api" \
    scripts/smoke/read-only-api-smoke.py

  log "run DELETE disabled-write probe for tagged checkouts whose smoke helper predates it"
  SMOKE_API_BASE_URL="${BASE_URL}/api" \
  SMOKE_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  python3 - <<'PY'
import json
import os
import urllib.error
import urllib.request

base_url = os.environ["SMOKE_API_BASE_URL"].rstrip("/")
password = os.environ["SMOKE_ADMIN_PASSWORD"]


def request(method, path, payload=None, token=None, expected=200):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{base_url}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read().decode("utf-8")
            status = response.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        status = exc.code
    if status != expected:
        raise SystemExit(f"{method} {path} returned HTTP {status}, expected {expected}; body={raw[:300]}")
    return json.loads(raw) if raw else None

login = request("POST", "/auth/login", {"username": "admin", "password": password})
token = login.get("access_token")
books = request("GET", "/books", token=token)
book = next((item for item in books if item.get("is_default")), books[0])
book_id = book["id"]
body = request(
    "DELETE",
    f"/books/{book_id}/transactions/smoke-nonexistent-transaction",
    token=token,
    expected=403,
)
detail = str(body.get("detail", "")).lower()
if "writes are disabled" not in detail and "read-only" not in detail:
    raise SystemExit(f"DELETE disabled-write response did not explain read-only/write-disabled state: {body!r}")
print("ok: delete endpoint is write-disabled")
PY

  log "run browser dogfood at mobile viewport"
  SMOKE_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
    scripts/smoke/read-only-browser-dogfood.py \
      --base-url "$BASE_URL" \
      --fixture-path "$RUNTIME_FIXTURE" \
      --viewport-width 320 \
      --viewport-height 720

  log "run browser dogfood at desktop viewport"
  SMOKE_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
    scripts/smoke/read-only-browser-dogfood.py \
      --base-url "$BASE_URL" \
      --fixture-path "$RUNTIME_FIXTURE" \
      --viewport-width 1280 \
      --viewport-height 900

  log "verify no raw screenshot/export/backup artifacts were created in clone"
  python3 - <<'PY'
from pathlib import Path
import subprocess
tracked = set(subprocess.check_output(['git', 'ls-files'], text=True).splitlines())
blocked_suffixes = {'.csv', '.png', '.jpg', '.jpeg', '.webp'}
issues = []
for path in Path('.').rglob('*'):
    if not path.is_file():
        continue
    rel = str(path)
    if rel in tracked:
        continue
    parts = set(path.parts)
    if '.git' in parts or 'node_modules' in parts or '.svelte-kit' in parts or '__pycache__' in parts:
        continue
    if path.suffix.lower() in blocked_suffixes:
        issues.append(rel)
    if path.parts[:2] == ('data', 'backups') and path.name != '.gitkeep':
        issues.append(rel)
if issues:
    print('\n'.join(issues))
    raise SystemExit(1)
print('ok: no new raw screenshot/export/backup artifacts found')
PY

  log "fresh-clone smoke PASS head=$(git rev-parse --short HEAD) base_url=$BASE_URL fixture_sha=$fixture_sha"
)
