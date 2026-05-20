import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.check_public_status as guard


def test_public_status_guard_reads_only_declared_public_files():
    checked = set(guard.PUBLIC_STATUS_FILES + guard.CONFIG_FILES)

    assert Path(".env") not in checked
    assert all(not str(path).startswith("data/") for path in checked)
    assert all("backups" not in path.parts for path in checked)
    assert all("books" not in path.parts for path in checked)
    assert all(path.name != "app.db" for path in checked)


def test_public_status_guard_rejects_stale_current_write_alpha_claim():
    stale = "- Current published write-alpha pre-release: `v0.2.0-writealpha`"

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "v0.2.0-writealpha" in str(exc)
    else:
        raise AssertionError("stale current write-alpha release should fail guard")


def test_public_status_guard_rejects_phase_172_as_current_baseline():
    stale = "- Completed through Phase 172."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 172" in str(exc)
    else:
        raise AssertionError("stale Phase 172 current baseline should fail guard")


def test_public_status_guard_tracks_current_completed_phase():
    assert guard.CURRENT_COMPLETED_PHASE == "Phase 227"


def test_public_status_guard_rejects_affirmative_production_claims():
    unsafe = "This is production-ready software."

    try:
        guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
    except AssertionError as exc:
        assert "production" in str(exc).lower()
    else:
        raise AssertionError("affirmative production claim should fail guard")


def test_public_status_guard_accepts_negative_production_security_limitations():
    safe = "- Not production-ready and not security-audited."

    guard.reject_patterns(Path("CHANGELOG.md"), safe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
