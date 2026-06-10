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
    GnuCash Desktop 5.12 write-compatible.
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


def test_public_status_guard_rejects_recent_stale_phase_baselines():
    stale_claims = [
        "- Completed through Phase 829.",
        "- Phase 0–829 are complete.",
        "- Фазы 0–829 завершены.",
    ]

    for stale in stale_claims:
        try:
            guard.reject_patterns(Path("docs/ROADMAP.md"), stale, guard.RECENT_STALE_CURRENT_PATTERNS)
        except AssertionError as exc:
            assert "829" in str(exc)
        else:
            raise AssertionError(f"recent stale phase baseline should fail guard: {stale}")


def test_public_status_guard_accepts_current_phase_baselines():
    current_claims = [
        "- Completed through Phase 830.",
        "- Phase 0–830 are complete.",
        "- Фазы 0–830 завершены.",
    ]

    for current in current_claims:
        guard.reject_patterns(Path("docs/ROADMAP.md"), current, guard.RECENT_STALE_CURRENT_PATTERNS)


def test_public_status_guard_accepts_historical_prior_phase_baseline_context():
    historical = "Completed through Phase 630 was the prior public-status guard baseline before this run."

    guard.reject_patterns(Path("PROJECT_STATUS.md"), historical, guard.RECENT_STALE_CURRENT_PATTERNS)


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
    unsafe_claims = [
        "This is production-ready software.",
        "Production ready release published.",
    ]

    for unsafe in unsafe_claims:
        try:
            guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
        except AssertionError as exc:
            assert "production" in str(exc).lower()
        else:
            raise AssertionError(f"affirmative production claim should fail guard: {unsafe}")


def test_public_status_guard_rejects_affirmative_public_write_beta_action_claims():
    unsafe_claims = [
        "Ready to release public write beta.",
        "We can publish the write-beta rollout.",
        "Ship the owner-writebeta release to users.",
        "Ship the owner write beta release to users.",
        "Launch public writes for real books.",
    ]

    for unsafe in unsafe_claims:
        try:
            guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
        except AssertionError as exc:
            assert "write" in str(exc).lower()
        else:
            raise AssertionError(f"affirmative public write-beta action claim should fail guard: {unsafe}")


def test_public_status_guard_accepts_negative_public_write_beta_action_claims():
    safe_claims = [
        "Do not release public write beta.",
        "No public writes are enabled.",
        "This prevents consent to\nship owner-writebeta.",
        "- forbidden implication: clean checks publish owner-writebeta.",
    ]

    for safe in safe_claims:
        guard.reject_patterns(Path("README.md"), safe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)


def test_public_status_guard_rejects_affirmative_public_write_beta_claims():
    unsafe_claims = [
        "The public write beta is ready for users.",
        "Public write beta is release-ready.",
        "Public write beta is safe for users.",
        "Write beta is ship ready.",
        "Write-beta is suitable for public use.",
    ]

    for unsafe in unsafe_claims:
        try:
            guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
        except AssertionError as exc:
            assert "write" in str(exc).lower()
        else:
            raise AssertionError(f"affirmative public write beta claim should fail guard: {unsafe}")


def test_public_status_guard_rejects_affirmative_public_write_beta_publication_claims():
    unsafe = "Public write beta is published."

    try:
        guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
    except AssertionError as exc:
        assert "public" in str(exc).lower()
        assert "write" in str(exc).lower()
    else:
        raise AssertionError("affirmative public write beta publication claim should fail guard")


def test_public_status_guard_rejects_affirmative_public_write_beta_launch_claims():
    unsafe = "Public write beta launch is authorized."

    try:
        guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
    except AssertionError as exc:
        assert "public" in str(exc).lower()
        assert "write" in str(exc).lower()
    else:
        raise AssertionError("affirmative public write beta launch claim should fail guard")


def test_public_status_guard_rejects_affirmative_writebeta_status_claims():
    unsafe_claims = [
        "Owner-writebeta is public.",
        "Owner write beta is public.",
        "Writebeta is ready.",
        "Owner writebeta is available.",
        "Owner write beta is available.",
        "Writebeta has launched.",
        "Owner-write beta has launched.",
        "Owner-writebeta rollout is released.",
        "Owner write beta rollout is released.",
    ]

    for unsafe in unsafe_claims:
        try:
            guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
        except AssertionError as exc:
            assert "write" in str(exc).lower()
        else:
            raise AssertionError(f"affirmative writebeta status claim should fail guard: {unsafe}")


def test_public_status_guard_rejects_affirmative_writebeta_authorization_claims():
    unsafe_claims = [
        "Owner-writebeta is authorized.",
        "Owner-writebeta authorized.",
        "Owner write beta is authorized.",
        "Owner write beta authorized.",
        "Write beta released.",
        "Write beta has been approved.",
        "Writebeta published.",
        "Writebeta has been released.",
        "Owner-writebeta has been published.",
        "Owner write beta has been authorized.",
        "Public write beta has been authorized.",
    ]

    for unsafe in unsafe_claims:
        try:
            guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
        except AssertionError as exc:
            assert "write" in str(exc).lower()
        else:
            raise AssertionError(f"affirmative writebeta authorization claim should fail guard: {unsafe}")


def test_public_status_guard_rejects_affirmative_public_write_beta_private_book_scope():
    unsafe = "Public write beta for private books is acceptable."

    try:
        guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
    except AssertionError as exc:
        assert "public" in str(exc).lower()
        assert "private" in str(exc).lower()
    else:
        raise AssertionError("public write beta private-book scope claim should fail guard")


def test_public_status_guard_rejects_write_beta_stable_security_claims():
    unsafe_claims = [
        "Write beta is stable.",
        "Write-beta is stable.",
        "Write beta is security-audited.",
        "Write-beta is security-audited.",
        "Write beta release is production-ready.",
        "Write-beta release is production-ready.",
    ]

    for unsafe in unsafe_claims:
        try:
            guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
        except AssertionError as exc:
            assert "write" in str(exc).lower()
        else:
            raise AssertionError(f"unsafe write beta claim should fail guard: {unsafe}")


def test_public_status_guard_rejects_write_beta_ga_and_production_safe_claims():
    unsafe_claims = [
        "Write beta is general availability.",
        "Write beta is generally available.",
        "Write beta general availability release is available.",
        "Write beta GA is released.",
        "Owner-writebeta is production-safe.",
        "Owner write beta is generally available.",
        "Owner write beta is field-tested.",
    ]

    for unsafe in unsafe_claims:
        try:
            guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
        except AssertionError as exc:
            assert "write" in str(exc).lower()
        else:
            raise AssertionError(f"unsafe write beta GA/production-safe claim should fail guard: {unsafe}")


def test_public_status_guard_rejects_affirmative_real_book_approval_claims():
    unsafe_claims = [
        "Real-book approved.",
        "Real book trial is authorized.",
        "Real-book mutation approved.",
        "Release approved.",
        "Public write beta approved.",
        "Only-copy safe.",
    ]

    for unsafe in unsafe_claims:
        try:
            guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
        except AssertionError as exc:
            assert any(
                marker in str(exc).lower()
                for marker in ("real", "release", "public", "only-copy")
            )
        else:
            raise AssertionError(f"unsafe approval/safety claim should fail guard: {unsafe}")


def test_public_status_guard_accepts_negative_real_book_approval_limitations():
    safe = (
        "#44 is not mutation approval, not release approval, and not public write beta approval.\n"
        "Only-copy books are not safe. Real-book trial is not approved."
    )

    guard.reject_patterns(Path("README.md"), safe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)


def test_public_status_guard_accepts_negative_production_security_limitations():
    safe = "- Not production-ready and not security-audited.\nIs owner-writebeta published? No. It remains unpublished."

    guard.reject_patterns(Path("CHANGELOG.md"), safe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)


def test_public_status_guard_accepts_wrapped_negative_safety_limitations():
    safe = "- No hosted SaaS readiness, collaborative accounting, or\n  safe production write mode is claimed."

    guard.reject_patterns(Path("CHANGELOG.md"), safe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)


def test_public_status_guard_accepts_denial_of_stable_release_claims():
    safe = "Release notes deny production readiness and stable release status."

    guard.reject_patterns(Path("CHANGELOG.md"), safe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)


def test_public_status_guard_accepts_hard_wrapped_negative_list():
    safe = "not production-ready and not safe for only-copy books. No\nstable release is claimed."

    guard.reject_patterns(Path("PROJECT_STATUS.md"), safe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)


def test_public_status_guard_rejects_unrelated_claim_after_negative_context():
    unsafe = "- No public write beta is authorized.\nThe public write beta is ready for users."

    try:
        guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
    except AssertionError as exc:
        assert "public" in str(exc).lower()
        assert "write" in str(exc).lower()
    else:
        raise AssertionError("new affirmative claim after negative line should fail guard")


def test_public_status_guard_rejects_unbulleted_claim_after_negative_colon():
    unsafe = "Even future closure must not mean:\nThe public write beta is ready for users."

    try:
        guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
    except AssertionError as exc:
        assert "public" in str(exc).lower()
        assert "write" in str(exc).lower()
    else:
        raise AssertionError("unbulleted affirmative claim after negative heading should fail guard")


def test_public_status_guard_rejects_affirmative_broad_compatibility_claims():
    unsafe = "Broad GnuCash compatibility is supported."

    try:
        guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
    except AssertionError as exc:
        assert "compatibility" in str(exc).lower()
    else:
        raise AssertionError("affirmative broad compatibility claim should fail guard")


def test_public_status_guard_rejects_affirmative_broad_compatibility_completeness_claims():
    unsafe_claims = [
        "Broad GnuCash compatibility is complete.",
        "Broad GnuCash Desktop compatibility is comprehensive.",
    ]

    for unsafe in unsafe_claims:
        try:
            guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
        except AssertionError as exc:
            assert "compatibility" in str(exc).lower()
        else:
            raise AssertionError(f"affirmative broad compatibility completeness claim should fail guard: {unsafe}")


def test_public_status_guard_rejects_hyphenated_public_write_beta_claims():
    unsafe_claims = [
        "Public write-beta is ready.",
        "Public write-beta launch is authorized.",
        "Write-beta available for public use.",
    ]

    for unsafe in unsafe_claims:
        try:
            guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
        except AssertionError as exc:
            assert "write" in str(exc).lower()
        else:
            raise AssertionError(f"hyphenated unsafe write-beta claim should fail guard: {unsafe}")


def test_public_status_guard_rejects_write_beta_launch_without_public_prefix():
    unsafe_claims = [
        "Write beta launch is authorized.",
        "Write-beta rollout is released.",
        "Write beta rollout is complete.",
        "Public write beta rollout is complete.",
        "Owner write beta rollout is complete.",
    ]

    for unsafe in unsafe_claims:
        try:
            guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
        except AssertionError as exc:
            assert "write" in str(exc).lower()
        else:
            raise AssertionError(f"unsafe write beta launch claim should fail guard: {unsafe}")


def test_public_status_guard_rejects_affirmative_broad_compatibility_confirmed_claims():
    unsafe_claims = [
        "Broad GnuCash Desktop compatibility is confirmed.",
        "Broad GnuCash compatibility has been proven.",
        "Broad GnuCash Desktop compatibility been validated.",
    ]

    for unsafe in unsafe_claims:
        try:
            guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
        except AssertionError as exc:
            assert "compatibility" in str(exc).lower()
        else:
            raise AssertionError(
                f"affirmative broad compatibility confirmed claim should fail guard: {unsafe}"
            )


def test_public_status_guard_rejects_compatibility_guarantee_wording():
    unsafe_claims = [
        "Fully compatible with GnuCash Desktop releases.",
        "Guaranteed compatible with GnuCash SQL books.",
        "Production-ready compatibility for write beta.",
        "All SQL backends are supported.",
        "GnuCash Desktop 5.12.1 write-compatible.",
    ]

    for unsafe in unsafe_claims:
        try:
            guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
        except AssertionError as exc:
            assert "compat" in str(exc).lower() or "backend" in str(exc).lower()
        else:
            raise AssertionError(f"unsafe compatibility guarantee should fail guard: {unsafe}")


def test_public_status_guard_rejects_stable_security_audited_status_claims():
    unsafe_claims = [
        "Release is stable.",
        "Deployment is security-audited.",
        "Software is production ready.",
        "Build is production-ready.",
    ]

    for unsafe in unsafe_claims:
        try:
            guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
        except AssertionError as exc:
            assert (
                "stable" in str(exc).lower()
                or "production" in str(exc).lower()
                or "security" in str(exc).lower()
            )
        else:
            raise AssertionError(f"unsafe stable/security status claim should fail guard: {unsafe}")


def test_public_status_guard_rejects_affirmative_only_copy_write_safety_claims():
    unsafe = "Only-copy books are safe for writes."

    try:
        guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
    except AssertionError as exc:
        assert "only-copy" in str(exc).lower()
    else:
        raise AssertionError("affirmative only-copy write-safety claim should fail guard")


def test_public_status_guard_rejects_affirmative_real_private_write_safety_claims():
    unsafe_claims = [
        "Real books are safe for writes.",
        "Private book writes are safe.",
        "Original books are safe for mutation.",
    ]

    for unsafe in unsafe_claims:
        try:
            guard.reject_patterns(Path("README.md"), unsafe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
        except AssertionError as exc:
            assert "safe" in str(exc).lower()
        else:
            raise AssertionError(f"unsafe real/private write-safety claim should fail guard: {unsafe}")


def test_public_status_guard_accepts_negative_broad_compatibility_limitations():
    safe = "- Not broad GnuCash compatibility and not real/private book write-safety."

    guard.reject_patterns(Path("CHANGELOG.md"), safe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)


def test_public_status_guard_accepts_must_not_mean_safety_limitations():
    safe = "Even future closure must not mean:\n- real working-book writes are safe;"

    guard.reject_patterns(Path("CHANGELOG.md"), safe, guard.UNSAFE_AFFIRMATIVE_PATTERNS)
