import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.check_public_status as guard
import scripts.check_write_safety_defaults as write_defaults_guard


def test_public_status_guard_reuses_write_safety_defaults_guard() -> None:
    assert guard.DEFAULT_WRITE_SAFETY_GUARD_FILES == (
        Path(".env.example"),
        Path("docker-compose.yml"),
        Path("docs/write-alpha/owner-writebeta-operating-guide.md"),
    )
    assert guard.check_default_write_safety() == []
    assert write_defaults_guard.WRITE_DEFAULT_TEXT == "GNUCASH_WRITES_ENABLED=false"


def test_public_status_guard_reads_only_declared_public_files():
    checked = set(guard.PUBLIC_STATUS_FILES + guard.CONFIG_FILES + guard.COMPATIBILITY_STATUS_FILES)

    assert Path(".env") not in checked
    assert all(not str(path).startswith("data/") for path in checked)
    assert all("backups" not in path.parts for path in checked)
    assert all("books" not in path.parts for path in checked)
    assert all(path.name != "app.db" for path in checked)


def test_compatibility_status_guard_requires_narrow_desktop_fixture_closure_language() -> None:
    safe = """
    Issue #22 is closed for narrow Desktop-generated synthetic SQLite fixture evidence only.
    Compatibility evidence is based on synthetic/disposable fixtures only.
    PostgreSQL/MySQL/MariaDB GnuCash backends are unclaimed.
    No broad GnuCash Desktop version support is claimed.
    No production, stable, security, public-write, all-version, or real-book claim.
    """

    guard.check_compatibility_status_claims(Path("docs/gnucash-compatibility.md"), safe)


def test_compatibility_status_guard_rejects_desktop_or_backend_support_claims() -> None:
    unsafe = """
    Issue #22 is closed for narrow Desktop-generated synthetic SQLite fixture evidence only.
    Compatibility evidence is based on synthetic/disposable fixtures only.
    PostgreSQL/MySQL/MariaDB GnuCash backends are unclaimed.
    No broad GnuCash Desktop version support is claimed.
    GnuCash Desktop 5.10 is supported and PostgreSQL/MySQL/MariaDB supported.
    """

    try:
        guard.check_compatibility_status_claims(Path("docs/gnucash-compatibility.md"), unsafe)
    except AssertionError as exc:
        assert "forbidden compatibility claim" in str(exc)
    else:
        raise AssertionError("affirmative Desktop/backend compatibility claim should fail guard")


def test_compatibility_status_guard_rejects_broad_desktop_support_after_issue_22_closure() -> None:
    unsafe = """
    Issue #22 is closed for narrow Desktop-generated synthetic SQLite fixture evidence only.
    Compatibility evidence is based on synthetic/disposable fixtures only.
    PostgreSQL/MySQL/MariaDB GnuCash backends are unclaimed.
    No broad GnuCash Desktop version support is claimed.
    Closing #22 means Desktop-version support for GnuCash Desktop 5.14 is supported.
    """

    try:
        guard.check_compatibility_status_claims(Path("docs/gnucash-compatibility.md"), unsafe)
    except AssertionError as exc:
        assert "forbidden compatibility claim" in str(exc)
    else:
        raise AssertionError("broad Desktop support claim should fail after narrow #22 closure")


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
    assert guard.CURRENT_COMPLETED_PHASE == "Phase 830"


def test_public_status_guard_rejects_phase_300_as_current_baseline():
    stale = "- Completed through Phase 300."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 300" in str(exc)
    else:
        raise AssertionError("stale Phase 300 current baseline should fail guard")


def test_public_status_guard_rejects_phase_319_as_current_baseline():
    stale = "- Completed through Phase 319."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 319" in str(exc)
    else:
        raise AssertionError("stale Phase 319 current baseline should fail guard")


def test_public_status_guard_rejects_phase_264_as_current_baseline():
    stale = "- Completed through Phase 264."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 264" in str(exc)
    else:
        raise AssertionError("stale Phase 264 current baseline should fail guard")


def test_public_status_guard_rejects_phase_258_as_current_baseline():
    stale = "- Completed through Phase 258."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 258" in str(exc)
    else:
        raise AssertionError("stale Phase 258 current baseline should fail guard")


def test_public_status_guard_rejects_phase_257_as_current_baseline():
    stale = "- Completed through Phase 257."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 257" in str(exc)
    else:
        raise AssertionError("stale Phase 257 current baseline should fail guard")


def test_public_status_guard_rejects_phase_256_as_current_baseline():
    stale = "- Completed through Phase 256."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 256" in str(exc)
    else:
        raise AssertionError("stale Phase 256 current baseline should fail guard")


def test_public_status_guard_rejects_phase_254_as_current_baseline():
    stale = "- Completed through Phase 254."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 254" in str(exc)
    else:
        raise AssertionError("stale Phase 254 current baseline should fail guard")


def test_public_status_guard_rejects_phase_253_as_current_baseline():
    stale = "- Completed through Phase 253."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 253" in str(exc)
    else:
        raise AssertionError("stale Phase 253 current baseline should fail guard")


def test_public_status_guard_rejects_phase_251_as_current_baseline():
    stale = "- Completed through Phase 251."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 251" in str(exc)
    else:
        raise AssertionError("stale Phase 251 current baseline should fail guard")


def test_public_status_guard_rejects_phase_249_as_current_baseline():
    stale = "- Completed through Phase 249."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 249" in str(exc)
    else:
        raise AssertionError("stale Phase 249 current baseline should fail guard")


def test_public_status_guard_rejects_phase_248_as_current_baseline():
    stale = "- Completed through Phase 248."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 248" in str(exc)
    else:
        raise AssertionError("stale Phase 248 current baseline should fail guard")


def test_public_status_guard_rejects_phase_240_as_current_baseline():
    stale = "- Completed through Phase 240."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 240" in str(exc)
    else:
        raise AssertionError("stale Phase 240 current baseline should fail guard")


def test_public_status_guard_rejects_phase_239_as_current_baseline():
    stale = "- Completed through Phase 239."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 239" in str(exc)
    else:
        raise AssertionError("stale Phase 239 current baseline should fail guard")


def test_public_status_guard_rejects_phase_238_as_current_baseline():
    stale = "- Completed through Phase 238."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 238" in str(exc)
    else:
        raise AssertionError("stale Phase 238 current baseline should fail guard")


def test_public_status_guard_rejects_phase_237_as_current_baseline():
    stale = "- Completed through Phase 237."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 237" in str(exc)
    else:
        raise AssertionError("stale Phase 237 current baseline should fail guard")


def test_public_status_guard_rejects_phase_236_as_current_baseline():
    stale = "- Completed through Phase 236."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 236" in str(exc)
    else:
        raise AssertionError("stale Phase 236 current baseline should fail guard")


def test_public_status_guard_rejects_phase_235_as_current_baseline():
    stale = "- Completed through Phase 235."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 235" in str(exc)
    else:
        raise AssertionError("stale Phase 235 current baseline should fail guard")


def test_public_status_guard_rejects_phase_234_as_current_baseline():
    stale = "- Completed through Phase 234."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 234" in str(exc)
    else:
        raise AssertionError("stale Phase 234 current baseline should fail guard")


def test_public_status_guard_rejects_phase_233_as_current_baseline():
    stale = "- Completed through Phase 233."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 233" in str(exc)
    else:
        raise AssertionError("stale Phase 233 current baseline should fail guard")


def test_public_status_guard_rejects_phase_232_as_current_baseline():
    stale = "- Completed through Phase 232."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 232" in str(exc)
    else:
        raise AssertionError("stale Phase 232 current baseline should fail guard")


def test_public_status_guard_rejects_phase_231_as_current_baseline():
    stale = "- Completed through Phase 231."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 231" in str(exc)
    else:
        raise AssertionError("stale Phase 231 current baseline should fail guard")


def test_public_status_guard_rejects_phase_229_as_current_baseline():
    stale = "- Completed through Phase 229."

    try:
        guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.STALE_CURRENT_PATTERNS)
    except AssertionError as exc:
        assert "Phase 229" in str(exc)
    else:
        raise AssertionError("stale Phase 229 current baseline should fail guard")


def test_public_status_guard_rejects_affirmative_production_claims():
    unsafe = "This is production-ready software."

    try:
        guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
    except AssertionError as exc:
        assert "production" in str(exc).lower()
    else:
        raise AssertionError("affirmative production claim should fail guard")


def test_public_status_guard_rejects_affirmative_public_write_beta_claims():
    unsafe = "The public write beta is ready for users."

    try:
        guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
    except AssertionError as exc:
        assert "public" in str(exc).lower()
        assert "write" in str(exc).lower()
    else:
        raise AssertionError("affirmative public write beta claim should fail guard")


def test_public_status_guard_rejects_affirmative_writebeta_status_claims():
    unsafe = "Owner-writebeta is public."

    try:
        guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
    except AssertionError as exc:
        assert "writebeta" in str(exc).lower()
    else:
        raise AssertionError("affirmative writebeta status claim should fail guard")


def test_public_status_guard_accepts_negative_production_security_limitations():
    safe = "- Not production-ready and not security-audited."

    guard.reject_patterns(Path("CHANGELOG.md"), safe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)


def test_public_status_guard_accepts_wrapped_negative_safety_limitations():
    safe = "- No hosted SaaS readiness, collaborative accounting, or\n  safe production write mode is claimed."

    guard.reject_patterns(Path("CHANGELOG.md"), safe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
