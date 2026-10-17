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
import lightjet_items as IT                                          # noqa: E402
import lightjet_projects as PRJ                                      # noqa: E402
import lightjet_quality as QA                                        # noqa: E402
import lightjet_requirements as REQ                                  # noqa: E402
import lightjet_structure as ST                                      # noqa: E402
from aviation_model import GROUPS, NUMBERING                          # noqa: E402
from aviation_types import ALL_TYPES                                  # noqa: E402
from build_customization import classification_folders               # noqa: E402

# Where the out-of-the-box type definitions live. A validator has to resolve the whole
# inheritance chain, and half of it is out of the box.
OOTB_TYPES_DIR = Path(
    r"C:\Github\Nexus.PLM.Installer\payload\Engine\types\ootb")

OOTB_DEFAULT_STATES = ["Draft", "In-work", "Released", "Obsolete"]


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
        + D.ITEMS_21 + IT.ITEMS_23 + IT.ITEMS_25
        + DOC.ALL_DOCUMENTS
        + REQ.REQUIREMENTS
        + QA.FAI_REPORTS + QA.NCRS + QA.COCS + QA.ARCS
        + QA.SUPPLIER_RECORDS + QA.PROCESS_SPECS + QA.SERVICE_BULLETINS
        + PRJ.WORK_ITEMS
    )


def change_records() -> list[dict]:
    """The out-of-the-box change objects, as plain records."""
    out = []
    for report in QA.PROBLEM_REPORTS:
        out.append({"type": "ProblemReport", **report})
    for chain_def in QA.CHANGE_CHAINS:
        for kind, type_name in (("ecr", "ECR"), ("eco", "ECO"), ("ecn", "ECN")):
            change = chain_def.get(kind)
            if change:
                out.append({"type": type_name, "folder": QA.F_PR, **change})
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

    # Bill of materials.
    for link in ST.ALL_BOM:
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
            for status, _comment in change.get("transitions", []):
                if status not in states:
                    problems.append(f"{change['pn']}: transition to '{status}' is not a "
                                    f"live {type_name} state.")
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

    def put(self, path, body):
        return self._call("PUT", path, json=body)

    def post(self, path, body=None):
        return self._call("POST", path, json=body)

    def patch(self, path, body):
        return self._call("PATCH", path, json=body)

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


def deterministic_id(part_number: str) -> str:
    """A stable object id per part number, so a re-run updates rather than duplicates."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL,
                          f"nexus-plm:lightjet-demo:{part_number}"))


def load(engine: Engine, registry: dict[str, dict], verbose: bool = True,
         vault_url: str | None = None,
         documents_dir: Path | None = None) -> None:
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
        user_id = str(uuid.uuid4())
        engine.put(f"/api/users/{user_id}", {
            "id": user_id, "username": username, "displayName": display,
            "accountType": role, "isActive": True, "password": "Nexus2025!",
            "groupIds": [group_ids[g] for g in groups if g in group_ids],
        })
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
    # The customization set already carries the tree, so this only fills gaps.
    folders = classification_folders()["folders"]
    live_folders = {f.get("path") for f in (engine.get("/api/classification/folders")
                                            or [])}
    created = 0
    for folder in folders:
        if folder["path"] in live_folders:
            continue
        engine.post("/api/classification/folders", {"path": folder["path"]})
        created += 1
    say(f"classification folders created: {created}")

    # ── Objects, with revision history ──────────────────────────────────────
    records = all_records() + change_records()
    ids: dict[str, str] = {}
    revision_ids: dict[tuple[str, str], str] = {}

    for record in records:
        pn = record["pn"]
        object_id = deterministic_id(pn)
        ids[pn] = object_id
        engine.put(f"/api/plmobjects/{object_id}", {
            "plmObjectId": object_id,
            "typeName": record["type"],
            "partNumber": pn,
            "description": record.get("description"),
        })

        history = record.get("history") or [(record.get("revision", "A"),
                                             record.get("status"))]
        for label, status in history:
            revision_id = deterministic_id(f"{pn}#{label}")
            revision_ids[(pn, label)] = revision_id
            engine.put(f"/api/plmobjects/{object_id}/revisions/{revision_id}", {
                "revisionId": revision_id, "plmObjectId": object_id,
                "revision": label, "status": status,
                "extensionData": "{}",
            })

        # Attributes go on the latest revision only. PATCH rather than PUT so the
        # Engine applies them through the attribute path that validates them.
        latest_label = history[-1][0]
        attrs = {k: v for k, v in (record.get("attrs") or {}).items() if v is not None}
        if attrs:
            engine.patch(
                f"/api/plmobjects/{object_id}/revisions/"
                f"{revision_ids[(pn, latest_label)]}/attributes",
                {k: (str(v).lower() if isinstance(v, bool) else v)
                 for k, v in attrs.items()})

        if record.get("notes"):
            engine.patch(f"/api/plmobjects/{object_id}/notes",
                         {"notes": record["notes"]})
    say(f"objects: {len(records)}")

    # ── Classification assignment ───────────────────────────────────────────
    for record in records:
        folder = record.get("folder")
        if not folder:
            continue
        engine.post(f"/api/plmobjects/{ids[record['pn']]}/classifications",
                    {"path": folder})
    say("classification assigned")

    # ── Bill of materials ───────────────────────────────────────────────────
    for link in ST.ALL_BOM:
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
    for link in REQ.TRACE_LINKS:
        body = {
            "sourceObjectId": ids[link["source"]],
            "targetObjectId": ids[link["target"]],
            "linkType": link["type"],
            "note": link.get("note"),
        }
        if link.get("pin"):
            target = next(r for r in records if r["pn"] == link["target"])
            label = (target.get("history") or [("A", None)])[-1][0]
            body["targetRevisionId"] = revision_ids[(link["target"], label)]
        engine.post("/api/requirement-trace-links", body)
    say(f"trace links: {len(REQ.TRACE_LINKS)}")

    # ── Requirement baseline ────────────────────────────────────────────────
    for baseline in REQ.BASELINES:
        engine.post("/api/requirements/baselines", {
            "name": baseline["name"],
            "scopeObjectId": ids[baseline["scope"]] if baseline["scope"] else None,
            "notes": baseline["notes"],
        })
    say(f"requirement baselines: {len(REQ.BASELINES)}")

    # ── Work breakdown ──────────────────────────────────────────────────────
    for parent, child in PRJ.WBS_LINKS:
        link_id = deterministic_id(f"wbs:{parent}>{child}")
        engine.put(f"/api/workitems/{ids[parent]}/children/{link_id}",
                   {"childObjectId": ids[child]})
    for predecessor, successor, kind, note in PRJ.TASK_DEPENDENCIES:
        dependency_id = deterministic_id(f"dep:{predecessor}>{successor}")
        engine.put(f"/api/workitems/dependencies/{dependency_id}", {
            "predecessorId": ids[predecessor], "successorId": ids[successor],
            "dependencyType": kind, "note": note,
        })
    say(f"wbs links: {len(PRJ.WBS_LINKS)}, dependencies: "
        f"{len(PRJ.TASK_DEPENDENCIES)}")

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
            for affected_pn, action, revision in change.get("affects", []):
                body = {"affectedObjectId": ids[affected_pn],
                        "changeAction": action,
                        "proposedRevision": revision}
                engine.post(f"/api/{route}/{change_id}/affected-items", body)
            for problem_pn in change.get("problems", []):
                if route == "ecrs":
                    engine.post(f"/api/ecrs/{change_id}/problem-reports",
                                {"problemId": ids[problem_pn]})
            if route == "ecns" and change.get("distribution"):
                engine.put(f"/api/ecns/{change_id}/distribution", {
                    "userIds": [],
                    "groupIds": [group_ids[g] for g in change["distribution"]
                                 if g in group_ids],
                    "dueDays": 14,
                })
            for status, comment in change.get("transitions", []):
                engine.post(f"/api/{route}/{change_id}/transition",
                            {"toStatus": status, "comment": comment})
        if ecr and eco:
            engine.post(f"/api/ecos/{ids[eco['pn']]}/ecrs",
                        {"ecrId": ids[ecr['pn']]})
        if eco and ecn:
            engine.post(f"/api/ecns/{ids[ecn['pn']]}/ecos",
                        {"ecoId": ids[eco['pn']]})
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
    load(engine, registry, vault_url=args.vault, documents_dir=documents_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
