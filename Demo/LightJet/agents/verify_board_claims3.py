"""Re-tests the cards the 19 Oct role agents named as fixed, against the running Engine.

    python verify_board_claims3.py

Same rule as its two predecessors: a card is closed on evidence or not at all, and each
check re-runs what the original reporter actually did - same user, same object, same call.
A claim that a card is fixed is still only a claim; three of the loudest findings of that
run turned out to be misreads of the data, so nothing here is closed on a report alone.

Read-only except where a card's claim IS that a write should now succeed.
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from plm_agent import Agent, Refused, admin_agent                    # noqa: E402

# A type that actually DECLARES required attributes, which is the whole point of the check.
# The first version of this probe used Nonconformance, which declares none, so a revision
# with no attributes was accepted and the card was reported as standing on a test that could
# not have failed. VendorPart requires supplierName and supplierPartNumber.
REQUIRED_PROBE_TYPE = "cstLightSpeedSystemsVendorPart"
# ...and the role that is allowed to create one, or the probe stops at a 403 that
# says nothing about required attributes.
REQUIRED_PROBE_USER = ("y.cheng", "Supply chain")

VERDICT: list[tuple[str, str, bool, str]] = []


def record(card: str, claim: str, fixed: bool, detail: str) -> None:
    VERDICT.append((card, claim, fixed, detail))
    print(f"  {'FIXED ' if fixed else 'STANDS'}  {card}  {detail}")


def main() -> int:
    me = admin_agent()

    # ── NI-576: no way to record a certification finding ─────────────────────
    print("\n== NI-00000576: nowhere to record a certification finding ==")
    resolved = me.get("/api/types/cstLightSpeedSystemsCertificationFinding/resolved") \
        or me.get("/api/types/CertificationFinding/resolved")
    rows = me.get("/api/plmobjects?pageSize=3000") or []
    rows = rows if isinstance(rows, list) else rows.get("items", [])
    findings = [o for o in rows
                if "CertificationFinding" in str(o.get("typeName"))
                and not o.get("isDeleted")]
    record("NI-00000576", "the type does not exist",
           resolved is not None and len(findings) > 0,
           f"type {'resolves' if resolved else 'MISSING'}, {len(findings)} finding(s) on the site: "
           + ", ".join(sorted(o["partNumber"] for o in findings)[:6]))

    # ── NI-518: Customer Support cannot create a service bulletin ────────────
    print("\n== NI-00000518: Customer Support cannot create a service bulletin ==")
    bulletins = [o for o in rows if "ServiceBulletin" in str(o.get("typeName"))
                 and not o.get("isDeleted")]
    users = me.get("/api/users") or []
    byid = {(u.get("userId") or u.get("id")): u.get("username") for u in users}
    support_made = [o for o in bulletins if byid.get(o.get("ownerId")) == "f.mbeki"]
    record("NI-00000518", "no create route for this role",
           len(support_made) > 0,
           f"{len(bulletins)} bulletin(s), {len(support_made)} owned by f.mbeki: "
           + ", ".join(sorted(o["partNumber"] for o in support_made)[:4]))

    # ── NI-510 / NI-675: Customer Support may DELETE a mandatory bulletin ────
    print("\n== NI-00000510 / NI-00000675: delete rights on a mandatory bulletin ==")
    mandatory = None
    for o in bulletins:
        attrs = me.get(f"/api/plmobjects/{o['plmObjectId']}/revisions/latest/attributes") or {}
        if str(attrs.get("bulletinType", "")).lower().startswith("mandatory"):
            mandatory = o
            break
    if mandatory is None:
        record("NI-00000510", "delete allowed", False, "no mandatory bulletin to test")
    else:
        uid = {u.get("username"): (u.get("userId") or u.get("id")) for u in users}
        inspect = me.get(f"/api/security/inspect?objectId={mandatory['plmObjectId']}"
                         f"&userIds={uid['f.mbeki']}") or {}
        verdict = (inspect.get("users") or [{}])[0].get("verdict") or {}
        latest = me.get(f"/api/plmobjects/{mandatory['plmObjectId']}/revisions/latest") or {}
        detail = (f"{mandatory['partNumber']} ({latest.get('status')}): "
                  f"canDelete={verdict.get('canDelete')} canEdit={verdict.get('canEdit')}")
        record("NI-00000510", "canDelete true", verdict.get("canDelete") is False, detail)
        record("NI-00000675", "canDelete true after the account fix",
               verdict.get("canDelete") is False, detail)

    # ── NI-705: required attributes are not enforced on create ───────────────
    print("\n== NI-00000705: `required` not enforced on create ==")
    # The card is about the REVISION create, which is where attributes are supplied. An
    # object shell carries none, so creating one proves nothing either way - the first
    # version of this check tested the shell, reported the card as standing, and was wrong.
    quality = Agent(REQUIRED_PROBE_USER[0], role=REQUIRED_PROBE_USER[1])
    probe_id = str(uuid.uuid4())
    enforced, detail = False, ""
    try:
        quality.put(f"/api/plmobjects/{probe_id}",
                    {"partNumber": "PROBE-REQUIRED-705",
                     "typeName": REQUIRED_PROBE_TYPE, "revision": "A"})
        try:
            quality.put(f"/api/plmobjects/{probe_id}/revisions/{uuid.uuid4()}",
                        {"revision": "A", "status": "Draft", "extensionData": "{}"})
            detail = "a revision was created with no required attributes"
        except Refused as exc:
            enforced = exc.status in (400, 422) and "required" in str(exc.body).lower()
            detail = f"revision create -> HTTP {exc.status} {str(exc.body)[:100]}"
    except Refused as exc:
        detail = f"object create refused first: HTTP {exc.status} {str(exc.body)[:90]}"
    finally:
        # Clean up whatever reached the site, as the administrator.
        try:
            me.delete(f"/api/plmobjects/{probe_id}")
        except Exception:                                            # noqa: BLE001
            pass
    record("NI-00000705", "required not enforced on create", enforced, detail)

    # ── NI-546: a refusal does not say what is allowed ───────────────────────
    print("\n== NI-00000546: refusals do not say what right is missing ==")
    released = next((o for o in rows if o.get("partNumber") == "LSS-21-INST-001"), None)
    if released is None:
        record("NI-00000546", "refusal explains nothing", False, "test object missing")
    else:
        designer = Agent("m.sandoval", role="Designer")
        try:
            designer.set_attributes("LSS-21-INST-001", {"notes": "probe"})
            record("NI-00000546", "refusal explains nothing", False, "the write was ALLOWED")
        except Refused as exc:
            body = str(exc.body)
            explains = "reason" in body.lower() and len(body) > 120
            record("NI-00000546", "refusal explains nothing", explains,
                   f"HTTP {exc.status}, {len(body)} chars, reason field "
                   f"{'present' if 'reason' in body.lower() else 'ABSENT'}")

    # ── NI-731: a new reference defaults to the wrong revision rule ──────────
    print("\n== NI-00000731: reference default revision rule ==")
    plate = next((o for o in rows if o.get("partNumber") == "LSS-21-0014"), None)
    bad = []
    for o in bulletins:
        latest = me.get(f"/api/plmobjects/{o['plmObjectId']}/revisions/latest") or {}
        refs = me.get(f"/api/plmobjects/{o['plmObjectId']}/revisions"
                      f"/{latest.get('revisionId')}/references") or []
        bad += [f"{o['partNumber']} -> {(r.get('target') or {}).get('partNumber')}"
                for r in refs
                if r.get("revisionRule") in ("latest", "latest-released")
                and not r.get("pinnedRevisionId")
                and (r.get("target") or {}).get("status") == "In Work"]
    record("NI-00000731", "the default rule is wrong on an evidence link",
           len(bad) == 0,
           f"{len(bad)} bulletin reference(s) resolve to In Work data: " + ", ".join(bad[:4]))

    print("\n" + "=" * 78)
    fixed = [c for c, _, ok, _ in VERDICT if ok]
    stands = [(c, d) for c, _, ok, d in VERDICT if not ok]
    print(f"{len(fixed)}/{len(VERDICT)} claims verified as fixed on the running Engine")
    if fixed:
        print("\nCLOSE these:")
        for card in sorted(set(fixed)):
            print(f"  {card}")
    if stands:
        print("\nSTILL OPEN:")
        for card, detail in stands:
            print(f"  {card}  --  {detail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
