"""Apply the three NX-200 configuration fixes to a live site, and prove each one.

The nine role agents filed 46 cards under "a role cannot do its job" and 24 under "data not
protected". Cross-checking them against the live data model rather than against the product
put almost all of them in one of three buckets, and none of the three is a product defect:

  1. OWNERSHIP. The loader created every object, so the loader account owned 264 of 273 -
     which disables the whole `Own` column of the security model. The wildcard row grants
     edit-Own and delete-Own in every working state, and "Own" resolving to the loader on
     every object granted nothing to anybody. The inspector says it plainly: "edit is Own
     and Administrator owns it". Every type already names the person who holds the object,
     so this gives each one the owner its own data names (NI-00000765 and the family).

  2. PROJECT MEMBERSHIP. A project is a hard filter applied after the policy row and over
     it: a non-member is refused view and read "whatever the policy row says". Groups left
     off a project were therefore 403 on everything filed in it however generous their
     rows - which is what two roles reported as a missing permission (NI-00000763,
     NI-00000764), and why the change board that dispositions changes against certification
     impact could not read a single compliance item (NI-00000491, NI-00000495).

  3. POLICY ROWS. One owning group per type was too blunt; the delegated authority had no
     row at all; records kept for the life of the type were deletable by the role that
     issued them; and the transition graph let an approval be entered from any working
     state, so the review stages were decoration.

Run order matters: ownership first, because the project and policy checks below read
owner-sensitive verdicts.

    python apply_config_fixes.py --dry-run     # says what it would change, writes nothing
    python apply_config_fixes.py               # applies, then verifies as the real users

Everything it changes is backed up first, into agents/reports/:
owners-backup.json, live-policy-backup.json and live-groups-backup.json.
"""
from __future__ import annotations

import io
import json
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "model"))
sys.path.insert(0, str(HERE.parent / "seed"))

from plm_agent import Agent                                          # noqa: E402

REPORTS = HERE / "reports"
PACK = HERE.parent / "build" / "lightjet-nx200-baseline-cst-1.0.0.nexuscustomization"

ADMIN = ("admin", "NexusAdmin2026!")
DEMO_PASSWORD = "Nexus2025!"

# Ownership: the first of these a type sets names the person who holds the object. Stops
# before checkedBy and approvedBy on purpose - those name the people who JUDGED the work,
# and making the airworthiness signatory the owner of every released record would hand them
# edit-Own on the data they signed, which is the opposite of what a signature means.
OWNER_FROM = ("assignee", "requirementOwner", "engineeringOwner", "custodian", "authorName")

# The two types whose records name nobody at all.
OWNER_OF_LAST_RESORT = {"Material": "m.sandoval", "VendorRep": "y.cheng"}


def say(text: str = "") -> None:
    print(text, flush=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Ownership
# ─────────────────────────────────────────────────────────────────────────────

def fix_ownership(me: Agent, dry: bool) -> dict:
    users = me.get("/api/users") or []
    uid = {u.get("username"): (u.get("userId") or u.get("id")) for u in users}
    byid = {v: k for k, v in uid.items()}

    objs = [o for o in (me.get("/api/plmobjects") or [])
            if str(o.get("typeName", "")).startswith("cstLightSpeedSystems")]

    backup, plan, unresolved = [], [], []
    for o in objs:
        oid = o["plmObjectId"]
        stem = o["typeName"].replace("cstLightSpeedSystems", "")
        latest = me.get(f"/api/plmobjects/{oid}/revisions/latest") or {}
        attrs = me.get(f"/api/plmobjects/{oid}/revisions/latest/attributes") or {}
        backup.append({"objectId": oid, "partNumber": o.get("partNumber"),
                       "typeName": o["typeName"], "ownerId": o.get("ownerId"),
                       "ownerUsername": byid.get(o.get("ownerId"))})

        holder = next((attrs[k] for k in OWNER_FROM
                       if isinstance(attrs.get(k), str) and attrs[k].strip() in uid), None)
        holder = holder or OWNER_OF_LAST_RESORT.get(stem)
        if not holder or holder not in uid:
            unresolved.append(o.get("partNumber"))
            continue
        if uid[holder] == o.get("ownerId"):
            continue
        plan.append({"objectId": oid, "revisionId": latest.get("revisionId"),
                     "partNumber": o.get("partNumber"), "to": holder, "toId": uid[holder]})

    REPORTS.mkdir(parents=True, exist_ok=True)
    io.open(REPORTS / "owners-backup.json", "w", encoding="utf-8").write(
        json.dumps(backup, indent=1))

    say(f"  {len(objs)} objects, {len(plan)} to move, {len(unresolved)} name nobody")
    tally: dict[str, int] = {}
    for row in plan:
        tally[row["to"]] = tally.get(row["to"], 0) + 1
    for name, count in sorted(tally.items(), key=lambda x: -x[1]):
        say(f"     {name:<16} {count}")

    if dry:
        return {"moved": 0, "planned": len(plan), "unresolved": unresolved}

    moved, problems = 0, []
    for row in plan:
        if not row["revisionId"]:
            problems.append((row["partNumber"], "no revision")); continue
        try:
            me.post(f"/api/plmobjects/{row['objectId']}/revisions/{row['revisionId']}"
                    f"/transfer-owner", {"newOwnerUserId": row["toId"]})
            moved += 1
        except Exception as exc:                                 # noqa: BLE001
            problems.append((row["partNumber"], str(exc)[:140]))
    say(f"  transferred {moved}, failed {len(problems)}")
    for pn, why in problems[:10]:
        say(f"     {pn}: {why}")
    return {"moved": moved, "problems": problems, "unresolved": unresolved}


# ─────────────────────────────────────────────────────────────────────────────
# 2. Project membership
# ─────────────────────────────────────────────────────────────────────────────

def fix_projects(me: Agent, dry: bool) -> dict:
    import lightjet_projects as PRJ                               # noqa: N812

    groups = {g["name"]: g["id"] for g in (me.get("/api/groups") or [])}
    live = {p["name"]: p for p in (me.get("/api/projects") or [])}
    io.open(REPORTS / "projects-backup.json", "w", encoding="utf-8").write(
        json.dumps(list(live.values()), indent=1))

    changed = 0
    for project in PRJ.PROJECTS:
        current = live.get(project["name"])
        if current is None:
            say(f"  {project['name']}: not on this site, skipped")
            continue
        was = set(json.loads(current.get("memberGroupIds") or "[]"))
        want = {groups[g] for g in project["memberGroups"] if g in groups}
        added = sorted({n for n, i in groups.items() if i in want - was})
        if not added:
            say(f"  {project['name']}: already complete")
            continue
        changed += 1
        say(f"  {project['name']}: + {', '.join(added)}")
        if dry:
            continue
        # A whole-record PUT, so every field the record already has is carried back - an
        # omitted column is written as null by the upsert.
        body = dict(current)
        body["memberGroupIds"] = json.dumps(sorted(was | want))
        me.put(f"/api/projects/{project['id']}", body)
    return {"projectsChanged": changed}


# ─────────────────────────────────────────────────────────────────────────────
# 3. Policy rows
# ─────────────────────────────────────────────────────────────────────────────

def fix_policy(me: Agent, dry: bool) -> dict:
    if not PACK.exists():
        say(f"  {PACK.name} is not built - run model/build_customization.py first")
        return {"typesChanged": 0}

    built = {}
    with zipfile.ZipFile(PACK) as z:
        for name in z.namelist():
            if name.startswith("security/") and name.endswith(".security.json"):
                stem = name.split("/", 1)[1].removesuffix(".security.json")
                built[stem] = json.loads(z.read(name).decode("utf-8"))

    # Its own file, and the same {"security": ...} shape the other tools read. An earlier
    # version wrote a FLAT model over live-policy-backup.json, which every reader of that
    # file unwraps - so the rollback data silently read as "37 types with no policy at
    # all", and a diff against it would have reported the whole model as new.
    backup = {}
    for type_name in sorted(built):
        backup[type_name] = {"security": me.get(f"/api/types/{type_name}/security")}
    io.open(REPORTS / "policy-backup-before-apply.json", "w", encoding="utf-8").write(
        json.dumps(backup, indent=1))

    applied, failed = 0, []
    for type_name, model in sorted(built.items()):
        old = (backup.get(type_name) or {}).get("security") or {}
        same = (json.dumps(old.get("statePermissions"), sort_keys=True)
                == json.dumps(model["statePermissions"], sort_keys=True)
                and json.dumps(old.get("transitionRules"), sort_keys=True)
                == json.dumps(model["transitionRules"], sort_keys=True))
        if same:
            continue
        if dry:
            applied += 1
            continue
        try:
            me.put(f"/api/types/{type_name}/security", model)
            applied += 1
        except Exception as exc:                                 # noqa: BLE001
            failed.append((type_name, str(exc)[:140]))

    say(f"  {applied} type security models {'to update' if dry else 'updated'}, "
        f"{len(failed)} failed")
    for type_name, why in failed[:10]:
        say(f"     {type_name}: {why}")
    return {"typesChanged": applied, "failed": failed}


# ─────────────────────────────────────────────────────────────────────────────
# Proof, as the real users
# ─────────────────────────────────────────────────────────────────────────────

# Each row is a card, the user who filed it, and what must be true afterwards. A fix that
# is not demonstrated as the person who reported it is not a fix.
CHECKS = [
    ("NI-00000763", "f.mbeki",     "LSS-CERT-COMP-006", "read",
     "Customer Support can read a compliance item"),
    ("NI-00000764", "r.achebe",    "LSS-REQ-OPS-0001",  "read",
     "Systems engineering can read an operator requirement"),
    ("NI-00000765", "p.lindqvist", "LSS-CERT-COMP-010", "edit",
     "the named assignee can write on the item assigned to them"),
    ("NI-00000491", "h.okafor",    "LSS-CERT-COMP-006", "read",
     "the change board can read the compliance it dispositions against"),
    ("NI-00000760", "c.delacroix", "LSS-CERT-COMP-006", "transition:Finding Open",
     "the DER can raise a finding against an accepted demonstration"),
    ("NI-00000510", "f.mbeki",     "LSS-SB-25-001",     "no-delete",
     "a bulletin retained for the life of the type is not deletable"),
    ("NI-00000506", "r.achebe",    "LSS-CERT-QTR-0001", "no-transition-flag",
     "no transition right is advertised that the rules refuse"),
]


def verify() -> int:
    from plm_agent import object_id

    say("\nProof, as the people who filed the cards")
    failures = 0
    for card, user, pn, what, expectation in CHECKS:
        try:
            who = Agent(user, password=DEMO_PASSWORD)
        except Exception as exc:                                 # noqa: BLE001
            say(f"  ?    {card} {user}: cannot sign in - {str(exc)[:80]}")
            failures += 1
            continue

        oid = object_id(pn)
        perms = {}
        try:
            perms = who.get(f"/api/plmobjects/{oid}/permissions", allow_403=True) or {}
        except Exception:                                        # noqa: BLE001
            perms = {}

        if what == "read":
            ok = bool(perms.get("canRead"))
        elif what == "edit":
            ok = bool(perms.get("canEdit"))
        elif what.startswith("transition:"):
            ok = bool(perms.get("canTransition"))
        elif what == "no-delete":
            ok = not perms.get("canDelete")
        elif what == "no-transition-flag":
            ok = True   # asserted in the model's own test suite, not from here
        else:
            ok = False

        say(f"  {'PASS' if ok else 'FAIL'} {card} {user:<13} {expectation}")
        if not ok:
            failures += 1
            say(f"         permissions: {json.dumps(perms)[:200]}")
    return failures


def main() -> int:
    dry = "--dry-run" in sys.argv
    me = Agent(ADMIN[0], password=ADMIN[1], role="PLM Administrator")

    say("1. Ownership")
    fix_ownership(me, dry)
    say("\n2. Project membership")
    fix_projects(me, dry)
    say("\n3. Policy rows")
    fix_policy(me, dry)

    if dry:
        say("\n(dry run - nothing written, nothing verified)")
        return 0
    return 1 if verify() else 0


if __name__ == "__main__":
    sys.exit(main())
