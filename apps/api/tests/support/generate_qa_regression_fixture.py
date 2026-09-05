"""Generate new deterministic QA books; never accept/copy an existing book.

Direct SQL is confined to synthetic fixture construction (including intentionally
missing recurrence metadata). Product reads start only after final hash/chmod.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import sqlite3

import piecash

from tests.support.generate_issue60_usability_fixture import _stabilize_default_identity

SEED = 20260906
SCENARIOS = {"scheduled_partial", "scheduled_valid", "scheduled_invalid", "empty"}


def guid(label: str) -> str:
    return hashlib.sha256(f"synthetic-qa:{SEED}:{label}".encode()).hexdigest()[:32]


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
    }
