#!/usr/bin/env python3
"""Run the Phase 87 large-book read-only benchmark v1."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.performance.large_book_benchmark import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
