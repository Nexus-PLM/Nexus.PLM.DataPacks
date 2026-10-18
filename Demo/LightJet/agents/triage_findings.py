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

Grouping. A hundred loose cards on a board that already holds 257 is not a work list, it
is a pile. So every card is filed under a THEME, and a theme is how the work would
actually be picked up - one person can sit down with "authorisation and separation of
duties" and fix six things that share a cause. Each theme gets an EPIC card, each finding
references its epic, and the theme name also goes in `targetRelease` so the board can be
filtered on it without following links. Anything the rules cannot place lands in
"Unclassified" ON PURPOSE: a default that silently swallows a finding is worse than a
bucket you can see.

Re-running is safe. `reports/filed.json` records every key already on the board, so a
second pass files only what is new. That matters because the agents report in waves, and
a board with two copies of one finding is the thing this tool exists to prevent.
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


LEDGER = REPORTS / "filed.json"

# ── Themes ─────────────────────────────────────────────────────────────────────
# Ordered: the first rule that matches wins, so the most specific cause comes first.
#
# The needles are matched against the SUMMARY and the app, never the detail. Matching the
# detail put 91 of 165 findings in one theme, because a paragraph explaining a permission
# problem naturally mentions release, workflow, approval and access all at once. The
# summary is the one line the reporter chose to describe the thing, so it is the only
# field that discriminates.
THEMES = [
    ("Authorisation: data not protected",
     "Writes and reads that succeed when they should be refused - absent permission "
     "checks, released data still editable, and information disclosed to the wrong role.",
     ("no permission check", "performs no authorisation", "no authorisation check",
      "writable", "deletable", "candelete=true", "can edit", "can author",
      "can be rewritten", "not frozen", "readable", "visible", "discloses",
      "disclosing", "bypass", "bypassing", "silently re-configures", "ungated",
      "not enforced", "straight to released", "self-released", "accept their own",
      "without that user", "under a der identity", "one-way trapdoor")),

    ("Authorisation: a role cannot do its job",
     "Denials in the other direction: a role refused the thing it exists to do. Re-test "
     "each of these - the demo accounts carried an accountType that matched no policy "
     "row, and that alone produced denials that look like policy.",
     ("cannot", "can never", "denied", "refused", "403", "no write access",
      "belong to no project", "is 403", "invisible", "not navigable")),

    ("Audit trail and change history",
     "What the record says happened, and whether it matches what did.",
     ("audit trail", "change history", "two identical", "old or new value",
      "did not happen", "not written to")),

    ("Change and approval process",
     "The ECR/ECO/ECN route, release workflows, transition gates and the tasks they "
     "should create.",
     ("ecr", "eco", "ecn", "transition", "workflow", "approval route", "disposition",
      "change board", "sign-off", "signoff", "my tasks", "no task", "supersede",
      "effectivity", "material review board", "approval", "compliance item",
      "change order", "submitforrelease", "accept or raise a finding")),

    ("Traceability and navigation",
     "Relationships that exist only as text, links that do not go suspect, and chains "
     "that cannot be walked end to end.",
     ("trace", "suspect", "navigab", "reference", "link", "where used", "where_used",
      "bom-parent", "bom-children", "chain", "text, not a link", "baseline",
      "drawing that does not exist", "not discoverable", "free text")),

    ("Fleet and continued airworthiness",
     "Delivered aircraft: as-built configuration, service bulletins, effectivity, "
     "inspections, maintenance programme and in-service occurrences.",
     ("fleet", "aircraft", "airframe", "service bulletin", "bulletin", "as-built",
      "asbuilt", "in-service", "operator", "airworthiness directive", "calendar life",
      "life limit", "maintenance programme", "ica", "inspection", "occurrence")),

    ("Quality and conformity",
     "Nonconformances, material review, first article inspection and the AS9102 forms.",
     ("nonconform", "ncr", "first article", "fai", "as9102", "mrbdisposition",
      "conformity", "waiver", "deviation", "batch", "shelf life", "coc",
      "calibration", "measuring device")),

    ("Schedule and work management",
     "The work breakdown, the Gantt, forecasts, assignment, cost and programme health.",
     ("schedule", "gantt", "forecast", "critical path", "percentcomplete", "milestone",
      "work package", "work breakdown", "work item", "wbs", "constrainttype",
      "earned value", "cost actuals", "zoom", "timeline")),

    ("Data model and attribute coverage",
     "Fields that do not exist, defaults wrong every time, vocabularies that disagree, "
     "and attributes whose meaning has to be guessed.",
     ("attribute", "field", "default", "nowhere to record", "no place to record",
      "nowhere to put", "data model", "value attribute", "list-of-values", "lov",
      "vocabular", "duplicates", "contradicts", "named three different ways",
      "no file or cad", "notes", "numbering", "part number", "schema",
      "isown", "discussion message")),

    ("Change impact and revision comparison",
     "The questions a change always raises and the product cannot answer: what does "
     "this break, what moved between these two revisions, and is this fit to release.",
     ("change-impact", "change impact", "what a change breaks", "would break",
      "compare two revisions", "revision against the last", "release-readiness",
      "readiness gate", "revision rule", "follows", "no way to compare")),

    ("Security tooling and refusal messages",
     "The security model may be right, but nobody can see why. Inspection a user cannot "
     "run on themselves, and refusals that do not say what was wrong.",
     ("inspect", "does not say whether", "enumerate", "user directory",
      "error message", "bare 403", "empty body", "no reason")),

    ("Nova (AI assistant)",
     "The agentic service: retrieval, indexing, health and what it tells the user when "
     "it cannot answer.",
     ("nova", "agentic", "vector", "chroma", "embedding", "retrieval", "assistant",
      "ollama", "reconciliation")),
]

UNCLASSIFIED = (
    "Unclassified",
    "Findings the triage rules could not place. Read these first: an unplaceable "
    "finding is usually either badly written or genuinely novel.",
    (),
)

# Denial words. A security finding that reports a DENIAL may be an artefact of the
# accountType defect in the demo dataset rather than a product fault, so it is flagged
# for re-test instead of being filed as a Critical nobody can reproduce. A finding that
# reports EXCESS access is never excused this way: the "*" row still granted read and
# edit-Own, so anything beyond that was genuinely reachable.
DENIAL_WORDS = ("cannot", "can never", "denied", "refused", "403", "no write access",
                "is 403", "no access", "not permitted", "blocked")
EXCESS_WORDS = ("no permission check", "no authorisation check", "writable", "deletable",
                "can edit", "can author", "bypass", "discloses", "readable", "visible",
                "not enforced", "self-released", "accept their own")


def needs_retest(row: dict) -> bool:
    """True when a finding could be the accountType defect rather than the product.

    A finding that says it has already been re-tested is never held back, whatever its
    wording. The word-matching below is a guess about whether a denial was checked; an
    explicit `retested` flag is knowledge, and knowledge wins. Without this the rule
    swallowed the keystone finding of the whole exercise - "released data can never be
    revised" - purely because the summary contains "can never", when three agents had
    re-tested it against corrected accounts and I had confirmed the cause in source.
    """
    if row.get("retested"):
        return False
    if row.get("category") != "security":
        return False
    text = (row.get("summary") or "").lower()
    if any(word in text for word in EXCESS_WORDS):
        return False
    return any(word in text for word in DENIAL_WORDS)


def theme_of(row: dict) -> str:
    """Which theme a finding belongs to. Deliberately explicit and auditable."""
    haystack = " ".join(str(row.get(k) or "") for k in
                        ("summary", "foundInApp")).lower()
    for name, _description, needles in THEMES:
        if any(needle in haystack for needle in needles):
            return name
    return UNCLASSIFIED[0]


THEME_BY_NAME = {name: (name, description, needles)
                 for name, description, needles in [*THEMES, UNCLASSIFIED]}


def load_ledger() -> dict:
    """What is already on the board, so a second pass files only what is new."""
    if not LEDGER.exists():
        return {}
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def save_ledger(ledger: dict) -> None:
    LEDGER.write_text(json.dumps(ledger, indent=1, sort_keys=True), encoding="utf-8")


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


def create_issue(admin: Agent, title: str, issue_type: str, severity: str,
                 reporter: str, found_in_app: str, extra: dict,
                 notes: str) -> tuple[str, str, str]:
    """Create one NexusIssue card. Returns (part number, object id, revision id)."""
    number = admin.get(f"/api/partnumbers/next/{ISSUE_TYPE}")
    # The endpoint answers {"value": "NI-00000481"}. It has also been seen to answer a
    # bare string, and "partNumber"/"number" are the names the rest of the API uses, so
    # all four are accepted rather than guessing which one this build returns.
    part_number = number if isinstance(number, str) else next(
        (v for v in ((number or {}).get(k)
                     for k in ("value", "partNumber", "number", "nextNumber")) if v),
        None)
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
        "severity": severity,
        "priority": "Critical" if severity == "Critical"
        else "High" if severity == "Major" else "Medium",
        "reporter": reporter,
        "foundInApp": found_in_app,
        "environment": "Production",
        "dateFound": date.today().isoformat(),
        "docsUpdated": "Not needed",
        **extra,
    })
    admin.patch(f"/api/plmobjects/{object_id}/notes", {"notes": notes})
    return part_number, object_id, revision_id


def ensure_epic(admin: Agent, theme: str, ledger: dict, counts: dict) -> dict | None:
    """The epic card for one theme, created once and remembered."""
    key = f"epic:{theme}"
    if key in ledger:
        return ledger[key]
    if admin is None:
        return None

    _name, description, _needles = THEME_BY_NAME[theme]
    title = f"EPIC: {theme}"
    body = [
        description,
        "",
        "Raised from the NX-200 aviation demo run: nine role agents executed a certified "
        "aircraft programme on this site as themselves, each with its own account and "
        "permissions, and reported what it could not do, what it should not have been "
        "able to do, and what the system does not offer at all.",
        "",
        f"Findings filed under this theme in this pass: {counts.get(theme, 0)}.",
        "Each one references this card, and carries the theme in targetRelease.",
    ]
    part_number, object_id, revision_id = create_issue(
        admin, title, "Task", "Major", "Claude", "Other",
        {"workItemKind": "Task", "targetRelease": theme,
         "stepsToReproduce": "n/a - grouping card.",
         "expectedResult": "Every finding under this theme resolved or consciously "
                           "deferred with a reason.",
         "actualResult": description,
         "docsUpdated": "Pending"},
        "\n".join(body))
    record = {"partNumber": part_number, "objectId": object_id,
              "revisionId": revision_id}
    ledger[key] = record
    return record


def file_card(admin: Agent, row: dict, theme: str, epic: dict | None,
              dry_run: bool) -> str:
    issue_type = "Enhancement" if row["category"] == "missing" else "Bug"
    title = f"[{row['category']}] {row['summary']}"
    if dry_run:
        return "(not filed)"

    part_number, object_id, revision_id = create_issue(
        admin, title, issue_type, row["severity"], row["reporters"][0],
        normalise_app(row.get("foundInApp")),
        {"targetRelease": theme,
         "dateFound": row.get("dateFound") or date.today().isoformat(),
         "stepsToReproduce": row.get("stepsToReproduce") or "",
         "expectedResult": row.get("expectedResult") or "",
         "actualResult": row.get("actualResult") or ""},
        describe(row))

    # Reference the epic, so the grouping is navigable and not only a filter.
    if epic:
        admin.post(f"/api/plmobjects/{object_id}/revisions/{revision_id}/references",
                   {"targetObjectId": epic["objectId"],
                    "linkTypeName": "RelatedLink",
                    "revisionRule": "latest",
                    "note": f"Grouped under {theme}."},
                   allow_403=True)
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
    for row in merged:
        row["theme"] = theme_of(row)

    ledger = load_ledger()
    held = [r for r in merged if needs_retest(r)]
    merged = [r for r in merged if not needs_retest(r)]
    already = [r for r in merged if key_of(r) in ledger]
    todo = [r for r in merged if key_of(r) not in ledger]

    print(f"{len(rows)} report(s) from "
          f"{len({r['reporter'] for r in rows})} agent(s) -> {len(merged)} card(s)")
    if already:
        print(f"{len(already)} already on the board, left alone. {len(todo)} to file.")
    if held:
        print(f"{len(held)} security denial(s) HELD BACK for re-test - these may be the "
              f"accountType defect in the demo dataset rather than the product. "
              f"They are not filed; see the cause card.")
    print()

    if held and args.file and "cause:accounttype" not in ledger:
        admin_now = Agent("admin", password="NexusAdmin2026!",
                          role="PLM Administrator")
        detail = [
            "The NX-200 demo dataset created its users with accountType \"User\". The "
            "Engine evaluates policy against exactly three account types - Admin, Member "
            "and Guest (PackageValidator rejects any other role subject, and SeedService "
            "issues \"Member\" to an ordinary user). \"User\" matches no permission row, "
            "so all thirteen non-admin demo users fell through to the \"*\" row: read, "
            "edit-Own, and NO create.",
            "",
            "GET /api/security/inspect states it plainly: matchedSubject was \"the \\\"*\\\" "
            "row (everyone else)\". After correcting the accounts it reads \"the "
            "role:Member row\" with canCreate=True.",
            "",
            f"That one word produced {len(held)} security finding(s) reporting that a role "
            "could not do the thing it exists to do - customer support unable to raise a "
            "problem report, the project manager unable to create a work item. Those are "
            "NOT filed as product defects. They are listed below and are being re-tested "
            "against corrected accounts; whatever still fails will be filed on its own "
            "merits.",
            "",
            "Findings in the OTHER direction are unaffected and are filed as real: the "
            "\"*\" row still granted read and edit-Own, so anything reachable beyond that "
            "was genuinely reachable.",
            "",
            "Held back for re-test:",
        ] + [f"  - [{r['severity']}] {r['summary']}" for r in held]
        number, _oid, _rid = create_issue(
            admin_now,
            "Demo dataset accountType \"User\" matched no policy row - permission "
            "findings held for re-test",
            "Task", "Major", "Claude", "Other",
            {"workItemKind": "Task", "targetRelease": "Triage",
             "stepsToReproduce": "Create a user with accountType \"User\", then attempt "
                                 "to create any object of a type with the default policy.",
             "expectedResult": "Either the account type is rejected at creation, or an "
                               "unrecognised account type is reported rather than "
                               "silently matching no row.",
             "actualResult": "Creation is refused with a bare 403 and the cause is only "
                             "visible through /api/security/inspect.",
             "docsUpdated": "Not needed"},
            "\n".join(detail))
        ledger["cause:accounttype"] = {"partNumber": number, "theme": "Triage"}
        save_ledger(ledger)
        print(f"  {number:<14} cause card for the {len(held)} held finding(s)\n")

    counts: dict[str, int] = defaultdict(int)
    for row in todo:
        counts[row["theme"]] += 1

    admin = Agent("admin", password="NexusAdmin2026!", role="PLM Administrator")         if args.file else None

    by_category: dict[str, int] = defaultdict(int)
    order = [name for name, _d, _n in [*THEMES, UNCLASSIFIED]]
    for theme in order:
        in_theme = [r for r in todo if r["theme"] == theme]
        if not in_theme:
            continue
        epic = ensure_epic(admin, theme, ledger, counts)
        head = f"{theme}  ({len(in_theme)})"
        print(f"\n{head}\n{'-' * len(head)}"
              + (f"  epic {epic['partNumber']}" if epic else ""))
        for row in in_theme:
            by_category[row["category"]] += 1
            number = file_card(admin, row, theme, epic, dry_run=not args.file)
            if args.file:
                ledger[key_of(row)] = {"partNumber": number, "theme": theme}
                save_ledger(ledger)
            dupes = f"  (x{row['count']})" if row["count"] > 1 else ""
            print(f"  {number:<14} {row['severity']:<9} {row['category']:<10} "
                  f"{normalise_app(row.get('foundInApp')):<22} "
                  f"{row['summary'][:58]}{dupes}")
            print(f"                 reported by: {', '.join(row['reporters'])}")

    print("\nby category: "
          + ", ".join(f"{k} {v}" for k, v in sorted(by_category.items())))
    print("by theme:    "
          + ", ".join(f"{t} {counts[t]}" for t in order if counts[t]))
    if not args.file:
        print("\nDry run. Nothing was written. Re-run with --file to create the cards.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
