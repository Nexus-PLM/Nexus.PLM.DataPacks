"""Removes the old generic reference to a material where a MadeOfLink now says it properly.

This dataset recorded "what this part is made from" as a plain `RelatedLink` with a note,
because there was no kind that meant it. There is now: `cstLightSpeedSystemsMadeOfLink`
carries the material, the share of the part's volume and the mass it contributes, and the
Engine calculates from it. The old link is left saying the same thing in a weaker way.

Two reasons to clear it rather than leave it:

  * It already caused a wrong answer. Material content used to be recognised by what a
    reference pointed AT, so a part with both links had its material counted twice and
    every calculated mass came out exactly double. The Engine now decides by the KIND, so
    the stale link is harmless to the arithmetic - but the data still says "material"
    twice, in two kinds, with no rule about which is true.
  * It is the same trap as `unitWeight` beside `massKg`: a second place to state the same
    fact, which somebody will eventually update instead of the real one.

Only a reference that is genuinely redundant is removed: the target is a material, a
MadeOfLink on the same revision already points at that same material, and the kind carries
no material-content attributes of its own. A `RelatedLink` from a drawing or a test report
to a material is not touched - that one really is just "related".

    python dedupe_material_links.py             # says what it would remove
    python dedupe_material_links.py --apply

Everything removed is written to reports/material-link-dedupe-backup.json first, with the
note text and both endpoints, so any one of them can be recreated by hand.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from plm_agent import Refused, admin_agent                           # noqa: E402

REPORTS = HERE / "reports"
MATERIAL_KIND_MARKER = "MadeOf"
MATERIAL_TYPE_MARKER = "Material"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    me = admin_agent()

    objs = me.get("/api/plmobjects?pageSize=3000") or []
    rows = objs if isinstance(objs, list) else objs.get("items", [])
    parts = [o for o in rows
             if str(o.get("typeName", "")).startswith("cstLightSpeedSystems")
             and not o.get("isDeleted")]

    redundant = []
    for part in parts:
        latest = me.get(f"/api/plmobjects/{part['plmObjectId']}/revisions/latest") or {}
        if not latest.get("revisionId"):
            continue
        refs = me.get(f"/api/plmobjects/{part['plmObjectId']}/revisions"
                      f"/{latest['revisionId']}/references") or []

        # Which materials this revision already states properly.
        stated = {(r.get("target") or {}).get("objectId") for r in refs
                  if MATERIAL_KIND_MARKER in str(r.get("linkTypeName"))}
        if not stated:
            continue

        for ref in refs:
            kind = str(ref.get("linkTypeName"))
            target = ref.get("target") or {}
            if MATERIAL_KIND_MARKER in kind:
                continue
            if MATERIAL_TYPE_MARKER not in str(target.get("typeName")):
                continue
            if target.get("objectId") not in stated:
                continue      # a material nothing states properly - leave it, it is the
                              # only record there is
            redundant.append({
                "partNumber": part.get("partNumber"),
                "objectId": part["plmObjectId"],
                "revisionId": latest["revisionId"],
                "linkObjectId": ref.get("linkObjectId"),
                "linkTypeName": kind,
                "note": ref.get("note"),
                "revisionRule": ref.get("revisionRule"),
                "target": target.get("partNumber"),
                "targetObjectId": target.get("objectId"),
            })

    print(f"{len(redundant)} redundant reference(s) on "
          f"{len({r['partNumber'] for r in redundant})} part(s)")
    for row in redundant[:12]:
        print(f"   {row['partNumber']:18} {row['linkTypeName']:<14} -> {row['target']:<14} "
              f"{str(row['note'])[:48]}")
    if len(redundant) > 12:
        print(f"   ... {len(redundant) - 12} more")

    if not redundant:
        return 0

    REPORTS.mkdir(parents=True, exist_ok=True)
    io.open(REPORTS / "material-link-dedupe-backup.json", "w", encoding="utf-8").write(
        json.dumps(redundant, indent=1))

    if not args.apply:
        print("\n(report only - pass --apply; backup already written)")
        return 0

    removed, failed = 0, []
    for row in redundant:
        try:
            me.delete(f"/api/plmobjects/{row['objectId']}/revisions/{row['revisionId']}"
                      f"/references/{row['linkObjectId']}")
            removed += 1
        except Refused as exc:
            failed.append((row["partNumber"], exc.status, str(exc.body)[:100]))
        except Exception as exc:                                     # noqa: BLE001
            failed.append((row["partNumber"], "?", str(exc)[:100]))

    print(f"\nremoved {removed}, failed {len(failed)}")
    for pn, status, why in failed[:10]:
        print(f"   {pn:18} {status} {why}")

    # The arithmetic must not have moved: the kind test already excluded these.
    print("\nMass after, on the three aircraft:")
    for ac in ("LSS-AC-001", "LSS-AC-002", "LSS-AC-003"):
        o = me.latest(ac)
        if not o:
            continue
        r = me.get(f"/api/rollup/{o['plmObjectId']}?attribute=massKg") or {}
        print(f"   {ac}  {r.get('rolledUpValue')}  "
              f"{r.get('valuedParts')}/{r.get('totalParts')} valued")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
