"""Verifies the wave-4 fixes against the RUNNING Engine, as real users.

    python verify_wave4_live.py

A commit on `next` is not the running binary, and a board card that says "fixed" on the
strength of a merge is a rumour. Each check below names the card it settles and asserts the
deployed server's actual behaviour.

**Every check expects a refusal or a read, so this script writes nothing.** That is
deliberate: the wave-4 fixes are almost all "the server advertised a rule and did not apply
it", so proving them means offering a value the rule forbids and being told no. A test that
had to succeed in writing would leave edits in the demo dataset days before the demo.

The one exception is the attribute-contract group, which needs an object the actor may
genuinely edit - otherwise a 403 would be mistaken for the contract refusing the value.
LSS-21-0014 revision B is In Work and m.sandoval's group holds edit-Any on it, confirmed
through /api/security/inspect, so a 400 from these probes is the contract and nothing else.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plm_agent import ENGINE, Agent, Refused                           # noqa: E402

PLATE = "LSS-21-0014"          # In Work rev B, editable by LSS Design Engineering


class Checks:
    """Collects a pass/fail line per card so the run reads as a report, not a traceback."""

    def __init__(self) -> None:
        self.rows: list[tuple[str, str, bool, str]] = []

    def record(self, cards: str, what: str, passed: bool, detail: str) -> None:
        self.rows.append((cards, what, passed, detail))
        print(f"  {'PASS' if passed else 'FAIL'}  {cards:26} {what}")
        if not passed:
            print(f"         {detail}")

    def refused(self, cards: str, what: str, call, expect: str) -> None:
        """Asserts the server refuses, and that its reason contains `expect`."""
        try:
            result = call()
        except Refused as exc:
            body = str(exc.body)
            self.record(cards, what, expect.lower() in body.lower(),
                        f"refused {exc.status} but said: {body[:220]}")
            return
        self.record(cards, what, False, f"NOT refused - returned {str(result)[:220]}")

    def summary(self) -> int:
        ok = sum(1 for *_, p, _ in self.rows if p)
        print(f"\n{ok}/{len(self.rows)} checks passed")
        bad = [(c, w, d) for c, w, p, d in self.rows if not p]
        if bad:
            print("\nnot proven:")
            for c, w, d in bad:
                print(f"  {c:26} {w}\n      {d}")
        return 0 if not bad else 1


def main() -> int:
    print(f"Engine: {ENGINE}\n")
    c = Checks()
    admin = Agent("admin", password="NexusAdmin2026!", role="PLM Administrator")
    designer = Agent("m.sandoval")

    plate = designer.object(PLATE)
    rev = designer.latest(PLATE)
    attrs_path = f"/api/plmobjects/{plate['plmObjectId']}/revisions/{rev['revisionId']}/attributes"

    print("-- The declared attribute contract, now enforced on the edit path --")

    # NI-00000113 (* a card from before this exercise, kept because the check is the same
    # rule): a name that is not an attribute of the type used to be stored anyway, so a
    # typo created a second invisible field nothing could read back.
    c.refused("NI-00000113*", "an undeclared attribute name is refused",
              lambda: designer.patch(attrs_path, {"notAnAttributeAtAll": "x"}),
              "notAnAttributeAtAll")

    # NI-00000513: a Number field took a sentence and stored it as text, so every later
    # rollup, comparison and sort treated "about 1.4 kg" as nothing at all.
    c.refused("NI-00000513", "a sentence in a Number attribute is refused",
              lambda: designer.patch(attrs_path, {"massKg": "about 1.4 kg"}),
              "not a valid number")

    # NI-00000493: a declared list of values was published to the clients, which render it
    # as a dropdown, and enforced nowhere - so the API accepted what the UI refused.
    c.refused("NI-00000678/679", "a value outside a declared LOV is refused",
              lambda: designer.patch(attrs_path, {"buyMakeFlag": "Borrowed"}),
              "not an allowed value")

    # NI-00000660: an empty patch reported success having changed nothing, so a
    # client bug looked like a successful save.
    c.refused("NI-00000660", "an empty attribute patch is refused",
              lambda: designer.patch(attrs_path, {}),
              "no attributes")

    print("\n-- Authorisation --")

    # NI-00000621 / NI-00000671: GET /api/users had no authorisation at all - the full record
    # for every account, to any signed-in caller.
    directory = designer.get("/api/users")
    leaked = [u for u in directory
              if u.get("email") or u.get("lastLoginAt") or u.get("phoneNumber")]
    c.record("NI-00000621/671", "a Member sees a redacted user directory",
             not leaked, f"{len(leaked)} of {len(directory)} rows still carry email/lastLogin/phone")

    full = admin.get("/api/users")
    c.record("NI-00000621/671", "an administrator still sees full records",
             any(u.get("email") for u in full), "admin's own view was redacted too")

    # NI-00000662: GET /api/partnumbers/next was the only way to see the next
    # number, and seeing it spent it.
    peeks = {str(designer.get("/api/partnumbers/peek/cstLightSpeedSystemsAircraftPart"))
             for _ in range(3)}
    c.record("NI-00000662", "peek is advisory and does not consume a number",
             len(peeks) == 1, f"three peeks returned {len(peeks)} different values: {peeks}")

    # NI-00000600 / NI-00000587 / NI-00000506: canTransition was canEdit wearing a different
    # name, so a designer who could edit a drawing was told they could Release it. It is now
    # derived from the allowed-transition list, which also populates the control.
    perms = designer.get(f"/api/plmobjects/{plate['plmObjectId']}/permissions")
    allowed = perms.get("allowedTransitions") or []
    c.record("NI-00000600/587", "canTransition agrees with the allowed-transition list",
             bool(perms.get("canTransition")) == (len(allowed) > 0),
             f"canTransition={perms.get('canTransition')} but allowedTransitions={allowed}")

    # NI-00000672: the security inspector refused to explain a denial to the person denied,
    # which is the one person who needed the answer.
    whoami = designer.whoami()
    own = designer.get(
        f"/api/security/inspect?objectId={plate['plmObjectId']}&userIds={whoami['userId']}",
        allow_403=True)
    c.record("NI-00000672", "a Member may inspect their own access",
             not isinstance(own, Refused) and "users" in (own or {}),
             f"got {own if isinstance(own, Refused) else type(own).__name__}")

    return c.summary()


if __name__ == "__main__":
    sys.exit(main())
