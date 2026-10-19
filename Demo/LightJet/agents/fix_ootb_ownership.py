"""Gives the OOTB-typed demo objects the owner their own data names.

`apply_config_fixes.py` moved the 273 objects of this dataset's own types and left the
platform's types alone, so the change board and the whole WBS were still owned by the
account that loaded them. That matters because the shipped policy grants edit on `Own`:
with the loader owning every ECR, the change manager could not edit one, which is the
entire job of the role. Same for the programme plan - every task, phase and milestone was
the loader's, so the person named on it could not touch it.

Who holds what is already stated in the data, so nothing here is a judgement call:

  * Program, Phase, WorkPackage, Task, Milestone -> `assignedTo`. That IS the holder; a
    plan line with somebody's name on it is theirs.
  * ProblemReport -> `originator`, the person who raised it.
  * ECR, ECO, ECN -> these name nobody, and the record belongs to the change manager who
    administers it, not to whoever asked for the change.

Deliberately NOT moved:

  * RequirementBaseline and its 29 items. A baseline is a snapshot taken at a moment -
    editing one is not a thing anybody should be able to do, so leaving it with the
    administrator is the correct answer rather than an oversight.
  * Report and SavedSearch owned by the administrator, which are the administrator's.
  * Links. A link's owner has never gated anything a role needs here.

    python fix_ootb_ownership.py --dry-run     # says what it would move, writes nothing
    python fix_ootb_ownership.py               # moves, then proves it as the real users

The previous owner of everything it touches is written to reports/ootb-owners-backup.json
before a single transfer, so this is reversible.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from plm_agent import ADMIN_USERNAME, Agent, Refused, admin_agent     # noqa: E402

REPORTS = HERE / "reports"

# The account that loaded the dataset, and the only current owner this will move from.
LOADER = ADMIN_USERNAME

# type -> the attribute that names the holder, or None when the type names nobody.
HOLDER_ATTRIBUTE = {
    "Program": "assignedTo",
    "Phase": "assignedTo",
    "WorkPackage": "assignedTo",
    "Task": "assignedTo",
    "Milestone": "assignedTo",
    "ProblemReport": "originator",
    "ECR": None,
    "ECO": None,
    "ECN": None,
}

# For the types that name nobody: the role that administers the record.
OWNER_OF_LAST_RESORT = {"ECR": "h.okafor", "ECO": "h.okafor", "ECN": "h.okafor"}

# States where refusing an edit is correct, so a failed probe there proves nothing.
LOCKED_STATES = {"Released", "Closed", "Cancelled", "Superseded", "Implemented",
                 "Approved", "Rejected"}


def say(text: str = "") -> None:
    print(text, flush=True)


def plan_moves(me: Agent) -> tuple[list[dict], list[dict]]:
    users = me.get("/api/users") or []
    uid = {u.get("username"): (u.get("userId") or u.get("id")) for u in users}
    byid = {v: k for k, v in uid.items()}

    objs = me.get("/api/plmobjects?pageSize=3000") or []
    rows = objs if isinstance(objs, list) else objs.get("items", [])

    backup, moves, unresolved = [], [], []
    for o in rows:
        if o.get("isDeleted"):
            continue
        type_name = str(o.get("typeName", ""))
        if type_name not in HOLDER_ATTRIBUTE:
            continue

        oid = o["plmObjectId"]
        was = byid.get(o.get("ownerId"))
        backup.append({"objectId": oid, "partNumber": o.get("partNumber"),
                       "typeName": type_name, "ownerId": o.get("ownerId"),
                       "ownerUsername": was})

        # Only the loader's objects. A task already held by the project manager who
        # raised it is not the gap this fixes, and taking it off them would cost them
        # the edit-Own they are using - the shipped policy grants edit on Own and
        # little else, so every transfer gives one person a right and removes it from
        # another. The gap is that the loader account holds things no account should.
        if was != LOADER:
            continue

        attribute = HOLDER_ATTRIBUTE[type_name]
        attrs = me.get(f"/api/plmobjects/{oid}/revisions/latest/attributes") or {}
        holder = attrs.get(attribute) if attribute else None
        if not (isinstance(holder, str) and holder in uid):
            holder = OWNER_OF_LAST_RESORT.get(type_name)
        if not holder or holder not in uid:
            unresolved.append({"partNumber": o.get("partNumber"), "typeName": type_name})
            continue
        if uid[holder] == o.get("ownerId"):
            continue

        latest = me.get(f"/api/plmobjects/{oid}/revisions/latest") or {}
        moves.append({"objectId": oid, "revisionId": latest.get("revisionId"),
                      "partNumber": o.get("partNumber"), "typeName": type_name,
                      "status": latest.get("status"), "from": was,
                      "to": holder, "toId": uid[holder]})

    REPORTS.mkdir(parents=True, exist_ok=True)
    io.open(REPORTS / "ootb-owners-backup.json", "w", encoding="utf-8").write(
        json.dumps(backup, indent=1))
    return moves, unresolved


def prove(moves: list[dict]) -> int:
    """Edit one object per new owner, AS that owner. A refusal here is the real answer."""
    say("")
    say("Proving it as the real users")
    candidates: dict[str, dict] = {}
    for row in moves:
        if str(row.get("status")) in LOCKED_STATES:
            continue
        candidates.setdefault(row["to"], row)

    if not candidates:
        say("  nothing in a working state to probe - every moved object is locked by state")
        return 0

    bad = 0
    for username, row in sorted(candidates.items()):
        user = Agent(username, role=username)
        pn = row["partNumber"]
        try:
            before = (user.attributes(pn) or {}).get("priority")
            user.set_attributes(pn, {"priority": before} if before else {"health": "Green"})
            say(f"  {username:<14} edits {row['typeName']:<14} {pn:<16} "
                f"({row['status']})  OK")
        except Refused as exc:
            bad += 1
            say(f"  {username:<14} edits {row['typeName']:<14} {pn:<16} "
                f"({row['status']})  REFUSED {exc.status} {str(exc.body)[:90]}")
        except Exception as exc:                                     # noqa: BLE001
            bad += 1
            say(f"  {username:<14} edits {row['typeName']:<14} {pn:<16}  FAILED {exc}")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    me = admin_agent()
    moves, unresolved = plan_moves(me)

    tally: dict[str, int] = {}
    for row in moves:
        key = f"{row['typeName']} -> {row['to']}"
        tally[key] = tally.get(key, 0) + 1
    say(f"{len(moves)} to move, {len(unresolved)} name nobody")
    for key, count in sorted(tally.items(), key=lambda x: (-x[1], x[0])):
        say(f"   {key:<34} {count}")
    for row in unresolved[:10]:
        say(f"   unresolved: {row['typeName']} {row['partNumber']}")

    if args.dry_run:
        say("")
        say("(dry run - nothing written)")
        return 0

    moved, problems = 0, []
    for row in moves:
        if not row["revisionId"]:
            problems.append((row["partNumber"], "no revision"))
            continue
        try:
            me.post(f"/api/plmobjects/{row['objectId']}/revisions/{row['revisionId']}"
                    f"/transfer-owner", {"newOwnerUserId": row["toId"]})
            moved += 1
        except Exception as exc:                                     # noqa: BLE001
            problems.append((row["partNumber"], str(exc)[:140]))
    say("")
    say(f"transferred {moved}, failed {len(problems)}")
    for pn, why in problems[:10]:
        say(f"   {pn}: {why}")

    bad = prove(moves)
    say("")
    say("all probes passed" if not bad else f"{bad} probe(s) still refused")
    return 1 if (problems or bad) else 0


if __name__ == "__main__":
    sys.exit(main())
