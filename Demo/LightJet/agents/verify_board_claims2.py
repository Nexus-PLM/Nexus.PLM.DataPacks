"""Second pass: re-tests the cards that PR #790 should have closed, on their own objects.

    python verify_board_claims2.py

Three agents reported the revise gate independently (754, 757, 761) and two reported the
trace-link view check (767, 734). Each is re-run as the role that raised it, against the
object it named, because "the same defect" is a claim that has to be checked rather than
assumed - the last time I assumed, the reverse-route finding turned out to be my own tool.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plm_agent import ENGINE, Agent, object_id                       # noqa: E402

VERDICT: list[tuple[str, bool, str]] = []


def record(card: str, fixed: bool, detail: str) -> None:
    VERDICT.append((card, fixed, detail))
    print(f"  {'FIXED ' if fixed else 'STANDS'}  {card}  {detail}")


def call(agent: Agent, method: str, path: str, body=None):
    r = agent.session.request(method, f"{ENGINE}{path}", json=body, timeout=120)
    return r.status_code, (r.text or "")[:160]


def revise_check(card: str, agent: Agent, part: str, admin: Agent) -> None:
    obj = admin.object(part)
    if obj is None:
        record(card, False, f"{part} not found")
        return
    latest = admin.latest(part) or {}
    code, body = call(agent, "POST",
                      f"/api/plmobjects/{object_id(part)}/revisions/{latest.get('revisionId')}/revise",
                      {"status": None})
    # A 201 is the fix working. A 400 means the landing state was rejected, which is a
    # different (and benign) answer - the gate was passed. A 403 means it still stands.
    record(card, code in (201, 400, 409),
           f"{part} ({latest.get('status')}) revise as {agent.username} -> HTTP {code}")


def main() -> int:
    admin = Agent("admin", password="NexusAdmin2026!", role="PLM Administrator")

    print("\n== The revise gate, reported by three roles on three object families ==")
    revise_check("NI-00000754", Agent("m.sandoval", role="Design"), "LSS-21-0004", admin)
    revise_check("NI-00000757", Agent("m.sandoval", role="Design"), "LSS-21-0014", admin)
    revise_check("NI-00000761", Agent("t.brennan", role="Manufacturing"), "LSS-PS-0006", admin)

    print("\n== The trace-link view check, reported twice ==")
    achebe = Agent("r.achebe", role="Systems Engineering")
    for card, part in (("NI-00000767", "LSS-REQ-CMP-0009"), ("NI-00000734", "LSS-REQ-SYS-0001")):
        code, _ = call(achebe, "GET", f"/api/requirement-trace-links/for/{object_id(part)}")
        payload = achebe.get(f"/api/requirement-trace-links/for/{object_id(part)}") or {}
        total = len(payload.get("outgoing") or []) + len(payload.get("incoming") or [])
        record(card, code == 200, f"{part} trace read -> HTTP {code}, {total} link(s)")

    # Creating a link to a non-requirement target was the other half of 767.
    part = admin.object("LSS-21-0014")
    req = admin.object("LSS-REQ-CMP-0009")
    if part and req:
        code, body = call(achebe, "POST", "/api/requirement-trace-links",
                          {"sourceObjectId": req["plmObjectId"],
                           "targetObjectId": part["plmObjectId"],
                           "linkType": "verified-by",
                           "note": "post-fix check that a released part is a reachable target"})
        record("NI-00000767 (create)", code in (201, 409),
               f"link to a released AircraftPart -> HTTP {code} "
               f"{'(already present)' if code == 409 else ''}")

    print("\n== Nova's nightly reconciliation ==")
    status = admin.session.request("GET", "https://192.168.1.47:5500/api/agent/status",
                                   timeout=30, verify=False)
    idx = (status.json() or {}).get("indexing") or {}
    total, indexed = idx.get("totalObjects"), idx.get("indexedObjects")
    record("NI-00000556", bool(total) and indexed and indexed / total > 0.9,
           f"last pass saw {total} objects, {indexed} indexed, "
           f"coverage {idx.get('coverage'):.1%}" if total else "no indexing figures")

    print("\n" + "=" * 78)
    fixed = [v for v in VERDICT if v[1]]
    print(f"{len(fixed)}/{len(VERDICT)} verified fixed\n")
    print("CLOSE:   " + ", ".join(c for c, ok, _ in VERDICT if ok))
    still = [c for c, ok, _ in VERDICT if not ok]
    if still:
        print("OPEN:    " + ", ".join(still))
    return 0


if __name__ == "__main__":
    sys.exit(main())
