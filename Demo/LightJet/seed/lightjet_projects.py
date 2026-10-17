"""The NX-200 programme, its projects, and the work breakdown beneath them.

Two layers, because they are different things in this platform and the demo should not
blur them:

* A **project** is a security and membership container (`ProjectRecord`). Objects are
  assigned to it, and membership decides who sees what. Three of them here: the type
  certification programme, the ATA 21 development project, and the cabin completion
  project the launch operator's interior runs through.

* A **work breakdown** is schedule data - `Program`, `Phase`, `Milestone`, `WorkPackage`
  and `Task` objects joined by WBS links. These are out-of-the-box types, so the demo uses
  the platform's own schedule objects rather than company copies.

Phases follow an AS9145 APQP shape, because that is the structure an aerospace audience
expects a development programme to be run to: planning, product design and development,
process design and development, product and process validation, then production and
continuous improvement. Gate reviews sit on the phase boundaries, and the certification
milestones are the ones that actually gate the programme.
"""

from lightjet_data import PROGRAMME, ROOT_FOLDER

# ─────────────────────────────────────────────────────────────────────────────
# Projects - membership and visibility containers
# ─────────────────────────────────────────────────────────────────────────────

PROJECTS = [
    {
        "id": "a1000000-0000-4000-a000-000000000001",
        "name": f"{PROGRAMME} Type Certification",
        "description":
            "The EASA type certification programme for the NX-200 light jet, under "
            "certification basis CS-23 Amendment 5 with ASTM F44 consensus standards as "
            "the accepted means of compliance. Holds the certification plan, the "
            "compliance items, the safety assessments and the qualification evidence.",
        "type": "Internal",
        "status": "Active",
        "memberGroups": ["LSS Airworthiness and Certification", "LSS Systems Engineering",
                         "LSS Design Engineering", "LSS Stress and Loads",
                         # Without these two the programme and project managers were 403
                         # on every compliance item and every change they are
                         # accountable for - found by the project manager agent.
                         "LSS Programme Management", "LSS Project Management"],
        "privilegedGroups": ["LSS Airworthiness and Certification"],
    },
    {
        "id": "a1000000-0000-4000-a000-000000000002",
        "name": f"{PROGRAMME} ATA 21 Environmental Control System",
        "description":
            "Design, qualification and certification of the environmental control and "
            "pressurisation system, ATA chapter 21. Includes the bleed air supply, the "
            "cooling pack, cabin distribution, the digital controller and its software, "
            "and the pressurisation control and protection subsystems.",
        "type": "Internal",
        "status": "Active",
        "memberGroups": ["LSS Design Engineering", "LSS Systems Engineering",
                         "LSS Stress and Loads", "LSS Manufacturing Engineering",
                         "LSS Supply Chain",
                         "LSS Programme Management", "LSS Project Management",
                         # The fleet role has to read what is installed before it can
                         # say whether a change reaches a delivered aeroplane.
                         "LSS Customer Support",
                         # And the signatory has to read the type design data it signs.
                         # The DER was 403 on every object she was there to approve.
                         "LSS Airworthiness and Certification",
                         # Quality's own first article records are written against these
                         # parts; it was 403 on every one of them.
                         "LSS Quality Assurance", "LSS Material Review Board"],
        "privilegedGroups": ["LSS Design Engineering"],
    },
    {
        "id": "a1000000-0000-4000-a000-000000000003",
        "name": f"{PROGRAMME} Cabin Completion - Meridian Executive Charter",
        "description":
            "The launch operator's cabin configuration: club four seating with the swivel "
            "interlock, the forward divider and credenza variant, and the trim and finish "
            "selections. Membership is deliberately narrow because the configuration is "
            "commercially sensitive to the operator.",
        "type": "External",
        "status": "Active",
        "memberGroups": ["LSS Design Engineering", "LSS Customer Support",
                         "LSS Quality Assurance",
                         "LSS Programme Management", "LSS Project Management",
                         "LSS Airworthiness and Certification"],
        "privilegedGroups": ["LSS Customer Support"],
    },
]

# Which project each part number belongs to. Objects not listed stay unassigned, which is
# correct for a shared standard part or a consumable - it belongs to no one project.
PROJECT_ASSIGNMENT = {
    "a1000000-0000-4000-a000-000000000001": [
        "LSS-CERT-PLAN-001", "LSS-CERT-PLAN-002",
        "LSS-CERT-SAFE-001", "LSS-CERT-SAFE-002", "LSS-CERT-SAFE-003",
        "LSS-CERT-SAFE-004", "LSS-CERT-SAFE-005",
        "LSS-CERT-QUAL-012", "LSS-CERT-QUAL-001", "LSS-CERT-QUAL-002",
        "LSS-CERT-QUAL-003", "LSS-CERT-QUAL-004", "LSS-CERT-QUAL-005",
        "LSS-CERT-QUAL-006", "LSS-CERT-QUAL-007", "LSS-CERT-QUAL-008",
        "LSS-CERT-QUAL-009", "LSS-CERT-QUAL-010", "LSS-CERT-QUAL-011",
        "LSS-CERT-EMI-001", "LSS-CERT-EMI-002",
        "LSS-CERT-SWP-001", "LSS-CERT-SWP-002", "LSS-CERT-SWP-003",
        "LSS-CERT-SWP-004", "LSS-CERT-SWP-005", "LSS-CERT-SWP-006",
        "LSS-CERT-SWP-007", "LSS-CERT-SWP-008",
    ] + [f"LSS-CERT-COMP-{n:03d}" for n in range(1, 24)]
      + [f"LSS-REQ-ACFT-000{n}" for n in range(1, 5)]
      + ["LSS-REQ-CERT-0001", "LSS-REQ-CERT-0002", "LSS-REQ-CERT-0003",
         "LSS-REQ-CERT-0004", "LSS-REQ-CERT-0005"],

    "a1000000-0000-4000-a000-000000000002": [
        "LSS-21-INST-001", "LSS-21-0001", "LSS-21-0002", "LSS-21-0003",
        "LSS-21-0004", "LSS-21-0005", "LSS-21-0006", "LSS-21-0007",
        "LSS-21-0008", "LSS-21-0009", "LSS-21-0010", "LSS-21-0011",
        "LSS-21-0012", "LSS-21-0013", "LSS-21-0014",
        "LSS-E-00001", "LSS-SW-0001", "LSS-W21-001",
        "LSS-V-00001", "LSS-V-00002", "LSS-V-00003", "LSS-V-00004",
        "LSS-V-00005", "LSS-V-00006", "LSS-V-00007",
        "LSS-DWG-21-0001", "LSS-DWG-21-0002", "LSS-DWG-21-0005",
        "LSS-DWG-21-0006", "LSS-DWG-21-0012", "LSS-DWG-21-0015",
        "LSS-DWG-21-0016",
        "LSS-SPEC-DES-001", "LSS-SPEC-PRO-001", "LSS-SPEC-PRO-002",
        "LSS-ICD-001",
        "LSS-REQ-SYS-0001", "LSS-REQ-SYS-0002",
        "LSS-REQ-SUB-0001", "LSS-REQ-SUB-0002",
        "LSS-REQ-CMP-0001", "LSS-REQ-CMP-0002", "LSS-REQ-CMP-0007",
        "LSS-REQ-CMP-0008",
        "LSS-ECR-00001", "LSS-ECR-00002", "LSS-ECO-00004", "LSS-ECO-00002",
        "LSS-ECN-00004", "LSS-ECN-00002", "LSS-PR-00001", "LSS-PR-00002",
    ],

    "a1000000-0000-4000-a000-000000000003": [
        "LSS-25-INST-001", "LSS-F-00001", "LSS-F-00002", "LSS-F-00003",
        "LSS-F-00010", "LSS-F-00011", "LSS-F-00020", "LSS-F-00021",
        "LSS-F-00030", "LSS-F-00040", "LSS-F-00050", "LSS-F-00060",
        "LSS-F-00070", "LSS-F-00080", "LSS-F-00090", "LSS-F-00100",
        "LSS-F-00110",
        "LSS-DWG-25-0001", "LSS-DWG-25-0002", "LSS-DWG-25-0005",
        "LSS-DWG-25-0007", "LSS-DWG-25-0013", "LSS-DWG-25-0018",
        "LSS-SPEC-PRO-004", "LSS-SPEC-PRO-005", "LSS-ICD-003",
        "LSS-REQ-OPS-0001", "LSS-REQ-OPS-0004",
        "LSS-ECR-00004", "LSS-ECO-00001",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# Work breakdown
# ─────────────────────────────────────────────────────────────────────────────

F_WBS = f"{ROOT_FOLDER}/Certification/Certification Programme"


def wi(stem, pn, title, status, attrs, parent=None, notes=None):
    """One work item: Program, Phase, Milestone, WorkPackage or Task."""
    return {"type": stem, "pn": pn, "description": title, "status": status,
            "attrs": attrs, "parent": parent, "folder": F_WBS, "notes": notes,
            "revision": "A", "history": [("A", status)]}


def _wbs(code, start, finish, pct, health, owner, priority="High", duration=None,
         effort=None, leaf=False, pin=False, **extra):
    """One work item's schedule fields.

    `constraintType` is load-bearing and easy to get wrong. ASAP means "driven purely by
    predecessors": the engine ignores plannedStart entirely and schedules the item from
    the project start forward, so a whole plan collapses onto today and every bar lands
    in the wrong year. The planned dates only take effect through a dated constraint.

      SNET  start no earlier than - a floor. Right for ordinary work: the item cannot
            start before its planned date, but a late predecessor may still push it
            later, which is what produces honest float and honest lateness.
      MSO   must start on - an inflexible pin, honoured even against predecessors.
            Right for a committed milestone: an authority date does not move because
            an upstream task slipped; the slip shows up as negative float instead.

    `rollupMode` matters for the same reason. RollupFromChildren on an item with no
    children has nothing to roll up and falls back to today, which is why every
    milestone was showing today's date.
    """
    row = {
        "wbsCode": code, "plannedStart": start, "plannedFinish": finish,
        "percentComplete": pct, "health": health, "assignedTo": owner,
        "priority": priority,
        "rollupMode": "Manual" if leaf else "RollupFromChildren",
        # Leaf items are pinned with MSO, not SNET. SNET is only a FLOOR - it stops an
        # item starting early but cannot pull it earlier - so every task planned before
        # the view's project start still collapsed onto today. MSO is honoured even
        # against predecessors, and where a predecessor overruns the pin the engine
        # records the conflict rather than silently moving the date, which is exactly
        # what a late programme should show.
        "constraintType": "MSO" if (leaf or pin) else "SNET",
        "constraintDate": start,
    }
    if duration is not None:
        row["durationDays"] = duration
    if effort is not None:
        row["effortHours"] = effort
    row.update(extra)
    return row


WORK_ITEMS = [
    wi("Program", "NX00200001", f"{PROGRAMME} development and type certification",
       "Active",
       _wbs("1", "2025-01-06", "2027-12-17", 61, "At-Risk", "l.harkness",
            priority="Critical",
            programManager="l.harkness", portfolioCode="PF-NX",
            programPhase="Product and Process Validation",
            budget=184000000, targetMarketRelease="2028-01-31"),
       notes="At risk. The driver is the two certification items that cannot close until "
             "the passenger seat dynamic test report is released: LSS-CERT-COMP-014 and "
             "LSS-CERT-COMP-015."),

    # ── AS9145 APQP phases ──────────────────────────────────────────────────
    wi("Phase", "NX00200010", "Phase 1 - Planning", "Complete",
       _wbs("1.1", "2025-01-06", "2025-06-27", 100, "On-Track", "l.harkness",
            phaseNumber=1, gateType="Gate review", durationDays=124),
       parent="NX00200001"),

    wi("Phase", "NX00200020", "Phase 2 - Product design and development", "Complete",
       _wbs("1.2", "2025-06-30", "2026-04-30", 100, "On-Track", "d.okonjo",
            phaseNumber=2, gateType="Gate review", durationDays=219),
       parent="NX00200001"),

    wi("Phase", "NX00200030", "Phase 3 - Process design and development", "Active",
       _wbs("1.3", "2026-02-02", "2026-12-18", 78, "On-Track", "t.brennan",
            phaseNumber=3, gateType="Gate review", durationDays=229),
       parent="NX00200001"),

    wi("Phase", "NX00200040", "Phase 4 - Product and process validation", "Active",
       _wbs("1.4", "2026-05-04", "2027-09-30", 42, "At-Risk", "g.rossi",
            phaseNumber=4, gateType="Gate review", durationDays=346,
            priority="Critical"),
       parent="NX00200001",
       notes="The critical path. Validation cannot complete until every compliance item "
             "is accepted, and two are blocked on one test report."),

    wi("Phase", "NX00200050", "Phase 5 - Production and continuous improvement",
       "Planning",
       _wbs("1.5", "2027-07-01", "2027-12-17", 4, "On-Track", "t.brennan",
            phaseNumber=5, gateType="Gate review", durationDays=122),
       parent="NX00200001"),

    # ── Certification milestones ────────────────────────────────────────────
    wi("Milestone", "NX00200101", "Certification basis agreed with EASA", "Complete",
       _wbs("1.1.M1", "2025-06-27", "2025-06-27", 100, "On-Track", "g.rossi",
            priority="Critical", leaf=True, pin=True, milestoneCategory="Certification",
            plannedDate="2025-06-27", forecastDate="2025-06-27",
            actualDate="2025-06-20", isMandatory=True),
       parent="NX00200010"),

    wi("Milestone", "NX00200102", "Level of involvement agreed with EASA", "Complete",
       _wbs("1.2.M1", "2026-05-15", "2026-05-15", 100, "On-Track", "g.rossi",
            priority="Critical", leaf=True, pin=True, milestoneCategory="Certification",
            plannedDate="2026-05-15", forecastDate="2026-05-14",
            actualDate="2026-05-14", isMandatory=True),
       parent="NX00200020",
       notes="Agreeing the level of involvement is what lets most compliance items be "
             "closed under the design organisation privilege instead of item by item "
             "with the authority. It is the single most schedule-relevant milestone on "
             "a Part 21J programme."),

    wi("Milestone", "NX00200103", "Requirements baseline frozen", "Complete",
       _wbs("1.2.M2", "2026-05-14", "2026-05-14", 100, "On-Track", "s.vanderberg",
            priority="High", leaf=True, pin=True, milestoneCategory="Design",
            plannedDate="2026-05-14", forecastDate="2026-05-14",
            actualDate="2026-05-14", isMandatory=True),
       parent="NX00200020"),

    wi("Milestone", "NX00200104", "First flight, airframe 001", "Complete",
       _wbs("1.4.M1", "2026-06-30", "2026-06-30", 100, "On-Track", "l.harkness",
            priority="Critical", leaf=True, pin=True, milestoneCategory="Test",
            plannedDate="2026-06-30", forecastDate="2026-07-14",
            actualDate="2026-07-14", isMandatory=True),
       parent="NX00200040",
       notes="Two weeks late against plan. The slip came from the pack bay firewall "
             "penetration test, not from the airframe."),

    wi("Milestone", "NX00200105", "Cabin interior certification complete", "Active",
       _wbs("1.4.M2", "2027-01-29", "2027-01-29", 56, "Late", "g.rossi",
            priority="Critical", leaf=True, pin=True, milestoneCategory="Certification",
            plannedDate="2027-01-29", forecastDate="2027-03-19",
            isMandatory=True),
       parent="NX00200040",
       notes="Forecast seven weeks late. Blocked on the equivalent safety finding for "
             "seat orientation, which is blocked on the dynamic test report being "
             "released, which is sitting in airworthiness sign-off."),

    wi("Milestone", "NX00200106", "Type certificate issued", "Planning",
       _wbs("1.4.M3", "2027-09-30", "2027-09-30", 0, "At-Risk", "l.harkness",
            priority="Critical", leaf=True, pin=True, milestoneCategory="Certification",
            plannedDate="2027-09-30", forecastDate="2027-11-12",
            isMandatory=True),
       parent="NX00200040"),

    wi("Milestone", "NX00200107", "Production organisation approval extended",
       "Planning",
       _wbs("1.5.M1", "2027-11-30", "2027-11-30", 0, "On-Track", "k.tanaka",
            priority="High", leaf=True, pin=True, milestoneCategory="Quality",
            plannedDate="2027-11-30", forecastDate="2027-11-30",
            isMandatory=True),
       parent="NX00200050"),

    # ── Work packages ───────────────────────────────────────────────────────
    wi("WorkPackage", "NX00200201",
       "ATA 21 environmental control system design and substantiation", "Complete",
       _wbs("1.2.1", "2025-07-07", "2026-04-30", 100, "On-Track", "r.achebe",
            controlAccount="CA-21-001", budget=4820000, effortHours=18400),
       parent="NX00200020"),

    wi("WorkPackage", "NX00200202",
       "ATA 23 communications design and installation", "Complete",
       _wbs("1.2.2", "2025-09-01", "2026-03-31", 100, "On-Track", "d.okonjo",
            controlAccount="CA-23-001", budget=2140000, effortHours=8600),
       parent="NX00200020"),

    wi("WorkPackage", "NX00200203",
       "ATA 25 cabin interior design and substantiation", "Active",
       _wbs("1.2.3", "2025-08-04", "2026-11-27", 86, "At-Risk", "m.sandoval",
            controlAccount="CA-25-001", budget=6380000, effortHours=24200,
            priority="Critical"),
       parent="NX00200020",
       notes="At risk. The forward divider variant was added after the baseline and its "
             "flammability testing has not started."),

    wi("WorkPackage", "NX00200204",
       "Equipment qualification campaign, DO-160G", "Active",
       _wbs("1.4.1", "2026-02-02", "2027-02-26", 74, "On-Track", "s.vanderberg",
            controlAccount="CA-QT-001", budget=3240000, effortHours=9800),
       parent="NX00200040"),

    wi("WorkPackage", "NX00200205",
       "Compliance demonstration and certification evidence", "Active",
       _wbs("1.4.2", "2026-05-18", "2027-08-27", 48, "At-Risk", "g.rossi",
            controlAccount="CA-CERT-001", budget=5120000, effortHours=16800,
            priority="Critical"),
       parent="NX00200040"),

    wi("WorkPackage", "NX00200206",
       "Production process validation and first article programme", "Active",
       _wbs("1.3.1", "2026-02-02", "2026-12-18", 68, "On-Track", "t.brennan",
            controlAccount="CA-PROC-001", budget=2860000, effortHours=11200),
       parent="NX00200030"),

    wi("WorkPackage", "NX00200207",
       "Supplier development and source approval", "Active",
       _wbs("1.3.2", "2026-01-05", "2027-03-26", 71, "At-Risk", "y.cheng",
            controlAccount="CA-SUP-001", budget=1480000, effortHours=5400),
       parent="NX00200030",
       notes="At risk on one supplier: Pyrosafe Materials is on probation with three "
             "major findings open after the shelf-life escape."),

    # ── Tasks ───────────────────────────────────────────────────────────────
    wi("Task", "NX00200301",
       "Release ATA 21 installation drawing set under DOA privilege", "Complete",
       _wbs("1.2.1.1", "2026-04-06", "2026-05-14", 100, "On-Track", "m.sandoval",
            durationDays=29, effortHours=320, leaf=True, isMilestone=False, isSummary=False,
            sortOrder=10),
       parent="NX00200201"),

    wi("Task", "NX00200302",
       "Complete system safety assessment for pressurisation control", "Complete",
       _wbs("1.2.1.2", "2026-02-02", "2026-04-30", 100, "On-Track", "s.vanderberg",
            durationDays=64, effortHours=680, leaf=True, isMilestone=False, isSummary=False,
            sortOrder=20),
       parent="NX00200201"),

    wi("Task", "NX00200303",
       "Redesign ram air inlet scoop for pressure recovery", "Active",
       _wbs("1.3.1.1", "2026-09-07", "2026-11-27", 46, "At-Risk", "m.sandoval",
            durationDays=60, effortHours=420, leaf=True, isMilestone=False, isSummary=False,
            sortOrder=30, priority="High"),
       parent="NX00200206",
       notes="Against LSS-ECR-00002. Held in stress review: the change control board "
             "asked for the attachment stress case before it would disposition."),

    wi("Task", "NX00200304",
       "Run 16g dynamic test on passenger seat revision B", "Complete",
       _wbs("1.4.1.1", "2026-09-14", "2026-09-26", 100, "On-Track", "p.lindqvist",
            durationDays=11, effortHours=180, leaf=True, isMilestone=False, isSummary=False,
            sortOrder=10, priority="Critical"),
       parent="NX00200204"),

    wi("Task", "NX00200305",
       "Release passenger seat dynamic test report", "Active",
       _wbs("1.4.1.2", "2026-09-28", "2026-10-16", 80, "Late", "p.lindqvist",
            durationDays=15, effortHours=60, leaf=True, isMilestone=False, isSummary=False,
            sortOrder=20, priority="Critical",
            isCriticalPath=True),
       parent="NX00200204",
       notes="On the critical path and late. Two compliance items, one milestone and one "
             "service bulletin are all waiting on this one sign-off. It is the single "
             "best answer to 'what is actually holding the programme up?'"),

    wi("Task", "NX00200306",
       "Complete flammability testing for the forward divider variant", "Planning",
       _wbs("1.2.3.1", "2026-11-02", "2026-12-18", 0, "At-Risk", "m.sandoval",
            durationDays=35, effortHours=240, leaf=True, isMilestone=False, isSummary=False,
            sortOrder=40),
       parent="NX00200203"),

    wi("Task", "NX00200307",
       "Close the damage tolerance finding on the antenna doubler", "Active",
       _wbs("1.4.2.1", "2026-09-21", "2026-11-13", 35, "At-Risk", "p.lindqvist",
            durationDays=40, effortHours=200, leaf=True, isMilestone=False, isSummary=False,
            sortOrder=10, priority="High"),
       parent="NX00200205",
       notes="Re-run the damage tolerance analysis against the fatigue spectrum actually "
             "used rather than the generic spectrum. This is the open finding on "
             "LSS-CERT-COMP-010."),

    wi("Task", "NX00200308",
       "Resolve Pyrosafe Materials probation findings", "Active",
       _wbs("1.3.2.1", "2026-07-06", "2026-11-30", 55, "Late", "y.cheng",
            durationDays=106, effortHours=320, leaf=True, isMilestone=False, isSummary=False,
            sortOrder=10, priority="High"),
       parent="NX00200207"),

    wi("Task", "NX00200309",
       "Qualify an alternate source for the headset jack panel", "Planning",
       _wbs("1.3.2.2", "2026-11-02", "2027-03-26", 5, "At-Risk", "y.cheng",
            durationDays=105, effortHours=280, leaf=True, isMilestone=False, isSummary=False,
            sortOrder=20),
       parent="NX00200207",
       notes="Against LSS-ECR-00003. The last time buy date is 31 March 2027, which is "
             "the same week this task is due to finish. No float."),

    wi("Task", "NX00200310",
       "Complete delta first article on duct coupling revision B", "Active",
       _wbs("1.3.1.2", "2026-10-02", "2026-10-23", 70, "On-Track", "k.tanaka",
            durationDays=16, effortHours=48, leaf=True, isMilestone=False, isSummary=False,
            sortOrder=40),
       parent="NX00200206",
       notes="LSS-FAI-00004. Form 3 still open."),
]

# WBS links are parent/child relationships between work items, created through the work
# item API rather than as BOM links. Derived from the `parent` field above so there is one
# source of truth for the hierarchy.
WBS_LINKS = [(w["parent"], w["pn"]) for w in WORK_ITEMS if w.get("parent")]

# Finish-to-start dependencies that make the critical path real rather than decorative.
TASK_DEPENDENCIES = [
    ("NX00200304", "NX00200305", "FinishToStart",
     "The report cannot be written before the test is run."),
    ("NX00200305", "NX00200105", "FinishToStart",
     "Cabin interior certification is blocked on the test report being released."),
    ("NX00200307", "NX00200106", "FinishToStart",
     "The type certificate cannot be issued with a compliance finding open."),
    ("NX00200105", "NX00200106", "FinishToStart",
     "Cabin certification is a precondition of the type certificate."),
    ("NX00200306", "NX00200105", "FinishToStart",
     "The divider variant has to be substantiated before cabin certification closes."),
    ("NX00200303", "NX00200201", "FinishToStart",
     "The scoop redesign reopens part of the ATA 21 substantiation."),
]
