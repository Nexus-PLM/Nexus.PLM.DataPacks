"""Light Speed Systems NX-200 light jet - the demo site's data model, as data.

This module holds the whole customization: lifecycle states, numbering schemas, the type
tree, the security model each concrete type gets, the approval workflows, the ATA
classification tree, the groups and the kanban boards. `build_customization.py` turns it
into a sealed `.nexuscustomization` package.

Structural rules this model keeps by construction, matching what the Engine's applier and
Nova's DraftSetBuilder enforce:

* An attribute lives on the LOWEST type that needs it, so siblings share it rather than
  repeating it. The same rule the root CLAUDE.md states for NuGet packages.
* Concrete types never derive straight off an out-of-the-box base. Every one sits under an
  abstract company base, which sits under an abstract family base.
* A numbering schema is named before the type that uses it.
* No `canCreate` is ever true. The first true anywhere flips object creation to an
  allowlist for the entire site.
* Approvers are `{{GROUP:name}}` tokens the applier resolves to the ids this site mints for
  the groups the same package carries.

Domain references are recorded next to the attributes they justify so a reviewer can check
them: ATA iSpec 2200 chapter/subchapter numbering, CS-23 Amendment 5 / 14 CFR Part 23
Amendment 64 with ASTM F44 consensus standards as accepted means of compliance, EASA Part
21 Subpart J design organisation privileges, the EASA MC0-MC9 means-of-compliance codes,
ARP4754A/ARP4761A safety assessment, DO-178C software and DO-254 electronic hardware
assurance levels, DO-160G environmental qualification sections, AS9100D clauses, AS9102
Rev C first article inspection and AS9145 APQP/PPAP.
"""

# A site refuses any packaged type whose name does not start with ITS OWN configured
# prefix - GET /api/types/config reports it as `companyPrefix`. The installer payload's
# aviation stubs are "n5"; a given customer site may be anything two or three characters.
# So the prefix is an environment variable rather than a literal, and the model, the seed
# data and the package verifier all read this one value.
#
#     LIGHTJET_PREFIX=cst python model/build_customization.py
#
import os

PREFIX = os.environ.get("LIGHTJET_PREFIX", "n5").strip() or "n5"
if not 2 <= len(PREFIX) <= 3:
    raise SystemExit(f"LIGHTJET_PREFIX must be 2 or 3 characters; got {PREFIX!r}.")

COMPANY = "Light Speed Systems"
BASE = f"{PREFIX}LightSpeedSystems"   # the company type-name stem
PROGRAM = "NX-200"


def t(stem: str) -> str:
    """The registry type name for a company type stem."""
    return f"{BASE}{stem}"


# ─────────────────────────────────────────────────────────────────────────────
# Lifecycle state sets
# ─────────────────────────────────────────────────────────────────────────────
# Out-of-the-box PLMCoreAbstractModel declares Draft / In-work / Released / Obsolete. A type
# that wants a different set switches the ones it does not want off by name, the way the
# out-of-the-box ECR does, rather than leaving them live and unused.

OOTB_STATES = ["Draft", "In-work", "Released", "Obsolete"]

# Type design data under a Part 21J design organisation: the signatory step is explicit,
# because "Released" on type design data means somebody exercised a DOA privilege.
TYPE_DESIGN_STATES = [
    ("In Work",            "#607080"),
    ("In Design Review",   "#4A6FA5"),
    ("In Stress Review",   "#6A5ACD"),
    ("Airworthiness Sign-off", "#B8860B"),
    ("Released",           "#2E8B57"),
    ("Superseded",         "#8A7F6A"),
    ("Obsolete",           "#8B2828"),
]

# Items that are not type design data - tooling, consumables, vendor representatives.
SUPPORT_STATES = [
    ("Draft",     "#607080"),
    ("In Review", "#B8860B"),
    ("Active",    "#2E8B57"),
    ("Restricted", "#A0522D"),
    ("Withdrawn", "#8B2828"),
]

# A compliance demonstration tracked to closure. These are the lanes of the certification
# kanban board, so the order is the board's order.
COMPLIANCE_STATES = [
    ("Planned",          "#607080"),
    ("Method Agreed",    "#4A6FA5"),
    ("Evidence in Work", "#6A5ACD"),
    ("Submitted",        "#B8860B"),
    ("Accepted",         "#2E8B57"),
    ("Finding Open",     "#A0522D"),
    ("Closed",           "#2F6F4F"),
]

# A quality record: raised, dispositioned, closed. Shared by FAI, NCR and supplier records.
QUALITY_STATES = [
    ("Open",           "#607080"),
    ("Under Review",   "#B8860B"),
    ("Dispositioned",  "#4A6FA5"),
    ("Closed",         "#2E8B57"),
    ("Void",           "#8B2828"),
]

# A record issued once and then immutable: certificates of conformity, airworthiness
# release certificates. There is no edit path after Issued by design.
CERTIFICATE_STATES = [
    ("Draft",    "#607080"),
    ("Issued",   "#2E8B57"),
    ("Withdrawn", "#8B2828"),
]

# A publication with an effectivity and a compliance period.
PUBLICATION_STATES = [
    ("Draft",      "#607080"),
    ("In Review",  "#B8860B"),
    ("Issued",     "#2E8B57"),
    ("Superseded", "#8A7F6A"),
    ("Cancelled",  "#8B2828"),
]


def states(pairs):
    """Lifecycle rows for a state set, with the unused out-of-the-box states switched off."""
    names = [n for n, _ in pairs]
    rows = [{"name": s, "disabled": True} for s in OOTB_STATES if s not in names]
    rows += [{"name": n, "color": c, "order": i} for i, (n, c) in enumerate(pairs)]
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Shared lists of values
# ─────────────────────────────────────────────────────────────────────────────

ATA_CHAPTERS_IN_SCOPE = ["21", "23", "25"]

# CS-23 Amendment 5 and 14 CFR Part 23 Amendment 64 are the performance-based rules a light
# jet of this class is certified to; both are used with accepted means of compliance drawn
# from the ASTM F44 consensus standards. TSO/ETSO covers bought equipment approved in its
# own right. CS-25 is carried for the growth variant.
CERT_BASIS = [
    "CS-23 Amdt 5",
    "14 CFR Part 23 Amdt 64",
    "CS-23 Amdt 5 + ASTM F44 MoC",
    "ETSO authorisation",
    "FAA TSO authorisation",
    "CS-25 Amdt 27 (growth variant)",
    "Not applicable",
]

# EASA's means-of-compliance codes. A compliance item names how it will be shown, not just
# that it must be.
MEANS_OF_COMPLIANCE = [
    "MC0 - Compliance statement",
    "MC1 - Design review",
    "MC2 - Calculation / analysis",
    "MC3 - Safety assessment",
    "MC4 - Laboratory test",
    "MC5 - Ground test on aircraft",
    "MC6 - Flight test",
    "MC7 - Design inspection / audit",
    "MC8 - Equipment qualification",
    "MC9 - Simulation / modelling",
]

# ARP4754A failure effect classification. Drives the design assurance level.
FAILURE_EFFECT = [
    "Catastrophic",
    "Hazardous / Severe-Major",
    "Major",
    "Minor",
    "No Safety Effect",
]

DAL = ["A", "B", "C", "D", "E", "Not applicable"]

AIRWORTHINESS_CLASS = [
    "Flight Safety Critical",
    "Essential",
    "Non-Essential",
    "Standard Part",
    "Commercial Part",
]

EXPORT_JURISDICTION = ["None", "EAR", "ITAR", "EU Dual-Use 428/2009"]
EXPORT_CLASS = [
    "Not controlled",
    "EAR99",
    "ECCN 9A991.d",
    "ECCN 7A994",
    "ITAR USML VIII(h)",
    "EU Dual-Use 9A991",
]

# AS9100D clauses the quality records in this model are evidence for.
AS9100D_CLAUSES = [
    "8.1.2 Configuration Management",
    "8.1.3 Product Safety",
    "8.1.4 Prevention of Counterfeit Parts",
    "8.4 Externally Provided Processes",
    "8.5.1 Control of Production",
    "8.5.2 Identification and Traceability",
    "8.5.6 Control of Changes",
    "8.7 Control of Nonconforming Outputs",
    "9.2 Internal Audit",
    "10.2 Nonconformity and Corrective Action",
]

RETENTION = [
    "Type design - life of type",
    "Production record - 10 years",
    "Quality record - 7 years",
    "Airworthiness release - life of part",
    "Correspondence - 3 years",
]

CONFIDENTIALITY = ["Public", "Internal", "Confidential", "Export controlled"]

# DO-160G sections. Numbers verified against the published section list.
DO160_SECTIONS = [
    "4 Temperature and Altitude",
    "5 Temperature Variation",
    "6 Humidity",
    "7 Operational Shock and Crash Safety",
    "8 Vibration",
    "9 Explosive Atmosphere",
    "10 Waterproofness",
    "11 Fluids Susceptibility",
    "12 Sand and Dust",
    "13 Fungus Resistance",
    "14 Salt Fog",
    "15 Magnetic Effect",
    "16 Power Input",
    "17 Voltage Spike",
    "18 Audio Frequency Conducted Susceptibility",
    "19 Induced Signal Susceptibility",
    "20 Radio Frequency Susceptibility",
    "21 Emission of Radio Frequency Energy",
    "22 Lightning Induced Transient Susceptibility",
    "23 Lightning Direct Effects",
    "24 Icing",
    "25 Electrostatic Discharge",
    "26 Fire, Flammability",
]

NADCAP_FAMILIES = [
    "Chemical Processing",
    "Coatings",
    "Composites",
    "Heat Treating",
    "Materials Testing Laboratories",
    "Non-Destructive Testing",
    "Non-Conventional Machining",
    "Shot Peening",
    "Welding",
    "Sealants",
]


# ─────────────────────────────────────────────────────────────────────────────
# Attribute helper
# ─────────────────────────────────────────────────────────────────────────────

def a(name, display, kind="String", required=False, scope="Revision",
      unit=None, lov=None, default=None):
    """One attribute definition, shaped as the Engine's on-disk type JSON expects it.

    `defaultValue` is written as a JSON STRING, never a raw boolean or number. The Engine
    reads a type file through `TypeAttributeEntry`, whose `defaultValue` is `string?`; a
    raw `true` throws on deserialisation and takes the whole type file down with it.
    """
    row = {"name": name, "displayName": display, "type": kind,
           "required": required, "scope": scope}
    if unit is not None:
        row["unit"] = unit
    if lov is not None:
        row["lov"] = lov
    if default is not None:
        row["defaultValue"] = (
            "true" if default is True else
            "false" if default is False else
            str(default)
        )
    return row


# ─────────────────────────────────────────────────────────────────────────────
# Numbering schemas
# ─────────────────────────────────────────────────────────────────────────────
# A counter is keyed by the rendered skeleton of the number - every segment except the
# counter. So putting the ATA chapter in an `lov` segment ahead of the counter gives each
# chapter its own sequence, which is what an ATA-significant part number means.

def _seg(kind, value=None, lov=None, digits=None):
    row = {"type": kind, "value": value, "lovValues": lov, "digits": digits or 8}
    return row


def schema(name, description, segments):
    return {"name": name, "description": description, "segments": segments}


NUMBERING = [
    schema(
        f"{PREFIX}LssAircraftPart",
        "LSS-designed structural and mechanical parts. The ATA chapter is significant and "
        "each chapter sequences independently, e.g. LSS-21-0014.",
        [_seg("prefix", "LSS"), _seg("separator", "-"),
         _seg("lov", lov=ATA_CHAPTERS_IN_SCOPE), _seg("separator", "-"),
         _seg("counter", digits=4)],
    ),
    schema(
        f"{PREFIX}LssInstallation",
        "Installation items - the ATA installation that puts equipment on the aircraft, "
        "e.g. LSS-21-INST-003.",
        [_seg("prefix", "LSS"), _seg("separator", "-"),
         _seg("lov", lov=ATA_CHAPTERS_IN_SCOPE), _seg("separator", "-"),
         _seg("fixed", "INST"), _seg("separator", "-"), _seg("counter", digits=3)],
    ),
    schema(
        f"{PREFIX}LssElectricalPart",
        "LSS-designed electrical and avionics line-replaceable items, e.g. LSS-E-00042.",
        [_seg("prefix", "LSS-E"), _seg("separator", "-"), _seg("counter", digits=5)],
    ),
    schema(
        f"{PREFIX}LssInteriorPart",
        "Cabin furnishings and trim, e.g. LSS-F-00117.",
        [_seg("prefix", "LSS-F"), _seg("separator", "-"), _seg("counter", digits=5)],
    ),
    schema(
        f"{PREFIX}LssHarness",
        "Wiring harnesses, ATA-significant, e.g. LSS-W23-007.",
        [_seg("prefix", "LSS-W"), _seg("lov", lov=ATA_CHAPTERS_IN_SCOPE),
         _seg("separator", "-"), _seg("counter", digits=3)],
    ),
    schema(
        f"{PREFIX}LssSoftwareItem",
        "Airborne software configuration items under DO-178C, e.g. LSS-SW-0005.",
        [_seg("prefix", "LSS-SW"), _seg("separator", "-"), _seg("counter", digits=4)],
    ),
    schema(
        f"{PREFIX}LssAehItem",
        "Airborne electronic hardware items under DO-254, e.g. LSS-HW-0003.",
        [_seg("prefix", "LSS-HW"), _seg("separator", "-"), _seg("counter", digits=4)],
    ),
    schema(
        f"{PREFIX}LssStandardPart",
        "Aerospace standard parts. The number is a cross-reference; the industry "
        "designation is held in the standardNumber attribute. e.g. LSS-STD-00231.",
        [_seg("prefix", "LSS-STD"), _seg("separator", "-"), _seg("counter", digits=5)],
    ),
    schema(
        f"{PREFIX}LssVendorPart",
        "Supplier-designed bought items, e.g. LSS-V-00088.",
        [_seg("prefix", "LSS-V"), _seg("separator", "-"), _seg("counter", digits=5)],
    ),
    schema(
        f"{PREFIX}LssTooling",
        "Production tooling, fixtures and ground support equipment, e.g. LSS-TL-0042.",
        [_seg("prefix", "LSS-TL"), _seg("separator", "-"), _seg("counter", digits=4)],
    ),
    schema(
        f"{PREFIX}LssConsumable",
        "Sealants, adhesives, finishes and fluids, e.g. LSS-CM-0019.",
        [_seg("prefix", "LSS-CM"), _seg("separator", "-"), _seg("counter", digits=4)],
    ),
    schema(
        f"{PREFIX}LssDrawing",
        "Engineering drawings, ATA-significant, e.g. LSS-DWG-25-0031.",
        [_seg("prefix", "LSS-DWG"), _seg("separator", "-"),
         _seg("lov", lov=ATA_CHAPTERS_IN_SCOPE), _seg("separator", "-"),
         _seg("counter", digits=4)],
    ),
    schema(
        f"{PREFIX}LssSpecification",
        "Specifications, sequenced per class: design, material, process, test, procurement, "
        "software requirements. e.g. LSS-SPEC-PRC-012.",
        [_seg("prefix", "LSS-SPEC"), _seg("separator", "-"),
         _seg("lov", lov=["DES", "MAT", "PRC", "TST", "PRO", "SRS"]),
         _seg("separator", "-"), _seg("counter", digits=3)],
    ),
    schema(
        f"{PREFIX}LssInterfaceControl",
        "Interface control documents, e.g. LSS-ICD-014.",
        [_seg("prefix", "LSS-ICD"), _seg("separator", "-"), _seg("counter", digits=3)],
    ),
    schema(
        f"{PREFIX}LssCertificationDoc",
        "Certification deliverables, sequenced per kind: plan, compliance report, safety "
        "assessment, qualification, software/AEH plan, EMI report. e.g. LSS-CERT-COMP-021.",
        [_seg("prefix", "LSS-CERT"), _seg("separator", "-"),
         _seg("lov", lov=["PLAN", "COMP", "SAFE", "QUAL", "SWP", "EMI"]),
         _seg("separator", "-"), _seg("counter", digits=3)],
    ),
    schema(
        f"{PREFIX}LssQualityRecord",
        "Quality records, sequenced per kind: first article, nonconformance, certificate of "
        "conformity, airworthiness release, supplier approval, concession, corrective "
        "action and inspection record. e.g. LSS-NCR-00117.",
        [_seg("prefix", "LSS"), _seg("separator", "-"),
         _seg("lov", lov=["FAI", "NCR", "COC", "ARC", "SQR",
                          # A concession and a corrective action are each a record in
                          # their own right rather than fields on a nonconformance, so
                          # they sequence here beside it (NI-00000595, NI-00000570).
                          "CON", "CAR", "INSP"]),
         _seg("separator", "-"), _seg("counter", digits=5)],
    ),
    schema(
        f"{PREFIX}LssSubstantiation",
        "Structural substantiation and analysis reports, sequenced per discipline: static, "
        "fatigue, damage tolerance, flutter, loads, thermal. e.g. LSS-STR-FAT-0007.",
        [_seg("prefix", "LSS-STR"), _seg("separator", "-"),
         _seg("lov", lov=["STAT", "FAT", "DT", "FLUT", "LOAD", "THRM", "MECH"]),
         _seg("separator", "-"), _seg("counter", digits=4)],
    ),
    schema(
        f"{PREFIX}LssSerialisedUnit",
        "As-built serialised units - the physical article, as distinct from the part "
        "definition it was built to. e.g. LSS-SN-000142.",
        [_seg("prefix", "LSS-SN"), _seg("separator", "-"), _seg("counter", digits=6)],
    ),
    schema(
        f"{PREFIX}LssInServiceRecord",
        "Continued-airworthiness records against a delivered airframe, sequenced per kind: "
        "in-service occurrence, inspection finding, operator compliance return. "
        "e.g. LSS-ISR-OCC-0031.",
        [_seg("prefix", "LSS-ISR"), _seg("separator", "-"),
         _seg("lov", lov=["OCC", "FIND", "COMP"]),
         _seg("separator", "-"), _seg("counter", digits=4)],
    ),
    schema(
        f"{PREFIX}LssPublication",
        "Publications issued to operators and crews, sequenced per kind: airworthiness "
        "limitation, flight manual supplement, maintenance programme, maintenance task, "
        "instructions for continued airworthiness. e.g. LSS-PUB-ALS-0002.",
        [_seg("prefix", "LSS-PUB"), _seg("separator", "-"),
         _seg("lov", lov=["ALS", "AFMS", "MP", "MPTASK", "ICA"]),
         _seg("separator", "-"), _seg("counter", digits=4)],
    ),
    schema(
        f"{PREFIX}LssCertificationFinding",
        "Findings, observations and published limitations raised by the authority or by a "
        "delegated representative. e.g. LSS-CF-0014.",
        [_seg("prefix", "LSS-CF"), _seg("separator", "-"), _seg("counter", digits=4)],
    ),
    schema(
        f"{PREFIX}LssServiceBulletin",
        "Service bulletins, ATA-significant, e.g. LSS-SB-21-004.",
        [_seg("prefix", "LSS-SB"), _seg("separator", "-"),
         _seg("lov", lov=ATA_CHAPTERS_IN_SCOPE), _seg("separator", "-"),
         _seg("counter", digits=3)],
    ),
    schema(
        f"{PREFIX}LssProcessSpec",
        "Special process specifications, e.g. LSS-PS-0024.",
        [_seg("prefix", "LSS-PS"), _seg("separator", "-"), _seg("counter", digits=4)],
    ),
    schema(
        f"{PREFIX}LssAircraft",
        "Individual airframes, by manufacturer serial number, e.g. LSS-AC-002.",
        [_seg("prefix", "LSS-AC"), _seg("separator", "-"), _seg("counter", digits=3)],
    ),
    schema(
        f"{PREFIX}LssMaterial",
        "Qualified materials, e.g. LSS-MAT-00009.",
        [_seg("prefix", "LSS-MAT"), _seg("separator", "-"), _seg("counter", digits=5)],
    ),
    schema(
        f"{PREFIX}LssRequirement",
        "Requirements, sequenced per level: aircraft, operator, system, subsystem, "
        "component and certification. The level is in the number because a requirement's "
        "level is how it is read in a review, e.g. LSS-REQ-SYS-0012.",
        [_seg("prefix", "LSS-REQ"), _seg("separator", "-"),
         _seg("lov", lov=["ACFT", "OPS", "SYS", "SUB", "CMP", "CERT"]),
         _seg("separator", "-"), _seg("counter", digits=4)],
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# Groups
# ─────────────────────────────────────────────────────────────────────────────

GROUPS = [
    ("LSS Design Engineering",
     "Airframe, systems and interiors design authority for the NX-200."),
    ("LSS Systems Engineering",
     "Requirements, architecture and interface ownership across ATA systems."),
    ("LSS Stress and Loads",
     "Structural substantiation; signs off static, fatigue and damage tolerance."),
    ("LSS Airworthiness and Certification",
     "Part 21 Subpart J design organisation signatories. Only this group may release type "
     "design data or accept a means-of-compliance demonstration."),
    ("LSS Quality Assurance",
     "AS9100D quality management system owner; first article and nonconformance authority."),
    ("LSS Manufacturing Engineering",
     "Build definition, tooling and special process control."),
    ("LSS Supply Chain",
     "Supplier approval, flowdown and obsolescence management."),
    ("LSS Change Control Board",
     "Dispositions engineering change requests against cost, weight, schedule and "
     "certification impact."),
    ("LSS Material Review Board",
     "Dispositions nonconforming product. Airworthiness concurrence is required for any "
     "disposition other than scrap or return to supplier."),
    ("LSS Customer Support",
     "Service bulletins, in-service reporting and continued airworthiness."),
    ("LSS Programme Management",
     "Owns the programme plan, the gate reviews and the certification schedule. Reads "
     "everything, approves nothing technical."),
    ("LSS Project Management",
     "Owns the work packages and tasks inside a project: assignment, dates, progress "
     "and the critical path."),
    ("FAA Designated Engineering Representatives",
     "Individuals delegated by the FAA to find compliance on the Administrator's behalf. "
     "A DER approves data within the limits of their delegated authority and nothing "
     "outside it, which is why this is a group of its own rather than a seat in "
     "Airworthiness."),
]


# ─────────────────────────────────────────────────────────────────────────────
# Workflows
# ─────────────────────────────────────────────────────────────────────────────

# Node types that carry a polymorphic discriminator. The workflow designer deserialises
# nodes by `$nodeType`, not by `NodeType`: without it an Approver node loads as a base
# node with no approver fields, and the designer's render map then calls a node renderer
# that does not exist - "zD is not a function or its return value is not iterable", and
# the whole page replaced by "Workflow could not be displayed".
#
# Start and End nodes carry no discriminator, which is why copying one of those as the
# template for every node hid the problem. Every out-of-the-box workflow has it on its
# Approver and Status nodes; none of these did until it crashed the designer.
DISCRIMINATED_NODES = {"Approver", "Status", "Action"}


def _node(node_id, node_type, title, row, col, **extra):
    node = {
        "Id": node_id, "NodeType": node_type, "Title": title,
        "GridRow": row, "GridColumn": col, "RowSpan": 1, "ColSpan": 1,
        "ActionKey": None, "TargetStatus": None, "Parameters": None,
        "ApproverUserIds": [], "ApproverGroupIds": [], "ApproverRoleIds": [],
        "PrivilegedUserIds": [], "PrivilegedGroupIds": [], "PrivilegedRoleIds": [],
        "ApprovalMode": None, "RequiredApprovalCount": 0,
    }
    node.update(extra)
    if node_type in DISCRIMINATED_NODES:
        # Written first in the serialised object, as the out-of-the-box files have it.
        return {"$nodeType": node_type, **node}
    return node


def _approver(node_id, title, group, row, col, mode="All", count=1, asks=None):
    """One approval gate.

    `asks` is the question the approver is actually being asked, and it is not decoration.
    The Engine puts a node's `Parameters["instruction"]` on every task it creates and into
    the notification body; with no instruction a task arrives as a title, a null
    instruction and two buttons, so the approver is asked to approve something without
    being told what approving it will do. The reporter of NI-00000586 put it exactly that
    way: "a title, a null instruction, and Approve or Reject".

    Writing the question also makes the route reviewable. An approval gate whose question
    cannot be written down in a sentence is usually a gate nobody has thought about.
    """
    parameters = {"instruction": asks} if asks else None
    return _node(node_id, "Approver", title, row, col,
                 ActionKey="approve_workflow",
                 Parameters=parameters,
                 ApproverGroupIds=[f"{{{{GROUP:{group}}}}}"],
                 ApprovalMode=mode, RequiredApprovalCount=count,
                 AssignToInitiator=False)


def _status(node_id, title, status, row, col):
    return _node(node_id, "Status", title, row, col,
                 ActionKey="change_status", TargetStatus=status)


def _conn(cid, src, dst, reject=False):
    """One connection between two nodes.

    The side names are CAPITALISED, and that is not cosmetic. The workflow designer
    resolves a connection's anchor point through a lookup keyed on "Left"/"Right"/
    "Top"/"Bottom". A lowercase "right" misses the lookup, the lookup returns undefined,
    and the designer's map over connections then tries to call it - "zD is not a
    function or its return value is not iterable", and the entire page is replaced by
    "Workflow could not be displayed".

    The route still EXECUTES correctly with lowercase sides, because the server never
    reads them: tasks were created, routed to the right groups and completed. Only the
    drawing of it breaks, which is the worst kind of bug to carry into a demonstration -
    everything works until somebody opens the picture.
    """
    return {"Id": cid, "SourceNodeId": src, "SourceSide": "Right",
            "TargetNodeId": dst, "TargetSide": "Left", "IsRejectPath": reject}


def workflow(wf_id, name, display, nodes, connections, description):
    return {
        "id": wf_id,
        "name": name,
        "displayName": display,
        "description": description,
        "isOnline": True,
        "definition": {
            "TriggerEvent": "Manual",
            "AssignedUserIds": [], "AssignedGroupIds": [],
            "AssignedRoleIds": [], "AssignedProjectIds": [],
            "Nodes": nodes,
            "Connections": connections,
        },
    }


# Deterministic ids so a re-export of the same model is byte-identical and a type's
# action can name the workflow before the workflow file is written.
WF_TYPE_DESIGN = "21a10000-0000-4000-a000-000000000001"
WF_FAI = "21a10000-0000-4000-a000-000000000002"
WF_MRB = "21a10000-0000-4000-a000-000000000003"
WF_COMPLIANCE = "21a10000-0000-4000-a000-000000000004"
WF_SUPPLIER = "21a10000-0000-4000-a000-000000000005"
WF_PUBLICATION = "21a10000-0000-4000-a000-000000000006"
WF_PROCESS_SPEC = "21a10000-0000-4000-a000-000000000007"
WF_SUBSTANTIATION = "21a10000-0000-4000-a000-000000000008"
WF_CONCESSION = "21a10000-0000-4000-a000-000000000009"
WF_FINDING = "21a10000-0000-4000-a000-00000000000a"
WF_CORRECTIVE_ACTION = "21a10000-0000-4000-a000-00000000000b"
WF_CERTIFICATE_ISSUE = "21a10000-0000-4000-a000-00000000000c"

WORKFLOWS = [
    workflow(
        WF_TYPE_DESIGN, f"{PREFIX}LssTypeDesignRelease", "Type design data release",
        [
            _node("start", "Start", "Submit for release", 2, 0),
            _approver("design", "Design check", "LSS Design Engineering", 0, 2,
                      asks='Is the definition complete and correct, and does it match the drawing? Approving sends it to stress; it does not release it.'),
            _approver("stress", "Stress substantiation", "LSS Stress and Loads", 2, 2,
                      asks='Is the structural substantiation complete, with positive margins against the critical load case? Approving sends it to airworthiness; it does not release it.'),
            _approver("airworthiness", "Airworthiness sign-off (DOA privilege)",
                      "LSS Airworthiness and Certification", 1, 4,
                      asks='Exercise the Part 21A.263 design organisation privilege: does this data comply with the certification basis? APPROVING RELEASES IT - aeroplanes may be built to it, and the only ways out afterwards are a new revision or supersession.'),
            _status("release", "Set Released", "Released", 1, 6),
            _node("end", "End", "End", 1, 8),
        ],
        [
            _conn("c1", "start", "design"),
            _conn("c2", "start", "stress"),
            _conn("c3", "design", "airworthiness"),
            _conn("c4", "stress", "airworthiness"),
            _conn("c5", "airworthiness", "release"),
            _conn("c6", "release", "end"),
            _conn("r1", "airworthiness", "start", reject=True),
        ],
        "Releases type design data. Design check and stress substantiation run in parallel; "
        "both must pass before an Airworthiness and Certification signatory exercises the "
        "Part 21A.263 design organisation privilege. A rejection returns the item to the "
        "originator with the reviewer's comment on the audit trail.",
    ),
    workflow(
        WF_FAI, f"{PREFIX}LssFaiApproval", "First article inspection approval",
        [
            _node("start", "Start", "Submit FAI", 1, 0),
            _approver("quality", "Quality review (AS9102 Forms 1-3 complete)",
                      "LSS Quality Assurance", 1, 2,
                      asks='Are AS9102 Forms 1, 2 and 3 complete, and is every ballooned characteristic accounted for? Approving sends it to manufacturing engineering.'),
            _approver("mfg", "Manufacturing engineering concurrence",
                      "LSS Manufacturing Engineering", 1, 4,
                      asks='Are the production process and tooling that made this part the ones the first article covers? Approving sets the report Dispositioned.'),
            _status("accept", "Set Dispositioned", "Dispositioned", 1, 6),
            _node("end", "End", "End", 1, 8),
        ],
        [
            _conn("c1", "start", "quality"),
            _conn("c2", "quality", "mfg"),
            _conn("c3", "mfg", "accept"),
            _conn("c4", "accept", "end"),
            _conn("r1", "quality", "start", reject=True),
        ],
        "Approves an AS9102 Rev C first article inspection. Quality confirms Forms 1, 2 and "
        "3 are complete and every ballooned characteristic is accounted for; manufacturing "
        "engineering confirms the production process and tooling that produced it are the "
        "ones the FAI covers.",
    ),
    workflow(
        WF_MRB, f"{PREFIX}LssMrbDisposition", "Material review board disposition",
        [
            _node("start", "Start", "Raise nonconformance", 1, 0),
            _approver("quality", "Quality containment review",
                      "LSS Quality Assurance", 1, 2,
                      asks='Is the nonconformance contained - suspect product identified, quarantined and bounded? Approving sends it to the material review board for disposition.'),
            _approver("mrb", "Material review board", "LSS Material Review Board", 1, 4,
                      asks='Decide the disposition: use as is, rework, repair to an approved scheme, scrap or return to supplier. Any disposition that leaves the deviation in the aeroplane needs airworthiness concurrence next, which approving will request.'),
            _approver("airworthiness", "Airworthiness concurrence",
                      "LSS Airworthiness and Certification", 1, 6,
                      asks='Does the proposed disposition leave the aeroplane compliant with the certification basis? Approving sets the nonconformance Dispositioned.'),
            _status("disposition", "Set Dispositioned", "Dispositioned", 1, 8),
            _node("end", "End", "End", 1, 10),
        ],
        [
            _conn("c1", "start", "quality"),
            _conn("c2", "quality", "mrb"),
            _conn("c3", "mrb", "airworthiness"),
            _conn("c4", "airworthiness", "disposition"),
            _conn("c5", "disposition", "end"),
            _conn("r1", "mrb", "start", reject=True),
        ],
        "Dispositions nonconforming product under AS9100D 8.7. Containment first, then the "
        "material review board decides use-as-is, rework, repair, scrap or return. Any "
        "disposition that leaves the deviation in the aircraft needs an Airworthiness and "
        "Certification signature, so the decision and the signature sit on one trail.",
    ),
    workflow(
        WF_COMPLIANCE, f"{PREFIX}LssComplianceAcceptance", "Means-of-compliance acceptance",
        [
            _node("start", "Start", "Submit evidence", 1, 0),
            _approver("systems", "Systems engineering review",
                      "LSS Systems Engineering", 0, 2,
                      asks='Is the evidence complete and does it actually demonstrate the means of compliance that was agreed? Approving offers it to certification for acceptance.'),
            _approver("airworthiness", "Certification acceptance",
                      "LSS Airworthiness and Certification", 1, 4,
                      asks='Accept this means-of-compliance demonstration under the DOA privilege. APPROVING SETS IT ACCEPTED - the only route afterwards is a finding that re-opens it.'),
            _status("accept", "Set Accepted", "Accepted", 1, 6),
            _node("end", "End", "End", 1, 8),
        ],
        [
            _conn("c1", "start", "systems"),
            _conn("c2", "systems", "airworthiness"),
            _conn("c3", "airworthiness", "accept"),
            _conn("c4", "accept", "end"),
            _conn("r1", "airworthiness", "start", reject=True),
        ],
        "Accepts the evidence offered against one certification requirement. The route "
        "records which means of compliance (MC0-MC9) was used and who accepted it, which is "
        "what the compliance checklist is later audited against.",
    ),
    workflow(
        WF_SUPPLIER, f"{PREFIX}LssSupplierPartApproval", "Supplier part source approval",
        [
            _node("start", "Start", "Request source approval", 1, 0),
            _approver("supply", "Supply chain review", "LSS Supply Chain", 0, 2,
                      asks="Is the supplier's qualification evidence complete - audit, capability, flowdown accepted? Approving sends it to quality."),
            _approver("quality", "Quality approval (AS9100D 8.4)",
                      "LSS Quality Assurance", 2, 2,
                      asks='Does this supplier meet the AS9100D 8.4 control requirements for the scope being approved? Approving sends it to engineering for technical acceptance.'),
            _approver("engineering", "Engineering technical acceptance",
                      "LSS Design Engineering", 1, 4,
                      asks='Can this supplier make the parts to the drawing and the special-process specifications? Approving adds them to the approved source list.'),
            _status("approve", "Set Active", "Active", 1, 6),
            _node("end", "End", "End", 1, 8),
        ],
        [
            _conn("c1", "start", "supply"),
            _conn("c2", "start", "quality"),
            _conn("c3", "supply", "engineering"),
            _conn("c4", "quality", "engineering"),
            _conn("c5", "engineering", "approve"),
            _conn("c6", "approve", "end"),
            _conn("r1", "quality", "start", reject=True),
        ],
        "Approves a source for a bought item. Supply chain confirms the commercial and "
        "obsolescence position, quality confirms the AS9100D 8.4 external provider controls "
        "and the counterfeit-parts safeguards of 8.1.4, and engineering accepts the part "
        "technically.",
    ),
    workflow(
        WF_PUBLICATION, f"{PREFIX}LssPublicationIssue", "Publication issue",
        [
            _node("start", "Start", "Submit for issue", 1, 0),
            _approver("support", "Customer support review",
                      "LSS Customer Support", 0, 2,
                      asks='Are the embodiment instructions, effectivity and compliance period correct and achievable by an operator? Approving sends it to airworthiness.'),
            _approver("airworthiness", "Airworthiness approval",
                      "LSS Airworthiness and Certification", 1, 4,
                      asks='Approve this publication for issue to operators under the DOA privilege. APPROVING ISSUES IT - it becomes the instruction the fleet works to, and a mandatory bulletin carries a compliance period.'),
            _status("issue", "Set Issued", "Issued", 1, 6),
            _node("end", "End", "End", 1, 8),
        ],
        [
            _conn("c1", "start", "support"),
            _conn("c2", "support", "airworthiness"),
            _conn("c3", "airworthiness", "issue"),
            _conn("c4", "issue", "end"),
            _conn("r1", "airworthiness", "start", reject=True),
        ],
        "Issues a service bulletin or other continued-airworthiness publication. A mandatory "
        "bulletin carries an airworthiness signature because operators act on it.",
    ),
    workflow(
        WF_PROCESS_SPEC, f"{PREFIX}LssProcessSpecApproval", "Special process approval",
        [
            _node("start", "Start", "Submit for approval", 1, 0),
            _approver("process", "Process owner review",
                      "LSS Manufacturing Engineering", 0, 2,
                      asks="Are the parameters, their limits and the qualification evidence "
                           "complete, and is the process capable at those limits? Approving "
                           "sends it to quality."),
            _approver("quality", "Quality approval (NADCAP scope)",
                      "LSS Quality Assurance", 2, 2,
                      asks="Is the process under control - operator approval, equipment "
                           "calibration, periodic re-qualification, and NADCAP accreditation "
                           "where the specification requires it? Approving sends it to "
                           "airworthiness."),
            _approver("airworthiness", "Airworthiness approval",
                      "LSS Airworthiness and Certification", 1, 4,
                      asks="A special process is one whose result cannot be verified by "
                           "inspecting the part afterwards, so releasing it accepts the "
                           "parameters AS the evidence of conformity. Does that hold? "
                           "APPROVING RELEASES IT."),
            _status("release", "Set Released", "Released", 1, 6),
            _node("end", "End", "End", 1, 8),
        ],
        [
            _conn("c1", "start", "process"),
            _conn("c2", "start", "quality"),
            _conn("c3", "process", "airworthiness"),
            _conn("c4", "quality", "airworthiness"),
            _conn("c5", "airworthiness", "release"),
            _conn("c6", "release", "end"),
            _conn("r1", "airworthiness", "start", reject=True),
        ],
        "Approves a special process specification. The manufacturing engineer could not "
        "invoke any action on a process specification at all - every declared action "
        "answered 422 no_workflow_bound and the object was frozen - so release was a bare "
        "status flip with no approver and no trail (NI-00000567, NI-00000689). That is the "
        "wrong shape for this type in particular: a special process is defined as one whose "
        "result cannot be verified by inspecting the finished part, so the approved "
        "parameters ARE the evidence of conformity and who approved them is the whole "
        "record.",
    ),
    workflow(
        WF_SUBSTANTIATION, f"{PREFIX}LssSubstantiationRelease", "Substantiation release",
        [
            _node("start", "Start", "Submit substantiation", 1, 0),
            _approver("check", "Independent stress check",
                      "LSS Stress and Loads", 0, 2,
                      asks="Independently check the analysis: method, load cases, "
                           "allowables basis and the arithmetic. This is a CHECK, not a "
                           "review - it must be someone other than the author, and the "
                           "minimum margin is the number to confirm."),
            _approver("design", "Design acceptance",
                      "LSS Design Engineering", 2, 2,
                      asks="Does the substantiated configuration match the design as "
                           "defined, and can any inspection threshold or life limit it "
                           "imposes actually be met in service?"),
            _approver("airworthiness", "Airworthiness sign-off (DOA privilege)",
                      "LSS Airworthiness and Certification", 1, 4,
                      asks="Accept this as compliance evidence for the structural "
                           "paragraphs of the certification basis. APPROVING RELEASES IT, "
                           "and any inspection threshold or life limit it carries has to "
                           "reach the airworthiness limitations section."),
            _status("release", "Set Released", "Released", 1, 6),
            _node("end", "End", "End", 1, 8),
        ],
        [
            _conn("c1", "start", "check"),
            _conn("c2", "start", "design"),
            _conn("c3", "check", "airworthiness"),
            _conn("c4", "design", "airworthiness"),
            _conn("c5", "airworthiness", "release"),
            _conn("c6", "release", "end"),
            _conn("r1", "airworthiness", "start", reject=True),
        ],
        "Releases a structural substantiation. The independent check comes first and is "
        "separate from the review on purpose: an unchecked stress analysis is not evidence, "
        "and the one thing the platform cannot yet enforce is that the checker is not the "
        "author - which is why the gate's question says so in words.",
    ),
    workflow(
        WF_CONCESSION, f"{PREFIX}LssConcessionApproval", "Concession approval",
        [
            _node("start", "Start", "Raise concession", 1, 0),
            _approver("engineering", "Engineering justification",
                      "LSS Design Engineering", 0, 2,
                      asks="Is the departure technically acceptable, and is the "
                           "justification one that would survive being read back in two "
                           "years? State the effect on fit, form, function and life."),
            _approver("quality", "Quality control of the concession",
                      "LSS Quality Assurance", 2, 2,
                      asks="Are the quantity, serial range and expiry bounded and "
                           "enforceable? An open-ended concession is a finding in any "
                           "audit."),
            _approver("airworthiness", "Airworthiness concurrence",
                      "LSS Airworthiness and Certification", 1, 4,
                      asks="Does the aeroplane remain compliant with the certification "
                           "basis with this departure embodied? APPROVING AUTHORISES THE "
                           "DEPARTURE for the stated effectivity."),
            _status("approve", "Set Dispositioned", "Dispositioned", 1, 6),
            _node("end", "End", "End", 1, 8),
        ],
        [
            _conn("c1", "start", "engineering"),
            _conn("c2", "start", "quality"),
            _conn("c3", "engineering", "airworthiness"),
            _conn("c4", "quality", "airworthiness"),
            _conn("c5", "airworthiness", "approve"),
            _conn("c6", "approve", "end"),
            _conn("r1", "airworthiness", "start", reject=True),
        ],
        "Authorises a deviation or waiver. It was two values in a nonconformance's "
        "disposition list, so a departure from the approved design could be authorised with "
        "no route, no named approver, no effectivity and no expiry (NI-00000595).",
    ),
    workflow(
        WF_FINDING, f"{PREFIX}LssFindingClosure", "Finding closure",
        [
            _node("start", "Start", "Submit response", 1, 0),
            _approver("discipline", "Discipline response review",
                      "LSS Systems Engineering", 0, 2,
                      asks="Does the response actually address the finding, with evidence? "
                           "A response that restates the position without new evidence "
                           "will be returned by the authority."),
            _approver("airworthiness", "Closure recommendation",
                      "LSS Airworthiness and Certification", 1, 4,
                      asks="Is this ready to put to the authority as a closure proposal, "
                           "and does it say plainly what certification credit is affected? "
                           "Approving records the closure basis."),
            _status("close", "Set Closed", "Closed", 1, 6),
            _node("end", "End", "End", 1, 8),
        ],
        [
            _conn("c1", "start", "discipline"),
            _conn("c2", "discipline", "airworthiness"),
            _conn("c3", "airworthiness", "close"),
            _conn("c4", "close", "end"),
            _conn("r1", "airworthiness", "start", reject=True),
        ],
        "Closes out a certification finding. The applicant responds, the response is "
        "reviewed by the discipline it concerns, and airworthiness decides whether it is "
        "fit to put to the authority. The finding itself is the authority's instrument, so "
        "nothing here closes it unilaterally - it records the basis on which closure is "
        "proposed.",
    ),
    workflow(
        WF_CORRECTIVE_ACTION, f"{PREFIX}LssCorrectiveActionClosure",
        "Corrective action closure",
        [
            _node("start", "Start", "Submit for closure", 1, 0),
            _approver("owner", "Action owner confirmation",
                      "LSS Manufacturing Engineering", 0, 2,
                      asks="Has the action been implemented as written, and is the "
                           "preventive action in place rather than merely planned?"),
            _approver("quality", "Effectiveness verification",
                      "LSS Quality Assurance", 1, 4,
                      asks="Has effectiveness been VERIFIED by the declared method, with "
                           "evidence? This is the gate that separates a corrective action "
                           "from an intention - do not approve on the strength of the "
                           "action having been done."),
            _status("close", "Set Closed", "Closed", 1, 6),
            _node("end", "End", "End", 1, 8),
        ],
        [
            _conn("c1", "start", "owner"),
            _conn("c2", "owner", "quality"),
            _conn("c3", "quality", "close"),
            _conn("c4", "close", "end"),
            _conn("r1", "quality", "start", reject=True),
        ],
        "Closes an AS9100D corrective action. A nonconformance could be dispositioned and "
        "closed with its corrective action pointing at nothing, and nothing anywhere said "
        "whether the action had worked (NI-00000570). Effectiveness verification is its own "
        "gate because that is the step that gets skipped.",
    ),
    workflow(
        WF_CERTIFICATE_ISSUE, f"{PREFIX}LssCertificateIssue", "Certificate issue",
        [
            _node("start", "Start", "Submit for issue", 1, 0),
            _approver("quality", "Quality verification",
                      "LSS Quality Assurance", 0, 2,
                      asks="Does the certificate match the purchase order and the "
                           "flowed-down requirements, and is every statement on it "
                           "supported? Approving sends it for signature."),
            _approver("airworthiness", "Authorised signature",
                      "LSS Airworthiness and Certification", 1, 4,
                      asks="Sign this certificate under the organisation's privilege. "
                           "APPROVING ISSUES IT, and an issued certificate is immutable - "
                           "the lifecycle has no route back out of Issued, only "
                           "withdrawal."),
            _status("issue", "Set Issued", "Issued", 1, 6),
            _node("end", "End", "End", 1, 8),
        ],
        [
            _conn("c1", "start", "quality"),
            _conn("c2", "quality", "airworthiness"),
            _conn("c3", "airworthiness", "issue"),
            _conn("c4", "issue", "end"),
            _conn("r1", "airworthiness", "start", reject=True),
        ],
        "Issues a certificate of conformity or an airworthiness release certificate. Both "
        "had an Issued state that only a signatory could enter and NO action to reach it, "
        "so the only way to issue either was a direct status change - on the two documents "
        "whose entire purpose is to carry a signature. Found by a model invariant rather "
        "than by a role agent, which is the point of having the invariant.",
    ),
]
