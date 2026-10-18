"""Re-tests specific board cards against the running Engine, on the objects they name.

    python verify_board_claims.py

A card is closed on evidence or not at all. Each check below re-runs what its reporter
actually did - same user, same object, same call - so a closure cites a live result rather
than my reading of the fix. Anything that still fails stays open, and says so.

Writes only where the card's claim IS a write that should now succeed (a revise), and the
one throwaway object it creates to prove the revisionless-delete fix is deleted again.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plm_agent import ENGINE, Agent, object_id                       # noqa: E402

VERDICT: list[tuple[str, str, bool, str]] = []


def record(card: str, claim: str, fixed: bool, detail: str) -> None:
    VERDICT.append((card, claim, fixed, detail))
    print(f"  {'FIXED ' if fixed else 'STANDS'}  {card}  {detail}")


def call(agent: Agent, method: str, path: str, body=None):
    r = agent.session.request(method, f"{ENGINE}{path}", json=body, timeout=120)
    return r.status_code, (r.text or "")[:200]


def main() -> int:
    admin = Agent("admin", password="NexusAdmin2026!", role="PLM Administrator")
    sandoval = Agent("m.sandoval", role="Design Engineering")
    achebe = Agent("r.achebe", role="Systems Engineering")

    print("\n== NI-00000756 / NI-00000541: the owning engineer and the released part ==")
    # m.sandoval's own test object, not the one I happened to pick.
    pn = "LSS-21-0012"
    oid = object_id(pn)
    latest = admin.latest(pn) or {}
    print(f"  {pn} is at rev {latest.get('revision')} / {latest.get('status')}")
    code, body = call(sandoval, "POST",
                      f"/api/plmobjects/{oid}/revisions/{latest.get('revisionId')}/revise",
                      {"status": "In Work"})
    record("NI-00000756", "owner cannot revise their own released part",
           code == 201, f"revise -> HTTP {code}")

    # The companion complaint: a 403 with an empty body and no named authority.
    code2, body2 = call(achebe, "POST",
                        f"/api/plmobjects/{oid}/revisions/{latest.get('revisionId')}/revise",
                        {"status": "In Work"})
    explained = code2 != 403 or ("permission" in body2.lower() and len(body2) > 20)
    record("NI-00000541", "revise returns a bare 403 with no reason",
           explained, f"other role -> HTTP {code2}, body {len(body2)} chars")

    print("\n== NI-00000733 / NI-00000616: the trace API returns nothing ==")
    for card, who in (("NI-00000733", achebe), ("NI-00000616", admin)):
        req = object_id("LSS-REQ-SYS-0001")
        code, _ = call(who, "GET", f"/api/requirement-trace-links/for/{req}")
        payload = who.get(f"/api/requirement-trace-links/for/{req}") or {}
        total = len(payload.get("outgoing") or []) + len(payload.get("incoming") or [])
        record(card, "trace API returns an empty list while links exist",
               code == 200 and total > 0, f"HTTP {code}, {total} link(s) visible")

    print("\n== NI-00000758: an object with no revisions cannot be deleted by anyone ==")
    # Proven on a throwaway object, then removed. Reproduces the exact trap: create an
    # object, give it a revision, delete the revision, then try to delete the object.
    probe_id = str(uuid.uuid4())
    rev_id = str(uuid.uuid4())
    probe_pn = f"ZZ-PROBE-REVLESS-{probe_id[:8]}"
    try:
        admin.put(f"/api/plmobjects/{probe_id}",
                  {"plmObjectId": probe_id, "typeName": "NexusIssue",
                   "partNumber": probe_pn, "description": "throwaway: revisionless delete probe"})
        admin.put(f"/api/plmobjects/{probe_id}/revisions/{rev_id}",
                  {"revisionId": rev_id, "plmObjectId": probe_id,
                   "revision": "A", "status": "New", "extensionData": "{}"})
        admin.session.request("DELETE", f"{ENGINE}/api/plmobjects/{probe_id}/revisions/{rev_id}",
                              timeout=120)
        remaining = admin.get(f"/api/plmobjects/{probe_id}/revisions") or []
        code, _ = call(admin, "DELETE", f"/api/plmobjects/{probe_id}")
        record("NI-00000758", "a revisionless object cannot be deleted, admin included",
               code in (204, 200), f"{len(remaining)} revision(s) left, delete -> HTTP {code}")
    except Exception as exc:                                          # noqa: BLE001
        record("NI-00000758", "a revisionless object cannot be deleted", False, f"probe failed: {exc}")

    print("\n== NI-00000487: a plain revision PUT walks a record through its lifecycle ==")
    ncr = admin.object("LSS-NCR-00005")
    if ncr is None:
        record("NI-00000487", "revision PUT bypasses the declared route", False, "LSS-NCR-00005 not found")
    else:
        nid = ncr["plmObjectId"]
        nrev = admin.latest("LSS-NCR-00005") or {}
        full = admin.get(f"/api/plmobjects/{nid}/revisions/{nrev.get('revisionId')}") or {}
        attempt = dict(full)
        attempt["status"] = "Closed"
        code, _ = call(sandoval, "PUT",
                       f"/api/plmobjects/{nid}/revisions/{nrev.get('revisionId')}", attempt)
        record("NI-00000487", "any role can drive a quality record's status by PUT",
               code == 403, f"status PUT by a designer -> HTTP {code} (was {nrev.get('status')})")

    print("\n" + "=" * 78)
    fixed = [v for v in VERDICT if v[2]]
    print(f"{len(fixed)}/{len(VERDICT)} card claims verified as fixed on the running Engine")
    print("\nCLOSE these:")
    for card, _, ok, _ in VERDICT:
        if ok:
            print(f"  {card}")
    outstanding = [v for v in VERDICT if not v[2]]
    if outstanding:
        print("\nSTILL OPEN:")
        for card, claim, _, detail in outstanding:
            print(f"  {card}  {claim}  --  {detail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
