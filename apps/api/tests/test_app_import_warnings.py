"""Regression tests for dependency deprecation warnings during app import."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[1]


def test_app_import_does_not_emit_deprecated_starlette_422_warning() -> None:
    env = os.environ.copy()
    env["PYTHONWARNINGS"] = "default::DeprecationWarning"
    env["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"

    result = subprocess.run(
        [sys.executable, "-c", "import app.main"],
        cwd=API_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "HTTP_422_UNPROCESSABLE_ENTITY" not in result.stderr
    assert "HTTP_422_UNPROCESSABLE_CONTENT" not in result.stderr
