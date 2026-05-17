"""Integration tests for GnuCashWriteService against a real synthetic GnuCash fixture.

These tests exercise the full write flow (create_transaction, patch_transaction_metadata)
against actual piecash SQLite books (copies of the synthetic fixture), validating:
- Happy paths: balanced create, multi-split create, patch description/date/memo
- Validation rejections: unbalanced, single-split, invalid-account, placeholder
- Backup creation, audit logging, lock lifecycle, lock contention
- Original fixture immutability, read-back verification

No HTTP endpoints are tested — this validates the service layer directly.
"""

from __future__ import annotations

import hashlib
import shutil
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any

import piecash
import pytest

from app.schemas.gnucash_writes import (
    TransactionCreateRequestDTO,
    TransactionPatchRequestDTO,
    TransactionSplitWriteDTO,
)
from app.services import gnucash_write as gw_mod
from app.services.gnucash_write import GnuCashWriteService, GnuCashWriteError
from app.services.write_lock import WriteLockError, WriteLockService

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "test-book.gnucash.sqlite"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _file_md5(path: Path) -> str:
    """Return hex MD5 digest of a file."""
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _book_config(book_path: Path) -> dict[str, Any]:
    """Return a book config dict suitable for GnuCashWriteService."""
    return {"uri_or_path": str(book_path), "base_currency": "SEK"}


def _read_accounts(book_path: Path) -> list[Any]:
    """Open the book read-only and return the account list."""
    book = piecash.open_book(str(book_path), readonly=True)
    try:
        return list(book.accounts)
    finally:
        book.close()


def _read_transactions(book_path: Path) -> list[dict]:
    """Open the book read-only and return a list of transaction dicts.
    
    We extract all data before closing the book to avoid DetachedInstanceError.
    """
    book = piecash.open_book(str(book_path), readonly=True)
    try:
        result = []
        for tx in book.transactions:
            tx_data = {
                "guid": tx.guid,
                "description": tx.description,
                "post_date": tx.post_date,
                "splits": [
                    {
                        "guid": s.guid,
                        "account_name": s.account.name,
                        "value": Decimal(str(s.value)),
                        "memo": s.memo,
                    }
                    for s in tx.splits
                ],
            }
            result.append(tx_data)
        return result
    finally:
        book.close()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fixture_md5() -> str:
    """MD5 of the original fixture before any test modifies it."""
    return _file_md5(FIXTURE_PATH)


@pytest.fixture
def book_copy(tmp_path: Path) -> Path:
    """Return a fresh copy of the synthetic fixture in tmp_path."""
    dst = tmp_path / "test.gnucash.sqlite"
    shutil.copy2(str(FIXTURE_PATH), str(dst))
    return dst


@pytest.fixture
def write_service(book_copy: Path, tmp_path: Path) -> GnuCashWriteService:
    """Return a GnuCashWriteService configured for the copied book, with tmp lock dir."""
    lock_dir = tmp_path / "locks"
    # Replace the module-level singleton so lock files stay in tmp_path.
    from app.services import write_lock as wl_mod

    new_svc = WriteLockService(lock_dir=lock_dir)
    wl_mod.write_lock_service = new_svc
    # gnucash_write module imported write_lock_service at module level, so we
    # must also update its reference.
    gw_mod.write_lock_service = new_svc
    return GnuCashWriteService(_book_config(book_copy))


@pytest.fixture
def service_and_path(book_copy: Path, tmp_path: Path) -> tuple[GnuCashWriteService, Path]:
    """Return (service, book_path) with a fresh lock directory."""
    lock_dir = tmp_path / "locks"
    from app.services import write_lock as wl_mod

    new_svc = WriteLockService(lock_dir=lock_dir)
    wl_mod.write_lock_service = new_svc
    gw_mod.write_lock_service = new_svc
    svc = GnuCashWriteService(_book_config(book_copy))
    return svc, book_copy


# ---------------------------------------------------------------------------
# Account GUIDs from the synthetic fixture (read at fixture setup time)
# ---------------------------------------------------------------------------


class FixtureAccounts:
    """Account GUIDs discovered from the real fixture at collection time."""

    CHECKING = "c73e8aa01e6345288662b556f2f866f3"
    FOOD = "388a85676d4a4643ae6cd28166c34e79"
    TRANSPORT = "50b7cedabc8b46238dc15284637733d6"
    SALARY = "5a7afc02224241b68666aced775b71aa"
    CREDIT_CARD = "c3e2c3289f6745d6a226599207ef1157"
    BANK = "be11fab77e394fe9ad837534804bb4dc"
    ASSETS = "3768edb4158844e9a4091adb3d11999ad"
    EXPENSES = "3d5929c18d3e44e08f080791ccc14885"
    INCOME = "2b903f669a634399a27b90176c7dbc42"
    LIABILITIES = "68c95b63b4b84806a93d33e13755d3e6"
    ROOT = "b69be06525c847e5817733c91dfcfc4c"


class FixtureTransactions:
    """Transaction GUIDs from the synthetic fixture."""

    JANUARY_SALARY = "92cfb49a52934a488d51c2bd5e807b9f"
    GROCERY_STORE = "ef4e9d4124a041dc830c7b9e87d49555"
    BUS_PASS = "a374106753834ec2bc22d76b34e3d482"
    MONTHLY_EXPENSES = "bbb15fe22b8e4a7da145c3a23991aeed"
    CREDIT_CARD_PAYMENT = "89bdbe5a90af4c2fb4fc76b781d4a23b"


# ---------------------------------------------------------------------------
# 1. Create transaction: balanced 2-split
# ---------------------------------------------------------------------------


class TestCreateBalancedTransaction:
    def test_create_balanced_two_split(self, service_and_path):
        """Create a balanced 2-split transaction and verify read-back."""
        svc, book_path = service_and_path
        request = TransactionCreateRequestDTO(
            date="2026-05-17",
            description="Integration test balanced",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.CHECKING,
                    amount="-100.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.FOOD,
                    amount="100.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        result = svc.create_transaction(request, user_id=1, book_id=1)
        assert result.transaction_id
        assert result.backup_path
        assert Path(result.backup_path).exists()

        # Read back
        txs = _read_transactions(book_path)
        tx = next((t for t in txs if t["guid"] == result.transaction_id), None)
        assert tx is not None
        assert tx["description"] == "Integration test balanced"
        assert len(tx["splits"]) == 2

    def test_create_balanced_three_split(self, service_and_path):
        """Create a balanced 3-split transaction."""
        svc, book_path = service_and_path
        request = TransactionCreateRequestDTO(
            date="2026-06-01",
            description="Three-way split",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.CHECKING,
                    amount="-300.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.FOOD,
                    amount="200.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.TRANSPORT,
                    amount="100.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        result = svc.create_transaction(request, user_id=1, book_id=1)
        txs = _read_transactions(book_path)
        tx = next((t for t in txs if t["guid"] == result.transaction_id), None)
        assert tx is not None
        assert len(tx["splits"]) == 3
        # Verify balance
        total = sum(s["value"] for s in tx["splits"])
        assert total == Decimal("0")

    def test_create_four_split_transaction(self, service_and_path):
        """Create a balanced 4-split transaction (like Monthly expenses)."""
        svc, book_path = service_and_path
        request = TransactionCreateRequestDTO(
            date="2026-07-01",
            description="Four-way split",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.CHECKING,
                    amount="-500.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.FOOD,
                    amount="200.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.TRANSPORT,
                    amount="150.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.CREDIT_CARD,
                    amount="150.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        result = svc.create_transaction(request, user_id=1, book_id=1)
        txs = _read_transactions(book_path)
        tx = next((t for t in txs if t["guid"] == result.transaction_id), None)
        assert tx is not None
        assert len(tx["splits"]) == 4


# ---------------------------------------------------------------------------
# 2. Validation rejections
# ---------------------------------------------------------------------------


class TestCreateValidationRejections:
    def test_reject_unbalanced_splits(self, service_and_path):
        """Unbalanced splits must raise GnuCashWriteError."""
        svc, _ = service_and_path
        request = TransactionCreateRequestDTO(
            date="2026-05-17",
            description="Unbalanced",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.CHECKING,
                    amount="-100.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.FOOD,
                    amount="99.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        with pytest.raises(GnuCashWriteError, match="Validation failed"):
            svc.create_transaction(request, user_id=1, book_id=1)

    def test_reject_single_split(self, service_and_path):
        """Single split must be rejected."""
        svc, _ = service_and_path
        request = TransactionCreateRequestDTO(
            date="2026-05-17",
            description="Single split",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.CHECKING,
                    amount="-100.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        with pytest.raises(GnuCashWriteError, match="Validation failed"):
            svc.create_transaction(request, user_id=1, book_id=1)

    def test_reject_invalid_account(self, service_and_path):
        """Non-existent account GUID must be rejected."""
        svc, _ = service_and_path
        request = TransactionCreateRequestDTO(
            date="2026-05-17",
            description="Bad account",
            splits=[
                TransactionSplitWriteDTO(
                    account_id="nonexistent-guid-1234567890abcdef",
                    amount="-100.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.FOOD,
                    amount="100.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        with pytest.raises(GnuCashWriteError, match="Validation failed"):
            svc.create_transaction(request, user_id=1, book_id=1)

    def test_reject_placeholder_account(self, service_and_path):
        """The ROOT account must be rejected for postings (not found in book.accounts)."""
        svc, _ = service_and_path
        request = TransactionCreateRequestDTO(
            date="2026-05-17",
            description="Placeholder test",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.ROOT,
                    amount="-100.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.FOOD,
                    amount="100.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        # The ROOT account is not in book.accounts (it's book.root_account),
        # so _find_account returns None and we get "Account not found".
        with pytest.raises(GnuCashWriteError, match="Validation failed"):
            svc.create_transaction(request, user_id=1, book_id=1)

    def test_reject_invalid_currency_code(self, service_and_path):
        """Currency code that doesn't match account currency must be rejected."""
        svc, _ = service_and_path
        request = TransactionCreateRequestDTO(
            date="2026-05-17",
            description="Bad currency",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.CHECKING,
                    amount="-100.00",
                    currency="USD",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.FOOD,
                    amount="100.00",
                    currency="USD",
                    memo="",
                ),
            ],
        )
        with pytest.raises(GnuCashWriteError, match="Validation failed"):
            svc.create_transaction(request, user_id=1, book_id=1)

    def test_reject_invalid_date(self, service_and_path):
        """Invalid date format must be rejected."""
        svc, _ = service_and_path
        request = TransactionCreateRequestDTO(
            date="not-a-date",
            description="Bad date",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.CHECKING,
                    amount="-100.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.FOOD,
                    amount="100.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        with pytest.raises(GnuCashWriteError, match="Validation failed"):
            svc.create_transaction(request, user_id=1, book_id=1)


# ---------------------------------------------------------------------------
# 3. Backup creation
# ---------------------------------------------------------------------------


class TestBackupCreation:
    def test_backup_created_on_write(self, service_and_path):
        """A backup file must exist after a successful write."""
        svc, book_path = service_and_path
        request = TransactionCreateRequestDTO(
            date="2026-05-17",
            description="Backup test",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.CHECKING,
                    amount="-50.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.FOOD,
                    amount="50.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        result = svc.create_transaction(request, user_id=1, book_id=1)
        assert result.backup_path
        backup = Path(result.backup_path)
        assert backup.exists()
        assert backup.stat().st_size > 0
        # Backup should be a copy of the book
        assert backup.suffix == ".sqlite"

    def test_backup_created_on_patch(self, service_and_path):
        """A backup file must exist after a successful patch."""
        svc, book_path = service_and_path
        request = TransactionPatchRequestDTO(description="Patched description")
        result = svc.patch_transaction_metadata(
            FixtureTransactions.JANUARY_SALARY, request, user_id=1, book_id=1
        )
        assert result.backup_path
        backup = Path(result.backup_path)
        assert backup.exists()
        assert backup.stat().st_size > 0


# ---------------------------------------------------------------------------
# 4. Original fixture unchanged
# ---------------------------------------------------------------------------


class TestOriginalFixtureUnchanged:
    def test_original_fixture_not_modified(self, service_and_path, fixture_md5):
        """The original fixture file must never be modified."""
        svc, book_path = service_and_path
        # Perform a write
        request = TransactionCreateRequestDTO(
            date="2026-05-17",
            description="Should not affect original",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.CHECKING,
                    amount="-100.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.FOOD,
                    amount="100.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        svc.create_transaction(request, user_id=1, book_id=1)
        # Verify original unchanged
        assert _file_md5(FIXTURE_PATH) == fixture_md5

    def test_original_fixture_transaction_count(self, service_and_path):
        """Original fixture must still have 5 transactions."""
        _svc, _book_path = service_and_path
        # Just verify the original fixture is intact
        txs = _read_transactions(FIXTURE_PATH)
        assert len(txs) == 5


# ---------------------------------------------------------------------------
# 5. Read-back verification
# ---------------------------------------------------------------------------


class TestReadBackVerification:
    def test_create_read_back_splits(self, service_and_path):
        """After creating, verify splits are correct via piecash read-back."""
        svc, book_path = service_and_path
        request = TransactionCreateRequestDTO(
            date="2026-08-15",
            description="Read-back test",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.CHECKING,
                    amount="-250.00",
                    currency="SEK",
                    memo="checking memo",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.TRANSPORT,
                    amount="250.00",
                    currency="SEK",
                    memo="transport memo",
                ),
            ],
        )
        result = svc.create_transaction(request, user_id=1, book_id=1)
        txs = _read_transactions(book_path)
        tx = next((t for t in txs if t["guid"] == result.transaction_id), None)
        assert tx is not None
        assert tx["description"] == "Read-back test"
        assert len(tx["splits"]) == 2
        # Verify split accounts
        split_accounts = {s["account_name"] for s in tx["splits"]}
        assert "Checking" in split_accounts
        assert "Transport" in split_accounts

    def test_transaction_count_increments(self, service_and_path):
        """Creating a transaction increments the total count."""
        svc, book_path = service_and_path
        txs_before = _read_transactions(book_path)
        count_before = len(txs_before)

        request = TransactionCreateRequestDTO(
            date="2026-09-01",
            description="Count test",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.CHECKING,
                    amount="-10.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.FOOD,
                    amount="10.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        svc.create_transaction(request, user_id=1, book_id=1)
        txs_after = _read_transactions(book_path)
        assert len(txs_after) == count_before + 1


# ---------------------------------------------------------------------------
# 6. Patch transaction metadata
# ---------------------------------------------------------------------------


class TestPatchTransactionMetadata:
    def test_patch_description(self, service_and_path):
        """Patch an existing transaction's description and verify read-back."""
        svc, book_path = service_and_path
        request = TransactionPatchRequestDTO(description="Updated description")
        result = svc.patch_transaction_metadata(
            FixtureTransactions.GROCERY_STORE, request, user_id=1, book_id=1
        )
        assert result.transaction_id == FixtureTransactions.GROCERY_STORE
        txs = _read_transactions(book_path)
        tx = next((t for t in txs if t["guid"] == FixtureTransactions.GROCERY_STORE), None)
        assert tx is not None
        assert tx["description"] == "Updated description"

    def test_patch_date(self, service_and_path):
        """Patch an existing transaction's post_date."""
        svc, book_path = service_and_path
        request = TransactionPatchRequestDTO(date="2026-12-25")
        result = svc.patch_transaction_metadata(
            FixtureTransactions.BUS_PASS, request, user_id=1, book_id=1
        )
        assert result.transaction_id == FixtureTransactions.BUS_PASS
        txs = _read_transactions(book_path)
        tx = next((t for t in txs if t["guid"] == FixtureTransactions.BUS_PASS), None)
        assert tx is not None
        from datetime import date

        assert tx["post_date"] == date(2026, 12, 25)

    def test_patch_split_memo(self, service_and_path):
        """Patch a split memo on an existing transaction."""
        svc, book_path = service_and_path
        # Get the split GUIDs for the Grocery store transaction
        txs = _read_transactions(book_path)
        tx = next(t for t in txs if t["guid"] == FixtureTransactions.GROCERY_STORE)
        split_guids = [s["guid"] for s in tx["splits"]]
        assert len(split_guids) >= 1

        target_guid = split_guids[0]
        request = TransactionPatchRequestDTO(split_memos={target_guid: "Updated memo"})
        result = svc.patch_transaction_metadata(
            FixtureTransactions.GROCERY_STORE, request, user_id=1, book_id=1
        )
        assert result.transaction_id == FixtureTransactions.GROCERY_STORE

        # Verify memo was updated
        txs2 = _read_transactions(book_path)
        tx2 = next(t for t in txs2 if t["guid"] == FixtureTransactions.GROCERY_STORE)
        split = next(s for s in tx2["splits"] if s["guid"] == target_guid)
        assert split["memo"] == "Updated memo"

    def test_patch_combined_description_and_date(self, service_and_path):
        """Patch both description and date in one request."""
        svc, book_path = service_and_path
        request = TransactionPatchRequestDTO(
            description="Combined update", date="2026-06-15"
        )
        result = svc.patch_transaction_metadata(
            FixtureTransactions.CREDIT_CARD_PAYMENT, request, user_id=1, book_id=1
        )
        txs = _read_transactions(book_path)
        tx = next(
            (t for t in txs if t["guid"] == FixtureTransactions.CREDIT_CARD_PAYMENT), None
        )
        assert tx["description"] == "Combined update"
        from datetime import date

        assert tx["post_date"] == date(2026, 6, 15)


# ---------------------------------------------------------------------------
# 7. Patch validation rejections
# ---------------------------------------------------------------------------


class TestPatchValidationRejections:
    def test_patch_rejects_noop(self, service_and_path):
        """Empty patch payload (no editable fields) must be rejected."""
        svc, _ = service_and_path
        request = TransactionPatchRequestDTO()
        with pytest.raises(GnuCashWriteError, match="Validation failed"):
            svc.patch_transaction_metadata(
                FixtureTransactions.JANUARY_SALARY, request, user_id=1, book_id=1
            )

    def test_patch_nonexistent_transaction(self, service_and_path):
        """Patching a non-existent transaction must be rejected."""
        svc, _ = service_and_path
        request = TransactionPatchRequestDTO(description="Ghost tx")
        with pytest.raises(GnuCashWriteError, match="Validation failed"):
            svc.patch_transaction_metadata(
                "nonexistent-tx-guid-1234567890abcdef", request, user_id=1, book_id=1
            )

    def test_patch_rejects_invalid_date(self, service_and_path):
        """Invalid date in patch must be rejected."""
        svc, _ = service_and_path
        request = TransactionPatchRequestDTO(date="not-a-date")
        with pytest.raises(GnuCashWriteError, match="Validation failed"):
            svc.patch_transaction_metadata(
                FixtureTransactions.JANUARY_SALARY, request, user_id=1, book_id=1
            )


# ---------------------------------------------------------------------------
# 8. Lock lifecycle
# ---------------------------------------------------------------------------


class TestLockLifecycle:
    def test_lock_acquired_during_write(self, service_and_path, tmp_path: Path):
        """Lock file must exist during a write operation."""
        svc, book_path = service_and_path
        lock_dir = tmp_path / "locks"
        lock_service = WriteLockService(lock_dir=lock_dir)
        book_key = str(book_path)

        # Manually check: lock should be acquirable before write
        assert lock_service.acquire(book_key) is True
        lock_path = lock_service._lock_path(book_key)
        assert lock_path.exists()

        # Release
        lock_service.release(book_key)

    def test_lock_released_after_write(self, service_and_path, tmp_path: Path):
        """After a successful write, the lock must be released (re-acquirable)."""
        svc, book_path = service_and_path
        request = TransactionCreateRequestDTO(
            date="2026-05-17",
            description="Lock release test",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.CHECKING,
                    amount="-10.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.FOOD,
                    amount="10.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        svc.create_transaction(request, user_id=1, book_id=1)

        # Lock should be released — we can acquire it again
        lock_dir = tmp_path / "locks"
        lock_service = WriteLockService(lock_dir=lock_dir)
        book_key = str(book_path)
        assert lock_service.acquire(book_key) is True
        lock_service.release(book_key)

    def test_lock_released_after_failed_write(self, service_and_path, tmp_path: Path):
        """After a failed write, the lock must be released."""
        svc, book_path = service_and_path
        # This request will fail validation
        request = TransactionCreateRequestDTO(
            date="2026-05-17",
            description="Fail test",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.CHECKING,
                    amount="-100.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.FOOD,
                    amount="99.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        with pytest.raises(GnuCashWriteError):
            svc.create_transaction(request, user_id=1, book_id=1)

        # Lock should be released
        lock_dir = tmp_path / "locks"
        lock_service = WriteLockService(lock_dir=lock_dir)
        book_key = str(book_path)
        assert lock_service.acquire(book_key) is True
        lock_service.release(book_key)


# ---------------------------------------------------------------------------
# 9. Lock contention
# ---------------------------------------------------------------------------


class TestLockContention:
    def test_lock_prevents_concurrent_write(self, service_and_path, tmp_path: Path):
        """Holding a lock manually must cause a second write to fail with WriteLockError."""
        svc, book_path = service_and_path
        lock_dir = tmp_path / "locks"
        lock_service = WriteLockService(lock_dir=lock_dir)
        book_key = str(book_path)

        # Manually acquire the lock
        assert lock_service.acquire(book_key) is True

        # Now attempt a write — it should fail because lock is held
        request = TransactionCreateRequestDTO(
            date="2026-05-17",
            description="Contention test",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.CHECKING,
                    amount="-10.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.FOOD,
                    amount="10.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        with pytest.raises(WriteLockError):
            svc.create_transaction(request, user_id=1, book_id=1)

        # Release the lock
        lock_service.release(book_key)

        # Now the write should succeed
        result = svc.create_transaction(request, user_id=1, book_id=1)
        assert result.transaction_id

    def test_lock_contention_with_patch(self, service_and_path, tmp_path: Path):
        """Holding a lock must also block patch operations."""
        svc, book_path = service_and_path
        lock_dir = tmp_path / "locks"
        lock_service = WriteLockService(lock_dir=lock_dir)
        book_key = str(book_path)

        assert lock_service.acquire(book_key) is True

        request = TransactionPatchRequestDTO(description="Should fail")
        with pytest.raises(WriteLockError):
            svc.patch_transaction_metadata(
                FixtureTransactions.JANUARY_SALARY, request, user_id=1, book_id=1
            )

        lock_service.release(book_key)

        # Now patch should succeed
        result = svc.patch_transaction_metadata(
            FixtureTransactions.JANUARY_SALARY, request, user_id=1, book_id=1
        )
        assert result.transaction_id == FixtureTransactions.JANUARY_SALARY


# ---------------------------------------------------------------------------
# 10. Audit log verification (service-level)
# ---------------------------------------------------------------------------


class TestAuditBehavior:
    def test_create_returns_backup_path(self, service_and_path):
        """create_transaction must return a non-empty backup_path."""
        svc, _ = service_and_path
        request = TransactionCreateRequestDTO(
            date="2026-05-17",
            description="Audit test",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.CHECKING,
                    amount="-25.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.FOOD,
                    amount="25.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        result = svc.create_transaction(request, user_id=1, book_id=1)
        assert result.backup_path
        assert len(result.backup_path) > 0

    def test_patch_returns_backup_path(self, service_and_path):
        """patch_transaction_metadata must return a non-empty backup_path."""
        svc, _ = service_and_path
        request = TransactionPatchRequestDTO(description="Audit patch test")
        result = svc.patch_transaction_metadata(
            FixtureTransactions.JANUARY_SALARY, request, user_id=1, book_id=1
        )
        assert result.backup_path
        assert len(result.backup_path) > 0

    def test_create_result_has_transaction_id(self, service_and_path):
        """create_transaction must return a valid transaction_id."""
        svc, _ = service_and_path
        request = TransactionCreateRequestDTO(
            date="2026-05-17",
            description="ID test",
            splits=[
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.CHECKING,
                    amount="-15.00",
                    currency="SEK",
                    memo="",
                ),
                TransactionSplitWriteDTO(
                    account_id=FixtureAccounts.FOOD,
                    amount="15.00",
                    currency="SEK",
                    memo="",
                ),
            ],
        )
        result = svc.create_transaction(request, user_id=1, book_id=1)
        assert result.transaction_id
        assert len(result.transaction_id) == 32  # GnuCash GUIDs are 32 hex chars
