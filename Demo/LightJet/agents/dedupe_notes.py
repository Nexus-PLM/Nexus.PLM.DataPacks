"""Collapses a note block that was appended twice on the same card.

    python dedupe_notes.py             # show what it would do
    python dedupe_notes.py --apply

resolve_cards.py appends its resolution under whatever notes a card already carries, so
running it twice over the same plan writes the same block twice. That happened to the 143
cards in the wave-4 plan.

Only CONSECUTIVE IDENTICAL blocks are collapsed, and only down to one. A card that
legitimately carries a wave-3 resolution followed by a different wave-4 one is left alone,
and two genuinely different notes that happen to sit next to each other are left alone too -
the thing being removed is a byte-for-byte repeat of the block immediately before it.

Every write reads the whole revision record first and sends it back entire: a partial PUT
nulls the columns it omits.
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plm_agent import Agent, Refused                                 # noqa: E402

HERE = Path(__file__).parent
BOARD = HERE / "reports" / "board.json"
SEPARATOR = "\n\n"


def collapse(notes: str) -> str:
    """Drops each block that exactly repeats the one before it."""
    blocks = notes.split(SEPARATOR)
    kept: list[str] = []
    for block in blocks:
        if kept and block.strip() and block.strip() == kept[-1].strip():
            continue
        kept.append(block)
    return SEPARATOR.join(kept)


def main() -> int:
    apply = "--apply" in sys.argv
    rows = json.loads(io.open(BOARD, encoding="utf-8").read())
    me = Agent("admin", password="NexusAdmin2026!", role="PLM Administrator")

    fixed = 0
    for card in rows:
        notes = card.get("notes") or ""
        if not notes.strip():
            continue
        tidy = collapse(notes)
        if tidy == notes:
            continue

        fixed += 1
        saved = len(notes) - len(tidy)
        print(f"  {card['partNumber']}: {notes.count('RESOLUTION (')} blocks -> "
              f"{tidy.count('RESOLUTION (')} (-{saved} chars)")
        if not apply:
            continue

        oid, rid = card["objectId"], card["revisionId"]
        try:
            me.patch(f"/api/plmobjects/{oid}/revisions/{rid}/notes", {"notes": tidy})
        except Refused as exc:
            print(f"    REFUSED {exc.status}")

    verb = "de-duplicated" if apply else "would de-duplicate"
    print(f"\n{verb} {fixed} card(s)" + ("" if apply else " (dry run - pass --apply)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
