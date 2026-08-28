#!/usr/bin/env python3
"""Focused regression tests for C1 build and CDP smoke hardening."""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import struct
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
HARNESS_PATH = Path(__file__).with_name("read-only-browser-dogfood.py")
SPEC = importlib.util.spec_from_file_location("read_only_browser_dogfood", HARNESS_PATH)
assert SPEC is not None and SPEC.loader is not None
HARNESS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = HARNESS
SPEC.loader.exec_module(HARNESS)


class FakeSocket:
    def __init__(self, payload: bytes) -> None:
        self.payload = bytearray(payload)
        self.sent = bytearray()

    def recv(self, length: int) -> bytes:
        chunk = bytes(self.payload[:length])
        del self.payload[:length]
        return chunk

    def sendall(self, payload: bytes) -> None:
        self.sent.extend(payload)


def server_frame(opcode: int, payload: bytes, *, final: bool = True) -> bytes:
    first = opcode | (0x80 if final else 0)
    length = len(payload)
    if length < 126:
        return bytes((first, length)) + payload
    if length < 65536:
        return bytes((first, 126)) + struct.pack("!H", length) + payload
    return bytes((first, 127)) + struct.pack("!Q", length) + payload


class WebSocketProtocolTests(unittest.TestCase):
    def test_fragmented_cdp_json_with_interleaved_ping_is_reassembled(self) -> None:
        payload = json.dumps({"id": 7, "result": {"product": "Chrome/151"}}).encode("utf-8")
        split = len(payload) // 2
        frames = b"".join(
            (
                server_frame(0x1, payload[:split], final=False),
                server_frame(0x9, b"health"),
                server_frame(0x0, payload[split:]),
            )
        )
        websocket = HARNESS.WebSocket.__new__(HARNESS.WebSocket)
        websocket.sock = FakeSocket(frames)

        self.assertEqual(websocket.recv_json(), json.loads(payload))
        self.assertTrue(websocket.sock.sent, "client must answer an interleaved ping with pong")

    def test_handshake_rejects_wrong_websocket_accept_value(self) -> None:
        response = (
            b"HTTP/1.1 101 Switching Protocols\r\n"
            b"Upgrade: websocket\r\n"
            b"Connection: Upgrade\r\n"
            b"Sec-WebSocket-Accept: wrong\r\n\r\n"
        )
        websocket = HARNESS.WebSocket.__new__(HARNESS.WebSocket)
        websocket.host = "127.0.0.1"
        websocket.port = 9222
        websocket.path = "/devtools/page/test"
        websocket.sock = FakeSocket(response)
        fixed_nonce = b"0123456789abcdef"
        expected_key = base64.b64encode(fixed_nonce).decode("ascii")
        expected_accept = base64.b64encode(
            hashlib.sha1((expected_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")).digest()
        ).decode("ascii")
        self.assertNotEqual(expected_accept, "wrong")

        with mock.patch.object(HARNESS.os, "urandom", return_value=fixed_nonce):
            with self.assertRaisesRegex(HARNESS.DogfoodFailure, "Sec-WebSocket-Accept"):
                websocket._handshake()


class Chrome151ProbeContractTests(unittest.TestCase):
    def test_parser_exposes_standalone_cdp_probe(self) -> None:
        args = HARNESS.parse_args(["--cdp-probe"])
        self.assertTrue(args.cdp_probe)

    def test_harness_uses_bounded_loopback_debug_endpoint(self) -> None:
        source = HARNESS_PATH.read_text(encoding="utf-8")
        self.assertIn("--remote-debugging-address=127.0.0.1", source)
        self.assertIn("_wait_for_devtools", source)
        self.assertNotIn('"--remote-debugging-port=0"', source)


class ProductionBuildContractTests(unittest.TestCase):
    def test_web_build_syncs_sveltekit_before_vite(self) -> None:
        package = json.loads((ROOT / "apps/web/package.json").read_text(encoding="utf-8"))
        self.assertEqual(package["scripts"].get("sync"), "svelte-kit sync")
        dockerfile = (ROOT / "apps/web/Dockerfile").read_text(encoding="utf-8")
        self.assertIn("RUN npm run sync\nRUN npm run build", dockerfile)

    def test_per_app_dockerignore_blocks_local_and_private_artifacts(self) -> None:
        required = {
            "apps/web/.dockerignore": {
                "node_modules/",
                ".svelte-kit/",
                "build/",
                ".env*",
                "*.sqlite*",
                "*.gnucash*",
            },
            "apps/api/.dockerignore": {
                ".venv/",
                "__pycache__/",
                ".pytest_cache/",
                ".env*",
                "*.sqlite*",
                "*.gnucash*",
            },
        }
        for relative_path, expected_patterns in required.items():
            path = ROOT / relative_path
            self.assertTrue(path.is_file(), f"missing {relative_path}")
            patterns = {
                line.strip()
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.lstrip().startswith("#")
            }
            self.assertTrue(
                expected_patterns <= patterns,
                f"{relative_path} missing {sorted(expected_patterns - patterns)}",
            )

    def test_lockfile_is_present_for_reproducible_install(self) -> None:
        self.assertTrue((ROOT / "apps/web/package-lock.json").is_file())
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertNotIn("package-lock.json", {line.strip() for line in gitignore})


if __name__ == "__main__":
    unittest.main(verbosity=2)
