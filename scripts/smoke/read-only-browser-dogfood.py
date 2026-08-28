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


BOUNDED_TRANSACTION_FILTERS: tuple[tuple[str, str], ...] = (
    ("date_from", "2024-01-01"),
    ("date_to", "2024-12-31"),
    ("transaction_state", "unreconciled"),
    ("sort", "date_desc"),
    ("page_size", "25"),
)
SUPPORTED_EXPORT_FILTERS = BOUNDED_TRANSACTION_FILTERS[:3]


def _bounded_transactions_url(base_url: str) -> str:
    query = urllib.parse.urlencode(BOUNDED_TRANSACTION_FILTERS)
    return f"{base_url.rstrip('/')}/transactions?{query}"


def _assert_export_preserves_supported_filters(export_href: str | None) -> None:
    if not isinstance(export_href, str):
        raise DogfoodFailure(
            f"CSV export link did not preserve supported active filters: {export_href!r}"
        )
    query = urllib.parse.parse_qs(
        urllib.parse.urlparse(export_href).query,
        keep_blank_values=True,
    )
    if any(query.get(name) != [value] for name, value in SUPPORTED_EXPORT_FILTERS):
        raise DogfoodFailure(
            f"CSV export link did not preserve supported active filters: {export_href!r}"
        )


class WebSocket:
    """Small RFC 6455 client for loopback CDP connections."""

    _GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    _MAX_MESSAGE_BYTES = 16 * 1024 * 1024

    def __init__(self, url: str) -> None:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "ws":
            raise DogfoodFailure(f"unsupported WebSocket URL scheme: {parsed.scheme}")
        self.host = parsed.hostname or "127.0.0.1"
        self.port = parsed.port or 80
        self.path = parsed.path or "/"
        if parsed.query:
            self.path += f"?{parsed.query}"
        self._recv_buffer = bytearray()
        self.sock = socket.create_connection((self.host, self.port), timeout=10)
        self.sock.settimeout(10)
        self._handshake()
        self.sock.settimeout(1)

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
            if len(response) > 64 * 1024:
                raise DogfoodFailure("CDP WebSocket handshake headers exceeded 64 KiB")
        headers_blob, separator, remainder = response.partition(b"\r\n\r\n")
        if not separator:
            raise DogfoodFailure("CDP WebSocket handshake ended before headers completed")
        lines = headers_blob.split(b"\r\n")
        if not lines or b" 101 " not in lines[0]:
            raise DogfoodFailure(f"CDP WebSocket handshake failed: {headers_blob[:200]!r}")
        headers: dict[str, str] = {}
        for line in lines[1:]:
            name, delimiter, value = line.partition(b":")
            if not delimiter:
                continue
            headers[name.decode("ascii", errors="replace").strip().lower()] = value.decode(
                "ascii", errors="replace"
            ).strip()
        expected_accept = base64.b64encode(
            hashlib.sha1((key + self._GUID).encode("ascii")).digest()
        ).decode("ascii")
        if headers.get("sec-websocket-accept") != expected_accept:
            raise DogfoodFailure("CDP WebSocket Sec-WebSocket-Accept validation failed")
        if headers.get("upgrade", "").lower() != "websocket":
            raise DogfoodFailure("CDP WebSocket handshake omitted Upgrade: websocket")
        connection_tokens = {
            token.strip().lower() for token in headers.get("connection", "").split(",")
        }
        if "upgrade" not in connection_tokens:
            raise DogfoodFailure("CDP WebSocket handshake omitted Connection: Upgrade")
        if remainder:
            self._recv_buffer.extend(remainder)

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
        fragments = bytearray()
        fragmented_opcode: int | None = None
        while True:
            first = self._recv_exact(2)
            final = bool(first[0] & 0x80)
            reserved = first[0] & 0x70
            opcode = first[0] & 0x0F
            masked = bool(first[1] & 0x80)
            length = first[1] & 0x7F
            if reserved:
                raise DogfoodFailure("CDP WebSocket used unsupported reserved frame bits")
            if length == 126:
                length = struct.unpack("!H", self._recv_exact(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self._recv_exact(8))[0]
            if length > self._MAX_MESSAGE_BYTES:
                raise DogfoodFailure("CDP WebSocket frame exceeded 16 MiB safety limit")
            if masked:
                raise DogfoodFailure("CDP WebSocket server sent an invalid masked frame")
            if opcode >= 0x8 and (not final or length > 125):
                raise DogfoodFailure("CDP WebSocket sent an invalid control frame")
            payload = self._recv_exact(length) if length else b""
            if opcode == 0x8:
                raise DogfoodFailure("CDP WebSocket closed unexpectedly")
            if opcode == 0x9:
                self._send_pong(payload)
                continue
            if opcode == 0xA:
                continue
            if opcode == 0x1:
                if fragmented_opcode is not None:
                    raise DogfoodFailure("CDP WebSocket started a message before continuation completed")
                if final:
                    return self._decode_json(payload)
                fragmented_opcode = opcode
                fragments.extend(payload)
                continue
            if opcode == 0x0:
                if fragmented_opcode != 0x1:
                    raise DogfoodFailure("CDP WebSocket sent an unexpected continuation frame")
                fragments.extend(payload)
                if len(fragments) > self._MAX_MESSAGE_BYTES:
                    raise DogfoodFailure("CDP WebSocket message exceeded 16 MiB safety limit")
                if final:
                    return self._decode_json(bytes(fragments))
                continue
            raise DogfoodFailure(f"CDP WebSocket sent unsupported opcode 0x{opcode:x}")

    @staticmethod
    def _decode_json(payload: bytes) -> dict[str, Any]:
        try:
            decoded = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise DogfoodFailure("CDP WebSocket returned invalid JSON") from exc
        if not isinstance(decoded, dict):
            raise DogfoodFailure("CDP WebSocket JSON message was not an object")
        return decoded

    def _send_pong(self, payload: bytes) -> None:
        header = bytearray([0x8A, 0x80 | len(payload)])
        mask = os.urandom(4)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        self.sock.sendall(bytes(header) + mask + masked)

    def _recv_exact(self, length: int) -> bytes:
        buffer = getattr(self, "_recv_buffer", bytearray())
        data = bytearray()
        if buffer:
            take = min(length, len(buffer))
            data.extend(buffer[:take])
            del buffer[:take]
        while len(data) < length:
            chunk = self.sock.recv(length - len(data))
            if not chunk:
                raise DogfoodFailure("CDP WebSocket connection ended")
            data.extend(chunk)
        return bytes(data)

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass


class CDPPage:
    def __init__(self, websocket_url: str, *, command_timeout: float = 60) -> None:
        self.ws = WebSocket(websocket_url)
        self.next_id = 1
        self.command_timeout = command_timeout

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        message_id = self.next_id
        self.next_id += 1
        self.ws.send_json({"id": message_id, "method": method, "params": params or {}})
        deadline = time.monotonic() + self.command_timeout
        while time.monotonic() < deadline:
            try:
                message = self.ws.recv_json()
            except socket.timeout:
                continue
            if message.get("id") != message_id:
                continue
            if "error" in message:
                raise DogfoodFailure(f"CDP {method} failed: {message['error']}")
            result = message.get("result", {})
            if not isinstance(result, dict):
                raise DogfoodFailure(f"CDP {method} returned an invalid result")
            return result
        raise DogfoodFailure(f"CDP {method} timed out after {self.command_timeout:g}s")

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


def _free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _wait_for_devtools(
    debug_port: int,
    proc: subprocess.Popen[str],
    timeout: float = 30,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    version_url = f"http://127.0.0.1:{debug_port}/json/version"
    last_error = "endpoint not ready"
    while time.monotonic() < deadline:
        return_code = proc.poll()
        if return_code is not None:
            raise DogfoodFailure(f"Chromium exited before CDP became ready: exit={return_code}")
        try:
            data = _http_json(version_url)
            if isinstance(data, dict) and isinstance(data.get("webSocketDebuggerUrl"), str):
                return data
            last_error = "version response omitted webSocketDebuggerUrl"
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
            last_error = type(exc).__name__
        time.sleep(0.1)
    raise DogfoodFailure(f"Chromium CDP endpoint did not become ready: {last_error}")


def _page_websocket_url(debug_port: int) -> str:
    base = f"http://127.0.0.1:{debug_port}"
    targets = _http_json(f"{base}/json/list")
    if isinstance(targets, list):
        for target in targets:
            if (
                isinstance(target, dict)
                and target.get("type") == "page"
                and isinstance(target.get("webSocketDebuggerUrl"), str)
            ):
                return target["webSocketDebuggerUrl"]
    request = urllib.request.Request(f"{base}/json/new?about:blank", method="PUT")
    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    websocket_url = data.get("webSocketDebuggerUrl") if isinstance(data, dict) else None
    if not isinstance(websocket_url, str):
        raise DogfoodFailure("DevTools did not expose a page websocket URL")
    return websocket_url


def _launch_chrome(
    chrome: str,
    user_data: Path,
) -> tuple[subprocess.Popen[str], int, dict[str, Any]]:
    debug_port = _free_loopback_port()
    proc = subprocess.Popen(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-background-networking",
            "--disable-component-update",
            "--disable-default-apps",
            "--no-first-run",
            "--no-proxy-server",
            "--proxy-server=direct://",
            "--proxy-bypass-list=*",
            "--remote-debugging-address=127.0.0.1",
            f"--remote-debugging-port={debug_port}",
            f"--user-data-dir={user_data}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        version = _wait_for_devtools(debug_port, proc)
    except Exception:
        _stop_chrome(proc)
        raise
    return proc, debug_port, version


def _stop_chrome(proc: subprocess.Popen[str] | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)


def _probe_cdp(args: argparse.Namespace) -> str:
    chrome = _chrome_binary(args.chromium)
    temp_root = Path(tempfile.mkdtemp(prefix="gwc-cdp-probe-"))
    page: CDPPage | None = None
    proc: subprocess.Popen[str] | None = None
    try:
        proc, debug_port, endpoint_version = _launch_chrome(
            chrome,
            temp_root / "chromium-profile",
        )
        page = CDPPage(_page_websocket_url(debug_port))
        cdp_version = page.call("Browser.getVersion")
        product = cdp_version.get("product") or endpoint_version.get("Browser")
        protocol = cdp_version.get("protocolVersion") or endpoint_version.get("Protocol-Version")
        if not isinstance(product, str) or not product:
            raise DogfoodFailure("CDP Browser.getVersion omitted product")
        if not isinstance(protocol, str) or not protocol:
            raise DogfoodFailure("CDP Browser.getVersion omitted protocol version")
        return f"{product} protocol={protocol}"
    finally:
        if page is not None:
            page.close()
        _stop_chrome(proc)
        if not args.keep_temp:
            shutil.rmtree(temp_root, ignore_errors=True)


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

    proc: subprocess.Popen[str] | None = None
    page: CDPPage | None = None
    results: list[CheckResult] = []
    try:
        proc, debug_port, endpoint_version = _launch_chrome(chrome, user_data)
        page = CDPPage(_page_websocket_url(debug_port))
        cdp_version = page.call("Browser.getVersion")
        browser_product = cdp_version.get("product") or endpoint_version.get("Browser")
        if not isinstance(browser_product, str) or not browser_product:
            raise DogfoodFailure("CDP Browser.getVersion omitted product")
        results.append(CheckResult("browser_cdp", browser_product))
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

        if args.unavailable_book_id is not None:
            page.navigate(f"{base_url}/books/{int(args.unavailable_book_id)}/select?next=/dashboard")
            page.wait_for(
                "location.pathname === '/books' && location.search.includes('book_context=unavailable_selected_book')",
                timeout=15,
            )
            page.wait_for("document.body && document.body.innerText.includes('storage diagnostics')")
            unsafe_unavailable_links = page.evaluate(
                f"Array.from(document.querySelectorAll('a[href*=\"/books/{int(args.unavailable_book_id)}/select\"]')).map((a) => a.getAttribute('href'))"
            )
            if unsafe_unavailable_links:
                raise DogfoodFailure(
                    f"unavailable book advertised read-only data links: {unsafe_unavailable_links!r}"
                )
            unavailable_body = page.evaluate("document.body ? document.body.innerText : ''") or ""
            for unsafe_fragment in ["/data/", "/tmp/", "gnucash.sqlite", "uri_or_path", "backup", "memo", "0.00"]:
                if unsafe_fragment in unavailable_body:
                    raise DogfoodFailure(f"unavailable-book recovery leaked unsafe fragment: {unsafe_fragment}")
            results.append(CheckResult("unavailable_book_recovery", "redirected to /books with path-safe diagnostics and no data-view links"))

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

        filter_url = _bounded_transactions_url(base_url)
        page.navigate(filter_url)
        page.wait_for(
            "(() => { const params = new URLSearchParams(location.search); return "
            "location.pathname === '/transactions' && "
            "params.get('date_from') === '2024-01-01' && "
            "params.get('date_to') === '2024-12-31' && "
            "params.get('transaction_state') === 'unreconciled' && "
            "params.get('sort') === 'date_desc' && "
            "params.get('page_size') === '25' && "
            "!params.has('query') && !params.has('limit') && !params.has('offset'); })()"
        )
        page.wait_for("document.body && document.body.innerText.includes('Transactions')")
        if page.evaluate("document.body.innerText.includes('New transaction')"):
            raise DogfoodFailure("write UI unexpectedly visible on transactions page")
        assert_no_mobile_overflow("transactions_filters")
        export_href = page.evaluate(
            "Array.from(document.querySelectorAll('a[href*=\"/transactions/export\"]')).map(a => a.getAttribute('href')).find(Boolean) || null"
        )
        _assert_export_preserves_supported_filters(export_href)
        results.append(
            CheckResult(
                "transactions_filters",
                "bounded transactions page loaded; export link preserved date/state filters",
            )
        )

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
        _stop_chrome(proc)
        if not args.keep_temp:
            shutil.rmtree(temp_root, ignore_errors=True)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run headless browser dogfood against local Docker/Caddy deployment.")
    parser.add_argument("--base-url", default=os.environ.get("SMOKE_WEB_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--username", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--chromium", default=os.environ.get("CHROMIUM_BIN"))
    parser.add_argument(
        "--cdp-probe",
        action="store_true",
        help="Launch Chrome, verify the CDP transport, report version, and exit without loading the app",
    )
    parser.add_argument("--keep-temp", action="store_true", help="Keep temporary browser profile for debugging only")
    parser.add_argument("--fixture-path", default=None, help="Optional fixture path to hash/report without printing full path")
    parser.add_argument("--viewport-width", type=int, default=320, help="Viewport width for read-only UI dogfood")
    parser.add_argument("--viewport-height", type=int, default=720, help="Viewport height for read-only UI dogfood")
    parser.add_argument(
        "--unavailable-book-id",
        type=int,
        default=None,
        help="Optional accessible-but-unavailable synthetic book id for selected-book recovery dogfood",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.cdp_probe:
            print(f"PASS: Chrome CDP probe completed: {_probe_cdp(args)}")
            return 0
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
