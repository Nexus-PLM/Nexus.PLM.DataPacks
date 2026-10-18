"""Loads the NX-200 demo dataset into a Nexus PLM site through the Engine REST API.

    python seed_lightjet.py --dry-run
    python seed_lightjet.py --engine http://192.168.1.47:5000 --user admin --password admin

`--dry-run` touches no server. It resolves every type through its inheritance chain -
including the out-of-the-box bases - and checks the dataset actually holds together:

  * no duplicate part number;
  * every type named by the data exists, and is concrete;
  * every attribute set on an object is declared on that type or one of its ancestors;
  * every status is a live lifecycle state of that type;
  * every part number matches the pattern its type's numbering schema would mint;
  * every bill-of-materials parent and child exists;
  * every trace link has two real ends;
  * every classification folder path exists in the packaged tree;
  * every project assignment, work item parent and dependency resolves.

That matters more than it sounds. A misspelled attribute name is accepted silently by the
Engine - it lands in the revision's extension data and simply never appears on a form - so
without this check a demo dataset can load with a clean exit code and a third of its
content invisible.

The live load is ordered so nothing is ever created before something it points at:
groups and users, projects, classification folders, objects with their revision history,
bill-of-materials links, requirement parentage, trace links, the baseline, work items and
their links, then the change chains with their affected items and transitions, and finally
the document files.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "model"))

import lightjet_data as D                                            # noqa: E402
import lightjet_documents as DOC                                     # noqa: E402
import lightjet_evidence as EV                                       # noqa: E402
import lightjet_fleet as FLEET                                       # noqa: E402
import lightjet_items as IT                                          # noqa: E402
import lightjet_links as LN                                          # noqa: E402
import lightjet_materials as MAT                                     # noqa: E402
import lightjet_projects as PRJ                                      # noqa: E402
import lightjet_quality as QA                                        # noqa: E402
import lightjet_requirements as REQ                                  # noqa: E402
import lightjet_structure as ST                                      # noqa: E402
import lightjet_value_attrs as VA                                    # noqa: E402
from aviation_model import GROUPS, NUMBERING                          # noqa: E402
from aviation_types import ALL_TYPES                                  # noqa: E402
from build_customization import classification_folders               # noqa: E402

# Where the out-of-the-box type definitions live. A validator has to resolve the whole
# inheritance chain, and half of it is out of the box.
OOTB_TYPES_DIR = Path(
    r"C:\Github\Nexus.PLM.Installer\payload\Engine\types\ootb")

OOTB_DEFAULT_STATES = ["Draft", "In-work", "Released", "Obsolete"]

# Every out-of-the-box change type (ECR, ECO, ECN, ProblemReport) starts at Draft.
CHANGE_START_STATE = "Draft"

# Ownership fields, most specific first. `assignee` on a card means "who has it now", and
# the first of these a type sets is the best available answer.
ASSIGNEE_FROM = ("assignee", "engineeringOwner", "requirementOwner", "custodian",
                 "authorName", "checkedBy", "approvedBy")

# The field each type already records its outcome in. A nonconformance closes with an MRB
# disposition, a first article with a result, a supplier record with an approval status,
# a compliance item with a compliance status.
RESOLUTION_FROM = ("mrbDisposition", "faiResult", "approvalStatus", "complianceStatus",
                   "testResult", "assessmentResult", "auditResult")

# ChangeBase's `priority` for each change, so the boards and lists sort the way a change
# board actually prioritises. Safety-related and certification-blocking changes are
# Critical; an obsolescence case is High; a performance recovery is Medium.
CHANGE_PRIORITY = {
    "LSS-PR-00001": "Critical", "LSS-PR-00002": "Low", "LSS-PR-00003": "High",
    "LSS-ECR-00001": "Critical", "LSS-ECR-00002": "Medium",
    "LSS-ECR-00003": "High", "LSS-ECR-00004": "Critical",
    "LSS-ECO-00001": "Critical", "LSS-ECO-00002": "Low", "LSS-ECO-00004": "Critical",
    "LSS-ECN-00002": "Low", "LSS-ECN-00004": "Critical",
}

# The legal transition maps the Engine enforces, copied from the controllers that own
# them: EcrsController, EcosController, EcnsController. A change type refuses any move
# that is not an edge here, so a sequence that skips a state fails with a 400 part-way
# through a load - which is a slow and expensive way to learn it. Validating the sequence
# against these maps turns that into a dry-run failure.
#
# This IS duplication of the Engine's own tables. It is worth it because the alternative
# is discovering a bad path on a live run, but it can drift: if a sequence fails here and
# the Engine accepts it, re-read the controller and update this map.
CHANGE_TRANSITIONS: dict[str, dict[str, list[str]]] = {
    "ECR": {
        "Draft": ["Submitted", "Cancelled"],
        "Submitted": ["Under Review", "Cancelled"],
        "Under Review": ["Approved", "Rejected"],
        "Approved": [], "Rejected": [], "Cancelled": [],
    },
    "ECO": {
        "Draft": ["Submitted", "Cancelled"],
        "Submitted": ["Under Review", "Cancelled"],
        "Under Review": ["Approved", "Rejected"],
        "Approved": ["Released"],
        "Released": ["Closed"],
        "Closed": [], "Rejected": [], "Cancelled": [],
    },
    "ECN": {
        "Draft": ["Submitted", "Cancelled"],
        "Submitted": ["Under Review", "Cancelled"],
        "Under Review": ["Approved", "Rejected"],
        "Approved": ["Issued"],
        "Issued": ["Closed"],
        "Closed": [], "Rejected": [], "Cancelled": [],
    },
}

# Fields that must be set before a change may ENTER a status (the mandatory-field gate).
# Also copied from the controllers. A missing one is a 422 mid-load.
CHANGE_REQUIRED_FOR_STATUS: dict[str, dict[str, list[str]]] = {
    "ECR": {"Submitted": ["reason", "proposedSolution"],
            "Under Review": ["justification"]},
    "ECO": {"Submitted": ["reason", "implementationPlan"],
            "Under Review": ["disposition"],
            "Released": ["effectivityType", "effectivityValue"]},
    "ECN": {"Submitted": ["changeSummary"],
            "Issued": ["effectivityType", "effectivityValue"]},
}


# ─────────────────────────────────────────────────────────────────────────────
# Type registry: the packaged types plus the out-of-the-box ones
# ─────────────────────────────────────────────────────────────────────────────

def load_registry(ootb_dir: Path) -> dict[str, dict]:
    """Every type definition this dataset could name, keyed by type name."""
    registry: dict[str, dict] = {}

    if ootb_dir.is_dir():
        for path in sorted(ootb_dir.glob("*.json")):
            try:
                definition = json.loads(path.read_text(encoding="utf-8-sig"))
            except json.JSONDecodeError:
                continue
            if isinstance(definition, dict) and definition.get("typeName"):
                registry[definition["typeName"]] = definition

    for definition in ALL_TYPES:
        registry[definition["typeName"]] = definition

    return registry


def chain(registry: dict[str, dict], type_name: str) -> list[dict]:
    """A type and its ancestors, most derived first. Stops on a missing base."""
    out, seen, current = [], set(), type_name
    while current and current in registry and current not in seen:
        seen.add(current)
        definition = registry[current]
        out.append(definition)
        base = definition.get("baseTypeName")
        current = base if base != current else None
    return out


def declared_attributes(registry: dict[str, dict], type_name: str) -> set[str]:
    """Every attribute name a type carries, inherited included."""
    names: set[str] = set()
    for definition in chain(registry, type_name):
        for attr in definition.get("attributes", []):
            if not attr.get("disabled"):
                names.add(attr["name"])
    return names


def live_states(registry: dict[str, dict], type_name: str) -> list[str]:
    """A type's live lifecycle states, taken from the nearest ancestor that declares them."""
    for definition in chain(registry, type_name):
        rows = definition.get("lifecycleStates")
        if rows:
            live = [r["name"] for r in rows if not r.get("disabled")]
            if live:
                return live
    return OOTB_DEFAULT_STATES


def numbering_schema_for(registry: dict[str, dict], type_name: str) -> dict | None:
    """The numbering schema a type's objects are numbered by, inherited included."""
    by_name = {s["name"]: s for s in NUMBERING}
    for definition in chain(registry, type_name):
        schema_name = definition.get("numberingSchemaName")
        if schema_name:
            return by_name.get(schema_name)
    return None


def schema_pattern(schema: dict | None) -> re.Pattern:
    """A regex for the numbers a schema can mint. No schema means the default NX + 8."""
    if schema is None:
        return re.compile(r"^NX\d{8}$")
    parts = []
    for segment in schema["segments"]:
        kind = segment["type"]
        if kind in ("prefix", "separator", "fixed", "suffix"):
            parts.append(re.escape(segment.get("value") or ""))
        elif kind == "lov":
            values = segment.get("lovValues") or []
            parts.append("(?:" + "|".join(re.escape(v) for v in values) + ")")
        elif kind == "counter":
            parts.append(r"\d{%d}" % (segment.get("digits") or 8))
    return re.compile("^" + "".join(parts) + "$")


# ─────────────────────────────────────────────────────────────────────────────
# The dataset, flattened
# ─────────────────────────────────────────────────────────────────────────────

def all_records() -> list[dict]:
    """Every object the seed creates, in creation order."""
    return (
        D.VENDOR_REPS
        + MAT.MATERIALS
        + FLEET.AIRCRAFT
        + D.ITEMS_21 + IT.ITEMS_23 + IT.ITEMS_25
        + DOC.ALL_DOCUMENTS
        + EV.EVIDENCE
        + REQ.REQUIREMENTS
        + QA.FAI_REPORTS + QA.NCRS + QA.COCS + QA.ARCS
        + QA.SUPPLIER_RECORDS + QA.PROCESS_SPECS + QA.SERVICE_BULLETINS
        + PRJ.WORK_ITEMS
    )


def change_records() -> list[dict]:
    """The out-of-the-box change objects, as plain records.

    A change that carries a transition sequence is created at the state its sequence
    starts FROM, not at the state it ends in. The Engine enforces the lifecycle, so
    creating an ECR at Approved and then asking it to transition to Submitted is refused
    outright. Walking it up is also what puts the change control board's comment on each
    step of the audit trail, which is the part worth demonstrating.
    """
    out = []
    for report in QA.PROBLEM_REPORTS:
        record = {"type": "ProblemReport", **report}
        record["attrs"] = {"title": report["title"],
                           "priority": CHANGE_PRIORITY.get(report["pn"], "High"),
                           **report.get("attrs", {})}
        out.append(record)
    for chain_def in QA.CHANGE_CHAINS:
        for kind, type_name in (("ecr", "ECR"), ("eco", "ECO"), ("ecn", "ECN")):
            change = chain_def.get(kind)
            if not change:
                continue
            record = {"type": type_name, "folder": QA.F_PR, **change}
            record["attrs"] = {"title": change["title"],
                               "priority": CHANGE_PRIORITY.get(change["pn"], "High"),
                               **change.get("attrs", {})}
            if record.get("transitions"):
                record["status"] = CHANGE_START_STATE
                record["history"] = [("A", CHANGE_START_STATE)]
            out.append(record)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────────────────────────────────────

def validate(registry: dict[str, dict], notes: list[str] | None = None) -> list[str]:
    problems: list[str] = []
    notes = notes if notes is not None else []

    records = all_records()
    changes = change_records()
    everything = records + changes

    # Part numbers, and the index everything else resolves against.
    by_pn: dict[str, dict] = {}
    for record in everything:
        pn = record["pn"]
        if pn in by_pn:
            problems.append(f"Duplicate part number {pn}.")
        by_pn[pn] = record

    group_names = {name for name, _ in GROUPS}
    usernames = {u[0] for u in D.USERS}
    folder_paths = {f["path"] for f in classification_folders()["folders"]}

    for record in everything:
        pn, type_name = record["pn"], record["type"]
        where = f"{pn} ({type_name})"

        definition = registry.get(type_name)
        if definition is None:
            problems.append(f"{where}: type is not in the registry.")
            continue
        if definition.get("abstract"):
            problems.append(f"{where}: type is abstract, so no object can be created.")
            continue

        # Attributes have to be declared, or they vanish into extension data unseen.
        declared = declared_attributes(registry, type_name)
        for key in record.get("attrs", {}):
            if key not in declared:
                problems.append(f"{where}: attribute '{key}' is not declared on the "
                                f"type or any ancestor.")

        # Status has to be a live lifecycle state.
        states = live_states(registry, type_name)
        status = record.get("status")
        if status and status not in states:
            problems.append(f"{where}: status '{status}' is not a live lifecycle state "
                            f"({', '.join(states)}).")
        for label, hist_status in record.get("history", []):
            if hist_status not in states:
                problems.append(f"{where}: revision {label} status '{hist_status}' is "
                                f"not a live lifecycle state.")

        # The number has to be one the schema could have minted - where there IS a
        # schema. An explicit part number is always accepted by the Engine; a schema only
        # decides what the site MINTS when it is asked to generate one. So a company type
        # that names a schema and then carries a number that schema could not produce is a
        # mistake worth failing on, while a type falling back to the site default is a
        # deliberate choice: the out-of-the-box change types cannot be given a company
        # schema without packaging a type that shadows them, and "LSS-ECR-00001" is worth
        # far more in a demo than "NX00000042".
        schema = numbering_schema_for(registry, type_name)
        pattern = schema_pattern(schema)
        if not pattern.match(pn):
            if schema is None:
                notes.append(f"{where}: numbered by hand. The type names no company "
                             f"numbering schema, so the site would mint "
                             f"{pattern.pattern}.")
            else:
                problems.append(f"{where}: part number does not match numbering schema "
                                f"'{schema['name']}' ({pattern.pattern}).")

        # Classification folder has to exist in the packaged tree.
        folder = record.get("folder")
        if folder and folder not in folder_paths:
            problems.append(f"{where}: classification folder '{folder}' is not in the "
                            f"packaged tree.")

        # An owner or author that is not a seeded user cannot be resolved on the site.
        for field in ("engineeringOwner", "requirementOwner", "authorName",
                      "checkedBy", "approvedBy", "custodian", "acceptedBy",
                      "assignedTo", "programManager", "originator"):
            value = record.get("attrs", {}).get(field)
            if value and value not in usernames and "." in str(value):
                problems.append(f"{where}: {field} '{value}' is not a seeded user.")

    # Bill of materials, including each aeroplane's as-built configuration.
    for link in ST.ALL_BOM + FLEET.AS_BUILT:
        for end in ("parent", "child"):
            if link[end] not in by_pn:
                problems.append(f"BOM {link['parent']} -> {link['child']}: "
                                f"{end} does not exist.")
        if link["rule"] == ST.PINNED and not link.get("pinRevision"):
            problems.append(f"BOM {link['parent']} -> {link['child']}: pinned rule with "
                            f"no revision to pin to.")
        if link.get("pinRevision"):
            child = by_pn.get(link["child"])
            if child:
                labels = [lbl for lbl, _ in child.get("history", [])]
                if link["pinRevision"] not in labels:
                    problems.append(
                        f"BOM {link['parent']} -> {link['child']}: pinned to revision "
                        f"{link['pinRevision']}, which the child does not have "
                        f"({', '.join(labels) or 'none'}).")

    # Requirement parentage and trace links.
    for requirement in REQ.REQUIREMENTS:
        parent = requirement.get("parent")
        if parent and parent not in by_pn:
            problems.append(f"{requirement['pn']}: parent {parent} does not exist.")

    for link in REQ.TRACE_LINKS:
        for end in ("source", "target"):
            if link[end] not in by_pn:
                problems.append(f"Trace {link['source']} -> {link['target']}: "
                                f"{end} does not exist.")

    for source, target, _note in EV.EVIDENCE_LINKS:
        for end, pn in (("source", source), ("target", target)):
            if pn not in by_pn:
                problems.append(f"Evidence link {source} -> {target}: {end} does not "
                                f"exist.")
    for pn in EV.EVIDENCE_REF_UPDATES:
        if pn not in by_pn:
            problems.append(f"Evidence reference update: {pn} does not exist.")

    # Object references: a part to its drawing, its specifications, its material and
    # its evidence. Both ends must exist, and a pin must name a revision the target has.
    for link in LN.ALL_REFERENCES:
        for end in ("source", "target"):
            if link[end] not in by_pn:
                problems.append(f"Reference {link['source']} -> {link['target']}: "
                                f"{end} does not exist.")
        if link["rule"] == LN.PINNED and not link.get("pin"):
            problems.append(f"Reference {link['source']} -> {link['target']}: pinned "
                            f"with no revision to pin to.")
        if link.get("pin") and link["target"] in by_pn:
            labels = [lbl for lbl, _ in by_pn[link["target"]].get("history", [])]
            if link["pin"] not in labels:
                problems.append(
                    f"Reference {link['source']} -> {link['target']}: pinned to "
                    f"revision {link['pin']}, which the target does not have "
                    f"({', '.join(labels) or 'none'}).")

    for part, mat in MAT.PART_MATERIAL.items():
        if part not in by_pn:
            problems.append(f"Material link: part {part} does not exist.")
        if mat not in by_pn:
            problems.append(f"Material link: material {mat} does not exist.")
    for part, mat, _why in MAT.MATERIAL_ALTERNATES:
        for pn in (part, mat):
            if pn not in by_pn:
                problems.append(f"Material alternate: {pn} does not exist.")

    # Value attributes, and the bodies that reference them. A chip naming an attribute
    # no ancestor owns renders as missing, which looks like a data error to a reviewer.
    owners = {pn: {a["name"] for a in rows} for pn, rows in VA.VALUE_ATTRS.items()}
    parent_of = {r["pn"]: r.get("parent") for r in REQ.REQUIREMENTS}
    for pn in list(VA.VALUE_ATTRS) + list(VA.BODIES):
        if pn not in by_pn:
            problems.append(f"Value attributes: requirement {pn} does not exist.")
    import re as _re
    for pn, body in VA.BODIES.items():
        visible = set()
        walker = pn
        for _ in range(12):
            visible |= owners.get(walker, set())
            walker = parent_of.get(walker)
            if not walker:
                break
        for name in _re.findall(r'data-name="([^"]+)"', body):
            if name not in visible:
                problems.append(
                    f"{pn}: body references value attribute '{name}', which neither it "
                    f"nor any ancestor owns - the chip would render as missing.")

    # Projects.
    for project_id, members in PRJ.PROJECT_ASSIGNMENT.items():
        if project_id not in {p["id"] for p in PRJ.PROJECTS}:
            problems.append(f"Project assignment for unknown project {project_id}.")
        for pn in members:
            if pn not in by_pn:
                problems.append(f"Project {project_id}: assigned object {pn} does not "
                                f"exist.")
    for project in PRJ.PROJECTS:
        for group in project["memberGroups"] + project["privilegedGroups"]:
            if group not in group_names:
                problems.append(f"Project {project['name']}: group '{group}' is not in "
                                f"the packaged group list.")

    # Work breakdown.
    for parent, child in PRJ.WBS_LINKS:
        for pn in (parent, child):
            if pn not in by_pn:
                problems.append(f"WBS {parent} -> {child}: {pn} does not exist.")
    for predecessor, successor, _kind, _note in PRJ.TASK_DEPENDENCIES:
        for pn in (predecessor, successor):
            if pn not in by_pn:
                problems.append(f"Dependency {predecessor} -> {successor}: {pn} does "
                                f"not exist.")

    # Change chains.
    for chain_def in QA.CHANGE_CHAINS:
        for kind in ("ecr", "eco", "ecn"):
            change = chain_def.get(kind)
            if not change:
                continue
            type_name = {"ecr": "ECR", "eco": "ECO", "ecn": "ECN"}[kind]
            states = live_states(registry, type_name)
            if CHANGE_START_STATE not in states:
                problems.append(f"{change['pn']}: {type_name} has no "
                                f"'{CHANGE_START_STATE}' state to start from.")

            # Every step has to be a legal edge, and every step's mandatory fields have
            # to be set by the time it is taken.
            legal = CHANGE_TRANSITIONS.get(type_name, {})
            gates = CHANGE_REQUIRED_FOR_STATUS.get(type_name, {})
            attrs = change.get("attrs", {})
            at = CHANGE_START_STATE
            for status, _comment in change.get("transitions", []):
                if status not in states:
                    problems.append(f"{change['pn']}: transition to '{status}' is not a "
                                    f"live {type_name} state.")
                    continue
                allowed = legal.get(at)
                if allowed is not None and status not in allowed:
                    problems.append(
                        f"{change['pn']}: {type_name} cannot go '{at}' -> '{status}'. "
                        f"Legal from '{at}': {', '.join(allowed) or 'nothing'}.")
                for field in gates.get(status, []):
                    if not str(attrs.get(field) or "").strip():
                        problems.append(
                            f"{change['pn']}: entering '{status}' requires "
                            f"'{field}', which is not set.")
                at = status
            for affected_pn, _action, revision in change.get("affects", []):
                if affected_pn not in by_pn:
                    problems.append(f"{change['pn']}: affected item {affected_pn} does "
                                    f"not exist.")
                elif revision:
                    labels = [lbl for lbl, _ in by_pn[affected_pn].get("history", [])]
                    if revision not in labels:
                        problems.append(
                            f"{change['pn']}: affected item {affected_pn} named at "
                            f"revision {revision}, which it does not have "
                            f"({', '.join(labels) or 'none'}).")
            for problem_pn in change.get("problems", []):
                if problem_pn not in by_pn:
                    problems.append(f"{change['pn']}: linked problem report "
                                    f"{problem_pn} does not exist.")
            for group in change.get("distribution", []):
                if group not in group_names:
                    problems.append(f"{change['pn']}: distribution group '{group}' is "
                                    f"not in the packaged group list.")

    # Users and groups.
    for username, _display, _role, groups in D.USERS:
        for group in groups:
            if group not in group_names:
                problems.append(f"User {username}: group '{group}' is not in the "
                                f"packaged group list.")

    return problems


def summarise() -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in all_records() + change_records():
        counts[record["type"]] = counts.get(record["type"], 0) + 1
    return counts


# ─────────────────────────────────────────────────────────────────────────────
# The live client
# ─────────────────────────────────────────────────────────────────────────────

class Engine:
    """A thin, explicit client. Every call names the endpoint it was written against."""

    def __init__(self, base_url: str, token: str | None = None, verify: bool = False):
        import requests                       # imported here so --dry-run needs no requests
        self._requests = requests
        self.base = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.verify = verify
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    @classmethod
    def login(cls, base_url: str, username: str, password: str, verify: bool = False):
        import requests
        response = requests.post(f"{base_url.rstrip('/')}/api/auth/login",
                                 json={"username": username, "password": password},
                                 verify=verify, timeout=30)
        response.raise_for_status()
        body = response.json()
        # The field is tokenValue, not token.
        if not body.get("success"):
            raise RuntimeError(f"Login refused: {body.get('message')}")
        return cls(base_url, body["tokenValue"], verify=verify)

    def _call(self, method: str, path: str, **kwargs):
        response = self.session.request(method, f"{self.base}{path}", timeout=60,
                                        **kwargs)
        # A GET that 404s is an answer - "there is nothing here" - and every existence
        # guard below relies on it. Only a GET: a 404 on a write means the route or the
        # target is wrong and must surface.
        if response.status_code == 404 and method == "GET":
            return None
        if response.status_code >= 400:
            raise RuntimeError(f"{method} {path} -> {response.status_code} "
                               f"{response.text[:400]}")
        if not response.content:
            return None
        try:
            return response.json()
        except ValueError:
            return response.text

    def get(self, path):
        return self._call("GET", path)

    def exists(self, path) -> bool:
        """True when a GET answers 2xx. A 404 is an answer, not a failure."""
        response = self.session.get(f"{self.base}{path}", timeout=60)
        return 200 <= response.status_code < 300

    def put(self, path, body):
        return self._call("PUT", path, json=body)

    def post(self, path, body=None, allow_409=False):
        """POST, optionally treating 409 as an answer rather than a failure.

        A duplicate object reference - same revision, target and kind - answers 409.
        On a reload that is the normal case, so it has to be distinguishable from a
        real failure.
        """
        if not allow_409:
            return self._call("POST", path, json=body)
        response = self.session.post(f"{self.base}{path}", json=body, timeout=60)
        if response.status_code == 409:
            return "duplicate"
        if response.status_code >= 400:
            raise RuntimeError(f"POST {path} -> {response.status_code} "
                               f"{response.text[:400]}")
        return response.json() if response.content else None

    def patch(self, path, body):
        return self._call("PATCH", path, json=body)

    def get_from(self, absolute_url: str):
        """GET from another service - the Vault - carrying the same bearer token."""
        response = self.session.get(absolute_url, timeout=60)
        if response.status_code == 404:
            return None
        if response.status_code >= 400:
            raise RuntimeError(f"GET {absolute_url} -> {response.status_code} "
                               f"{response.text[:400]}")
        return response.json() if response.content else None

    def post_to(self, absolute_url: str, body):
        """POST to another service - the Vault - carrying the same bearer token."""
        response = self.session.post(absolute_url, json=body, timeout=120)
        if response.status_code >= 400:
            raise RuntimeError(f"POST {absolute_url} -> {response.status_code} "
                               f"{response.text[:400]}")
        return response.json() if response.content else None

    def upload(self, absolute_url: str, file_name: str, handle):
        """Multipart upload of one blob to the Vault's content-addressed store."""
        response = self.session.post(absolute_url,
                                     files={"file": (file_name, handle)},
                                     timeout=300)
        if response.status_code >= 400:
            raise RuntimeError(f"POST {absolute_url} -> {response.status_code} "
                               f"{response.text[:400]}")
        return response.json() if response.content else None


def preflight(engine: Engine) -> list[str]:
    """Refuse to load until the customization set has been applied."""
    problems = []
    types = engine.get("/api/types")
    live = {t.get("typeName") for t in (types or [])}
    required = [d["typeName"] for d in ALL_TYPES if not d.get("abstract")]
    missing = [name for name in required if name not in live]
    if missing:
        problems.append(
            "The customization set has not been applied to this site. "
            f"{len(missing)} of {len(required)} company types are missing, for example: "
            + ", ".join(missing[:5]) + ". Apply "
            "lightjet-nx200-baseline-1.0.0.nexuscustomization in the Customization Sets "
            "app first.")
    return problems


FOLDER_SEPARATORS = ("||", "/")

DEMO_PASSWORD = "Nexus2025!"


def resolve_folder_ids(engine) -> dict[str, str]:
    """Map every live classification folder's "/"-joined path to its id.

    The Engine answers with a FLAT list of folder rows carrying `id`, `parentId`, `name`
    and a `pathCache`. The cache uses the store's own separator, which is not "/", so the
    path is rebuilt from the parent chain and the cache is only a fallback.
    """
    rows = engine.get("/api/classification/folders") or []
    if isinstance(rows, dict):                      # a tree wrapper rather than a list
        rows = rows.get("folders") or rows.get("items") or []
    by_id = {r["id"]: r for r in rows if isinstance(r, dict) and r.get("id")}

    def path_of(row) -> str:
        parts, current, guard = [], row, 0
        while current is not None and guard < 64:
            parts.append(current.get("name") or "")
            parent = current.get("parentId")
            current = by_id.get(parent) if parent else None
            guard += 1
        return "/".join(reversed(parts))

    paths: dict[str, str] = {}
    for row in by_id.values():
        paths[path_of(row)] = row["id"]
        cache = row.get("pathCache")
        if cache:
            for separator in FOLDER_SEPARATORS:
                if separator in cache:
                    paths.setdefault(cache.replace(separator, "/"), row["id"])
                    break
    return paths


def derive_priority(attrs: dict) -> str:
    """Priority from what the record actually says, not a flat default.

    A board where every card is Medium tells nobody anything. These are the signals an
    aerospace programme really prioritises on: a safety impact, a catastrophic or
    hazardous failure effect, a flight-safety-critical classification, an escape to a
    customer, an open authority finding. Reading them off the record means the board
    agrees with the data instead of being coloured in by hand.
    """
    def truthy(key):
        return str(attrs.get(key) or "").strip().lower() in ("true", "yes", "1")

    failure = str(attrs.get("failureEffectClassification") or "")
    if (truthy("safetyImpact")
            or attrs.get("severity") == "Critical"
            or failure.startswith(("Catastrophic", "Hazardous"))
            or attrs.get("airworthinessClassification") == "Flight Safety Critical"
            or attrs.get("bulletinType") == "Mandatory"
            or attrs.get("approvalStatus") in ("Probation", "Suspended")):
        return "Critical"

    if (truthy("escapeToCustomer")
            or attrs.get("severity") == "Major"
            or failure.startswith("Major")
            or attrs.get("riskRating") in ("High", "Critical")
            or str(attrs.get("openFindingCount") or "0") not in ("0", "", "None")
            or attrs.get("complianceStatus") in ("Not compliant", "In work")
            or attrs.get("obsolescenceStatus", "").startswith("Last time buy")
            or attrs.get("testResult") == "Pass with deviation"):
        return "High"

    if (attrs.get("severity") == "Minor"
            or attrs.get("complianceStatus") == "Compliant"
            or attrs.get("itemMaturity") in ("Certified", "In production")):
        return "Low"

    return "Medium"


def deterministic_id(part_number: str) -> str:
    """A stable object id per part number, so a re-run updates rather than duplicates."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL,
                          f"nexus-plm:lightjet-demo:{part_number}"))


def load(engine: Engine, registry: dict[str, dict], verbose: bool = True,
         vault_url: str | None = None,
         documents_dir: Path | None = None,
         only_new: bool = False) -> None:
    """Create everything, in an order where nothing precedes what it points at."""
    def say(message):
        if verbose:
            print(message, flush=True)

    # ── Groups and users ────────────────────────────────────────────────────
    existing_groups = {g.get("name"): g.get("id")
                       for g in (engine.get("/api/groups") or [])}
    group_ids: dict[str, str] = {}
    for name, description in GROUPS:
        if name in existing_groups:
            group_ids[name] = existing_groups[name]
            continue
        group_id = str(uuid.uuid4())
        engine.put(f"/api/groups/{group_id}",
                   {"id": group_id, "name": name, "description": description})
        group_ids[name] = group_id
    say(f"groups: {len(group_ids)}")

    existing_users = {u.get("username") for u in (engine.get("/api/users") or [])}
    for username, display, role, groups in D.USERS:
        if username in existing_users:
            continue
        user_id = deterministic_id(f"user:{username}")
        engine.put(f"/api/users/{user_id}", {
            "id": user_id, "username": username, "displayName": display,
            "accountType": role, "isActive": True,
        })
        engine.post(f"/api/users/{user_id}/set-password", {"password": DEMO_PASSWORD})
        for group in groups:
            if group in group_ids:
                engine.post(f"/api/users/{user_id}/groups/{group_ids[group]}")
    say(f"users: {len(D.USERS)}")

    # ── Projects ────────────────────────────────────────────────────────────
    for project in PRJ.PROJECTS:
        engine.put(f"/api/projects/{project['id']}", {
            "id": project["id"], "name": project["name"],
            "description": project["description"],
            "status": project["status"], "projectType": project["type"],
            "memberGroupIds": json.dumps(
                [group_ids[g] for g in project["memberGroups"] if g in group_ids]),
            "privilegedGroupIds": json.dumps(
                [group_ids[g] for g in project["privilegedGroups"] if g in group_ids]),
        })
    say(f"projects: {len(PRJ.PROJECTS)}")

    # ── Classification folders ──────────────────────────────────────────────
    # The customization set already carries the tree, so normally this only resolves it.
    # A folder is created by NAME under a PARENT ID - there is no create-by-path - so the
    # tree is walked shallowest first and each level's id is remembered for the next.
    folder_ids = resolve_folder_ids(engine)
    created = 0
    for folder in sorted(classification_folders()["folders"],
                         key=lambda f: f["path"].count("/")):
        path = folder["path"]
        if path in folder_ids:
            continue
        parent_path, _, name = path.rpartition("/")
        parent_id = folder_ids.get(parent_path) if parent_path else None
        if parent_path and parent_id is None:
            say(f"  ! cannot create {path!r}: parent is missing")
            continue
        result = engine.post("/api/classification/folders",
                             {"name": name, "parentId": parent_id})
        new_id = result.get("id") if isinstance(result, dict) else None
        if new_id is None:            # the create answered with the tree, not the row
            folder_ids = resolve_folder_ids(engine)
            new_id = folder_ids.get(path)
        if new_id:
            folder_ids[path] = new_id
            created += 1
    say(f"classification folders: {len(folder_ids)} resolved, {created} created")

    # ── Objects, at their first revision ──────────────────────────────────────
    records = all_records() + change_records()
    ids: dict[str, str] = {}
    revision_ids: dict[tuple[str, str], str] = {}

    # Which objects are already on the site. In `only_new` mode the loader adds what is
    # missing and leaves everything else exactly as it is - including whatever people
    # have changed since. A plain run rewrites every attribute from this dataset, which
    # is right for a reset and wrong while anyone is working: it silently reverts their
    # edits, and the only trace is an "AttributesUpdated" line in somebody else's name.
    untouched: set[str] = set()
    if only_new:
        for record in records:
            if engine.get(f"/api/plmobjects/{deterministic_id(record['pn'])}"):
                untouched.add(record["pn"])
        say(f"already present and left alone: {len(untouched)}")

    for record in records:
        pn = record["pn"]
        object_id = deterministic_id(pn)
        ids[pn] = object_id
        for label, _status in (record.get("history") or [("A", None)]):
            revision_ids[(pn, label)] = deterministic_id(f"{pn}#{label}")
        if pn in untouched:
            continue
        engine.put(f"/api/plmobjects/{object_id}", {
            "plmObjectId": object_id,
            "typeName": record["type"],
            "partNumber": pn,
            "description": record.get("description"),
        })

        # Only the FIRST revision here. The later ones come after the trace links, so
        # that a link's review baseline is the revision that existed when it was made.
        history = record.get("history") or [(record.get("revision", "A"),
                                             record.get("status"))]
        label, status = history[0]
        revision_id = deterministic_id(f"{pn}#{label}")
        revision_ids[(pn, label)] = revision_id
        engine.put(f"/api/plmobjects/{object_id}/revisions/{revision_id}", {
            "revisionId": revision_id, "plmObjectId": object_id,
            "revision": label, "status": status,
            "extensionData": "{}",
        })
    say(f"objects: {len(records)} (first revision)")

    # ── Requirement parentage ───────────────────────────────────────────────
    reparented = 0
    for requirement in REQ.REQUIREMENTS:
        parent = requirement.get("parent")
        if not parent:
            continue
        engine.put(f"/api/requirements/{ids[requirement['pn']]}/parent",
                   {"newParentPlmId": ids[parent]})
        reparented += 1
    say(f"requirement parentage: {reparented}")

    # ── Trace links ─────────────────────────────────────────────────────────
    existing_traces: set[tuple[str, str, str]] = set()
    for pn in {l["source"] for l in REQ.TRACE_LINKS}:
        for row in (engine.get(f"/api/requirement-trace-links/for/{ids[pn]}") or {}) \
                .get("outgoing", []) or []:
            existing_traces.add((ids[pn], row.get("target", {}).get("objectId", ""),
                                 row.get("linkType") or ""))

    created_traces = 0
    for link in REQ.TRACE_LINKS:
        key = (ids[link["source"]], ids[link["target"]], link["type"])
        if key in existing_traces:
            continue
        body = {
            "sourceObjectId": ids[link["source"]],
            "targetObjectId": ids[link["target"]],
            "linkType": link["type"],
            "note": link.get("note"),
        }
        if link.get("pin"):
            # The FIRST revision: a pin means "which revision this link is about", and
            # the data's own notes say it is the revision the test was run on. Pinning to
            # whatever happens to be latest is a no-op and tells the reader nothing.
            target = next(r for r in records if r["pn"] == link["target"])
            label = link.get("pinRevision") or \
                (target.get("history") or [("A", None)])[0][0]
            body["targetRevisionId"] = revision_ids[(link["target"], label)]
        engine.post("/api/requirement-trace-links", body)
        existing_traces.add(key)
        created_traces += 1
    say(f"trace links: {created_traces} created, "
        f"{len(REQ.TRACE_LINKS) - created_traces} already present")

    # ── Later revisions ─────────────────────────────────────────────────────
    # After the trace links on purpose. A link holds the endpoint revisions the reviewer
    # has seen, so revising a target NOW is what makes the links onto it suspect - which
    # is what happened in the story this data tells. Create every revision up front and
    # no link can ever be suspect, which quietly removes the best moment in the demo.
    later = 0
    for record in records:
        pn = record["pn"]
        if pn in untouched:
            continue
        for label, status in (record.get("history") or [])[1:]:
            revision_id = deterministic_id(f"{pn}#{label}")
            revision_ids[(pn, label)] = revision_id
            engine.put(f"/api/plmobjects/{ids[pn]}/revisions/{revision_id}", {
                "revisionId": revision_id, "plmObjectId": ids[pn],
                "revision": label, "status": status,
                "extensionData": "{}",
            })
            later += 1
    say(f"later revisions: {later}")

    # ── Attributes and notes ────────────────────────────────────────────────
    # On each object's LATEST revision, so this has to follow the step above. PATCH
    # rather than PUT so the Engine applies them through the path that validates them.
    for record in records:
        pn = record["pn"]
        if pn in untouched:
            continue
        history = record.get("history") or [(record.get("revision", "A"), None)]
        latest = history[-1][0]
        attrs = {k: v for k, v in (record.get("attrs") or {}).items() if v is not None}
        # A board card, a grid row and a search hit all read `title`. Default it from the
        # object's description rather than making every record repeat itself.
        declared = declared_attributes(registry, record["type"])
        if "title" not in attrs and "title" in declared:
            attrs["title"] = record.get("description") or record["pn"]
        # Who has the ball: the first of the type's own ownership fields that is set.
        if "assignee" not in attrs and "assignee" in declared:
            holder = next((attrs[f] for f in ASSIGNEE_FROM if attrs.get(f)), None)
            if holder:
                attrs["assignee"] = holder
        # The outcome, taken from whichever field this type already records it in.
        if "resolution" not in attrs and "resolution" in declared:
            outcome = next((attrs[f] for f in RESOLUTION_FROM if attrs.get(f)), None)
            if outcome:
                attrs["resolution"] = outcome
        if "priority" not in attrs and "priority" in declared:
            attrs["priority"] = derive_priority(attrs)
        if attrs:
            engine.patch(
                f"/api/plmobjects/{ids[pn]}/revisions/{revision_ids[(pn, latest)]}"
                f"/attributes",
                {k: (str(v).lower() if isinstance(v, bool) else v)
                 for k, v in attrs.items()})
        if record.get("notes"):
            engine.patch(f"/api/plmobjects/{ids[pn]}/notes", {"notes": record["notes"]})
    say("attributes and notes applied")

    # ── Classification assignment ────────────────────────────────────────
    # Runs after step C on purpose: it classifies the LATEST revision, which does not
    # exist until the later revisions have been created.
    # POST on an already-classified revision is an error, not a no-op, so an existing
    # classification is left alone. Everything created with POST below is guarded the
    # same way: a demo dataset gets reloaded the morning of a demo, and silently doubling
    # its traceability would be worse than failing.
    # A classification belongs to a REVISION, not to an object, and is keyed by folder id.
    # /api/plmobjects/{id}/classifications is read-only apart from a consolidate action;
    # the writer is a POST on the revision's own classification route.
    classified, unresolved = 0, []
    for record in records:
        folder = record.get("folder")
        if not folder:
            continue
        folder_id = folder_ids.get(folder)
        if folder_id is None:
            unresolved.append(folder)
            continue
        pn = record["pn"]
        label = (record.get("history") or [(record.get("revision", "A"), None)])[-1][0]
        revision_id = revision_ids[(pn, label)]
        if engine.exists(f"/api/plmobjects/{ids[pn]}/revisions/{revision_id}"
                         f"/classification"):
            continue
        engine.post(f"/api/plmobjects/{ids[pn]}/revisions/{revision_id}/classification",
                    {"folderId": folder_id, "values": None})
        classified += 1
    say(f"classified: {classified}")
    if unresolved:
        say(f"  ! {len(set(unresolved))} folder path(s) unresolved: "
            f"{', '.join(sorted(set(unresolved))[:3])}")

    # ── Bill of materials ───────────────────────────────────────────────────
    for link in ST.ALL_BOM + FLEET.AS_BUILT:
        link_id = deterministic_id(f"bom:{link['parent']}>{link['child']}:"
                                   f"{link.get('find')}")
        body = {
            "childObjectId": ids[link["child"]],
            "instanceName": link.get("instance"),
            "quantity": link["qty"],
            "sortOrder": link.get("find") or 0,
            "childRevisionRule": link["rule"],
            "scrapPercent": link.get("scrap") or 0,
        }
        if link["rule"] == ST.PINNED:
            body["pinnedRevisionId"] = revision_ids[(link["child"],
                                                     link["pinRevision"])]
        engine.put(f"/api/plmobjects/{ids[link['parent']]}/bom-children/{link_id}",
                   body)
    say(f"bom links: {len(ST.ALL_BOM)}")

    # ── Object references ───────────────────────────────────────────────────
    # A part to its drawing, its specifications, its material and its evidence. Runs
    # after the later revisions because a pinned reference names a specific revision.
    def add_reference(source, target, kind, rule, pin=None, note=None):
        source_rev = revision_ids[(source, (by_pn_all[source].get("history")
                                            or [("A", None)])[-1][0])]
        body = {"targetObjectId": ids[target], "linkTypeName": kind,
                "revisionRule": rule, "note": note}
        if rule == LN.PINNED and pin:
            body["pinnedRevisionId"] = revision_ids[(target, pin)]
        return engine.post(f"/api/plmobjects/{ids[source]}/revisions/{source_rev}"
                           f"/references", body, allow_409=True)

    by_pn_all = {r["pn"]: r for r in records}
    made, already = 0, 0
    for source, target, note in EV.EVIDENCE_LINKS:
        result = add_reference(source, target, LN.RELATED, LN.RELEASED, None, note)
        already += 1 if result == "duplicate" else 0
        made += 0 if result == "duplicate" else 1
    for link in LN.ALL_REFERENCES:
        result = add_reference(link["source"], link["target"], link["kind"],
                               link["rule"], link.get("pin"), link.get("note"))
        if result == "duplicate":
            already += 1
        else:
            made += 1
    # Every part to the material it is made from, and the one unqualified alternate.
    for part, mat in MAT.PART_MATERIAL.items():
        result = add_reference(part, mat, LN.RELATED, LN.RELEASED, None,
                               "The material this part is made from.")
        already += 1 if result == "duplicate" else 0
        made += 0 if result == "duplicate" else 1
    for part, mat, why in MAT.MATERIAL_ALTERNATES:
        result = add_reference(part, mat, LN.RELATED, LN.RELEASED, None, why)
        already += 1 if result == "duplicate" else 0
        made += 0 if result == "duplicate" else 1
    say(f"object references: {made} created, {already} already present")

    for pn, refs in EV.EVIDENCE_REF_UPDATES.items():
        if pn in untouched:
            continue
        latest = (by_pn_all[pn].get("history") or [("A", None)])[-1][0]
        engine.patch(f"/api/plmobjects/{ids[pn]}/revisions/"
                     f"{revision_ids[(pn, latest)]}/attributes",
                     {"evidenceDocumentRefs": refs})
    say(f"compliance evidence references repointed: {len(EV.EVIDENCE_REF_UPDATES)}")

    # ── Requirement value attributes, and the text that uses them ───────────
    # A value attribute is the number held once, on the requirement that owns it. The
    # body references it with a chip the client re-resolves at display time, so changing
    # the attribute changes every sentence that references it - including in descendant
    # requirements, which inherit their ancestors' attributes and render them as
    # inherited rather than owned.
    attrs_written = 0
    for pn, rows in VA.VALUE_ATTRS.items():
        for order, attr in enumerate(rows):
            attr_id = deterministic_id(f"valueattr:{pn}:{attr['name']}")
            engine.put(f"/api/requirements/{ids[pn]}/value-attrs/{attr_id}", {
                "id": attr_id, "plmObjectId": ids[pn],
                "name": attr["name"], "value": attr["value"],
                "magnitude": attr["magnitude"], "sortOrder": order,
            })
            attrs_written += 1
    say(f"requirement value attributes: {attrs_written}")

    bodies = 0
    for pn, body in VA.BODIES.items():
        latest = (by_pn_all[pn].get("history") or [("A", None)])[-1][0]
        engine.patch(f"/api/plmobjects/{ids[pn]}/revisions/"
                     f"{revision_ids[(pn, latest)]}/attributes", {"body": body})
        bodies += 1
    say(f"requirement bodies with value chips: {bodies}")

    # ── Requirement baseline ────────────────────────────────────────────────
    # Guarded: a baseline POST always creates one, so an unguarded reload leaves a pile
    # of identical baselines and the compare view becomes a guessing game.
    present = {x.get("name") for x in (engine.get("/api/requirements/baselines") or [])}
    made = 0
    for baseline in REQ.BASELINES:
        if baseline["name"] in present:
            continue
        engine.post("/api/requirements/baselines", {
            "name": baseline["name"],
            "scopeObjectId": ids[baseline["scope"]] if baseline["scope"] else None,
            "notes": baseline["notes"],
        })
        made += 1
    say(f"requirement baselines: {made} created, {len(present)} already present")

    # ── Work breakdown ──────────────────────────────────────────────────────
    by_pn = {r["pn"]: r for r in records}
    wbs_created = 0
    for parent, child in PRJ.WBS_LINKS:
        present = {row.get("childObjectId") for row in
                   (engine.get(f"/api/workitems/{ids[parent]}/children") or [])}
        if ids[child] in present:
            continue
        attrs = by_pn[child].get("attrs") or {}
        engine.post("/api/workitems/wbs-links", {
            "parentObjectId": ids[parent], "childObjectId": ids[child],
            "sortOrder": attrs.get("sortOrder") or 0,
            "wbsCode": attrs.get("wbsCode"),
        })
        wbs_created += 1
    # The Engine takes the two-letter code, not a spelled-out name.
    codes = {"FinishToStart": "FS", "StartToStart": "SS",
             "FinishToFinish": "FF", "StartToFinish": "SF"}
    dep_created = 0
    for predecessor, successor, kind, _note in PRJ.TASK_DEPENDENCIES:
        found = engine.get(f"/api/workitems/{ids[successor]}/dependencies") or {}
        pres = {row.get("predecessorId") for row in (found.get("predecessors") or [])}
        if ids[predecessor] in pres:
            continue
        engine.post("/api/workitems/dependencies", {
            "predecessorId": ids[predecessor], "successorId": ids[successor],
            "dependencyType": codes.get(kind, "FS"),
            "lagDays": 0, "leadDays": 0, "crossProject": False,
        })
        dep_created += 1
    say(f"wbs links: {wbs_created} created of {len(PRJ.WBS_LINKS)}, "
        f"dependencies: {dep_created} created of {len(PRJ.TASK_DEPENDENCIES)}")

    # ── Project assignment ──────────────────────────────────────────────────
    assigned = 0
    for project_id, members in PRJ.PROJECT_ASSIGNMENT.items():
        for pn in members:
            engine.put(f"/api/plmobjects/{ids[pn]}/projects/{project_id}", {})
            assigned += 1
    say(f"project assignments: {assigned}")

    # ── Change chains ───────────────────────────────────────────────────────
    for chain_def in QA.CHANGE_CHAINS:
        ecr, eco, ecn = (chain_def.get("ecr"), chain_def.get("eco"),
                         chain_def.get("ecn"))
        for kind, change, route in (("ecr", ecr, "ecrs"), ("eco", eco, "ecos"),
                                    ("ecn", ecn, "ecns")):
            if not change:
                continue
            change_id = ids[change["pn"]]
            present = {row.get("affectedObjectId") for row in
                       (engine.get(f"/api/{route}/{change_id}/affected-items") or [])}
            for affected_pn, action, revision in change.get("affects", []):
                if ids[affected_pn] in present:
                    continue
                body = {"affectedObjectId": ids[affected_pn],
                        "changeAction": action,
                        "proposedRevision": revision}
                engine.post(f"/api/{route}/{change_id}/affected-items", body)
            if route == "ecrs" and change.get("problems"):
                linked = {row.get("problemObjectId") for row in
                          (engine.get(f"/api/ecrs/{change_id}/problem-reports") or [])}
                for problem_pn in change["problems"]:
                    if ids[problem_pn] in linked:
                        continue
                    engine.post(f"/api/ecrs/{change_id}/problem-reports",
                                {"problemId": ids[problem_pn]})
            if route == "ecns" and change.get("distribution"):
                engine.put(f"/api/ecns/{change_id}/distribution", {
                    "userIds": [],
                    "groupIds": [group_ids[g] for g in change["distribution"]
                                 if g in group_ids],
                    "dueDays": 14,
                })
            # Only the steps the change has not already taken. A reload must not try to
            # walk a chain that is already at its end state.
            current = engine.get(f"/api/plmobjects/{change_id}/revisions/latest") or {}
            reached = str(current.get("status") or "")
            sequence = [st for st, _ in change.get("transitions", [])]
            start = sequence.index(reached) + 1 if reached in sequence else 0
            for status, comment in change.get("transitions", [])[start:]:
                engine.post(f"/api/{route}/{change_id}/transition",
                            {"toStatus": status, "comment": comment})
        # A chain link already made answers 409 - "this ECR is already promoted into an
        # ECO" - which on a reload is the normal case, not a failure.
        if ecr and eco:
            engine.post(f"/api/ecos/{ids[eco['pn']]}/ecrs",
                        {"ecrId": ids[ecr['pn']]}, allow_409=True)
        if eco and ecn:
            engine.post(f"/api/ecns/{ids[ecn['pn']]}/ecos",
                        {"ecoId": ids[eco['pn']]}, allow_409=True)
    say(f"change chains: {len(QA.CHANGE_CHAINS)}")

    # ── Document files ──────────────────────────────────────────────────────
    # Three steps, in this order, because each one needs the last:
    #   1. POST the bytes to the Vault, which stores them by SHA-256 and returns the key;
    #   2. POST a file reference joining that key to the revision;
    #   3. tell the Engine, so the revision shows the file and the indexer picks it up.
    # Step 3 is the one that is easy to forget and the one whose absence looks like a
    # broken Vault: the blob is there, the reference is there, and the object shows
    # nothing.
    if vault_url and documents_dir and documents_dir.is_dir():
        attached, missing = 0, []
        for record in records:
            name = record.get("file")
            if not name:
                continue
            path = documents_dir / name
            if not path.is_file():
                missing.append(name)
                continue
            pn = record["pn"]
            label = (record.get("history") or [(record.get("revision", "A"), None)])[-1][0]
            revision_id = revision_ids[(pn, label)]

            # A reference the previous run already registered must not be registered
            # again: POSTing the same reference id a second time answers 500, not 409,
            # so there is no way to tell a duplicate from a real failure after the fact.
            already = engine.get_from(f"{vault_url}/api/files?plmId={ids[pn]}") or []
            if any((row or {}).get("fileName") == name for row in already):
                attached += 1
                continue

            with path.open("rb") as handle:
                upload = engine.upload(f"{vault_url}/api/vault/upload", name, handle)
            vault_key = (upload or {}).get("vaultKey") or (upload or {}).get("key")
            if not vault_key:
                missing.append(f"{name} (no vault key returned)")
                continue

            engine.post_to(f"{vault_url}/api/files", {
                "id": deterministic_id(f"file:{pn}:{name}"),
                "plmId": ids[pn], "revisionId": revision_id,
                "vaultKey": vault_key, "fileName": name,
                "fileSize": path.stat().st_size,
                "isPrimary": True, "isCurrent": True,
            })
            engine.post(f"/api/plmobjects/{ids[pn]}/revisions/{revision_id}/"
                        f"file-attached",
                        {"vaultKey": vault_key, "fileName": name, "mimeType": None})
            attached += 1
        say(f"document files attached: {attached}")
        if missing:
            say(f"  ! {len(missing)} not attached: {', '.join(missing[:6])}")
    else:
        say("document files: skipped (no --vault or no generated documents directory)")

    say("done")


# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Load the NX-200 light jet demo dataset.")
    parser.add_argument("--engine", default="http://localhost:5000",
                        help="Engine base URL.")
    parser.add_argument("--user", default="admin")
    parser.add_argument("--password", default="admin")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate the dataset locally; touch no server.")
    parser.add_argument("--ootb-types", default=str(OOTB_TYPES_DIR),
                        help="Folder holding the out-of-the-box type definitions.")
    parser.add_argument("--vault", default=None,
                        help="Vault File Service base URL, e.g. "
                             "http://192.168.1.47:5200. Omit to skip file attachment.")
    parser.add_argument("--documents", default=None,
                        help="Folder of generated document files. Defaults to "
                             "../build/documents.")
    parser.add_argument("--only-new", action="store_true",
                        help="Add what is missing and leave every existing object "
                             "exactly as it is. Use this when people - or agents - are "
                             "working in the site; a plain run rewrites every attribute "
                             "from this dataset and reverts their edits.")
    parser.add_argument("--verify-tls", action="store_true",
                        help="Verify the server certificate (off by default, since the "
                             "demo site uses a per-installation CA).")
    args = parser.parse_args()

    ootb_dir = Path(args.ootb_types)
    if not ootb_dir.is_dir():
        print(f"! Out-of-the-box types not found at {ootb_dir}. Attribute and lifecycle "
              f"checks against inherited definitions will be incomplete.",
              file=sys.stderr)

    registry = load_registry(ootb_dir)
    counts = summarise()
    total = sum(counts.values())

    print(f"NX-200 demo dataset: {total} objects across {len(counts)} types")
    for type_name in sorted(counts):
        print(f"  {counts[type_name]:>4}  {type_name}")
    print(f"  {len(ST.ALL_BOM):>4}  bill-of-materials links")
    print(f"  {len(REQ.TRACE_LINKS):>4}  requirement trace links")
    print(f"  {len(PRJ.WBS_LINKS):>4}  work breakdown links")
    print(f"  {len(PRJ.PROJECTS):>4}  projects")
    print()

    notes: list[str] = []
    problems = validate(registry, notes)
    if notes:
        by_type: dict[str, int] = {}
        for note in notes:
            key = note.split("(")[1].split(")")[0]
            by_type[key] = by_type.get(key, 0) + 1
        print("Notes (not failures):")
        for key in sorted(by_type):
            print(f"  - {by_type[key]} {key} object(s) carry a hand-written number; "
                  f"the type names no company numbering schema.")
        print()
    if problems:
        print(f"{len(problems)} problem(s):")
        for problem in problems:
            print(f"  ! {problem}")
        return 1
    print("Validation passed: every type, attribute, status, number, link and folder "
          "resolves.")

    if args.dry_run:
        return 0

    print(f"\nConnecting to {args.engine} as {args.user} ...")
    engine = Engine.login(args.engine, args.user, args.password,
                          verify=args.verify_tls)
    blockers = preflight(engine)
    if blockers:
        for blocker in blockers:
            print(f"  ! {blocker}")
        return 1

    documents_dir = (Path(args.documents) if args.documents
                     else HERE.parent / "build" / "documents")
    if args.vault and not documents_dir.is_dir():
        print(f"  ! --vault given but no documents at {documents_dir}. Run "
              f"docgen/generate_documents.py first, or the objects load without files.")
    load(engine, registry, vault_url=args.vault, documents_dir=documents_dir,
         only_new=args.only_new)
    return 0


if __name__ == "__main__":
    sys.exit(main())
