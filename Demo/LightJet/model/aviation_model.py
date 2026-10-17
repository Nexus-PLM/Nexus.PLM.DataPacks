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

PREFIX = "n5"
COMPANY = "Light Speed Systems"
BASE = "n5LightSpeedSystems"          # the existing company type-name stem
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
        "n5LssAircraftPart",
        "LSS-designed structural and mechanical parts. The ATA chapter is significant and "
        "each chapter sequences independently, e.g. LSS-21-0014.",
        [_seg("prefix", "LSS"), _seg("separator", "-"),
         _seg("lov", lov=ATA_CHAPTERS_IN_SCOPE), _seg("separator", "-"),
         _seg("counter", digits=4)],
    ),
    schema(
        "n5LssInstallation",
        "Installation items - the ATA installation that puts equipment on the aircraft, "
        "e.g. LSS-21-INST-003.",
        [_seg("prefix", "LSS"), _seg("separator", "-"),
         _seg("lov", lov=ATA_CHAPTERS_IN_SCOPE), _seg("separator", "-"),
         _seg("fixed", "INST"), _seg("separator", "-"), _seg("counter", digits=3)],
    ),
    schema(
        "n5LssElectricalPart",
        "LSS-designed electrical and avionics line-replaceable items, e.g. LSS-E-00042.",
        [_seg("prefix", "LSS-E"), _seg("separator", "-"), _seg("counter", digits=5)],
    ),
    schema(
        "n5LssInteriorPart",
        "Cabin furnishings and trim, e.g. LSS-F-00117.",
        [_seg("prefix", "LSS-F"), _seg("separator", "-"), _seg("counter", digits=5)],
    ),
    schema(
        "n5LssHarness",
        "Wiring harnesses, ATA-significant, e.g. LSS-W23-007.",
        [_seg("prefix", "LSS-W"), _seg("lov", lov=ATA_CHAPTERS_IN_SCOPE),
         _seg("separator", "-"), _seg("counter", digits=3)],
    ),
    schema(
        "n5LssSoftwareItem",
        "Airborne software configuration items under DO-178C, e.g. LSS-SW-0005.",
        [_seg("prefix", "LSS-SW"), _seg("separator", "-"), _seg("counter", digits=4)],
    ),
    schema(
        "n5LssAehItem",
        "Airborne electronic hardware items under DO-254, e.g. LSS-HW-0003.",
        [_seg("prefix", "LSS-HW"), _seg("separator", "-"), _seg("counter", digits=4)],
    ),
    schema(
        "n5LssStandardPart",
        "Aerospace standard parts. The number is a cross-reference; the industry "
        "designation is held in the standardNumber attribute. e.g. LSS-STD-00231.",
        [_seg("prefix", "LSS-STD"), _seg("separator", "-"), _seg("counter", digits=5)],
    ),
    schema(
        "n5LssVendorPart",
        "Supplier-designed bought items, e.g. LSS-V-00088.",
        [_seg("prefix", "LSS-V"), _seg("separator", "-"), _seg("counter", digits=5)],
    ),
    schema(
        "n5LssTooling",
        "Production tooling, fixtures and ground support equipment, e.g. LSS-TL-0042.",
        [_seg("prefix", "LSS-TL"), _seg("separator", "-"), _seg("counter", digits=4)],
    ),
    schema(
        "n5LssConsumable",
        "Sealants, adhesives, finishes and fluids, e.g. LSS-CM-0019.",
        [_seg("prefix", "LSS-CM"), _seg("separator", "-"), _seg("counter", digits=4)],
    ),
    schema(
        "n5LssDrawing",
        "Engineering drawings, ATA-significant, e.g. LSS-DWG-25-0031.",
        [_seg("prefix", "LSS-DWG"), _seg("separator", "-"),
         _seg("lov", lov=ATA_CHAPTERS_IN_SCOPE), _seg("separator", "-"),
         _seg("counter", digits=4)],
    ),
    schema(
        "n5LssSpecification",
        "Specifications, sequenced per class: design, material, process, test, procurement, "
        "software requirements. e.g. LSS-SPEC-PRC-012.",
        [_seg("prefix", "LSS-SPEC"), _seg("separator", "-"),
         _seg("lov", lov=["DES", "MAT", "PRC", "TST", "PRO", "SRS"]),
         _seg("separator", "-"), _seg("counter", digits=3)],
    ),
    schema(
        "n5LssInterfaceControl",
        "Interface control documents, e.g. LSS-ICD-014.",
        [_seg("prefix", "LSS-ICD"), _seg("separator", "-"), _seg("counter", digits=3)],
    ),
    schema(
        "n5LssCertificationDoc",
        "Certification deliverables, sequenced per kind: plan, compliance report, safety "
        "assessment, qualification, software/AEH plan, EMI report. e.g. LSS-CERT-COMP-021.",
        [_seg("prefix", "LSS-CERT"), _seg("separator", "-"),
         _seg("lov", lov=["PLAN", "COMP", "SAFE", "QUAL", "SWP", "EMI"]),
         _seg("separator", "-"), _seg("counter", digits=3)],
    ),
    schema(
        "n5LssQualityRecord",
        "Quality records, sequenced per kind: first article, nonconformance, certificate of "
        "conformity, airworthiness release, supplier approval. e.g. LSS-NCR-00117.",
        [_seg("prefix", "LSS"), _seg("separator", "-"),
         _seg("lov", lov=["FAI", "NCR", "COC", "ARC", "SQR"]),
         _seg("separator", "-"), _seg("counter", digits=5)],
    ),
    schema(
        "n5LssServiceBulletin",
        "Service bulletins, ATA-significant, e.g. LSS-SB-21-004.",
        [_seg("prefix", "LSS-SB"), _seg("separator", "-"),
         _seg("lov", lov=ATA_CHAPTERS_IN_SCOPE), _seg("separator", "-"),
         _seg("counter", digits=3)],
    ),
    schema(
        "n5LssProcessSpec",
        "Special process specifications, e.g. LSS-PS-0024.",
        [_seg("prefix", "LSS-PS"), _seg("separator", "-"), _seg("counter", digits=4)],
    ),
    schema(
        "n5LssRequirement",
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
]


# ─────────────────────────────────────────────────────────────────────────────
# Workflows
# ─────────────────────────────────────────────────────────────────────────────

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
    return node


def _approver(node_id, title, group, row, col, mode="All", count=1):
    return _node(node_id, "Approver", title, row, col,
                 ActionKey="approve_workflow",
                 ApproverGroupIds=[f"{{{{GROUP:{group}}}}}"],
                 ApprovalMode=mode, RequiredApprovalCount=count,
                 AssignToInitiator=False)


def _status(node_id, title, status, row, col):
    return _node(node_id, "Status", title, row, col,
                 ActionKey="change_status", TargetStatus=status)


def _conn(cid, src, dst, reject=False):
    return {"Id": cid, "SourceNodeId": src, "SourceSide": "right",
            "TargetNodeId": dst, "TargetSide": "left", "IsRejectPath": reject}


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

WORKFLOWS = [
    workflow(
        WF_TYPE_DESIGN, "n5LssTypeDesignRelease", "Type design data release",
        [
            _node("start", "Start", "Submit for release", 2, 0),
            _approver("design", "Design check", "LSS Design Engineering", 0, 2),
            _approver("stress", "Stress substantiation", "LSS Stress and Loads", 2, 2),
            _approver("airworthiness", "Airworthiness sign-off (DOA privilege)",
                      "LSS Airworthiness and Certification", 1, 4),
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
        WF_FAI, "n5LssFaiApproval", "First article inspection approval",
        [
            _node("start", "Start", "Submit FAI", 1, 0),
            _approver("quality", "Quality review (AS9102 Forms 1-3 complete)",
                      "LSS Quality Assurance", 1, 2),
            _approver("mfg", "Manufacturing engineering concurrence",
                      "LSS Manufacturing Engineering", 1, 4),
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
        WF_MRB, "n5LssMrbDisposition", "Material review board disposition",
        [
            _node("start", "Start", "Raise nonconformance", 1, 0),
            _approver("quality", "Quality containment review",
                      "LSS Quality Assurance", 1, 2),
            _approver("mrb", "Material review board", "LSS Material Review Board", 1, 4),
            _approver("airworthiness", "Airworthiness concurrence",
                      "LSS Airworthiness and Certification", 1, 6),
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
        WF_COMPLIANCE, "n5LssComplianceAcceptance", "Means-of-compliance acceptance",
        [
            _node("start", "Start", "Submit evidence", 1, 0),
            _approver("systems", "Systems engineering review",
                      "LSS Systems Engineering", 0, 2),
            _approver("airworthiness", "Certification acceptance",
                      "LSS Airworthiness and Certification", 1, 4),
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
        WF_SUPPLIER, "n5LssSupplierPartApproval", "Supplier part source approval",
        [
            _node("start", "Start", "Request source approval", 1, 0),
            _approver("supply", "Supply chain review", "LSS Supply Chain", 0, 2),
            _approver("quality", "Quality approval (AS9100D 8.4)",
                      "LSS Quality Assurance", 2, 2),
            _approver("engineering", "Engineering technical acceptance",
                      "LSS Design Engineering", 1, 4),
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
        WF_PUBLICATION, "n5LssPublicationIssue", "Publication issue",
        [
            _node("start", "Start", "Submit for issue", 1, 0),
            _approver("support", "Customer support review",
                      "LSS Customer Support", 0, 2),
            _approver("airworthiness", "Airworthiness approval",
                      "LSS Airworthiness and Certification", 1, 4),
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
]
