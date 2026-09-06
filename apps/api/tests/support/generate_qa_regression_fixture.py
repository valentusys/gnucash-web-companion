"""Generate new deterministic QA books; never accept/copy an existing book.

Direct SQL is confined to synthetic fixture construction (including intentionally
missing recurrence metadata). Product reads start only after final hash/chmod.
"""
from __future__ import annotations

import hashlib
from datetime import date
from decimal import Decimal
from pathlib import Path
import sqlite3

import piecash

from tests.support.generate_issue60_usability_fixture import _stabilize_default_identity

SEED = 20260906
SCENARIOS = {"scheduled_partial", "scheduled_valid", "scheduled_invalid", "empty", "money"}


def guid(label: str) -> str:
    return hashlib.sha256(f"synthetic-qa:{SEED}:{label}".encode()).hexdigest()[:32]


def _money_scenario(book):
    rub = book.default_currency
    usd = piecash.Commodity(namespace="CURRENCY", mnemonic="USD", fullname="Synthetic USD", fraction=100)
    usd.guid = guid("usd")
    accounts = {}
    for name, kind, currency in [("cash", "BANK", rub), ("savings", "BANK", rub), ("income", "INCOME", rub), ("expense", "EXPENSE", rub), ("fees", "EXPENSE", rub), ("credit", "CREDIT", rub), ("usd", "BANK", usd)]:
        account = piecash.Account(name=f"SYNTHETIC {name}", type=kind, commodity=currency, parent=book.root_account)
        account.guid = guid(f"account:{name}")
        accounts[name] = account
    cases = {
        "income": [("income", "-2500", "-2500"), ("cash", "2500", "2500")],
        "expense": [("cash", "-123.45", "-123.45"), ("expense", "123.45", "123.45")],
        "refund": [("expense", "-25.01", "-25.01"), ("cash", "25.01", "25.01")],
        "transfer": [("cash", "-80", "-80"), ("savings", "80", "80")],
        "credit": [("credit", "-40", "-40"), ("expense", "40", "40")],
        "zero": [("cash", "0", "0"), ("savings", "0", "0")],
        "large": [("cash", "-90071992547409.91", "-90071992547409.91"), ("savings", "90071992547409.91", "90071992547409.91")],
        "composite": [("cash", "-31", "-31"), ("expense", "30", "30"), ("fees", "1", "1")],
        "multicurrency": [("cash", "-90", "-90"), ("usd", "90", "1")],
    }
    manifest = {}
    for name, specs in cases.items():
        splits = []
        for index, (account, value, quantity) in enumerate(specs):
            split = piecash.Split(account=accounts[account], value=Decimal(value), quantity=Decimal(quantity))
            split.guid = guid(f"split:{name}:{index}")
            splits.append(split)
        tx = piecash.Transaction(currency=rub, description=f"SYNTHETIC QA {name}", post_date=date(2026, 9, 1), splits=splits)
        tx.guid = guid(f"tx:{name}")
        manifest[name] = {"id": tx.guid, "magnitude": str(abs(Decimal(specs[0][1]))) if name not in {"composite", "multicurrency"} else None, "currency": "RUB"}
    return manifest


def generate_qa_regression_fixture(root: Path | str, *, scenario: str = "scheduled_partial") -> dict:
    """Create only in a NEW caller-owned disposable directory; refuse reuse."""
    if scenario not in SCENARIOS:
        raise ValueError("Unknown synthetic scenario")
    root = Path(root).absolute()
    root.mkdir(parents=True, exist_ok=False, mode=0o700)
    path = root / "synthetic-qa.gnucash.sqlite"
    book = piecash.create_book(currency="RUB", sqlite_file=str(path), overwrite=False)
    try:
        identities = {
            "old_book": book.guid, "new_book": guid("book"),
            "old_root": book.root_account.guid, "new_root": guid("root"),
            "old_template_root": book.root_template.guid, "new_template_root": guid("template-root"),
            "old_rub": book.default_currency.guid, "new_rub": guid("rub"),
        }
        transactions = _money_scenario(book) if scenario == "money" else {}
        book.save()
    finally:
        book.close()
    _stabilize_default_identity(path, identities, seed=SEED)
    valid_ids = [guid(f"schedule:{index:02d}") for index in range(15)] if scenario in {"scheduled_partial", "scheduled_valid"} else []
    invalid_ids = [guid("schedule:invalid")] if scenario in {"scheduled_partial", "scheduled_invalid"} else []
    with sqlite3.connect(path) as db:
        for index, schedule_id in enumerate(valid_ids + invalid_ids):
            db.execute(
                """INSERT INTO schedxactions
                (guid,name,enabled,start_date,end_date,last_occur,num_occur,rem_occur,
                 auto_create,auto_notify,adv_creation,adv_notify,instance_count,template_act_guid)
                VALUES (?,?,1,'20260901',NULL,NULL,0,0,0,0,0,0,0,?)""",
                (schedule_id, f"SYNTHETIC QA schedule {index:02d}", guid("template-root")),
            )
            if schedule_id in valid_ids:
                db.execute(
                    """INSERT INTO recurrences
                    (obj_guid,recurrence_mult,recurrence_period_type,recurrence_period_start,recurrence_weekend_adjust)
                    VALUES (?,1,'month','20260901','none')""", (schedule_id,),
                )
        db.commit()
        db.execute("VACUUM")
    path.chmod(0o400)
    return {
        "seed": SEED, "scenario": scenario, "book_path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "valid_schedule_ids": valid_ids, "invalid_schedule_ids": invalid_ids,
        "transactions": transactions,
    }
