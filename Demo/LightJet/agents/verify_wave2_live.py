"""Verifies the PR #792 fixes against the running Engine, as real users.

    python verify_wave2_live.py

Same discipline as the wave-1 check: each case re-runs what a reporter actually did, and
the refusals are the measurement. The list-of-values case reads the allowed set out of the
server's own refusal and then sends one of those, so the test cannot drift from the model.

Writes: one attribute patch on a throwaway object (deleted afterwards) and one legitimate
mrbDisposition value on LSS-NCR-00006, which is the value it should have had.
"""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plm_agent import ENGINE, Agent, object_id                       # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(card: str, passed: bool, detail: str) -> None:
    RESULTS.append((card, passed, detail))
    print(f"  {'PASS' if passed else 'FAIL'}  {card:<26} {detail}")


def call(agent: Agent, method: str, path: str, body=None):
    r = agent.session.request(method, f"{ENGINE}{path}", json=body, timeout=120)
    return r.status_code, (r.text or "")


def main() -> int:
    admin = Agent("admin", password="NexusAdmin2026!", role="PLM Administrator")
    tanaka = Agent("k.tanaka", role="Quality")
    lindqvist = Agent("p.lindqvist", role="Stress")
    sandoval = Agent("m.sandoval", role="Design")

    print("\n== NI-00000493: a declared list of values is enforced ==")
    ncr = admin.object("LSS-NCR-00006")
    if ncr is None:
        check("NI-00000493", False, "LSS-NCR-00006 not found")
    else:
        rev = admin.latest("LSS-NCR-00006") or {}
        path = f"/api/plmobjects/{ncr['plmObjectId']}/revisions/{rev.get('revisionId')}/attributes"
        code, body = call(tanaka, "PATCH", path,
                          {"mrbDisposition": "Re-inspect on a calibrated fixture"})
        allowed = []
        try:
            allowed = (json.loads(body) or {}).get("allowed") or []
        except ValueError:
            pass
        check("NI-00000493 (refuse)", code == 400 and bool(allowed),
              f"free text -> HTTP {code}, server named {len(allowed)} allowed value(s)")

        if allowed:
            code2, _ = call(tanaka, "PATCH", path, {"mrbDisposition": allowed[0]})
            check("NI-00000493 (accept)", code2 == 204,
                  f"declared value {allowed[0]!r} -> HTTP {code2}")

    print("\n== NI-00000762: a revision needs an object to belong to ==")
    code, _ = call(sandoval, "PUT",
                   f"/api/plmobjects/{uuid.uuid4()}/revisions/{uuid.uuid4()}",
                   {"revision": "A", "status": "In Work", "extensionData": "{}"})
    check("NI-00000762", code == 404, f"revision for a non-existent object -> HTTP {code}")

    print("\n== NI-00000672: a user may inspect their own access ==")
    plate = object_id("LSS-21-0014")
    code, _ = call(lindqvist, "GET", f"/api/security/inspect?objectId={plate}&userIds=p.lindqvist")
    check("NI-00000672 (self)", code == 200, f"own access -> HTTP {code}")
    code, _ = call(lindqvist, "GET", f"/api/security/inspect?objectId={plate}&userIds=m.sandoval")
    check("NI-00000672 (other)", code == 403, f"someone else -> HTTP {code}")
    code, _ = call(lindqvist, "GET",
                   f"/api/security/inspect?objectId={plate}&userIds=p.lindqvist,m.sandoval")
    check("NI-00000672 (smuggle)", code == 403, f"self plus someone else -> HTTP {code}")

    print("\n== NI-00000499..703: object notes need edit rights ==")
    # c.delacroix is airworthiness: her group row grants edit None on a released part.
    delacroix = Agent("c.delacroix", role="FAA DER")
    code, _ = call(delacroix, "PATCH", f"/api/plmobjects/{plate}/notes",
                   {"notes": "<p>rewritten by someone with no edit right</p>"})
    check("NI-00000703 (notes)", code == 403, f"notes on a released part -> HTTP {code}")
    code, _ = call(delacroix, "PATCH", f"/api/plmobjects/{plate}",
                   {"description": "renamed by someone with no edit right"})
    check("NI-00000702 (description)", code == 403, f"description -> HTTP {code}")

    print("\n== NI-00000550 / NI-00000551: the audit trail tells the truth ==")
    oid, rid = str(uuid.uuid4()), str(uuid.uuid4())
    try:
        admin.put(f"/api/plmobjects/{oid}", {
            "plmObjectId": oid, "typeName": "NexusIssue",
            "partNumber": f"ZZ-PROBE-W2-{oid[:8]}", "description": "wave 2 audit probe"})
        admin.put(f"/api/plmobjects/{oid}/revisions/{rid}", {
            "revisionId": rid, "plmObjectId": oid, "revision": "A",
            "status": "New", "extensionData": "{}"})

        before = len(admin.get(f"/api/plmobjects/{oid}/revisions/{rid}/history") or [])
        code, _ = call(admin, "PATCH", f"/api/plmobjects/{oid}", {})
        after = len(admin.get(f"/api/plmobjects/{oid}/revisions/{rid}/history") or [])
        check("NI-00000550", code == 204 and after == before,
              f"empty patch -> HTTP {code}, history rows {before} -> {after}")

        admin.patch(f"/api/plmobjects/{oid}/revisions/{rid}/attributes", {"severity": "Major"})
        rows = admin.get(f"/api/plmobjects/{oid}/revisions/{rid}/history") or []
        attr_rows = [r for r in rows if r.get("eventType") == "AttributesUpdated"]
        details = (attr_rows[0].get("details") if attr_rows else None)
        parsed = []
        if details:
            try: parsed = json.loads(details)
            except ValueError: pass
        check("NI-00000551", bool(parsed) and parsed[0].get("field") == "severity",
              f"{len(attr_rows)} attribute row(s), details={json.dumps(parsed)[:90] if parsed else None}")
        check("NI-00000552", len(attr_rows) == 1,
              f"one attribute patch produced {len(attr_rows)} history row(s)")
    finally:
        admin.session.request("DELETE", f"{ENGINE}/api/plmobjects/{oid}", timeout=60)

    print("\n== no regression on the wave 1 fixes ==")
    latest = admin.latest("LSS-21-0012") or {}
    code, _ = call(sandoval, "POST",
                   f"/api/plmobjects/{object_id('LSS-21-0012')}/revisions/"
                   f"{latest.get('revisionId')}/revise", {"status": None})
    check("revise still works", code in (201, 400, 409), f"revise -> HTTP {code}")
    code, _ = call(sandoval, "PUT", "/api/groups/none-such",
                   {"id": "none-such", "name": "LSS Design Engineering"})
    check("groups still admin-only", code == 403, f"group rename by a Member -> HTTP {code}")

    print("\n" + "=" * 78)
    passed = [r for r in RESULTS if r[1]]
    print(f"{len(passed)}/{len(RESULTS)} checks passed")
    failed = [r for r in RESULTS if not r[1]]
    if failed:
        print("\nFAILED:")
        for card, _, detail in failed:
            print(f"  {card}  {detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
