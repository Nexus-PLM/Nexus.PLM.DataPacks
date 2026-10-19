"""Who can do what, asked of the live server as each person in turn.

    python verify_security_matrix.py                 # one object per NX-200 type
    python verify_security_matrix.py --all-types     # include OOTB types too
    python verify_security_matrix.py --part LSS-21-0014

Every row is the server's own answer to `GET /api/plmobjects/{id}/permissions`, fetched
while logged in as that person. Nothing here reads the policy tables or re-implements the
evaluator: the point is to catch the case where the model SAYS one thing and the running
Engine does another, which is how the whole canCreate family got missed.

Why this script exists
----------------------
The nine role agents re-run the NX-200 scenario and report what they could not do. That is
the right test, but it is slow and it conflates two different failures - a product defect
and a configuration mistake. This is the cheap version: it asks the same questions in a few
seconds, so a configuration change can be checked before nine agents spend an hour
discovering it did not work.

`canCreate` is the interesting column. It is a right on the TYPE, not on the object, so
every object of a type answers identically - and it is the one right that used to read its
policy backwards, granting create to everyone when the model granted it to nobody.

**Sample by state, not by type.** Edit, delete and transition are decided per lifecycle
state, so one object per type measures nothing: the first object of most types is Released
or Closed, where no edit is the CORRECT answer, and a per-type sweep reports that as 28
types nobody can edit. This probes one object per (type, state) pair and judges each state
on its own terms - a live state no role can edit is a defect, a settled state no role can
edit is the model working.

Read-only. It performs no writes and spends no part numbers; `peek` exists for that reason.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from concurrent import futures
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plm_agent import ENGINE, Agent, Refused                            # noqa: E402

sys.path.insert(0, str(Path(__file__).parent.parent / "model"))
import build_customization as MODEL                                     # noqa: E402

# A state where editing is withheld on purpose: a released or settled record is immutable,
# and a record awaiting a signature is frozen so data cannot change under the signatory.
# Imported from the model that built the policy rather than restated here, so the two
# cannot drift apart.
LOCKED_BY_DESIGN = MODEL.RELEASE_LOCKED | MODEL.AWAITING_DECISION

HERE = Path(__file__).parent
OUT = HERE / "reports" / "security_matrix.json"

# The nine people the scenario is run by, with what each one is for. The comment is the
# expectation a reader should judge the row against.
ROLES = {
    "f.mbeki":      "Customer support - problem reports, bulletins, fleet",
    "h.okafor":     "Change board chair - dispositions change requests",
    "m.sandoval":   "Design engineer - parts and drawings",
    "y.cheng":      "Materials engineer - materials and approved sources",
    "t.brennan":    "Manufacturing engineer - process specifications",
    "p.lindqvist":  "Stress engineer - structural substantiation",
    "r.achebe":     "Requirements engineer - requirements and trace",
    "k.tanaka":     "Quality engineer - nonconformance and first articles",
    "c.delacroix":  "Delegated authority (DER) - certification acceptance",
}

RIGHTS = ["canView", "canRead", "canCreate", "canEdit", "canDelete", "canTransition"]


def pick_targets(admin: Agent, all_types: bool) -> dict[str, dict]:
    """One representative object per (type, state), because rights are per-state.

    Costs one permissions call per candidate object to learn its state, done as the
    administrator and once per run, so the nine per-person sweeps that follow are cheap.
    """
    objects = admin.get("/api/plmobjects?pageSize=2000")
    rows = objects if isinstance(objects, list) else objects.get("items", [])
    rows = [r for r in rows
            if not r.get("isDeleted")
            and (all_types or str(r.get("typeName")).startswith("cst"))]

    def state_of(row: dict) -> tuple[dict, str | None]:
        try:
            payload = admin.get(f"/api/plmobjects/{row['plmObjectId']}/permissions")
            return row, payload.get("currentState")
        except Exception:                                              # noqa: BLE001
            return row, None

    chosen: dict[str, dict] = {}
    with futures.ThreadPoolExecutor(max_workers=12) as pool:
        for row, state in pool.map(state_of, sorted(rows, key=lambda r: str(r.get("partNumber")))):
            if state is None:
                continue
            key = f"{row['typeName']}@{state}"
            if key not in chosen:
                chosen[key] = {**row, "state": state}
    return chosen


def probe(person: Agent, targets: dict[str, dict]) -> dict[str, dict]:
    """Ask the server what `person` may do to one object of each type."""
    answers: dict[str, dict] = {}
    for type_name, row in targets.items():
        object_id = row["plmObjectId"]
        try:
            payload = person.get(f"/api/plmobjects/{object_id}/permissions", allow_403=True)
        except Refused as exc:
            # A refusal IS the answer: the caller cannot even ask. Record it rather than
            # letting one unreadable object end the sweep.
            answers[type_name] = {"refused": exc.status, "partNumber": row.get("partNumber")}
            continue
        if isinstance(payload, Refused):
            answers[type_name] = {"refused": payload.status, "partNumber": row.get("partNumber")}
            continue

        answers[type_name] = {
            "partNumber": row.get("partNumber"),
            "state": payload.get("currentState"),
            "transitions": payload.get("allowedTransitions") or [],
            **{r: bool(payload.get(r)) for r in RIGHTS},
        }
    return answers


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all-types", action="store_true",
                    help="probe OOTB types as well as the NX-200 ones")
    ap.add_argument("--part", help="probe this one part number instead of a type sweep")
    args = ap.parse_args()

    print(f"Engine: {ENGINE}\n")
    admin = Agent("admin", password="NexusAdmin2026!", role="PLM Administrator")

    if args.part:
        row = admin.object(args.part)
        targets = {row["typeName"]: row}
    else:
        targets = pick_targets(admin, args.all_types)
    print(f"{len(targets)} type(s) to probe\n")

    matrix: dict[str, dict] = {}
    for username, purpose in ROLES.items():
        try:
            person = Agent(username)
        except Exception as exc:                                   # noqa: BLE001
            print(f"  {username}: COULD NOT LOG IN - {exc}")
            matrix[username] = {"error": str(exc)}
            continue
        matrix[username] = probe(person, targets)
        got = matrix[username]
        creatable = sum(1 for v in got.values() if v.get("canCreate"))
        editable = sum(1 for v in got.values() if v.get("canEdit"))
        readable = sum(1 for v in got.values() if v.get("canRead"))
        print(f"  {username:14} read {readable:3}/{len(targets)}  "
              f"create {creatable:3}  edit {editable:3}   {purpose}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"targets": {k: v.get("partNumber") for k, v in targets.items()},
                               "matrix": matrix}, indent=1), encoding="utf-8")
    print(f"\nwrote {OUT}")

    # Judged per state, because that is how the rights are decided. A settled state that
    # nobody can edit is the model working as designed; a WORKING state that nobody can
    # edit is a role unable to do its job, which is the finding worth raising. Reporting
    # one number per TYPE conflates the two and reads as 28 broken types on a model that
    # is behaving correctly.
    def any_role(key, right):
        return any(matrix.get(u, {}).get(key, {}).get(right) for u in ROLES)

    types = {k.split("@", 1)[0] for k in targets}
    nobody_creates = sorted(
        t for t in types
        if not any(any_role(k, "canCreate") for k in targets if k.startswith(t + "@")))

    working_uneditable, locked_uneditable = [], []
    for key, row in sorted(targets.items()):
        if any_role(key, "canEdit"):
            continue
        bucket = locked_uneditable if row["state"] in LOCKED_BY_DESIGN else working_uneditable
        bucket.append((key, row))

    if nobody_creates:
        print("\n!! %d type(s) NO role can create:" % len(nobody_creates))
        for t in nobody_creates:
            print("     " + t)
    else:
        print("\nEvery probed type has at least one role that can create it.")

    if working_uneditable:
        print("\n!! %d WORKING state(s) no role can edit - a role cannot do its job here:"
              % len(working_uneditable))
        for key, row in working_uneditable:
            type_name, state = key.split("@", 1)
            print("     %-26s %-22s %s" % (state, row.get("partNumber"), type_name))
    else:
        print("Every working state has at least one role that can edit it.")

    print("\n%d settled state(s) nobody can edit, which is correct by design "
          "(RELEASE_LOCKED / AWAITING_DECISION)." % len(locked_uneditable))
    return 0


if __name__ == "__main__":
    sys.exit(main())
