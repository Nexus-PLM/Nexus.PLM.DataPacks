"""Collects the role agents' findings and files the real ones on the Nexus Issues board.

    python triage_findings.py            # show what would be filed, write nothing
    python triage_findings.py --file     # file them

The agents report; the administrator judges. That split is deliberate. Nine agents working
the same system will find the same default wrong nine times, and a board with nine copies
of one finding is worse than no board. So every report lands in a per-agent JSONL, and this
tool merges them, folds duplicates together with every reporter named, and files one card
each.

Mapping to the board's own vocabulary:

    category   issueType     what it means
    security   Bug           a permission that is wrong in either direction
    usability  Bug           possible, but needless work
    missing    Enhancement   a duty the role could not discharge at all

A security finding is filed Critical whatever the reporter said: being wrong about who can
see or change what is not a matter of degree.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plm_agent import Agent                                          # noqa: E402

REPORTS = Path(__file__).parent / "reports"
ISSUE_TYPE = "NexusIssue"
BOARD_ID = "b0a2d000-0000-4000-a000-000000000001"

# The board's foundInApp list is fixed; anything else has to land on "Other" or the
# attribute is silently dropped.
KNOWN_APPS = {
    "home / dashboard", "folders", "projects", "programs", "schedule", "my tasks",
    "problem reports", "changes (ecr)", "change orders (eco)", "change notices (ecn)",
    "requirements", "discussions", "contacts", "costing", "classification",
    "classification manager", "industry standards", "tables", "reports", "search",
    "nova (ai assistant)", "data model", "workflow designer", "workflow manager",
    "numbering", "user admin", "organization", "mime types", "indexing monitor",
    "system monitor", "integrations", "subscription", "pdf viewer", "3d viewer",
    "bom builder", "object detail", "catia addin", "freecad addin", "word addin",
    "save manager / tray", "engine api", "vault file service", "nexus issues",
    "kanban boards", "kanban manager", "other",
}

ALIASES = {
    "vault file service": "Vault File Service",
    "engine api": "Engine API",
    "schedule": "Schedule",
    "kanban boards": "Kanban Boards",
    "security": "Engine API",
    "permissions": "Engine API",
    "discussion boards": "Discussions",
    "discussions": "Discussions",
    "bom": "BOM Builder",
    "work items": "Schedule",
    "tasks": "My Tasks",
}


def normalise_app(value: str) -> str:
    raw = (value or "Other").strip()
    if raw.lower() in KNOWN_APPS:
        return next(a for a in ALIASES.values() if a.lower() == raw.lower()) \
            if raw.lower() in {v.lower() for v in ALIASES.values()} else raw
    return ALIASES.get(raw.lower(), "Other")


def key_of(row: dict) -> str:
    """A duplicate key: the app plus the meaningful words of the summary."""
    words = re.findall(r"[a-z0-9]+", (row.get("summary") or "").lower())
    stop = {"the", "a", "an", "is", "are", "no", "not", "to", "of", "in", "on", "for",
            "and", "or", "it", "its", "with", "when", "cannot", "can", "does", "do"}
    core = " ".join(sorted(w for w in words if w not in stop and len(w) > 2)[:7])
    return f"{normalise_app(row.get('foundInApp'))}|{core}"


SEVERITY_RANK = {"Critical": 3, "Major": 2, "Minor": 1}


def load_findings() -> list[dict]:
    rows = []
    for path in sorted(REPORTS.glob("bugs-*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"  ! unparseable line in {path.name}")
    return rows


def merge(rows: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[key_of(row)].append(row)

    merged = []
    for group in grouped.values():
        # The fullest report wins as the body; everyone who found it is credited.
        best = max(group, key=lambda r: len(r.get("detail") or ""))
        severities = [r.get("severity", "Minor") for r in group]
        category = "security" if any(r.get("category") == "security" for r in group) \
            else "missing" if all(r.get("category") == "missing" for r in group) \
            else best.get("category", "usability")
        merged.append({
            **best,
            "category": category,
            "severity": "Critical" if category == "security"
            else max(severities, key=lambda s: SEVERITY_RANK.get(s, 0)),
            "reporters": sorted({r["reporter"] for r in group}),
            "roles": sorted({r.get("role", "") for r in group if r.get("role")}),
            "count": len(group),
        })
    merged.sort(key=lambda r: (-SEVERITY_RANK.get(r["severity"], 0),
                               r["category"], r["summary"]))
    return merged


def describe(row: dict) -> str:
    found_by = ", ".join(f"{r}" for r in row["reporters"])
    body = [
        row.get("detail") or "",
        "",
        f"Finding category: {row['category']}.",
        f"Reported independently by {row['count']} agent(s): {found_by}"
        + (f" ({'; '.join(row['roles'])})" if row.get("roles") else "") + ".",
    ]
    if row.get("stepsToReproduce"):
        body += ["", "Steps: " + row["stepsToReproduce"]]
    return "\n".join(part for part in body if part is not None)


def file_card(admin: Agent, row: dict, dry_run: bool) -> str:
    issue_type = "Enhancement" if row["category"] == "missing" else "Bug"
    title = f"[{row['category']}] {row['summary']}"
    if dry_run:
        return "(not filed)"

    number = admin.get(f"/api/partnumbers/next/{ISSUE_TYPE}")
    part_number = number if isinstance(number, str) else \
        (number or {}).get("partNumber") or (number or {}).get("number")
    if not part_number:
        raise RuntimeError(f"could not mint a number: {number!r}")

    object_id = str(uuid.uuid4())
    revision_id = str(uuid.uuid4())
    admin.put(f"/api/plmobjects/{object_id}", {
        "plmObjectId": object_id, "typeName": ISSUE_TYPE,
        "partNumber": part_number, "description": title,
    })
    admin.put(f"/api/plmobjects/{object_id}/revisions/{revision_id}", {
        "revisionId": revision_id, "plmObjectId": object_id,
        "revision": "A", "status": "New", "extensionData": "{}",
    })
    admin.patch(f"/api/plmobjects/{object_id}/revisions/{revision_id}/attributes", {
        "title": title,
        "issueType": issue_type,
        "severity": row["severity"],
        "priority": "Critical" if row["severity"] == "Critical"
        else "High" if row["severity"] == "Major" else "Medium",
        "reporter": row["reporters"][0],
        "foundInApp": normalise_app(row.get("foundInApp")),
        "environment": "Production",
        "dateFound": row.get("dateFound") or date.today().isoformat(),
        "stepsToReproduce": row.get("stepsToReproduce") or "",
        "expectedResult": row.get("expectedResult") or "",
        "actualResult": row.get("actualResult") or "",
        "docsUpdated": "Not needed",
    })
    admin.patch(f"/api/plmobjects/{object_id}/notes", {"notes": describe(row)})
    return part_number


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", action="store_true",
                        help="Actually create the cards. Without it, nothing is written.")
    args = parser.parse_args()

    rows = load_findings()
    if not rows:
        print(f"No findings in {REPORTS}. Have the agents run?")
        return 0
    merged = merge(rows)

    print(f"{len(rows)} report(s) from "
          f"{len({r['reporter'] for r in rows})} agent(s) -> {len(merged)} card(s)\n")

    admin = Agent("admin", password="NexusAdmin2026!", role="PLM Administrator") \
        if args.file else None

    by_category: dict[str, int] = defaultdict(int)
    for row in merged:
        by_category[row["category"]] += 1
        number = file_card(admin, row, dry_run=not args.file)
        dupes = f"  (x{row['count']})" if row["count"] > 1 else ""
        print(f"  {number:<14} {row['severity']:<9} {row['category']:<10} "
              f"{normalise_app(row.get('foundInApp')):<22} {row['summary'][:60]}{dupes}")
        print(f"                 reported by: {', '.join(row['reporters'])}")

    print("\nby category: " + ", ".join(f"{k} {v}" for k, v in sorted(by_category.items())))
    if not args.file:
        print("\nDry run. Nothing was written. Re-run with --file to create the cards.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
