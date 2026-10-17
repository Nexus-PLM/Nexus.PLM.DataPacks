"""Seals the NX-200 data model into a `.nexuscustomization` package.

Run:  python build_customization.py [output-directory]

The package is byte-reproducible: nothing in it depends on the clock or on a random id, so
two runs of this script produce the same archive and a re-import of the same build reads as
identical everywhere. That is deliberate - it is the quickest proof that a package is
complete, and it means a diff between two builds is a diff of the model, not of noise.

Integrity is written the way the Engine's reader verifies it:

* every entry carries the SHA-256 of its raw bytes;
* `contents` counts entries per kind;
* `manifestSha256` is the SHA-256 of the canonical manifest - properties sorted ordinally
  at every depth, nulls dropped, compact - with the hash property itself removed.

The canonical form has to match `CanonicalJson.Canonicalize` exactly, including how .NET's
default JSON encoder escapes a string, or the manifest hash will not verify. `verify/` holds
a small C# checker that opens the sealed package with the Engine's own
`CustomizationPackage.Read`, so this is proven rather than assumed.
"""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from aviation_model import (  # noqa: E402
    BASE, COMPANY, GROUPS, NUMBERING, PREFIX, PROGRAM, WORKFLOWS,
    COMPLIANCE_STATES, QUALITY_STATES, TYPE_DESIGN_STATES,
)
from aviation_types import (  # noqa: E402
    ALL_TYPES, CONCRETE_DOC_TYPES, CONCRETE_ITEM_TYPES, CONCRETE_MATERIAL_TYPES,
    CONCRETE_REQ_TYPES, t,
)

VERSION = "1.0.0"
PACKAGE_NAME = f"{COMPANY} {PROGRAM} aviation baseline"


# ─────────────────────────────────────────────────────────────────────────────
# .NET-compatible canonical JSON
# ─────────────────────────────────────────────────────────────────────────────
# System.Text.Json's default encoder (JavaScriptEncoder.Default) is deliberately
# conservative: it escapes every non-ASCII character and a block list of ASCII ones that
# could terminate a script or an HTML attribute. Reproducing that list is the whole reason
# this function exists rather than a call to json.dumps.

_ESCAPES = {
    '"': "\\u0022",
    "\\": "\\\\",
    "\b": "\\b",
    "\f": "\\f",
    "\n": "\\n",
    "\r": "\\r",
    "\t": "\\t",
    "<": "\\u003C",
    ">": "\\u003E",
    "&": "\\u0026",
    "'": "\\u0027",
    "+": "\\u002B",
    "`": "\\u0060",
}


def dotnet_json_string(value: str) -> str:
    """A JSON string literal escaped the way System.Text.Json's default encoder writes it."""
    out = ['"']
    for ch in value:
        esc = _ESCAPES.get(ch)
        if esc is not None:
            out.append(esc)
        elif ord(ch) < 0x20:
            out.append(f"\\u{ord(ch):04X}")
        elif ord(ch) > 0x7E:
            # Non-ASCII is escaped as UTF-16 code units, surrogate pairs included.
            encoded = ch.encode("utf-16-be")
            for i in range(0, len(encoded), 2):
                out.append(f"\\u{(encoded[i] << 8) | encoded[i + 1]:04X}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def canonicalize(node) -> str:
    """Canonical JSON: ordinal-sorted properties, nulls dropped, compact."""
    if node is None:
        return "null"
    if node is True:
        return "true"
    if node is False:
        return "false"
    if isinstance(node, str):
        return dotnet_json_string(node)
    if isinstance(node, int):
        return str(node)
    if isinstance(node, float):
        return repr(node)
    if isinstance(node, list):
        return "[" + ",".join(canonicalize(x) for x in node) + "]"
    if isinstance(node, dict):
        parts = []
        for key in sorted(node.keys()):
            if node[key] is None:
                continue
            parts.append(f"{dotnet_json_string(key)}:{canonicalize(node[key])}")
        return "{" + ",".join(parts) + "}"
    raise TypeError(f"Cannot canonicalize {type(node).__name__}")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def indented(obj) -> bytes:
    """Entry bytes: indented UTF-8 JSON, matching how the Engine writes a type file."""
    return json.dumps(obj, indent=2, ensure_ascii=False).encode("utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Security models
# ─────────────────────────────────────────────────────────────────────────────

RELEASE_LOCKED = {"Released", "Issued", "Accepted", "Closed", "Obsolete",
                  "Superseded", "Withdrawn", "Void", "Cancelled", "Dispositioned"}

# Which group owns each family. The owning group gets Any-scope edit in working states, so
# a stress engineer cannot quietly re-release an interiors drawing - the demo's whole point
# about who is allowed to do what.
OWNING_GROUP = {
    "AircraftPart": "LSS Design Engineering",
    "ElectricalPart": "LSS Design Engineering",
    "InteriorPart": "LSS Design Engineering",
    "Installation": "LSS Design Engineering",
    "Harness": "LSS Design Engineering",
    "AeroStdPart": "LSS Design Engineering",
    "VendorPart": "LSS Supply Chain",
    "SoftwareItem": "LSS Systems Engineering",
    "AehItem": "LSS Systems Engineering",
    "VendorRep": "LSS Supply Chain",
    "Tooling": "LSS Manufacturing Engineering",
    "Consumable": "LSS Manufacturing Engineering",
    "Drawing": "LSS Design Engineering",
    "Specification": "LSS Systems Engineering",
    "Icd": "LSS Systems Engineering",
    "ComplianceReport": "LSS Airworthiness and Certification",
    "QualTestPlan": "LSS Systems Engineering",
    "QualTestReport": "LSS Systems Engineering",
    "SafetyAssessment": "LSS Systems Engineering",
    "SwPlan": "LSS Systems Engineering",
    "PrjSpecificCertPlan": "LSS Airworthiness and Certification",
    "EMICAR": "LSS Systems Engineering",
    "FaiReport": "LSS Quality Assurance",
    "Ncr": "LSS Quality Assurance",
    "CofC": "LSS Quality Assurance",
    "AirworthinessRelease": "LSS Airworthiness and Certification",
    "ServiceBulletin": "LSS Customer Support",
    "ProcessSpec": "LSS Manufacturing Engineering",
    "SupplierQualRecord": "LSS Supply Chain",
    "AircraftRequirement": "LSS Systems Engineering",
    "OperatorRequirement": "LSS Systems Engineering",
    "SystemRequirement": "LSS Systems Engineering",
    "SubsystemRequirement": "LSS Systems Engineering",
    "ComponentRequirement": "LSS Systems Engineering",
    "CertRequirement": "LSS Airworthiness and Certification",
    "Material": "LSS Design Engineering",
}

# Types whose content is export-controlled often enough that the whole type is readable
# only by the groups that need it. Everyone else does not see the object at all.
EXPORT_RESTRICTED = {"SwPlan", "AehItem", "SoftwareItem"}


def security_model(stem: str, state_names: list[str]) -> dict:
    """The security model for one concrete type.

    Everyone may see and read, except on the export-restricted types. The owning group may
    edit anything of its own family while the revision is in a working state. A released or
    issued revision is read-only for everyone but an administrator, which is the rule that
    makes a release mean something. `canCreate` is never true anywhere: the first true on
    the site flips object creation to an allowlist for every type at once.
    """
    owner_group = OWNING_GROUP.get(stem)
    restricted = stem in EXPORT_RESTRICTED
    rows: list[dict] = []

    for state in state_names:
        locked = state in RELEASE_LOCKED
        rows.append({
            "stateName": state, "subjectType": "*", "subjectName": "",
            "canView": not restricted, "canRead": not restricted, "canCreate": False,
            "editScope": "None" if locked else "Own",
            "deleteScope": "None" if locked else "Own",
            "canTransition": False, "canDownload": not restricted,
        })
        if owner_group:
            rows.append({
                "stateName": state, "subjectType": "group", "subjectName": owner_group,
                "canView": True, "canRead": True, "canCreate": False,
                "editScope": "None" if locked else "Any",
                "deleteScope": "None" if locked else "Any",
                "canTransition": True, "canDownload": True,
            })
        # Airworthiness always sees type design data, whatever the state, because it has to
        # be able to answer a question about a released configuration without being granted
        # access first.
        rows.append({
            "stateName": state, "subjectType": "group",
            "subjectName": "LSS Airworthiness and Certification",
            "canView": True, "canRead": True, "canCreate": False,
            "editScope": "None", "deleteScope": "None",
            "canTransition": True, "canDownload": True,
        })
        rows.append({
            "stateName": state, "subjectType": "role", "subjectName": "Admin",
            "canView": True, "canRead": True, "canCreate": False,
            "editScope": "Any", "deleteScope": "Any",
            "canTransition": True, "canDownload": True,
        })

    return {
        "publicVisibilityState": None,
        "defaultRevisionState": state_names[0],
        "statePermissions": rows,
        "transitionRules": transition_rules(state_names, owner_group),
        "attributeEditability": [],
    }


# States whose entry is an act of approval. Only a Part 21 Subpart J signatory may enter
# one, which on this site means the airworthiness group or an administrator.
SIGNATORY_STATES = {"Released", "Accepted", "Issued"}

# Leaving an approved state is as consequential as entering one: un-releasing a drawing
# that aeroplanes were built to is a continued-airworthiness act, not an edit.
POST_APPROVAL_STATES = {"Superseded", "Obsolete", "Withdrawn"}

# Refusing or abandoning your own work needs no delegated authority.
NEGATIVE_STATES = {"Rejected", "Cancelled", "Void"}

SIGNATORY_GROUP = "LSS Airworthiness and Certification"


def transition_rules(state_names: list[str], owner_group: str | None) -> list[dict]:
    """Who may move a revision from each state to each other state.

    `transitionRules` is an ALLOWLIST, and an empty list is not a safe default: the
    Engine only enforces transitions at all when a type declares at least one rule
    (`HasTransitionRulesAsync`). A type with none has no transition control whatever its
    per-state `canTransition` flags say, which is how a designer could set type design
    data straight to Released with no workflow and no sign-off.

    The rules follow what a design organisation actually does, not what a state diagram
    makes convenient:

    * Working states move forward, and back for rework, under the owning group.
    * Entry into an APPROVED state - Released, Accepted, Issued - is the approval itself
      and belongs to a Part 21 Subpart J signatory alone.
    * **An approved revision never moves backwards.** There is no route from Released to
      In Design Review, because that is not how a change is made: you raise a change,
      revise the item, re-run whatever test the change invalidated, and release the new
      revision - or you supersede the part with a new number. The only ways out of an
      approved state are Superseded and Obsolete, and both are signatory acts, because
      aeroplanes may already have been built to it.
    * Abandoning or refusing work is the owning group's own business, but only while the
      work is still theirs - an approved revision cannot be cancelled.
    """
    admin = "role:Admin"
    signatory = f"{admin}, group:{SIGNATORY_GROUP}"
    working = signatory + (f", group:{owner_group}" if owner_group else "")

    rules: list[dict] = []
    seen: set[tuple[str, str]] = set()

    def allow(source: str, target: str, who: str):
        if source == target or (source, target) in seen:
            return
        seen.add((source, target))
        rules.append({"fromState": source, "toState": target, "allowedRoles": who})

    present_approved = SIGNATORY_STATES & set(state_names)
    present_retired = POST_APPROVAL_STATES & set(state_names)
    present_negative = NEGATIVE_STATES & set(state_names)

    for index, state in enumerate(state_names):
        if state in present_approved:
            # The only way out of an approved revision is to retire it. Everything else
            # is a new revision or a new part number, which is a create, not a move.
            for retired in present_retired:
                allow(state, retired, signatory)
            continue

        if state in present_retired:
            # A retired revision stays retired. Superseded may still go on to Obsolete.
            for retired in present_retired:
                allow(state, retired, signatory)
            continue

        # A working state: forward a step, and back a step for rework.
        for neighbour in (state_names[index + 1:index + 2] +
                          state_names[max(index - 1, 0):index]):
            if neighbour in present_approved or neighbour in present_retired:
                continue                      # handled below, signatory only
            allow(state, neighbour, working)

        # Approval may be granted from any working state, by a signatory only.
        for approved in present_approved:
            allow(state, approved, signatory)

        # Work may be abandoned or refused by the people doing it.
        for negative in present_negative:
            allow(state, negative, working)

    return rules


def state_names_for(type_def: dict) -> list[str]:
    """The live lifecycle states of a type, walking up to the base that declares them."""
    rows = type_def.get("lifecycleStates")
    if rows:
        return [r["name"] for r in rows if not r.get("disabled")]
    # Inherited: items and documents both default to the type-design set unless the type
    # or one of its bases overrode it, which `build_state_index` resolves.
    return [n for n, _ in TYPE_DESIGN_STATES]


def build_state_index() -> dict[str, list[str]]:
    """Resolve every type's effective lifecycle states through the inheritance chain."""
    by_name = {d["typeName"]: d for d in ALL_TYPES}
    resolved: dict[str, list[str]] = {}

    def resolve(name: str) -> list[str]:
        if name in resolved:
            return resolved[name]
        definition = by_name.get(name)
        if definition is None:                       # an out-of-the-box base
            return [n for n, _ in TYPE_DESIGN_STATES]
        rows = definition.get("lifecycleStates")
        if rows:
            states = [r["name"] for r in rows if not r.get("disabled")]
        else:
            states = resolve(definition["baseTypeName"])
        resolved[name] = states
        return states

    for definition in ALL_TYPES:
        resolve(definition["typeName"])
    return resolved


# ─────────────────────────────────────────────────────────────────────────────
# ATA classification tree
# ─────────────────────────────────────────────────────────────────────────────
# Chapter and subchapter numbering follows ATA iSpec 2200. The three chapters this demo
# builds out carry their full subchapter set; the rest of the aircraft is present at chapter
# level so the tree reads like a real aircraft breakdown rather than three orphan systems.

ATA_21 = [
    ("21-00", "Air Conditioning - General"),
    ("21-10", "Compression"),
    ("21-20", "Distribution"),
    ("21-30", "Pressurisation Control"),
    ("21-40", "Heating"),
    ("21-50", "Cooling"),
    ("21-60", "Temperature Control"),
    ("21-70", "Moisture and Air Contamination Control"),
]

ATA_23 = [
    ("23-00", "Communications - General"),
    ("23-10", "Speech Communications"),
    ("23-15", "Satellite Communications"),
    ("23-20", "Data Transmission and Automatic Calling"),
    ("23-30", "Passenger Address and Entertainment"),
    ("23-40", "Interphone"),
    ("23-50", "Audio Integrating"),
    ("23-60", "Static Discharging"),
    ("23-70", "Audio and Video Monitoring"),
    ("23-80", "Integrated Automatic Tuning"),
]

ATA_25 = [
    ("25-00", "Equipment and Furnishings - General"),
    ("25-10", "Flight Compartment"),
    ("25-20", "Passenger Compartment"),
    ("25-30", "Galley"),
    ("25-40", "Lavatories"),
    ("25-50", "Cargo and Baggage Compartments"),
    ("25-60", "Emergency Equipment"),
    ("25-80", "Insulation"),
]

OTHER_CHAPTERS = [
    ("05", "Time Limits and Maintenance Checks"),
    ("06", "Dimensions and Areas"),
    ("20", "Standard Practices - Airframe"),
    ("22", "Auto Flight"),
    ("24", "Electrical Power"),
    ("26", "Fire Protection"),
    ("27", "Flight Controls"),
    ("28", "Fuel"),
    ("29", "Hydraulic Power"),
    ("30", "Ice and Rain Protection"),
    ("31", "Indicating and Recording Systems"),
    ("32", "Landing Gear"),
    ("33", "Lights"),
    ("34", "Navigation"),
    ("35", "Oxygen"),
    ("36", "Pneumatic"),
    ("38", "Water and Waste"),
    ("49", "Airborne Auxiliary Power"),
    ("51", "Standard Practices - Structures"),
    ("52", "Doors"),
    ("53", "Fuselage"),
    ("54", "Nacelles and Pylons"),
    ("55", "Stabilizers"),
    ("56", "Windows"),
    ("57", "Wings"),
    ("71", "Power Plant"),
    ("72", "Engine"),
    ("73", "Engine Fuel and Control"),
    ("74", "Ignition"),
    ("75", "Air"),
    ("76", "Engine Controls"),
    ("77", "Engine Indicating"),
    ("78", "Exhaust"),
    ("79", "Oil"),
    ("80", "Starting"),
]


def classification_folders() -> dict:
    """The classification tree, parents before children so an apply never orphans a folder."""
    folders: list[dict] = []

    def add(path: str, attributes=None):
        folders.append({"path": path, "attributes": attributes or []})

    root = f"{PROGRAM} Light Jet"
    add(root, [
        {"name": "ataChapter", "attrType": "String"},
        {"name": "zone", "attrType": "String"},
    ])

    add(f"{root}/Product Structure")
    for chapter, title, subs in (
        ("21", "Air Conditioning", ATA_21),
        ("23", "Communications", ATA_23),
        ("25", "Equipment and Furnishings", ATA_25),
    ):
        base = f"{root}/Product Structure/ATA {chapter} {title}"
        add(base, [{"name": "systemOwner", "attrType": "String"}])
        for code, name in subs:
            add(f"{base}/{code} {name}")
    for chapter, title in OTHER_CHAPTERS:
        add(f"{root}/Product Structure/ATA {chapter} {title}")

    add(f"{root}/Certification")
    for leaf in ("Certification Programme", "Compliance Reports", "Safety Assessments",
                 "Equipment Qualification", "Software and Electronic Hardware",
                 "Certification Review Items"):
        add(f"{root}/Certification/{leaf}")

    add(f"{root}/Quality Records")
    for leaf in ("First Article Inspection", "Nonconformance and MRB",
                 "Certificates of Conformity", "Authorised Release Certificates",
                 "Supplier Approval", "Special Processes"):
        add(f"{root}/Quality Records/{leaf}")

    add(f"{root}/Continued Airworthiness")
    for leaf in ("Service Bulletins", "In-Service Reports", "Life Limited Parts"):
        add(f"{root}/Continued Airworthiness/{leaf}")

    add(f"{root}/Production")
    for leaf in ("Tooling and GSE", "Consumable Materials", "Build Definition"):
        add(f"{root}/Production/{leaf}")

    return {"folders": folders}


# ─────────────────────────────────────────────────────────────────────────────
# Kanban boards
# ─────────────────────────────────────────────────────────────────────────────
# A board's lanes must each map to one lifecycle state of the type it binds, so the lanes
# are generated from the same state tables the types use. A WIP limit is set only where the
# demo has a point to make about it.

def board(name, description, type_name, states, wip=None, viewer="members",
          manager_groups=None):
    columns = []
    for state, color in states:
        column = {"state": state, "label": state, "color": color}
        if wip and state in wip:
            column["wipLimit"] = wip[state]
        columns.append(column)
    return {
        "name": name,
        "description": description,
        "typeName": type_name,
        "columns": columns,
        "access": {
            "viewerScope": viewer,
            "viewerGroupIds": [],
            "managerGroupIds": [f"{{{{GROUP:{g}}}}}" for g in (manager_groups or [])],
        },
    }


def kanban_boards() -> list[dict]:
    return [
        board(
            f"{PROGRAM} Certification Compliance",
            "Every compliance demonstration for the NX-200, from planned through to closed. "
            "The lane a card sits in is the compliance item's real state, so the board and "
            "the compliance checklist cannot disagree.",
            t("ComplianceReport"), COMPLIANCE_STATES,
            wip={"Submitted": 8, "Finding Open": 5},
            manager_groups=["LSS Airworthiness and Certification"],
        ),
        board(
            f"{PROGRAM} Type Design Release",
            "Drawings moving through design check, stress substantiation and airworthiness "
            "sign-off. The sign-off lane has a work-in-progress limit because a queue there "
            "is a queue on one group of signatories.",
            t("Drawing"), TYPE_DESIGN_STATES,
            wip={"Airworthiness Sign-off": 6},
            manager_groups=["LSS Design Engineering",
                            "LSS Airworthiness and Certification"],
        ),
        board(
            "Nonconformance and Material Review Board",
            "Nonconformances from detection through containment to disposition and closure. "
            "Filter by severity or by whether the part escaped to a customer.",
            t("Ncr"), QUALITY_STATES,
            wip={"Under Review": 10},
            manager_groups=["LSS Quality Assurance", "LSS Material Review Board"],
        ),
        board(
            "First Article Inspection",
            "AS9102 Rev C first article submissions awaiting quality review, manufacturing "
            "concurrence and where required customer approval.",
            t("FaiReport"), QUALITY_STATES,
            manager_groups=["LSS Quality Assurance"],
        ),
        board(
            "Supplier Approval",
            "Supplier qualification records: assessment, audit outcome and approval status, "
            "with expiring AS9100 certificates visible before they lapse.",
            t("SupplierQualRecord"), QUALITY_STATES,
            manager_groups=["LSS Supply Chain", "LSS Quality Assurance"],
        ),
        board(
            "Engineering Change Control Board",
            "Engineering change requests awaiting change control board disposition against "
            "cost, weight, schedule and certification impact. Bound to the out-of-the-box "
            "ECR type, so it shows the platform's own change objects rather than a copy.",
            "ECR",
            [("Draft", "#607080"), ("Submitted", "#4A6FA5"),
             ("Under Review", "#B8860B"), ("Approved", "#2E8B57"),
             ("Rejected", "#8B2828"), ("Cancelled", "#555B66")],
            wip={"Under Review": 12},
            manager_groups=["LSS Change Control Board"],
        ),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Build
# ─────────────────────────────────────────────────────────────────────────────

def build(out_dir: Path) -> Path:
    entries: list[dict] = []
    files: dict[str, bytes] = {}

    def add(path: str, data: bytes, kind: str, key: str, depends_on=None):
        files[path] = data
        entries.append({"path": path, "kind": kind, "key": key,
                        "dependsOn": depends_on or []})

    # Groups first: workflows and boards reference them by {{GROUP:name}} token.
    add("groups/groups.json",
        indented([{"name": n, "description": d} for n, d in GROUPS]),
        "groups", "groups")

    for wf in WORKFLOWS:
        add(f"workflows/{wf['id']}.json",
            indented({
                "id": wf["id"], "name": wf["name"],
                "displayName": wf["displayName"], "description": wf["description"],
                "isOnline": wf["isOnline"],
                "definitionJson": json.dumps(wf["definition"], ensure_ascii=False),
            }),
            "workflow", wf["id"], ["groups:groups"])

    for schema in NUMBERING:
        add(f"numbering/{schema['name']}.json", indented(schema),
            "numbering", schema["name"])

    # Types in dependency order: a base is always written before anything deriving from it.
    state_index = build_state_index()
    written: set[str] = set()
    by_name = {d["typeName"]: d for d in ALL_TYPES}

    def write_type(definition: dict):
        name = definition["typeName"]
        if name in written:
            return
        base = definition["baseTypeName"]
        if base in by_name:
            write_type(by_name[base])
        depends = [f"type:{base}"]
        if definition.get("numberingSchemaName"):
            depends.append(f"numbering:{definition['numberingSchemaName']}")
        for act in definition.get("actions", []):
            if act.get("workflowDefinitionId"):
                depends.append(f"workflow:{act['workflowDefinitionId']}")
        add(f"types/{name}.json", indented(definition), "type", name, depends)
        written.add(name)

    for definition in ALL_TYPES:
        write_type(definition)

    # One security model per concrete type. Abstract bases get none: a policy on an abstract
    # type can never be the one evaluated, because no object is ever of that type.
    for definition in (CONCRETE_ITEM_TYPES + CONCRETE_DOC_TYPES
                       + CONCRETE_REQ_TYPES + CONCRETE_MATERIAL_TYPES):
        name = definition["typeName"]
        stem = name[len(BASE):]
        model = security_model(stem, state_index[name])
        add(f"security/{name}.security.json", indented(model),
            "security", name, [f"type:{name}", "groups:groups"])

    add("classification/folders.json", indented(classification_folders()),
        "classification", "classification")

    # The applier reads this file as a list of KanbanPayload: {id, name, status,
    # definitionJson} - the same envelope the workflow files use, with the board's own
    # definition as a SERIALISED STRING rather than a nested object. Writing the bare
    # definition instead makes every board deserialise with an empty id, and six rows
    # upserted on one empty id is one useless row and no boards. The report still says
    # "applied" six times, with an empty key, which is the only visible clue.
    boards = []
    for index, definition in enumerate(kanban_boards(), start=1):
        boards.append({
            # Deterministic, so re-applying updates the same board rather than adding one.
            "id": f"b0a2d000-0000-4000-c000-{index:012d}",
            "name": definition["name"],
            "status": "Published",
            "definitionJson": json.dumps(definition, ensure_ascii=False),
        })
    add("kanban/boards.json", indented(boards),
        "kanban", "kanban", ["groups:groups"])

    # ── Seal ────────────────────────────────────────────────────────────────
    for entry in entries:
        entry["sha256"] = sha256_hex(files[entry["path"]])

    contents: dict[str, int] = {}
    for entry in entries:
        contents[entry["kind"]] = contents.get(entry["kind"], 0) + 1

    manifest = {
        "formatVersion": 1,
        # A fixed id, not a fresh GUID: the package is the model, and a model that is
        # unchanged should seal to the same bytes.
        "packageId": f"9b1f4c20-6d3a-4e18-9f55-{PREFIX:<4}nx200base"[:38],
        "name": PACKAGE_NAME,
        "version": VERSION,
        "createdUtc": "2026-10-17T00:00:00+00:00",
        "createdBy": "demo-build",
        "source": {
            "kind": "export",
            "siteName": f"{COMPANY} ({PROGRAM} demonstration site)",
            "companyPrefix": PREFIX,
            "engineVersion": None,
        },
        "contents": contents,
        "entries": entries,
        "manifestSha256": None,
        "notes": NOTES,
        "warnings": [],
    }

    unsealed = dict(manifest)
    unsealed.pop("manifestSha256")
    manifest["manifestSha256"] = sha256_hex(canonicalize(unsealed).encode("utf-8"))

    out_dir.mkdir(parents=True, exist_ok=True)
    target = (out_dir /
              f"lightjet-nx200-baseline-{PREFIX}-{VERSION}.nexuscustomization")

    # A fixed entry timestamp. zipfile defaults each entry's date_time to the current
    # clock, which makes two builds of identical content differ in the container even
    # though every entry hash and the manifest hash agree. Pinning it is what makes
    # "two builds produce the same archive" actually true, and a reproducible archive is
    # how a reviewer tells a model change from noise.
    EPOCH = (1980, 1, 1, 0, 0, 0)

    def write_entry(zf, path: str, data: bytes):
        info = zipfile.ZipInfo(path, date_time=EPOCH)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        zf.writestr(info, data)

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        # The manifest is written first and the files in ordinal path order, matching the
        # Engine's writer, so the archive layout is reproducible too.
        write_entry(zf, "manifest.json",
                    json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8"))
        for path in sorted(files, key=lambda p: [ord(c) for c in p]):
            write_entry(zf, path, files[path])

    print(f"Sealed {target}")
    print(f"  {len(entries)} entries, {sum(len(b) for b in files.values()):,} bytes of content")
    for kind in sorted(contents):
        print(f"    {kind:<16} {contents[kind]}")
    return target


NOTES = f"""{COMPANY} - {PROGRAM} light jet baseline customization.

A complete aviation data model for a light-jet manufacturer holding an EASA Part 21 Subpart J
design organisation approval, built out for ATA chapters 21 Air Conditioning, 23
Communications and 25 Equipment and Furnishings.

Contains:
  * 7 abstract bases, filling the existing n5LightSpeedSystems stubs rather than standing a
    second aviation hierarchy beside them, and 24 concrete types.
  * 18 numbering schemas. The ATA-significant ones put the chapter in an lov segment ahead
    of the counter, so each chapter sequences independently (LSS-21-0014, LSS-25-0007).
  * 6 approval workflows, including a type design data release that runs design check and
    stress substantiation in parallel before a Part 21A.263 signatory, and a material review
    board route that requires airworthiness concurrence.
  * 10 groups, which the workflows and board manager scopes reference by name.
  * The ATA iSpec 2200 classification tree - chapters 21, 23 and 25 to subchapter level, the
    rest of the aircraft at chapter level - plus certification, quality, continued
    airworthiness and production trees.
  * 6 kanban boards over compliance items, drawing release, nonconformance, first article,
    supplier approval and the out-of-the-box ECR type.
  * One security model per concrete type: released revisions are read-only to everyone but
    an administrator, the owning group edits its own family, airworthiness can always read
    type design data, and canCreate is false everywhere.

No business objects, user accounts or numbering counters travel in a customization set. The
companion seed loader creates those against the Engine API.
"""


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "build"
    build(out)
