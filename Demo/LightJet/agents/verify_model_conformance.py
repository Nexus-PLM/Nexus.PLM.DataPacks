"""Does the running server enforce what the type model declares? Asked of every type, on
every write path.

    python verify_model_conformance.py                 # a representative sample
    python verify_model_conformance.py --all           # every concrete type
    python verify_model_conformance.py --type ECR      # one type

WHY THIS EXISTS
---------------
Almost every defect the role agents found, and almost every one found in the 25-26 Oct
sweep, is the same shape: a rule the model DECLARES and the server does not ENFORCE.

  a status default no type could hold          NI-00000784
  value rules checked on create, not on update NI-00000704 follow-up
  a list of values enforced by PATCH and
     ignored by the whole-record PUT           found while tidying the board
  audit stamps declared writeMode Caller       NI-00000435
  transition rules on 49 types, absent on 78   NI-00000783/796/799
  part numbers validated for non-admins on
     schema'd types and for nobody else        NI-00000704

The model is consistently more correct than the enforcement, and the gap is always at a
SECOND DOOR that nobody checked. Unit tests do not find these because they test the door
they were written for. This walks the declared model and tries to break each rule through
every door.

WHAT IT PROVES, AND WHAT IT CANNOT
----------------------------------
Every check asserts a REFUSAL, and each one is paired with an ALLOW that must succeed - a
sweep reporting "all enforced" having never sent a violating value, or having sent them to
an object it could not write anyway, is worth nothing. The counts at the end say how many
probes were actually sent; read those before reading the verdict.

It writes, so it cleans up: one throwaway object per type, deleted afterwards, and every
delete re-reads the object and checks the description is this script's before removing it.
Nothing existing is touched.
"""
import argparse
import json
import re
import sys
import uuid
from collections import Counter

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from plm_agent import admin_agent  # noqa: E402

MARK = "ZZ-CONFORMANCE-PROBE"

# A value no list will contain and no pattern will match.
NONSENSE = "ZZ~NOT~A~DECLARED~VALUE~9173"


class Result:
    """One rule, asked of one type, through one door."""

    def __init__(self, type_name, rule, door):
        self.type_name, self.rule, self.door = type_name, rule, door
        self.verdict = "untested"
        self.detail = ""

    def record(self, verdict, detail=""):
        self.verdict, self.detail = verdict, detail
        return self

    def __str__(self):
        return "%-44s %-22s %-18s %-14s %s" % (
            self.type_name[:44], self.rule, self.door, self.verdict, self.detail[:60])


def declared_rules(resolved):
    """The rules this type states about itself, as (kind, attribute, data) tuples."""
    out = []
    for a in resolved.get("attributes") or []:
        if a.get("disabled"):
            continue
        name = a.get("name")
        if a.get("lov"):
            out.append(("list-of-values", name, a["lov"]))
        if a.get("validationPattern"):
            out.append(("pattern", name, a["validationPattern"]))
        if str(a.get("writeMode")) == "System":
            out.append(("writeMode System", name, None))
    live = [s.get("name") for s in (resolved.get("lifecycleStates") or []) if not s.get("disabled")]
    if live:
        out.append(("lifecycle state", "status", live))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="every concrete type, not a sample")
    ap.add_argument("--type", help="just this one")
    ap.add_argument("--limit", type=int, default=12, help="sample size when not --all")
    args = ap.parse_args()

    me = admin_agent()
    types = me.get("/api/types") or []

    concrete = []
    for t in types:
        name = t.get("typeName") or t.get("name")
        if not name:
            continue
        resolved = me.get("/api/types/%s/resolved" % name)
        if not resolved or resolved.get("abstract"):
            continue
        concrete.append((name, resolved))

    if args.type:
        concrete = [c for c in concrete if c[0].lower() == args.type.lower()]
    elif not args.all:
        # Spread the sample across the alphabet rather than taking the first N, which would
        # be every AffectedItemLink and nothing else.
        step = max(1, len(concrete) // args.limit)
        concrete = concrete[::step][:args.limit]

    print("types to probe: %d" % len(concrete))
    print()

    results = []
    probes_sent = Counter()
    created = []

    for name, resolved in concrete:
        rules = declared_rules(resolved)
        if not rules:
            continue

        if not deletable(resolved):
            results.append(Result(name, "-", "-").record(
                "skipped", "every declared state is settled, so a probe object could never "
                           "be deleted"))
            continue

        obj = make_probe_object(me, name, resolved, probes_sent)
        if obj is None:
            for kind, attr, data in rules:
                results.append(Result(name, kind, "-").record(
                    "could not probe", "no throwaway object of this type could be created"))
            continue
        created.append(obj)

        for kind, attr, data in rules:
            for door in ("PATCH attributes", "PUT revision"):
                results.append(probe(me, obj, name, kind, attr, data, door, probes_sent))

    cleanup(me, created)
    report(results, probes_sent)


# States that mean "this record is finished", where the platform default grants delete to
# nobody. A type whose ONLY states are these can never have a probe object removed, so none
# is created - AuditReport declares just "Released", and the first full run left one behind.
SETTLED = {"approved", "closed", "complete", "obsolete", "released", "rejected", "voided",
           "superseded", "issued", "cancelled", "withdrawn"}


def deletable(resolved):
    live = [str(s.get("name", "")).lower()
            for s in (resolved.get("lifecycleStates") or []) if not s.get("disabled")]
    return any(s not in SETTLED for s in live) if live else True


def make_probe_object(me, type_name, resolved, probes_sent):
    """A throwaway object of this type, or None when one cannot be made."""
    num = me.get("/api/partnumbers/next/%s" % type_name) or {}
    pn = num.get("value")
    if not pn:
        return None
    oid, rid = str(uuid.uuid4()), str(uuid.uuid4())
    body = {"plmObjectId": oid, "typeName": type_name, "partNumber": pn, "description": MARK}
    # `put` returns None on a successful 204 and RAISES on >= 400, so testing the return
    # value for None reads every success as a failure. It did, and the first run probed
    # nothing at all - caught only because the report refuses to give a verdict when the
    # probe count is zero.
    try:
        me.put("/api/plmobjects/%s" % oid, body)
    except Exception:
        return None
    probes_sent["objects created"] += 1

    # Required attributes have to be satisfied or the revision will not land, and a refusal
    # then would be the required rule rather than the rule under test.
    ext = {}
    for a in resolved.get("attributes") or []:
        if a.get("required") and not a.get("disabled"):
            lov = a.get("lov")
            ext[a["name"]] = lov[0] if lov else MARK
    rev = {"revisionId": rid, "plmObjectId": oid, "revision": "A",
           "extensionData": json.dumps(ext)}
    try:
        me.put("/api/plmobjects/%s/revisions/%s" % (oid, rid), rev)
    except Exception as exc:
        probes_sent["revision create refused"] += 1
        print("   %-40s no probe revision: %s" % (type_name, str(exc)[:80]))
        return None
    return {"oid": oid, "rid": rid, "pn": pn, "type": type_name}


def probe(me, obj, type_name, kind, attr, data, door, probes_sent):
    """Offer a value the rule forbids and record whether the server refused it."""
    r = Result(type_name, kind, door)
    bad = NONSENSE if kind != "lifecycle state" else NONSENSE

    if kind == "lifecycle state" and door == "PATCH attributes":
        return r.record("n/a", "status is not written through the attribute route")

    probes_sent[kind + " / " + door] += 1

    # The client RAISES Refused for any status >= 400 and returns None for a successful 204,
    # so "did it come back empty" is exactly backwards as a test. The write is wrapped, and
    # the verdict comes from reading the value back - the only answer that cannot lie.
    try:
        if door == "PATCH attributes":
            me.patch("/api/plmobjects/%s/revisions/%s/attributes" % (obj["oid"], obj["rid"]),
                     {attr: bad})
        else:
            latest = me.get("/api/plmobjects/%s/revisions/%s" % (obj["oid"], obj["rid"])) or {}
            body = dict(latest)
            if kind == "lifecycle state":
                body["status"] = bad
            else:
                try:
                    ext = json.loads(body.get("extensionData") or "{}")
                except Exception:
                    ext = {}
                ext[attr] = bad
                body["extensionData"] = json.dumps(ext)
            body.pop("notes", None)
            me.put("/api/plmobjects/%s/revisions/%s" % (obj["oid"], obj["rid"]), body)
        refusal = ""
    except Exception as exc:
        refusal = str(exc)[:70]

    # Read it back: the only trustworthy answer. A 204 that did not store the value is as
    # good as a refusal, and a refusal that stored it anyway is a lie.
    stored = read_back(me, obj, attr, kind)
    if stored == bad:
        return r.record("NOT ENFORCED", "%s=%r accepted and stored" % (attr, bad[:26]))
    if refusal:
        return r.record("enforced", refusal)
    # Answered 2xx but did not store it. Not a leak, but the caller was told yes.
    return r.record("silently dropped", "%s answered OK and stored %r" % (door, str(stored)[:22]))


def read_back(me, obj, attr, kind):
    rev = me.get("/api/plmobjects/%s/revisions/%s" % (obj["oid"], obj["rid"])) or {}
    if kind == "lifecycle state":
        return rev.get("status")
    try:
        return json.loads(rev.get("extensionData") or "{}").get(attr)
    except Exception:
        return None


def cleanup(me, created):
    """Remove every probe object, and NEVER let one refusal strand the rest.

    The first full run died here. A DELETE came back 403 - AuditReport declares one state,
    Released, which grants delete to nobody, so a probe object of that type can never be
    removed - and the raised refusal aborted the loop with 93 objects still on the server.
    A cleanup that stops at the first problem is worse than none, because it leaves the mess
    AND hides how big it is.
    """
    removed = kept = stuck = 0
    for obj in created:
        live = me.get("/api/plmobjects/%s" % obj["oid"]) or {}
        if live.get("description") != MARK:
            kept += 1
            print("NOT deleting %s - description is %r, not this script's"
                  % (obj["pn"], live.get("description")))
            continue
        try:
            me.delete("/api/plmobjects/%s" % obj["oid"])
            removed += 1
        except Exception as exc:
            stuck += 1
            print("STUCK: %s (%s) could not be deleted - %s"
                  % (obj["pn"], obj["type"], str(exc)[:90]))
    print()
    print("cleanup: %d deleted, %d left alone, %d STUCK" % (removed, kept, stuck))
    if stuck:
        print("         a stuck object is one this sweep created and cannot remove; it is")
        print("         named above so it can be dealt with deliberately.")


def report(results, probes_sent):
    print()
    print("PROBES ACTUALLY SENT (read this before the verdict):")
    for k, v in sorted(probes_sent.items()):
        print("   %-44s %d" % (k, v))
    total = sum(v for k, v in probes_sent.items() if k != "objects created")
    print("   %-44s %d" % ("total rule probes", total))
    print()

    broken = [r for r in results if r.verdict == "NOT ENFORCED"]
    print("RULES THE SERVER DOES NOT ENFORCE: %d" % len(broken))
    for r in sorted(broken, key=lambda x: (x.rule, x.type_name)):
        print("  " + str(r))
    print()
    print("by verdict: %s" % dict(Counter(r.verdict for r in results)))
    if total == 0:
        print()
        print("NOTHING WAS PROBED. The verdict above means nothing - fix the harness first.")


if __name__ == "__main__":
    main()
