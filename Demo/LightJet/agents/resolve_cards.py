"""Moves Nexus Issues cards to their real state as the fixes land.

    python resolve_cards.py plan.json            # show what it would do
    python resolve_cards.py plan.json --apply

The board carried 292 cards from the NX-200 exercise, every one of them `New`, including
the ones that were fixed hours later. A board that does not move is not a board, and the
next person reading it cannot tell a live defect from a closed one.

The plan file is a list of decisions, each naming cards and what became of them:

    [{"state": "Closed",
      "reason": "Fixed in PR #790, deployed and verified live on prod.",
      "commit": "515577d",
      "cards": ["NI-00000676", "NI-00000677"]}]

States are the ones NexusIssue actually declares - New, In Work, In Review, Closed.
"Closed" is used only where the fix is deployed and checked against the running Engine;
a fix that is merged but not yet released goes to "In Review", because telling someone a
defect is closed when the binary still has it is worse than leaving the card alone.

Every write reads the whole revision record first and sends it back entire. A partial PUT
nulls the columns it omits - that is how an owner_id was wiped once - so the status change
is applied to the loaded record rather than to a hand-built body.
"""

from __future__ import annotations

import io
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plm_agent import Agent, Refused                                 # noqa: E402

HERE = Path(__file__).parent
BOARD = HERE / "reports" / "board.json"
LOG = HERE / "reports" / "resolved.json"
VALID = {"New", "In Work", "In Review", "Closed"}


def load_board() -> dict[str, dict]:
    rows = json.loads(io.open(BOARD, encoding="utf-8").read())
    return {r["partNumber"]: r for r in rows}


def resolve_one(me: Agent, card: dict, state: str, reason: str,
                commit: str | None, apply: bool) -> str:
    oid, rid = card["objectId"], card["revisionId"]

    if not apply:
        return f"would move {card['partNumber']} {card['status']} -> {state}"

    # Read the whole record, change one field, send it all back. Anything less nulls the
    # columns left out of the body.
    record = me.get(f"/api/plmobjects/{oid}/revisions/{rid}")
    if record is None:
        return f"SKIP {card['partNumber']}: revision {rid} not readable"
    before = record.get("status")
    record["status"] = state
    me.put(f"/api/plmobjects/{oid}/revisions/{rid}", record)

    # The resolution goes in the notes, under the agent's own report, so the card reads as
    # a history rather than being silently overwritten.
    existing = (record.get("notes") or "").rstrip()
    stamp = f"[{date.today().isoformat()}] RESOLUTION ({state})"
    body = f"{stamp}: {reason}"
    if commit:
        body += f" Commit {commit}."
    merged = f"{existing}\n\n{body}" if existing else body
    try:
        me.patch(f"/api/plmobjects/{oid}/revisions/{rid}/notes", {"notes": merged})
    except Refused as exc:
        return f"moved {card['partNumber']} {before} -> {state} (note not written: {exc.status})"
    return f"moved {card['partNumber']} {before} -> {state}"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    plan = json.loads(io.open(sys.argv[1], encoding="utf-8").read())
    apply = "--apply" in sys.argv

    board = load_board()
    me = Agent("admin", password="NexusAdmin2026!", role="PLM Administrator")

    done: list[dict] = []
    missing: list[str] = []
    for decision in plan:
        state = decision["state"]
        if state not in VALID:
            raise SystemExit(f"'{state}' is not a NexusIssue state; use one of {sorted(VALID)}")
        print(f"\n== {state}: {decision['reason'][:88]}")
        for pn in decision["cards"]:
            card = board.get(pn)
            if card is None:
                missing.append(pn)
                print(f"  ?? {pn} not in the local board dump")
                continue
            print("  " + resolve_one(me, card, state, decision["reason"],
                                     decision.get("commit"), apply))
            if apply:
                done.append({"partNumber": pn, "state": state,
                             "reason": decision["reason"],
                             "commit": decision.get("commit")})

    if apply and done:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        previous = json.loads(io.open(LOG, encoding="utf-8").read()) if LOG.exists() else []
        io.open(LOG, "w", encoding="utf-8").write(json.dumps(previous + done, indent=1))
        print(f"\n{len(done)} card(s) moved; ledger at {LOG}")
    else:
        print(f"\n{sum(len(d['cards']) for d in plan)} card(s) in the plan "
              f"({'applied' if apply else 'dry run - pass --apply'})")
    if missing:
        print(f"not found: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
