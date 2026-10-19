"""Pulls the NX-200 exercise cards off the Nexus Issues board into one local file.

    python dump_board.py

292 cards were filed by the nine role agents. Triaging them one API call at a time is
slow and hammers the server, and the detail that decides whether a card is a product
defect lives in its NOTES rather than its title. This fetches each card once -
attributes and notes together - into reports/board.json, so the triage itself is local.
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plm_agent import Agent                                          # noqa: E402

HERE = Path(__file__).parent
LEDGER = HERE / "reports" / "filed.json"
OUT = HERE / "reports" / "board.json"


def main() -> int:
    ledger = json.loads(io.open(LEDGER, encoding="utf-8").read())
    wanted = {}
    for key, value in ledger.items():
        pn = (value or {}).get("partNumber")
        if pn:
            wanted[pn] = {"ledgerKey": key, "theme": (value or {}).get("theme")}

    me = Agent("admin", password="NexusAdmin2026!", role="PLM Administrator")

    # One listing, then one attribute fetch per card - rather than resolving each part
    # number through a search.
    issues = me.get("/api/plmobjects?typeName=NexusIssue") or []
    print(f"{len(issues)} NexusIssue objects on the board; {len(wanted)} filed by the exercise")

    rows = []
    for i, obj in enumerate(issues, 1):
        pn = obj.get("partNumber")
        if pn not in wanted:
            continue
        oid = obj.get("plmObjectId")
        latest = me.get(f"/api/plmobjects/{oid}/revisions/latest") or {}
        attrs = me.get(f"/api/plmobjects/{oid}/revisions/latest/attributes") or {}
        rows.append({
            "partNumber": pn,
            "objectId": oid,
            "revisionId": latest.get("revisionId"),
            "status": latest.get("status"),
            "description": obj.get("description"),
            "notes": latest.get("notes") or "",
            "theme": wanted[pn]["theme"],
            "attrs": attrs if isinstance(attrs, dict) else {},
        })
        if i % 50 == 0:
            print(f"  ...{len(rows)} fetched")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(rows, indent=1))
    print(f"\nwrote {len(rows)} cards to {OUT}")

    by_status: dict[str, int] = {}
    by_sev: dict[str, int] = {}
    for r in rows:
        by_status[str(r["status"])] = by_status.get(str(r["status"]), 0) + 1
        by_sev[str(r["attrs"].get("severity"))] = by_sev.get(str(r["attrs"].get("severity")), 0) + 1
    print("\nby status:  " + ", ".join(f"{k}={v}" for k, v in sorted(by_status.items())))
    print("by severity:" + ", ".join(f" {k}={v}" for k, v in sorted(by_sev.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
