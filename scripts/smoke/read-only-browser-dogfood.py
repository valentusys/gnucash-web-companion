#!/usr/bin/env python3
"""Headless browser/UI dogfood for a local read-only deployment.

The script drives Chromium through the Chrome DevTools Protocol using only the
Python standard library. It is intended for local Docker/Caddy dogfood against a
synthetic/disposable GnuCash book. It does not write screenshots, downloads, raw
CSV exports, cookies, tokens, or private paths.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = "http://127.0.0.1:18080"


class DogfoodFailure(RuntimeError):
    """Raised when a browser dogfood check fails."""


@dataclass(frozen=True)
class CheckResult:
    name: str
    detail: str


class WebSocket:
    """Tiny client for unencrypted ws:// CDP connections."""

    def __init__(self, url: str) -> None:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "ws":
            raise DogfoodFailure(f"unsupported WebSocket URL scheme: {parsed.scheme}")
        self.host = parsed.hostname or "127.0.0.1"
        self.port = parsed.port or 80
        self.path = parsed.path or "/"
        if parsed.query:
            self.path += f"?{parsed.query}"
        self.sock = socket.create_connection((self.host, self.port), timeout=10)
        self.sock.settimeout(10)
        self._handshake()

    def _handshake(self) -> None:
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        request = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(request.encode("ascii"))
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            response += chunk
        if b" 101 " not in response.split(b"\r\n", 1)[0]:
            raise DogfoodFailure(f"CDP WebSocket handshake failed: {response[:200]!r}")

    def send_json(self, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        header = bytearray([0x81])
        length = len(data)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack("!Q", length))
        mask = os.urandom(4)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(data))
        self.sock.sendall(bytes(header) + mask + masked)

    def recv_json(self) -> dict[str, Any]:
        while True:
            first = self._recv_exact(2)
            opcode = first[0] & 0x0F
            masked = bool(first[1] & 0x80)
            length = first[1] & 0x7F
            if length == 126:
                length = struct.unpack("!H", self._recv_exact(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self._recv_exact(8))[0]
            mask = self._recv_exact(4) if masked else b""
            payload = self._recv_exact(length) if length else b""
            if masked:
                payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
            if opcode == 0x8:
                raise DogfoodFailure("CDP WebSocket closed unexpectedly")
            if opcode == 0x9:  # ping
                self._send_pong(payload)
                continue
            if opcode != 0x1:
                continue
            return json.loads(payload.decode("utf-8"))

    def _send_pong(self, payload: bytes) -> None:
        header = bytearray([0x8A])
        length = len(payload)
        header.append(0x80 | length)
        mask = os.urandom(4)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        self.sock.sendall(bytes(header) + mask + masked)

    def _recv_exact(self, length: int) -> bytes:
        data = b""
        while len(data) < length:
            chunk = self.sock.recv(length - len(data))
            if not chunk:
                raise DogfoodFailure("CDP WebSocket connection ended")
            data += chunk
        return data

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass


class CDPPage:
    def __init__(self, websocket_url: str) -> None:
        self.ws = WebSocket(websocket_url)
        self.next_id = 1

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        message_id = self.next_id
        self.next_id += 1
        self.ws.send_json({"id": message_id, "method": method, "params": params or {}})
        deadline = time.time() + 15
        while time.time() < deadline:
            message = self.ws.recv_json()
            if message.get("id") != message_id:
                continue
            if "error" in message:
                raise DogfoodFailure(f"CDP {method} failed: {message['error']}")
            return message.get("result", {})
        raise DogfoodFailure(f"CDP {method} timed out")

    def evaluate(self, expression: str, *, await_promise: bool = False) -> Any:
        result = self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "awaitPromise": await_promise,
                "returnByValue": True,
                "timeout": 10000,
            },
        )
        remote = result.get("result", {})
        if "exceptionDetails" in result:
            raise DogfoodFailure(f"browser evaluation failed: {result['exceptionDetails']}")
        return remote.get("value")

    def navigate(self, url: str) -> None:
        self.call("Page.navigate", {"url": url})
        self.wait_ready()

    def wait_ready(self, timeout: float = 10) -> None:
        deadline = time.time() + timeout
        last_state = "unknown"
        while time.time() < deadline:
            try:
                state = self.evaluate("document.readyState")
                last_state = str(state)
                if state == "complete":
                    return
            except DogfoodFailure:
                pass
            time.sleep(0.2)
        raise DogfoodFailure(f"page did not reach readyState=complete, last={last_state}")

    def wait_for(self, expression: str, timeout: float = 10) -> Any:
        deadline = time.time() + timeout
        last_value: Any = None
        while time.time() < deadline:
            last_value = self.evaluate(expression)
            if last_value:
                return last_value
            time.sleep(0.2)
        raise DogfoodFailure(f"browser condition timed out: {expression}; last={last_value!r}")

    def close(self) -> None:
        self.ws.close()


def _http_json(url: str) -> Any:
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _http_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.read().decode("utf-8")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _chrome_binary(explicit: str | None) -> str:
    candidates = [explicit] if explicit else []
    candidates += ["chromium", "chromium-browser", "google-chrome", "google-chrome-stable"]
    for candidate in candidates:
        if not candidate:
            continue
        resolved = shutil.which(candidate) if os.sep not in candidate else candidate
        if resolved and Path(resolved).exists():
            return resolved
    raise DogfoodFailure("Chromium/Chrome binary not found")


def _wait_for_debugger(stderr, timeout: float = 15) -> str:
    deadline = time.time() + timeout
    lines: list[str] = []
    while time.time() < deadline:
        line = stderr.readline()
        if not line:
            time.sleep(0.1)
            continue
        lines.append(line.strip())
        marker = "DevTools listening on "
        if marker in line:
            return line.split(marker, 1)[1].strip()
    raise DogfoodFailure(f"Chromium did not expose DevTools URL; stderr={lines[-5:]}")


def _new_page(browser_ws_url: str) -> str:
    parsed = urllib.parse.urlparse(browser_ws_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port
    if not port:
        raise DogfoodFailure("DevTools URL did not include a port")
    base = f"http://{host}:{port}"
    try:
        request = urllib.request.Request(f"{base}/json/new?about:blank", method="PUT")
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError:
        request = urllib.request.Request(f"{base}/json/new?about:blank", method="GET")
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    websocket_url = data.get("webSocketDebuggerUrl")
    if not isinstance(websocket_url, str):
        raise DogfoodFailure("DevTools /json/new did not return page websocket URL")
    return websocket_url


def _js_string(value: str) -> str:
    return json.dumps(value)


def run(args: argparse.Namespace) -> list[CheckResult]:
    password = args.password or os.environ.get("SMOKE_ADMIN_PASSWORD") or os.environ.get("APP_ADMIN_PASSWORD")
    username = args.username or os.environ.get("SMOKE_ADMIN_USERNAME") or os.environ.get("APP_ADMIN_USERNAME") or "admin"
    if not password:
        raise DogfoodFailure("Set SMOKE_ADMIN_PASSWORD or APP_ADMIN_PASSWORD; value is never printed")

    base_url = args.base_url.rstrip("/")
    chrome = _chrome_binary(args.chromium)
    temp_root = Path(tempfile.mkdtemp(prefix="gwc-browser-dogfood-"))
    user_data = temp_root / "chromium-profile"
    download_dir = temp_root / "downloads"
    download_dir.mkdir(parents=True, exist_ok=True)

    proc = subprocess.Popen(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--remote-debugging-port=0",
            f"--user-data-dir={user_data}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    page: CDPPage | None = None
    results: list[CheckResult] = []
    try:
        if proc.stderr is None:
            raise DogfoodFailure("Chromium stderr pipe unavailable")
        browser_ws = _wait_for_debugger(proc.stderr)
        page = CDPPage(_new_page(browser_ws))
        page.call("Page.enable")
        page.call("Runtime.enable")
        page.call("Browser.setDownloadBehavior", {"behavior": "deny"})
        is_mobile_viewport = args.viewport_width < 768
        page.call(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": args.viewport_width,
                "height": args.viewport_height,
                "deviceScaleFactor": 2,
                "mobile": is_mobile_viewport,
            },
        )
        viewport_kind = "mobile" if is_mobile_viewport else "desktop"
        results.append(CheckResult("browser_viewport", f"{viewport_kind} {args.viewport_width}x{args.viewport_height}"))

        def assert_no_mobile_overflow(route_name: str) -> None:
            metrics = page.evaluate(
                "(() => ({"
                "clientWidth: document.documentElement.clientWidth,"
                "scrollWidth: document.documentElement.scrollWidth,"
                "bodyScrollWidth: document.body ? document.body.scrollWidth : 0"
                "}))()"
            )
            if not isinstance(metrics, dict):
                raise DogfoodFailure(f"mobile overflow metrics unavailable on {route_name}: {metrics!r}")
            client_width = int(metrics.get("clientWidth") or 0)
            scroll_width = max(int(metrics.get("scrollWidth") or 0), int(metrics.get("bodyScrollWidth") or 0))
            if client_width <= 0 or scroll_width > client_width + 1:
                raise DogfoodFailure(f"mobile horizontal overflow on {route_name}: {metrics!r}")
            short_touch_targets = page.evaluate(
                "Array.from(document.querySelectorAll('a[href*=\"transactions/export\"]'))"
                ".map((el) => ({ text: (el.innerText || '').trim(), height: Math.round(el.getBoundingClientRect().height) }))"
                ".filter((item) => item.height > 0 && item.height < 44)"
            )
            if short_touch_targets:
                raise DogfoodFailure(f"mobile export touch target below 44px on {route_name}: {short_touch_targets!r}")
            results.append(CheckResult("mobile_no_overflow", f"{route_name}: scrollWidth={scroll_width} clientWidth={client_width}"))

        page.navigate(f"{base_url}/login")
        page.wait_for("document.body && document.body.innerText.includes('Sign in')")
        results.append(CheckResult("login_page", "loaded"))

        page.navigate(f"{base_url}/dashboard")
        page.wait_for("location.pathname === '/login' && location.search.includes('next=')")
        results.append(CheckResult("protected_redirect", "dashboard redirected to login"))

        login_js = f"""
        (() => {{
          const usernameInput = document.querySelector('input[name="username"]');
          const passwordInput = document.querySelector('input[name="password"]');
          const setValue = (input, value) => {{
            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            setter.call(input, value);
            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            input.dispatchEvent(new Event('change', {{ bubbles: true }}));
          }};
          setValue(usernameInput, {_js_string(username)});
          setValue(passwordInput, {_js_string(password)});
          document.querySelector('button[type="submit"]').click();
          return true;
        }})()
        """
        page.evaluate(login_js)
        try:
            page.wait_for("location.pathname === '/dashboard'", timeout=15)
        except DogfoodFailure as exc:
            location = page.evaluate("location.href")
            body = page.evaluate("document.body ? document.body.innerText.slice(0, 300) : ''")
            raise DogfoodFailure(f"login did not reach dashboard: location={location!r} body={body!r}") from exc
        page.wait_for("document.body.innerText.includes('Dashboard')")
        cookie_text = page.evaluate("document.cookie") or ""
        if "access_token" in cookie_text:
            raise DogfoodFailure("httpOnly access_token appeared in document.cookie")
        results.append(CheckResult("login", "authenticated; auth cookie not readable from document.cookie"))

        for route, label in [
            ("/dashboard", "dashboard"),
            ("/accounts", "accounts"),
            ("/books", "books"),
            ("/scheduled", "scheduled"),
        ]:
            page.navigate(f"{base_url}{route}")
            page.wait_for("document.body && document.body.innerText.length > 0")
            if page.evaluate("document.body.innerText.includes('New transaction')"):
                raise DogfoodFailure(f"write UI unexpectedly visible on {route}")
            assert_no_mobile_overflow(label)
            results.append(CheckResult(label, f"{route} loaded; write UI hidden"))

        page.navigate(f"{base_url}/accounts")
        account_href = page.evaluate(
            "Array.from(document.querySelectorAll('a[href^=\"/accounts/\"]')).map(a => a.getAttribute('href')).find(h => h && h.startsWith('/accounts/') && h.split('/').length === 3) || null"
        )
        if account_href:
            page.navigate(f"{base_url}{account_href}")
            page.wait_for("document.body && document.body.innerText.length > 0")
            assert_no_mobile_overflow("account_detail")
            results.append(CheckResult("account_detail", "first account detail loaded"))
        else:
            results.append(CheckResult("account_detail", "skipped: no account detail link found"))

        filter_url = f"{base_url}/transactions?query=Fixture&date_from=2024-01-01&date_to=2024-12-31&transaction_state=unreconciled&limit=25&offset=0"
        page.navigate(filter_url)
        page.wait_for("location.pathname === '/transactions' && location.search.includes('query=Fixture')")
        page.wait_for("document.body && document.body.innerText.includes('Transactions')")
        if page.evaluate("document.body.innerText.includes('New transaction')"):
            raise DogfoodFailure("write UI unexpectedly visible on transactions page")
        assert_no_mobile_overflow("transactions_filters")
        export_href = page.evaluate(
            "Array.from(document.querySelectorAll('a[href*=\"/transactions/export\"]')).map(a => a.getAttribute('href')).find(Boolean) || null"
        )
        if not isinstance(export_href, str) or "query=Fixture" not in export_href:
            raise DogfoodFailure(f"CSV export link did not preserve active filters: {export_href!r}")
        results.append(CheckResult("transactions_filters", "filtered transactions page loaded; export link preserved query"))

        page.navigate(f"{base_url}/transactions?limit=25&offset=0")
        row_clicked = page.evaluate(
            "(() => { const row = document.querySelector('tr[role=\"button\"], div[role=\"button\"]'); if (!row) return false; row.click(); return true; })()"
        )
        if row_clicked:
            page.wait_for("location.pathname.startsWith('/transactions/')", timeout=10)
            page.wait_for("document.body && document.body.innerText.length > 0")
            assert_no_mobile_overflow("transaction_detail")
            results.append(CheckResult("transaction_detail", "first transaction detail loaded"))
        else:
            results.append(CheckResult("transaction_detail", "skipped: no transaction row found"))

        csv_expression = (
            "(async () => {"
            f"const response = await fetch({_js_string(export_href)}, {{ credentials: 'same-origin' }});"
            "const text = await response.text();"
            "return {"
            "ok: response.ok,"
            "status: response.status,"
            "contentType: response.headers.get('content-type') || '',"
            "limit: response.headers.get('x-csv-export-limit') || '',"
            "total: response.headers.get('x-csv-export-total') || '',"
            "truncated: response.headers.get('x-csv-export-truncated') || '',"
            "header: text.split(String.fromCharCode(10))[0]"
            "};"
            "})()"
        )
        csv_check = page.evaluate(csv_expression, await_promise=True)
        if not isinstance(csv_check, dict) or not csv_check.get("ok"):
            raise DogfoodFailure(f"browser CSV export fetch failed: {csv_check!r}")
        if not str(csv_check.get("header", "")).startswith("id,date,description,amount,currency"):
            raise DogfoodFailure(f"browser CSV header unexpected: {csv_check!r}")
        if csv_check.get("limit") != "10000":
            raise DogfoodFailure(f"CSV export limit header unexpected: {csv_check!r}")
        results.append(
            CheckResult(
                "csv_export",
                f"status={csv_check['status']} total={csv_check.get('total')} truncated={csv_check.get('truncated')}",
            )
        )

        downloads = list(download_dir.iterdir())
        if downloads:
            raise DogfoodFailure("browser dogfood created download files unexpectedly")
        results.append(CheckResult("no_artifacts", "no screenshots/downloads/CSV files written"))

        return results
    finally:
        if page is not None:
            page.close()
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        if not args.keep_temp:
            shutil.rmtree(temp_root, ignore_errors=True)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run headless browser dogfood against local Docker/Caddy deployment.")
    parser.add_argument("--base-url", default=os.environ.get("SMOKE_WEB_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--username", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--chromium", default=os.environ.get("CHROMIUM_BIN"))
    parser.add_argument("--keep-temp", action="store_true", help="Keep temporary browser profile for debugging only")
    parser.add_argument("--fixture-path", default=None, help="Optional fixture path to hash/report without printing full path")
    parser.add_argument("--viewport-width", type=int, default=320, help="Viewport width for read-only UI dogfood")
    parser.add_argument("--viewport-height", type=int, default=720, help="Viewport height for read-only UI dogfood")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        print(f"read-only browser dogfood: target={args.base_url.rstrip('/')}")
        if args.fixture_path:
            fixture = Path(args.fixture_path)
            print(f"fixture: filename={fixture.name} sha256={_sha256_file(fixture)}")
        for result in run(args):
            print(f"ok: {result.name}: {result.detail}")
        print("PASS: read-only browser dogfood completed")
    except DogfoodFailure as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
