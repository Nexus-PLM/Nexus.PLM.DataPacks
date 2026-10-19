"""Puts the change records' priority back into the vocabulary their own type declares.

The platform's change types (ECR, ECO, ECN, ProblemReport) declare priority as
`P1 - Immediate / P2 - High / P3 - Normal / P4 - Low`. This dataset's own types declare it
as `Low / Medium / High / Critical`. The loader used the second scale for everything, so
thirteen change records hold a value their own type forbids.

That went unnoticed because nothing enforced a list of values when the data was loaded.
Now that something does, the records cannot be saved at all: any edit that sends priority
comes back `400 'Critical' is not an allowed value for priority` - and a form sends every
attribute, so in the client that is every edit. The change manager could not have worked
on these whatever their rights were.

The two scales say the same four things, so the mapping is not a judgement:

    Critical -> P1 - Immediate      Medium -> P3 - Normal
    High     -> P2 - High           Low    -> P4 - Low

    python fix_change_priorities.py              # says what it would change
    python fix_change_priorities.py --apply

The seed is fixed in the same commit, so a reload does not put the old scale back. This
script is for the site that is already loaded.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from plm_agent import Refused, admin_agent                           # noqa: E402

CHANGE_TYPES = ("ECR", "ECO", "ECN", "ProblemReport")

# The dataset's scale -> the scale the platform's change types declare.
TO_PLATFORM_SCALE = {
    "Critical": "P1 - Immediate",
    "High": "P2 - High",
    "Medium": "P3 - Normal",
    "Low": "P4 - Low",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    me = admin_agent()

    allowed: dict[str, set[str]] = {}
    for type_name in CHANGE_TYPES:
        resolved = me.get(f"/api/types/{type_name}/resolved") or {}
        attribute = next((a for a in (resolved.get("attributes") or [])
                          if str(a.get("name")) == "priority"), None)
        allowed[type_name] = set(attribute.get("lov") or []) if attribute else set()
        print(f"{type_name:<15} declares {sorted(allowed[type_name])}")

    objs = me.get("/api/plmobjects?pageSize=3000") or []
    rows = objs if isinstance(objs, list) else objs.get("items", [])

    plan = []
    for o in rows:
        type_name = str(o.get("typeName", ""))
        if type_name not in CHANGE_TYPES or o.get("isDeleted"):
            continue
        latest = me.get(f"/api/plmobjects/{o['plmObjectId']}/revisions/latest") or {}
        attrs = me.get(f"/api/plmobjects/{o['plmObjectId']}/revisions/latest/attributes") or {}
        current = attrs.get("priority")
        if not current or current in allowed[type_name]:
            continue
        wanted = TO_PLATFORM_SCALE.get(str(current))
        if wanted is None or wanted not in allowed[type_name]:
            print(f"   {o.get('partNumber')}: {current!r} maps to nothing this type allows")
            continue
        plan.append({"objectId": o["plmObjectId"], "revisionId": latest.get("revisionId"),
                     "partNumber": o.get("partNumber"), "typeName": type_name,
                     "status": latest.get("status"), "from": current, "to": wanted})

    print(f"\n{len(plan)} record(s) hold a priority their type forbids")
    for row in plan:
        print(f"   {row['partNumber']:18} {row['typeName']:<14} "
              f"{row['from']:<10} -> {row['to']}")

    if not plan or not args.apply:
        if plan:
            print("\n(report only - pass --apply)")
        return 0

    fixed, failed = 0, []
    for row in plan:
        try:
            me.patch(f"/api/plmobjects/{row['objectId']}/revisions/{row['revisionId']}"
                     f"/attributes", {"priority": row["to"]})
            fixed += 1
        except Refused as exc:
            failed.append((row["partNumber"], exc.status, str(exc.body)[:110]))
        except Exception as exc:                                     # noqa: BLE001
            failed.append((row["partNumber"], "?", str(exc)[:110]))

    print(f"\ncorrected {fixed}, failed {len(failed)}")
    for pn, status, why in failed:
        print(f"   {pn:18} {status} {why}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
