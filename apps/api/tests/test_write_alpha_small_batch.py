import importlib.util
import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "write_alpha_small_batch.py"
FIXTURE = REPO_ROOT / "apps" / "api" / "tests" / "fixtures" / "test-book.gnucash.sqlite"

spec = importlib.util.spec_from_file_location("write_alpha_small_batch", SCRIPT_PATH)
assert spec and spec.loader
small_batch = importlib.util.module_from_spec(spec)
sys.modules["write_alpha_small_batch"] = small_batch
spec.loader.exec_module(small_batch)


def test_small_batch_runs_exact_w3_operation_counts_on_copied_book(tmp_path):
    book = tmp_path / "copied-book.gnucash.sqlite"
    shutil.copy2(FIXTURE, book)

    evidence = small_batch.run(
        book,
        tmp_path / "work",
        tmp_path / "evidence",
    )

    assert evidence["result"] == "pass"
    assert evidence["operation_counts"] == {
        "create_attempts": 2,
        "create_successes": 2,
        "patch_attempts": 1,
        "patch_successes": 1,
        "delete_attempts": 1,
        "delete_successes": 1,
    }
    assert evidence["delete"]["deleted_created_transaction_absent"] is True
    assert evidence["default_disabled_probe"] == {
        "create_after_reset_status": 403,
        "patch_after_reset_status": 403,
        "delete_after_reset_status": 403,
        "writes_disabled_forbidden": True,
    }
