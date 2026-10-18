"""Verifies the ten PR #790 fixes against the RUNNING Engine, as real users.

    python verify_fixes_live.py            # refusals only - writes nothing
    python verify_fixes_live.py --revise   # also takes revision B of LSS-21-0014

Nine role agents found these defects by being refused things they should have been
allowed, and allowed things they should have been refused. This checks both directions
against the deployed binary, because a commit on `next` is not the running Engine.

Every check in the default run expects a REFUSAL, so the script writes nothing: it proves
the holes are closed. The one check that proves the revise fix has to create a revision,
so it is behind --revise and names what it will create before doing it.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plm_agent import ENGINE, Agent, object_id                       # noqa: E402

PLATE = "LSS-21-0014"          # Released titanium seal plate, the Wave 3 subject
DRAWING = "LSS-DWG-21-0014"


class Result:
    def __init__(self) -> None:
        self.rows: list[tuple[str, bool, str]] = []

    def check(self, name: str, passed: bool, detail: str = "") -> None:
        self.rows.append((name, passed, detail))
        print(f"  {'PASS' if passed else 'FAIL'}  {name}" + (f"  - {detail}" if detail else ""))

    def report(self) -> int:
        failed = [r for r in self.rows if not r[1]]
        print(f"\n{len(self.rows) - len(failed)}/{len(self.rows)} checks passed")
        for name, _, detail in failed:
            print(f"  ! {name}  {detail}")
        return 1 if failed else 0


def status_of(agent: Agent, method: str, path: str, body=None) -> int:
    """The HTTP status of a call, without raising.

    The Agent helper turns a refusal into an exception on purpose - an agent working the
    project should not sail past a 403. Here the status code IS the measurement, so this
    goes through the authenticated session directly rather than through the helper.
    """
    response = agent.session.request(
        method, f"{ENGINE}{path}", json=body, timeout=120)
    return response.status_code


def main() -> int:
    r = Result()
    take_revision = "--revise" in sys.argv

    admin = Agent("admin", password="NexusAdmin2026!", role="PLM Administrator")
    # A designer (owning group, may edit In Work) and an approver (airworthiness, may not).
    designer = Agent("m.sandoval", role="Design Engineering")
    approver = Agent("c.delacroix", role="FAA DER")

    plate_id = object_id(PLATE)

    print("\n== The administrative surfaces are administrator-only ==")
    groups = admin.get("/api/groups") or []
    target = next((g for g in groups if g.get("name") == "LSS Stress and Loads"), None)
    if target is None:
        r.check("a group exists to test against", False, "LSS Stress and Loads not found")
    else:
        # Renaming a group you belong to, to a privileged group's name, was total escalation.
        body = dict(target)
        body["name"] = "LSS Design Engineering"
        r.check("PUT /api/groups/{id} refuses a Member",
                status_of(designer, "PUT", f"/api/groups/{target['id']}", body) == 403)
        r.check("DELETE /api/groups/{id} refuses a Member",
                status_of(designer, "DELETE", f"/api/groups/{target['id']}") == 403)

    roles = admin.get("/api/roles") or []
    if roles:
        r.check("PUT /api/roles/{id} refuses a Member",
                status_of(designer, "PUT", f"/api/roles/{roles[0]['id']}", dict(roles[0])) == 403)

    r.check("POST /api/types refuses a Member",
            status_of(designer, "POST", "/api/types",
                      {"typeName": "cstProbeShouldNeverExist", "baseTypeName": "ItemsBase"}) == 403)

    lifecycle = admin.get("/api/lifecycle")
    if lifecycle:
        r.check("PUT /api/lifecycle refuses a Member",
                status_of(designer, "PUT", "/api/lifecycle", lifecycle) == 403)

    print("\n== Ownership cannot be taken ==")
    r.check("transfer-owner refuses a non-owner with no edit rights",
            status_of(approver, "POST",
                      f"/api/plmobjects/{plate_id}/revisions/"
                      f"{(admin.latest(PLATE) or {}).get('revisionId')}/transfer-owner",
                      {"newOwnerUserId": "c.delacroix"}) == 403)

    print("\n== The revision create path is checked ==")
    import uuid
    invented = str(uuid.uuid4())
    r.check("PUT a brand-new revision directly in Released is refused",
            status_of(designer, "PUT", f"/api/plmobjects/{plate_id}/revisions/{invented}",
                      {"revisionId": invented, "plmObjectId": plate_id,
                       "revision": "Z", "status": "Released", "extensionData": "{}"}) == 403)

    print("\n== Preferences are the caller's own ==")
    r.check("another user's preferences are refused",
            status_of(designer, "GET", "/api/user-preferences/c.delacroix/folder-columns") == 403)

    print("\n== Trace links reach released endpoints ==")
    traces = designer.get(f"/api/requirement-trace-links/for/{plate_id}")
    reachable = traces is not None
    r.check("the trace tree loads for a released part as a non-owner", reachable,
            "" if reachable else "still refused or empty")

    print("\n== Revise is judged by the landing state ==")
    latest = admin.latest(PLATE) or {}
    print(f"  {PLATE} is at rev {latest.get('revision')} / {latest.get('status')}")
    r.check("airworthiness may NOT revise (approves, does not author)",
            status_of(approver, "POST",
                      f"/api/plmobjects/{plate_id}/revisions/{latest.get('revisionId')}/revise",
                      {"status": "In Work"}) == 403)

    if not take_revision:
        print("\n  Design engineering's revise is the one check that WRITES.")
        print(f"  Re-run with --revise to take revision B of {PLATE} and {DRAWING}.")
    else:
        print(f"\n  Creating the next revision of {PLATE} as m.sandoval...")
        code = status_of(designer, "POST",
                         f"/api/plmobjects/{plate_id}/revisions/{latest.get('revisionId')}/revise",
                         {"status": "In Work"})
        r.check("design engineering CAN revise a released part", code == 201,
                f"HTTP {code}")
        after = admin.latest(PLATE) or {}
        r.check("the new revision exists and is In Work",
                after.get("revision") != latest.get("revision")
                and after.get("status") == "In Work",
                f"now rev {after.get('revision')} / {after.get('status')}")

    return r.report()


if __name__ == "__main__":
    sys.exit(main())
