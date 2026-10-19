"""Forces the Engine to recalculate every part's mass from its material.

    python recalculate_masses.py             # report only
    python recalculate_masses.py --apply

Needed whenever the CALCULATION changes rather than the data: a stored mass records what
the Engine worked out when the reference was made, so a fix to the arithmetic leaves every
existing part carrying the old answer. That happened on 2026-10-19 - material content was
recognised by the reference's target alone, so a part's old generic RelatedLink to a
material was counted alongside its MadeOfLink and every calculated mass was exactly double.

It works by writing each part's volume back unchanged. The Engine recalculates when
volumeCm3 is written, whether or not the value moved, so this re-derives the mass without
altering a single figure the dataset states. Nothing else is touched, and a part whose
mass is DECLARED keeps it - the Engine decides that, not this script.

Run as the administrator: most of this dataset is Released and correctly refuses an
engineer's edit. That is dataset maintenance, the same act as loading it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plm_agent import Agent, Refused                                   # noqa: E402

LINK_KIND_MARKER = "MadeOf"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    me = Agent("admin", password="NexusAdmin2026!", role="PLM Administrator")

    objects = me.get("/api/plmobjects?pageSize=3000")
    rows = objects if isinstance(objects, list) else objects.get("items", [])
    parts = [r for r in rows
             if str(r.get("typeName", "")).startswith("cst")
             and not r.get("isDeleted")]

    touched, skipped, failed, changes = 0, 0, [], []
    for part in parts:
        pn = part["partNumber"]
        latest = me.latest(pn)
        if not latest:
            continue
        refs = me.get(
            f"/api/plmobjects/{part['plmObjectId']}/revisions/{latest['revisionId']}/references") or []
        if not any(LINK_KIND_MARKER in str(r.get("linkTypeName")) for r in refs):
            continue

        attrs = me.attributes(pn) or {}
        volume = attrs.get("volumeCm3")
        before = attrs.get("massKg")
        if volume in (None, "", 0):
            skipped += 1
            continue

        if not args.apply:
            touched += 1
            continue

        try:
            # The same value, written back: the recalculation hook fires on the KEY being
            # present, so this re-derives the mass without changing anything stated.
            me.set_attributes(pn, {"volumeCm3": float(volume)})
            after = (me.attributes(pn) or {}).get("massKg")
            touched += 1
            if str(before) != str(after):
                changes.append((pn, before, after))
        except Refused as exc:
            failed.append((pn, exc.status, str(exc.body)[:120]))
        except Exception as exc:                                       # noqa: BLE001
            failed.append((pn, "?", str(exc)[:120]))

    verb = "recalculated" if args.apply else "would recalculate"
    print(f"{verb} {touched} part(s); {skipped} had no usable volume")

    if changes:
        print(f"\n{len(changes)} mass(es) changed:")
        for pn, b, a in changes[:20]:
            try:
                print(f"  {pn:20} {float(b):>10.4f} -> {float(a):>10.4f} kg "
                      f"({float(a) / float(b):.3f}x)")
            except (TypeError, ValueError, ZeroDivisionError):
                print(f"  {pn:20} {b} -> {a}")
        if len(changes) > 20:
            print(f"  ... {len(changes) - 20} more")
    elif args.apply:
        print("no mass changed - the stored values already match the calculation")

    if failed:
        print(f"\n{len(failed)} refused or failed:")
        for pn, status, body in failed[:10]:
            print(f"  {pn:20} {status}  {body}")

    if not args.apply:
        print("\n(report only - pass --apply)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
