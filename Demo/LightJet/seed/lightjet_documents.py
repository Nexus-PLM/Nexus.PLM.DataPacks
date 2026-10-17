"""NX-200 documents: drawings, specifications, interface control, and the certification set.

The certification set is the part a certification audience will push on, so it is complete
rather than indicative:

* one certification programme plan, which the whole compliance checklist hangs off;
* safety assessments at the levels ARP4754A and ARP4761A actually call for - a functional
  hazard assessment, a preliminary system safety assessment, a system safety assessment and
  a zonal common cause analysis;
* DO-160G qualification plans and reports, including one with a deviation taken during test,
  because a pass with a deviation is a different certification position from a clean pass;
* the DO-178C and DO-254 plan set by name, since an authority asks for a named plan and the
  set has to be shown complete;
* compliance reports, one per requirement demonstration, each naming its regulation
  paragraph, its means of compliance from the EASA MC0-MC9 codes, and who accepted it.

Three compliance items are deliberately not Accepted: one submitted and waiting, one with
an open finding, and one still planned. A board where every card is in the last lane proves
nothing.
"""

from lightjet_data import (
    ATA21, ATA23, ATA25, PROGRAMME, ROOT_FOLDER, S_REL, S_SIGN, S_SUPER, S_WORK, T,
)

C_PLANNED, C_METHOD, C_EVIDENCE, C_SUBMITTED, C_ACCEPTED, C_FINDING, C_CLOSED = (
    "Planned", "Method Agreed", "Evidence in Work", "Submitted", "Accepted",
    "Finding Open", "Closed")

F_CERT = f"{ROOT_FOLDER}/Certification"
F_COMP = f"{F_CERT}/Compliance Reports"
F_SAFE = f"{F_CERT}/Safety Assessments"
F_QUAL = f"{F_CERT}/Equipment Qualification"
F_SW = f"{F_CERT}/Software and Electronic Hardware"
F_PROG = f"{F_CERT}/Certification Programme"

DOA = "EASA.21J.0742"
BASIS = "CS-23 Amdt 5 + ASTM F44 MoC"


def doc(stem, pn, title, status, attrs, folder, revision="A", history=None, notes=None,
        doc_file=None):
    """One document. `doc_file` names the generated file the loader attaches, if any."""
    return {
        "type": f"{T}{stem}", "pn": pn, "description": title, "status": status,
        "revision": revision, "attrs": attrs, "folder": folder,
        "history": history or [("A", status)], "notes": notes, "file": doc_file,
    }


def _doc_common(author, issue, pages, retention="Type design - life of type",
                conf="Internal", checked=None, approved=None, **extra):
    base = {
        "authorName": author, "issueDate": issue, "pageCount": pages,
        "retentionClass": retention, "confidentiality": conf,
        "checkedBy": checked, "approvedBy": approved,
        "certificationBasis": BASIS, "certificationAuthority": "EASA",
        "approvalRoute": "DOA privilege (21A.263)",
        "typeDesignData": True,
    }
    base.update(extra)
    return {k: v for k, v in base.items() if v is not None}


# ─────────────────────────────────────────────────────────────────────────────
# Drawings
# ─────────────────────────────────────────────────────────────────────────────

def _drawing(pn, title, ata, folder, dtype, sheets, size, scale, chars=None,
             ballooned=False, status=S_REL, revision="A", history=None, owner="m.sandoval",
             notes=None, regs=None, extra=None):
    attrs = _doc_common(owner, "2026-04-20", sheets,
                        checked="p.lindqvist", approved="l.harkness",
                        drawingType=dtype, sheetSize=size, sheetCount=sheets,
                        drawingScale=scale, projectionAngle="First angle",
                        cadSourceSystem="FreeCAD 1.0 / STEP AP242",
                        gdtApplied=True, balloonedForFai=ballooned,
                        balloonedIssue=revision if ballooned else None,
                        characteristicCount=chars,
                        complianceRegulations=regs,
                        meansOfCompliance="MC7 - Design inspection / audit")
    attrs.update(extra or {})
    return doc("Drawing", pn, title, status, attrs, folder, revision=revision,
               history=history, notes=notes,
               doc_file=f"{pn}.pdf")


DRAWINGS = [
    _drawing("LSS-DWG-21-0001",
             "Installation drawing - environmental control system, NX-200",
             ATA21, f"{ROOT_FOLDER}/Product Structure/ATA 21 Air Conditioning",
             "Installation", 6, "A1", "1:5", regs="CS 23.2320, CS 23.2525"),
    _drawing("LSS-DWG-21-0002", "Assembly drawing - bleed air supply duct assembly",
             ATA21, f"{ROOT_FOLDER}/Product Structure/ATA 21 Air Conditioning",
             "Assembly", 3, "A2", "1:2", chars=48, ballooned=True),
    _drawing("LSS-DWG-21-0005", "Detail drawing - duct coupling, V-band, 50 mm",
             ATA21, f"{ROOT_FOLDER}/Product Structure/ATA 21 Air Conditioning",
             "Detail", 1, "A3", "2:1", chars=22, ballooned=True,
             revision="B", history=[("A", S_SUPER), ("B", S_REL)],
             notes="Revision B is the ballooned issue the delta first article report "
                   "LSS-FAI-00004 is written against. Revision A is superseded but "
                   "retained: parts built to it are in service."),
    _drawing("LSS-DWG-21-0006", "Assembly drawing - primary heat exchanger mount",
             ATA21, f"{ROOT_FOLDER}/Product Structure/ATA 21 Air Conditioning",
             "Assembly", 2, "A2", "1:1", chars=36, ballooned=True,
             owner="p.lindqvist"),
    _drawing("LSS-DWG-21-0012", "Detail drawing - ram air inlet scoop, composite",
             ATA21, f"{ROOT_FOLDER}/Product Structure/ATA 21 Air Conditioning",
             "Detail", 2, "A2", "1:1", chars=29, status=S_SIGN,
             history=[("A", S_SIGN)],
             notes="In the airworthiness sign-off lane of the type design release "
                   "board. Design check and stress are both complete."),
    _drawing("LSS-DWG-21-0015", "Schematic - environmental control system control",
             ATA21, f"{ROOT_FOLDER}/Product Structure/ATA 21 Air Conditioning",
             "Schematic", 4, "A1", "None", owner="d.okonjo"),
    _drawing("LSS-DWG-21-0016", "Wiring diagram - ECS control harness LSS-W21-001",
             ATA21, f"{ROOT_FOLDER}/Product Structure/ATA 21 Air Conditioning",
             "Wiring diagram", 5, "A1", "None", owner="d.okonjo"),
    _drawing("LSS-DWG-23-0001", "Installation drawing - communications system, NX-200",
             ATA23, f"{ROOT_FOLDER}/Product Structure/ATA 23 Communications",
             "Installation", 5, "A1", "1:5", owner="d.okonjo",
             regs="CS 23.2500, CS 23.2510"),
    _drawing("LSS-DWG-23-0004",
             "Detail drawing - antenna doubler, VHF, upper fuselage",
             ATA23, f"{ROOT_FOLDER}/Product Structure/ATA 23 Communications",
             "Detail", 2, "A2", "1:1", chars=31, ballooned=True, owner="p.lindqvist",
             regs="CS 23.2240, CS 23.2250"),
    _drawing("LSS-DWG-23-0007", "Wiring diagram - communications coaxial harness",
             ATA23, f"{ROOT_FOLDER}/Product Structure/ATA 23 Communications",
             "Wiring diagram", 3, "A1", "None", owner="d.okonjo"),
    _drawing("LSS-DWG-23-0009",
             "Wiring diagram - satellite communications RF and data harness",
             ATA23, f"{ROOT_FOLDER}/Product Structure/ATA 23 Communications",
             "Wiring diagram", 4, "A1", "None", owner="d.okonjo", status=S_SIGN,
             history=[("A", S_SIGN)],
             extra={"confidentiality": "Export controlled"},
             notes="Export controlled: carries the satellite terminal interface "
                   "definition, ECCN 7A994."),
    _drawing("LSS-DWG-25-0001",
             "Installation drawing - cabin interior, seven place standard",
             ATA25, f"{ROOT_FOLDER}/Product Structure/ATA 25 Equipment and Furnishings",
             "Installation", 8, "A0", "1:10", regs="CS 23.2270, CS 23.2325"),
    _drawing("LSS-DWG-25-0002", "Assembly drawing - pilot seat assembly, 16g",
             ATA25, f"{ROOT_FOLDER}/Product Structure/ATA 25 Equipment and Furnishings",
             "Assembly", 4, "A1", "1:2", chars=64, ballooned=True,
             regs="CS 23.2270"),
    _drawing("LSS-DWG-25-0005",
             "Assembly drawing - passenger seat assembly, club four",
             ATA25, f"{ROOT_FOLDER}/Product Structure/ATA 25 Equipment and Furnishings",
             "Assembly", 5, "A1", "1:2", chars=78, ballooned=True,
             revision="B", history=[("A", S_SUPER), ("B", S_REL)],
             regs="CS 23.2270, CS 23.2270(e)",
             notes="Revision B adds the swivel interlock required by the equivalent "
                   "safety finding. The ballooned issue for the delta first article "
                   "report is revision B."),
    _drawing("LSS-DWG-25-0004",
             "Detail drawing - seat track fitting, flight compartment",
             ATA25, f"{ROOT_FOLDER}/Product Structure/ATA 25 Equipment and Furnishings",
             "Detail", 1, "A3", "2:1", chars=26, ballooned=True, owner="p.lindqvist",
             regs="CS 23.2270"),
    _drawing("LSS-DWG-25-0007", "Detail drawing - sidewall panel, forward",
             ATA25, f"{ROOT_FOLDER}/Product Structure/ATA 25 Equipment and Furnishings",
             "Detail", 3, "A1", "1:2", chars=41, ballooned=True,
             regs="CS 23.2325"),
    _drawing("LSS-DWG-25-0011", "Detail drawing - cabin floor panel, composite sandwich",
             ATA25, f"{ROOT_FOLDER}/Product Structure/ATA 25 Equipment and Furnishings",
             "Detail", 2, "A1", "1:2", chars=34, ballooned=True, owner="p.lindqvist"),
    _drawing("LSS-DWG-25-0013", "Assembly drawing - galley monument, forward",
             ATA25, f"{ROOT_FOLDER}/Product Structure/ATA 25 Equipment and Furnishings",
             "Assembly", 6, "A1", "1:5", chars=52, regs="CS 23.2325"),
    _drawing("LSS-DWG-25-0018",
             "Assembly drawing - divider and credenza, forward cabin",
             ATA25, f"{ROOT_FOLDER}/Product Structure/ATA 25 Equipment and Furnishings",
             "Assembly", 4, "A1", "1:5", status=S_WORK, history=[("A", S_WORK)],
             notes="In work against operator requirement LSS-REQ-OPS-0004."),
]


# ─────────────────────────────────────────────────────────────────────────────
# Specifications and interface control
# ─────────────────────────────────────────────────────────────────────────────

def _spec(pn, title, spec_class, pages, author="r.achebe", status=S_REL,
          flowdown=False, verification=None, regs=None, notes=None, folder=None,
          supersedes=None, ata=None, revision="A", history=None):
    attrs = _doc_common(author, "2026-03-12", pages,
                        checked="s.vanderberg", approved="l.harkness",
                        specificationClass=spec_class,
                        specificationAuthority="LSS Systems Engineering",
                        flowdownRequired=flowdown,
                        verificationMethod=verification,
                        complianceRegulations=regs,
                        supersedesDocument=supersedes,
                        meansOfCompliance="MC1 - Design review")
    return doc("Specification", pn, title, status, attrs,
               folder or f"{F_CERT}/Certification Programme", notes=notes,
               revision=revision, history=history, doc_file=f"{pn}.docx")


SPECIFICATIONS = [
    _spec("LSS-SPEC-DES-001",
          "Design specification - environmental control and pressurisation system",
          "Design specification", 64, regs="CS 23.2320, CS 23.2525",
          verification="Analysis"),
    _spec("LSS-SPEC-DES-002", "Design specification - communications system",
          "Design specification", 38, "d.okonjo", regs="CS 23.2500",
          verification="Test"),
    _spec("LSS-SPEC-DES-003", "Design specification - cabin interior and furnishings",
          "Design specification", 52, "m.sandoval", regs="CS 23.2270, CS 23.2325",
          verification="Test"),
    _spec("LSS-SPEC-MAT-001", "Material specification - carbon/epoxy prepreg, 177 C cure",
          "Material specification", 22, "p.lindqvist", flowdown=True,
          verification="Test"),
    _spec("LSS-SPEC-MAT-002",
          "Material specification - carbon/Nomex sandwich, floor panel",
          "Material specification", 18, "p.lindqvist", flowdown=True,
          verification="Test"),
    _spec("LSS-SPEC-MAT-003", "Material specification - glass/epoxy prepreg, ducting",
          "Material specification", 16, "p.lindqvist", flowdown=True,
          verification="Test"),
    _spec("LSS-SPEC-MAT-005", "Material specification - structural film adhesive",
          "Material specification", 14, "p.lindqvist", flowdown=True,
          verification="Test"),
    _spec("LSS-SPEC-MAT-007",
          "Material specification - polyetherimide moulding compound, cabin air outlets",
          "Material specification", 12, "m.sandoval", flowdown=True,
          verification="Test", regs="CS 23.2325"),
    _spec("LSS-SPEC-PRC-004",
          "Process specification - fastener installation and torque control",
          "Process specification", 28, "t.brennan", flowdown=True,
          verification="Inspection"),
    _spec("LSS-SPEC-PRC-011",
          "Process specification - environmental control system rigging and leak check",
          "Process specification", 20, "t.brennan", verification="Test"),
    _spec("LSS-SPEC-PRC-012",
          "Process specification - avionics installation and bonding verification",
          "Process specification", 24, "d.okonjo", verification="Test"),
    _spec("LSS-SPEC-TST-009",
          "Test specification - EWIS zonal inspection and separation verification",
          "Test specification", 32, "d.okonjo", verification="Inspection",
          regs="CS 23.2525"),
    _spec("LSS-SPEC-PRO-001",
          "Procurement specification - cabin pressure controller, dual channel",
          "Procurement specification", 26, "r.achebe", flowdown=True,
          verification="Test", regs="CS 23.2525"),
    _spec("LSS-SPEC-PRO-002",
          "Procurement specification - cabin pressure safety valve",
          "Procurement specification", 18, "m.sandoval", flowdown=True,
          verification="Test"),
    _spec("LSS-SPEC-PRO-003",
          "Procurement specification - VHF transceiver, 8.33 kHz",
          "Procurement specification", 22, "d.okonjo", flowdown=True,
          verification="Inspection"),
    _spec("LSS-SPEC-PRO-004",
          "Procurement specification - passenger club seat, 16g with swivel interlock",
          "Procurement specification", 34, "m.sandoval", flowdown=True,
          verification="Test", regs="CS 23.2270, CS 23.2270(e)",
          revision="B", history=[("A", S_SUPER), ("B", S_REL)],
          supersedes="LSS-SPEC-PRO-004 revision A",
          notes="Flowed down to Caldera Seating. The interlock requirement entered at "
                "revision B, after the equivalent safety finding was agreed. Revision A "
                "is retained because seats were built to it."),
    _spec("LSS-SPEC-PRO-005",
          "Procurement specification - cabin lining panel, 65/65 heat release",
          "Procurement specification", 24, "m.sandoval", flowdown=True,
          verification="Test", regs="CS 23.2325"),
    _spec("LSS-SPEC-SRS-001",
          "Software requirements specification - ECS controller",
          "Software requirements specification", 86, "r.achebe",
          verification="Analysis", regs="CS 23.2510"),
]

INTERFACE_DOCS = [
    doc("Icd", "LSS-ICD-001",
        "Interface control - cabin pressure controller to ECS controller",
        S_REL,
        _doc_common("r.achebe", "2026-02-18", 24, checked="s.vanderberg",
                    approved="l.harkness",
                    interfaceType="Data bus", partyA="Light Speed Systems",
                    partyB="Meridian Air Systems",
                    busProtocol="ARINC 429",
                    interfaceBaselineRef="ICD-BL-002",
                    bilateralAgreementSigned=True,
                    supplierAgreementDate="2026-02-24",
                    complianceRegulations="CS 23.2510",
                    meansOfCompliance="MC1 - Design review"),
        f"{F_CERT}/Certification Programme", doc_file="LSS-ICD-001.docx"),

    doc("Icd", "LSS-ICD-002",
        "Interface control - audio control panel to VHF and satellite transceivers",
        S_REL,
        _doc_common("d.okonjo", "2026-03-05", 18, checked="s.vanderberg",
                    approved="l.harkness",
                    interfaceType="Electrical", partyA="Light Speed Systems",
                    partyB="Thorne Avionics",
                    busProtocol="Discrete",
                    interfaceBaselineRef="ICD-BL-003",
                    bilateralAgreementSigned=True,
                    supplierAgreementDate="2026-03-11",
                    meansOfCompliance="MC1 - Design review"),
        f"{F_CERT}/Certification Programme", doc_file="LSS-ICD-002.docx"),

    doc("Icd", "LSS-ICD-003",
        "Interface control - passenger seat to seat track and floor structure",
        S_REL,
        _doc_common("p.lindqvist", "2026-01-29", 16, checked="m.sandoval",
                    approved="l.harkness",
                    interfaceType="Structural attachment",
                    partyA="Light Speed Systems", partyB="Caldera Seating",
                    busProtocol="Not applicable",
                    interfaceBaselineRef="ICD-BL-005",
                    bilateralAgreementSigned=True,
                    supplierAgreementDate="2026-02-06",
                    complianceRegulations="CS 23.2270",
                    meansOfCompliance="MC2 - Calculation / analysis"),
        f"{F_CERT}/Certification Programme", doc_file="LSS-ICD-003.docx",
        notes="The seat and the airframe each own one side of the 16g load path. This "
              "document is the single controlled definition of where that load is "
              "handed over, and both dynamic test reports reference it."),

    doc("Icd", "LSS-ICD-004",
        "Interface control - satellite terminal to antenna and cabin data network",
        S_SIGN,
        _doc_common("d.okonjo", "2026-08-14", 20, checked="s.vanderberg",
                    interfaceType="Data bus", partyA="Light Speed Systems",
                    partyB="Thorne Avionics",
                    busProtocol="Ethernet",
                    bilateralAgreementSigned=False,
                    confidentiality="Export controlled",
                    meansOfCompliance="MC1 - Design review"),
        f"{F_CERT}/Certification Programme", doc_file="LSS-ICD-004.docx",
        notes="Not yet bilaterally agreed and export controlled, so it cannot be sent "
              "to a supplier contact without a current export briefing on file."),
]


# ─────────────────────────────────────────────────────────────────────────────
# Certification programme plan
# ─────────────────────────────────────────────────────────────────────────────

CERT_PLANS = [
    doc("PrjSpecificCertPlan", "LSS-CERT-PLAN-001",
        "NX-200 certification programme plan",
        S_REL,
        _doc_common("g.rossi", "2026-05-14", 118, checked="l.harkness",
                    approved="l.harkness",
                    retention="Type design - life of type",
                    certificationProgramme="NX-200 type certificate, EASA",
                    applicableSpecification=BASIS,
                    amendmentLevel="CS-23 Amendment 5, AMC and GM Issue 3",
                    specialConditions=
                    "SC-23-001 lithium battery installation; "
                    "SC-23-002 cabin data network security",
                    equivalentSafetyFindings=
                    "ESF-25-001 passenger seat orientation during taxi, take-off and "
                    "landing, met by a mechanical swivel interlock",
                    deviationsRequested="None",
                    certificationReviewItems=
                    "CRI-21-001 pressurisation system safety assessment; "
                    "CRI-23-001 cabin network security; "
                    "CRI-25-002 seat orientation equivalent safety finding; "
                    "CRI-25-004 forward divider egress path",
                    complianceChecklistRef="LSS-CERT-PLAN-002",
                    doaPrivilegesUsed=
                    "21A.263(c)(1) classification of changes; "
                    "21A.263(c)(2) approval of minor changes; "
                    "21A.263(c)(3) issue of information and instructions",
                    levelOfInvolvementAgreed=True,
                    plannedCertificationDate="2027-09-30",
                    doaApprovalReference=DOA,
                    meansOfCompliance="MC0 - Compliance statement"),
        F_PROG, revision="C",
        history=[("A", S_SUPER), ("B", S_SUPER), ("C", S_REL)],
        doc_file="LSS-CERT-PLAN-001.docx",
        notes="Revision C is the issue the requirements baseline was taken against. The "
              "level of involvement was agreed with EASA on 14 May 2026, which is what "
              "lets most compliance items be closed under the design organisation "
              "privilege without item-by-item authority review."),

    doc("PrjSpecificCertPlan", "LSS-CERT-PLAN-002",
        "NX-200 compliance checklist, CS-23 Amendment 5",
        S_REL,
        _doc_common("g.rossi", "2026-05-14", 206, checked="l.harkness",
                    approved="l.harkness",
                    certificationProgramme="NX-200 type certificate, EASA",
                    applicableSpecification=BASIS,
                    amendmentLevel="CS-23 Amendment 5",
                    complianceChecklistRef="Self",
                    doaPrivilegesUsed="21A.263(c)(2)",
                    levelOfInvolvementAgreed=True,
                    plannedCertificationDate="2027-09-30",
                    doaApprovalReference=DOA,
                    meansOfCompliance="MC0 - Compliance statement"),
        F_PROG, revision="C", history=[("A", S_SUPER), ("B", S_SUPER), ("C", S_REL)],
        doc_file="LSS-CERT-PLAN-002.xlsx",
        notes="The checklist. Every row is a compliance item object in this system, so "
              "the spreadsheet is a rendering of the data rather than the master."),
]


# ─────────────────────────────────────────────────────────────────────────────
# Safety assessments
# ─────────────────────────────────────────────────────────────────────────────

def _safety(pn, title, atype, arp, function, worst, target, achieved, dal, derived,
            open_hazards, status=S_REL, author="s.vanderberg", pages=48, notes=None,
            revision="A", history=None):
    attrs = _doc_common(author, "2026-04-02", pages, checked="r.achebe",
                        approved="l.harkness",
                        assessmentType=atype, arpReference=arp,
                        functionAnalysed=function, worstCaseFailureEffect=worst,
                        quantitativeTarget=target, achievedProbability=achieved,
                        allocatedDal=dal, derivedRequirementCount=derived,
                        openHazardCount=open_hazards,
                        meansOfCompliance="MC3 - Safety assessment",
                        designAssuranceLevel=dal)
    return doc("SafetyAssessment", pn, title, status, attrs, F_SAFE, notes=notes,
               revision=revision, history=history, doc_file=f"{pn}.docx")


SAFETY_ASSESSMENTS = [
    _safety("LSS-CERT-SAFE-001",
            "Functional hazard assessment - environmental control and pressurisation",
            "FHA - system level", "ARP4754A",
            "Maintain cabin pressure and temperature within habitable limits",
            "Hazardous / Severe-Major",
            "1E-7 per flight hour for the hazardous condition",
            "Not applicable at FHA stage", "B", 3, 0,
            notes="The assessment that raised the derived requirement for an independent "
                  "mechanical safety valve (LSS-REQ-SUB-0002). Three derived "
                  "requirements came out of it; all three are traced back here with a "
                  "derived-from link."),

    _safety("LSS-CERT-SAFE-002",
            "System safety assessment - pressurisation control",
            "SSA", "ARP4761A",
            "Control cabin pressure and protect against overpressure and rapid "
            "decompression",
            "Catastrophic",
            "1E-9 per flight hour for the catastrophic condition, "
            "1E-7 for the hazardous condition",
            "4.2E-10 catastrophic, 2.8E-8 hazardous", "B", 0, 0,
            pages=96,
            notes="Shows the catastrophic overpressure condition at 4.2E-10 per flight "
                  "hour against a 1E-9 target. The margin comes almost entirely from the "
                  "mechanical safety valve being independent of everything electrical."),

    _safety("LSS-CERT-SAFE-003",
            "Preliminary system safety assessment - communications",
            "PSSA", "ARP4754A",
            "Provide air-to-ground and air-to-air voice communication",
            "Major", "1E-5 per flight hour for the major condition",
            "6.1E-6", "C", 1, 1,
            author="d.okonjo", pages=42,
            notes="One hazard remains open: loss of both VHF transceivers from a single "
                  "power bus fault. The separation argument depends on the final wiring "
                  "routing, which is why harness LSS-W23-003 is still in sign-off."),

    _safety("LSS-CERT-SAFE-004",
            "Common cause analysis - zonal, forward avionics bay and pack bay",
            "CCA - zonal", "ARP4761A",
            "Independence of redundant communications and pressurisation functions",
            "Hazardous / Severe-Major",
            "No single zonal event may defeat both channels",
            "No common cause identified after routing change", "B", 2, 0,
            pages=58,
            notes="Zonal analysis is what catches two independent channels routed "
                  "through the same clamp. Two derived requirements on wiring separation "
                  "came out of this, and they are why LSS-W21-001 carries EWIS "
                  "separation category 2."),

    _safety("LSS-CERT-SAFE-005",
            "Failure modes and effects analysis - cabin interior occupant protection",
            "FMEA", "ARP4761A",
            "Retain occupants and items of mass under the emergency landing conditions",
            "Hazardous / Severe-Major",
            "No single fitting failure may release a seat",
            "Fail safe demonstrated by test with one fitting removed",
            "Not applicable", 1, 0,
            author="p.lindqvist", pages=36),
]


# ─────────────────────────────────────────────────────────────────────────────
# Qualification plans and reports
# ─────────────────────────────────────────────────────────────────────────────

LAB = "Northgate Environmental Test Laboratory"
LAB_ACC = "ISO/IEC 17025 accredited, UKAS 4471"

QUAL_DOCS = [
    doc("QualTestPlan", "LSS-CERT-QUAL-012",
        "DO-160G qualification test plan - ECS controller LSS-E-00001",
        S_REL,
        _doc_common("r.achebe", "2026-01-15", 44, checked="s.vanderberg",
                    approved="l.harkness",
                    do160Revision="DO-160G",
                    do160Sections="4 Temperature and Altitude",
                    environmentalCategories=
                    "Section 4 Cat A2; Section 5 Cat B; Section 7 Cat B; Section 8 Cat S "
                    "curve C; Section 16 Cat Z; Section 20 Cat T; Section 21 Cat M; "
                    "Section 22 Cat A3E3; Section 25 Cat A",
                    equipmentUnderTest="LSS-E-00001 ECS controller, dual channel",
                    specimenCount=3, testLaboratory=LAB, labAccreditation=LAB_ACC,
                    plannedStartDate="2026-02-02", witnessRequired=True,
                    meansOfCompliance="MC8 - Equipment qualification"),
        F_QUAL, doc_file="LSS-CERT-QUAL-012.docx"),

    doc("QualTestReport", "LSS-CERT-QUAL-003",
        "DO-160G qualification test report - air cycle machine LSS-V-00002",
        S_REL,
        _doc_common("r.achebe", "2026-03-28", 162, checked="s.vanderberg",
                    approved="l.harkness",
                    do160Revision="DO-160G",
                    do160Sections="8 Vibration",
                    environmentalCategories=
                    "Section 4 Cat A2; Section 8 Cat S curve C; Section 11 Cat F",
                    testPlanReference="MAS-QTP-7730-01",
                    testLaboratory=LAB, labAccreditation=LAB_ACC,
                    testStartDate="2026-02-09", testEndDate="2026-03-20",
                    specimenSerialNumbers="MAS7730-0007, MAS7730-0008",
                    testResult="Pass", retestRequired=False,
                    meansOfCompliance="MC8 - Equipment qualification"),
        F_QUAL, doc_file="LSS-CERT-QUAL-003.docx",
        notes="This report is the reason the air cycle machine is pinned at revision A "
              "in the bill of materials. The qualification credit is against this "
              "configuration and does not carry forward without a delta assessment."),

    doc("QualTestReport", "LSS-CERT-QUAL-004",
        "DO-160G qualification test report - cabin pressure controller LSS-V-00004",
        S_REL,
        _doc_common("r.achebe", "2026-04-11", 184, checked="s.vanderberg",
                    approved="l.harkness",
                    do160Revision="DO-160G",
                    do160Sections="22 Lightning Induced Transient Susceptibility",
                    environmentalCategories=
                    "Section 4 Cat A2; Section 16 Cat Z; Section 20 Cat T; "
                    "Section 21 Cat M; Section 22 Cat A3E3; Section 25 Cat A",
                    testPlanReference="MAS-QTP-9901-02",
                    testLaboratory=LAB, labAccreditation=LAB_ACC,
                    testStartDate="2026-03-02", testEndDate="2026-04-03",
                    specimenSerialNumbers="MAS9901-0011",
                    testResult="Pass with deviation",
                    deviationReferences="DEV-QUAL-004-01",
                    retestRequired=False,
                    meansOfCompliance="MC8 - Equipment qualification"),
        F_QUAL, doc_file="LSS-CERT-QUAL-004.docx",
        notes="Pass with deviation. Section 22 level 3 waveform 4 was applied at 90 "
              "percent of the category level because the laboratory generator could not "
              "reach the full level on the day. The deviation is accepted on the basis "
              "that the installation sits in an interior lightning zone, and the "
              "acceptance rationale is recorded on compliance item LSS-CERT-COMP-002."),

    doc("QualTestReport", "LSS-CERT-QUAL-005",
        "Qualification test report - cabin pressure safety valve LSS-V-00006",
        S_REL,
        _doc_common("m.sandoval", "2026-05-22", 68, checked="r.achebe",
                    approved="l.harkness",
                    do160Revision="DO-160G",
                    do160Sections="4 Temperature and Altitude",
                    environmentalCategories="Section 4 Cat A2; Section 8 Cat S curve C",
                    testPlanReference="LSS-CERT-QUAL-012",
                    testLaboratory=LAB, labAccreditation=LAB_ACC,
                    testStartDate="2026-05-04", testEndDate="2026-05-15",
                    specimenSerialNumbers="MAS5541-0003, MAS5541-0004",
                    testResult="Pass", retestRequired=False,
                    meansOfCompliance="MC4 - Laboratory test"),
        F_QUAL, doc_file="LSS-CERT-QUAL-005.docx",
        notes="Cracking pressure measured at 0.618 and 0.624 bar against a requirement "
              "of 0.62 plus or minus 0.02 bar, with no electrical power applied and the "
              "outflow valve failed closed. This is the evidence behind the derived "
              "requirement LSS-REQ-SUB-0002."),

    doc("QualTestReport", "LSS-CERT-QUAL-001",
        "Dynamic test report - pilot seat installation, 16g longitudinal",
        S_REL,
        _doc_common("p.lindqvist", "2026-06-18", 142, checked="m.sandoval",
                    approved="l.harkness",
                    do160Revision="DO-160G",
                    do160Sections="7 Operational Shock and Crash Safety",
                    environmentalCategories="Not applicable - dynamic sled test",
                    testPlanReference="LSS-DTP-25-001",
                    testLaboratory="Calspan Dynamic Test Services",
                    labAccreditation="ISO/IEC 17025 accredited",
                    testStartDate="2026-06-08", testEndDate="2026-06-12",
                    specimenSerialNumbers="LSS-F-00001 S/N 0003, 0004",
                    testResult="Pass", retestRequired=False,
                    complianceRegulations="CS 23.2270",
                    meansOfCompliance="MC4 - Laboratory test"),
        F_QUAL, doc_file="LSS-CERT-QUAL-001.docx",
        notes="Critical seat position, 16g longitudinal, yawed so restraint retention "
              "was demonstrated in the same run. Head injury criterion 412 against a "
              "limit of 1000; femur load 5.1 kN against 10.0 kN; no restraint release."),

    doc("QualTestReport", "LSS-CERT-QUAL-002",
        "Dynamic test report - passenger club seat installation with swivel interlock",
        S_SIGN,
        _doc_common("p.lindqvist", "2026-09-26", 158, checked="m.sandoval",
                    do160Revision="DO-160G",
                    do160Sections="7 Operational Shock and Crash Safety",
                    environmentalCategories="Not applicable - dynamic sled test",
                    testPlanReference="LSS-DTP-25-002",
                    testLaboratory="Calspan Dynamic Test Services",
                    labAccreditation="ISO/IEC 17025 accredited",
                    testStartDate="2026-09-14", testEndDate="2026-09-19",
                    specimenSerialNumbers="LSS-F-00010 S/N 0011, 0012",
                    testResult="Pass", retestRequired=False,
                    complianceRegulations="CS 23.2270, CS 23.2270(e)",
                    meansOfCompliance="MC4 - Laboratory test"),
        F_QUAL, doc_file="LSS-CERT-QUAL-002.docx",
        notes="Run on revision B of the seat, with the swivel interlock. Awaiting "
              "airworthiness sign-off. The compliance item for the equivalent safety "
              "finding cannot be accepted until this report is released, which is why "
              "LSS-CERT-COMP-015 sits in Submitted."),

    doc("QualTestReport", "LSS-CERT-QUAL-006",
        "Flammability test report - upholstery and seat facings, Appendix F Part I",
        S_REL,
        _doc_common("m.sandoval", "2026-02-27", 54, checked="g.rossi",
                    approved="l.harkness",
                    do160Revision="DO-160G",
                    do160Sections="26 Fire, Flammability",
                    environmentalCategories="Appendix F Part I, 12 second vertical",
                    testPlanReference="LSS-FTP-25-001",
                    testLaboratory="Skandia Flammability Laboratory",
                    labAccreditation="FAA accepted test facility",
                    testStartDate="2026-02-16", testEndDate="2026-02-20",
                    specimenSerialNumbers="Batch PYR-LTH-0820 lot 26041",
                    testResult="Pass", retestRequired=False,
                    complianceRegulations="CS 23.2325",
                    meansOfCompliance="MC4 - Laboratory test"),
        F_QUAL, doc_file="LSS-CERT-QUAL-006.docx"),

    doc("QualTestReport", "LSS-CERT-QUAL-007",
        "Flammability test report - seat cushions, Appendix F Part II oil burner",
        S_REL,
        _doc_common("m.sandoval", "2026-03-19", 48, checked="g.rossi",
                    approved="l.harkness",
                    do160Revision="DO-160G",
                    do160Sections="26 Fire, Flammability",
                    environmentalCategories=
                    "Appendix F Part II, oil burner, fire blocked construction",
                    testPlanReference="LSS-FTP-25-002",
                    testLaboratory="Skandia Flammability Laboratory",
                    labAccreditation="FAA accepted test facility",
                    testStartDate="2026-03-09", testEndDate="2026-03-13",
                    specimenSerialNumbers="LSS-F-00002 and LSS-F-00011, lot 26052",
                    testResult="Pass", retestRequired=False,
                    complianceRegulations="CS 23.2325",
                    meansOfCompliance="MC4 - Laboratory test"),
        F_QUAL, doc_file="LSS-CERT-QUAL-007.docx",
        notes="Burn-through and weight loss both within limits with the fire blocking "
              "layer present. The bill of materials pins the cushions to the revision "
              "tested, because the credit is construction specific."),

    doc("QualTestReport", "LSS-CERT-QUAL-008",
        "Heat release and smoke density test report - cabin lining panels",
        S_REL,
        _doc_common("m.sandoval", "2026-07-30", 72, checked="g.rossi",
                    approved="l.harkness",
                    do160Revision="DO-160G",
                    do160Sections="26 Fire, Flammability",
                    environmentalCategories=
                    "Appendix F Part IV heat release; Appendix F Part V smoke density",
                    testPlanReference="LSS-FTP-25-003",
                    testLaboratory="Skandia Flammability Laboratory",
                    labAccreditation="FAA accepted test facility",
                    testStartDate="2026-07-13", testEndDate="2026-07-24",
                    specimenSerialNumbers="LSS-F-00020 and LSS-F-00030, lot 26118",
                    testResult="Pass", retestRequired=False,
                    complianceRegulations="CS 23.2325",
                    meansOfCompliance="MC4 - Laboratory test"),
        F_QUAL, doc_file="LSS-CERT-QUAL-008.docx",
        notes="Peak heat release 41 kW/m2 and total 38 kW-min/m2 against the 65/65 "
              "criteria; specific optical smoke density 94 against a limit of 200. "
              "Tested with the production decorative finish, which is the configuration "
              "that matters."),

    doc("QualTestReport", "LSS-CERT-QUAL-009",
        "Flammability test report - carpets, soft goods and stowage",
        S_REL,
        _doc_common("m.sandoval", "2026-04-24", 38, checked="g.rossi",
                    approved="l.harkness",
                    do160Revision="DO-160G",
                    do160Sections="26 Fire, Flammability",
                    environmentalCategories="Appendix F Part I, 12 second vertical",
                    testPlanReference="LSS-FTP-25-004",
                    testLaboratory="Skandia Flammability Laboratory",
                    labAccreditation="FAA accepted test facility",
                    testStartDate="2026-04-13", testEndDate="2026-04-17",
                    specimenSerialNumbers="Lots 26063, 26064, 26071",
                    testResult="Pass", retestRequired=False,
                    complianceRegulations="CS 23.2325",
                    meansOfCompliance="MC4 - Laboratory test"),
        F_QUAL, doc_file="LSS-CERT-QUAL-009.docx"),

    doc("QualTestReport", "LSS-CERT-QUAL-010",
        "Heat release test report - galley and lavatory monuments",
        S_REL,
        _doc_common("m.sandoval", "2026-08-21", 56, checked="g.rossi",
                    approved="l.harkness",
                    do160Revision="DO-160G",
                    do160Sections="26 Fire, Flammability",
                    environmentalCategories="Appendix F Part IV heat release",
                    testPlanReference="LSS-FTP-25-005",
                    testLaboratory="Skandia Flammability Laboratory",
                    labAccreditation="FAA accepted test facility",
                    testStartDate="2026-08-10", testEndDate="2026-08-14",
                    specimenSerialNumbers="Lot 26134",
                    testResult="Pass", retestRequired=False,
                    complianceRegulations="CS 23.2325",
                    meansOfCompliance="MC4 - Laboratory test"),
        F_QUAL, doc_file="LSS-CERT-QUAL-010.docx"),

    doc("QualTestReport", "LSS-CERT-QUAL-011",
        "Flame propagation test report - thermal and acoustic insulation",
        S_REL,
        _doc_common("m.sandoval", "2026-09-04", 44, checked="g.rossi",
                    approved="l.harkness",
                    do160Revision="DO-160G",
                    do160Sections="26 Fire, Flammability",
                    environmentalCategories=
                    "Appendix F Part VI flame propagation, blanket covering",
                    testPlanReference="LSS-FTP-25-006",
                    testLaboratory="Skandia Flammability Laboratory",
                    labAccreditation="FAA accepted test facility",
                    testStartDate="2026-08-24", testEndDate="2026-08-28",
                    specimenSerialNumbers="Lot 26141",
                    testResult="Pass", retestRequired=False,
                    complianceRegulations="CS 23.2325",
                    meansOfCompliance="MC4 - Laboratory test"),
        F_QUAL, doc_file="LSS-CERT-QUAL-011.docx"),
]

EMI_REPORTS = [
    doc("EMICAR", "LSS-CERT-EMI-001",
        "EMI compliance assessment - ECS controller installation",
        S_REL,
        _doc_common("d.okonjo", "2026-05-08", 62, checked="s.vanderberg",
                    approved="l.harkness",
                    equipmentUnderTest="LSS-E-00001 ECS controller, as installed",
                    do160Sections="21 Emission of Radio Frequency Energy",
                    equipmentCategory="Category M, interior equipment",
                    hirfEnvironment="Certification environment",
                    lightningZone="Interior - induced only",
                    testLaboratory=LAB, assessmentDate="2026-04-29",
                    assessmentResult="Compliant",
                    meansOfCompliance="MC8 - Equipment qualification"),
        F_QUAL, doc_file="LSS-CERT-EMI-001.docx"),

    doc("EMICAR", "LSS-CERT-EMI-002",
        "EMI compliance assessment - communications installation and antenna coupling",
        S_REL,
        _doc_common("d.okonjo", "2026-07-16", 88, checked="s.vanderberg",
                    approved="l.harkness",
                    equipmentUnderTest=
                    "LSS-23-INST-001 communications installation, VHF and satellite",
                    do160Sections="20 Radio Frequency Susceptibility",
                    equipmentCategory="Category M interior, Category T exterior antenna",
                    hirfEnvironment="Certification environment",
                    lightningZone="Zone 1A",
                    testLaboratory=LAB, assessmentDate="2026-07-07",
                    assessmentResult="Compliant with installation limitation",
                    installationLimitations=
                    "The satellite terminal shall not transmit while either VHF "
                    "transceiver is transmitting on a frequency within 1.2 MHz of a "
                    "satellite terminal harmonic. Enforced in software by the audio "
                    "control panel.",
                    meansOfCompliance="MC8 - Equipment qualification"),
        F_QUAL, doc_file="LSS-CERT-EMI-002.docx",
        notes="Compliant with an installation limitation, which is a real certification "
              "position rather than a caveat: the limitation is enforced by the audio "
              "panel software, so it appears in that software's requirements."),
]


# ─────────────────────────────────────────────────────────────────────────────
# Software and electronic hardware plans
# ─────────────────────────────────────────────────────────────────────────────

def _sw_plan(pn, title, plan_type, standard, level, objectives, independence,
             author="r.achebe", status=S_REL, pages=42, notes=None, supplements=None):
    attrs = _doc_common(author, "2026-01-22", pages, checked="s.vanderberg",
                        approved="l.harkness",
                        confidentiality="Export controlled",
                        planType=plan_type, assuranceStandard=standard,
                        applicableLevel=level,
                        objectivesApplicable=objectives,
                        objectivesWithIndependence=independence,
                        supplementsApplied=supplements,
                        authorityAgreementRef="CRI-21-002",
                        designAssuranceLevel=level,
                        meansOfCompliance="MC1 - Design review")
    return doc("SwPlan", pn, title, status, attrs, F_SW, notes=notes,
               doc_file=f"{pn}.docx")


SW_PLANS = [
    _sw_plan("LSS-CERT-SWP-001",
             "Plan for software aspects of certification - ECS controller software",
             "PSAC - plan for software aspects of certification", "DO-178C / ED-12C",
             "C", 62, True, pages=58,
             notes="Level C. The objective count and the independence requirement are "
                   "held as data so the plan set can be checked for completeness "
                   "without reading every plan."),
    _sw_plan("LSS-CERT-SWP-002",
             "Plan for software aspects of certification - audio control panel software",
             "PSAC - plan for software aspects of certification", "DO-178C / ED-12C",
             "D", 28, False, author="d.okonjo", pages=34),
    _sw_plan("LSS-CERT-SWP-003",
             "Plan for hardware aspects of certification - audio matrix CPLD",
             "PHAC - plan for hardware aspects of certification", "DO-254 / ED-80",
             "D", 18, False, author="d.okonjo", pages=26,
             notes="Simple device under DO-254, so substantiation is by exhaustive test "
                   "of all input combinations rather than the full objective set."),
    _sw_plan("LSS-CERT-SWP-004",
             "Software accomplishment summary - ECS controller software v2.1.0",
             "SAS - software accomplishment summary", "DO-178C / ED-12C",
             "C", 62, True, pages=74,
             notes="Covers version 2.1.0, the load that closed the cabin temperature "
                   "oscillation problem report. An accomplishment summary is what an "
                   "authority reads to accept the software, so it names the exact load."),
    _sw_plan("LSS-CERT-SWP-005",
             "Software configuration index - ECS controller software v2.1.0",
             "SCI - software configuration index", "DO-178C / ED-12C",
             "C", 62, True, pages=22,
             notes="Identifies exactly what is in the released load. This is the "
                   "document an operator's configuration question resolves against."),
    _sw_plan("LSS-CERT-SWP-006",
             "Software accomplishment summary - audio control panel software v1.4.2",
             "SAS - software accomplishment summary", "DO-178C / ED-12C",
             "D", 28, False, author="d.okonjo", pages=38),
    _sw_plan("LSS-CERT-SWP-007",
             "Hardware accomplishment summary - audio matrix CPLD version B",
             "HAS - hardware accomplishment summary", "DO-254 / ED-80",
             "D", 18, False, author="d.okonjo", pages=30),
    _sw_plan("LSS-CERT-SWP-008",
             "Software verification plan - ECS controller software",
             "SVP - software verification plan", "DO-178C / ED-12C",
             "C", 62, True, pages=46,
             supplements="DO-331 model based development for the control laws"),
]


# ─────────────────────────────────────────────────────────────────────────────
# Compliance reports - the certification board
# ─────────────────────────────────────────────────────────────────────────────

# Who is producing the evidence for a compliance item, by the chapter it sits in. The
# author of the compliance record is the certification engineer who will accept it;
# the person actually holding the item is the engineer generating the substantiation,
# and a board that shows the acceptor on every card tells nobody who to chase.
EVIDENCE_OWNER = {
    ATA21: "r.achebe",
    ATA23: "d.okonjo",
    ATA25: "m.sandoval",
}

# The items whose evidence is structural rather than systems work, so they sit with
# stress rather than with the chapter's systems engineer.
STRUCTURAL_ITEMS = {"LSS-CERT-COMP-010", "LSS-CERT-COMP-014", "LSS-CERT-COMP-019"}

# The items that are certification argument rather than engineering evidence - an
# equivalent safety finding, a special condition, a plan - and stay with certification.
CERTIFICATION_ITEMS = {"LSS-CERT-COMP-015", "LSS-CERT-COMP-022", "LSS-CERT-COMP-023"}


def _comp(pn, para, requirement, moc, standard, status, evidence, accepted_by=None,
          accepted=None, findings=0, loi="DOA privilege - no authority involvement",
          ata=ATA21, dal="Not applicable", notes=None, compliance="In work"):
    owner = ("p.lindqvist" if pn in STRUCTURAL_ITEMS
             else "g.rossi" if pn in CERTIFICATION_ITEMS
             else EVIDENCE_OWNER.get(ata, "s.vanderberg"))
    attrs = _doc_common("g.rossi", "2026-05-14", 12, checked="l.harkness",
                        approved="l.harkness" if accepted_by else None,
                        regulationParagraph=para,
                        requirementText=requirement,
                        consensusStandardRef=standard,
                        complianceStatus=compliance,
                        evidenceDocumentRefs=evidence,
                        acceptedBy=accepted_by,
                        acceptanceDate=accepted,
                        openFindingCount=findings,
                        levelOfInvolvement=loi,
                        meansOfCompliance=moc,
                        complianceRegulations=para,
                        designAssuranceLevel=dal,
                        assignee=owner,
                        ataChapter=ata,
                        doaApprovalReference=DOA)
    return doc("ComplianceReport", pn, f"{para} - {requirement[:70]}", status, attrs,
               F_COMP, notes=notes, doc_file=None)


COMPLIANCE_ITEMS = [
    _comp("LSS-CERT-COMP-001", "CS 23.2320",
          "Occupant physical environment - cabin altitude, temperature and air quality",
          "MC6 - Flight test", "ASTM F3061/F3061M-22b", C_SUBMITTED,
          "LSS-CERT-SAFE-001, flight test report FTR-26-0114",
          findings=0, ata=ATA21, compliance="In work",
          notes="Evidence submitted. Cabin altitude measured at 2 310 m at 13 700 m "
                "against a 2 400 m requirement. Awaiting certification acceptance."),

    _comp("LSS-CERT-COMP-002", "CS 23.2525",
          "Pressurised cabin - system design, single failure and probable combinations",
          "MC3 - Safety assessment", "ASTM F3061/F3061M-22b", C_ACCEPTED,
          "LSS-CERT-SAFE-002, LSS-CERT-QUAL-004",
          accepted_by="g.rossi", accepted="2026-04-30", dal="B", ata=ATA21,
          compliance="Compliant",
          notes="Accepted under the design organisation privilege. The deviation taken "
                "during the controller lightning test is accepted here, with the "
                "rationale that the installation sits in an interior lightning zone."),

    _comp("LSS-CERT-COMP-003", "CS 23.2525(b)",
          "Independent means of limiting maximum cabin differential pressure",
          "MC4 - Laboratory test", "ASTM F3061/F3061M-22b", C_ACCEPTED,
          "LSS-CERT-QUAL-005",
          accepted_by="g.rossi", accepted="2026-05-29", ata=ATA21,
          compliance="Compliant",
          notes="Satisfies the derived requirement LSS-REQ-SUB-0002 that the "
                "preliminary system safety assessment raised."),

    _comp("LSS-CERT-COMP-004", "CS 23.2510",
          "Equipment, systems and installations - software and electronic hardware "
          "development assurance",
          "MC1 - Design review", "ASTM F3061/F3061M-22b", C_EVIDENCE,
          "LSS-CERT-SWP-001, LSS-CERT-SWP-004, LSS-CERT-SWP-008",
          dal="C", ata=ATA21, compliance="In work",
          loi="Authority reviewed and accepted"),

    _comp("LSS-CERT-COMP-005", "CS 23.2430",
          "Bleed air system - containment of hot high pressure air",
          "MC5 - Ground test on aircraft", "ASTM F3064/F3064M-21", C_ACCEPTED,
          "Proof pressure test record PPT-26-0042, LSS-PS-0001 penetrant records",
          accepted_by="g.rossi", accepted="2026-06-12", ata=ATA21,
          compliance="Compliant"),

    _comp("LSS-CERT-COMP-006", "CS 23.2440",
          "Flammable fluid fire protection - pack bay firewall penetration",
          "MC4 - Laboratory test", "ASTM F3061/F3061M-22b", C_ACCEPTED,
          "Firewall penetration test report FWT-26-0009",
          accepted_by="g.rossi", accepted="2026-06-26", ata=ATA21,
          compliance="Compliant"),

    _comp("LSS-CERT-COMP-007", "CS 23.2500",
          "Airplane level systems requirements - two independent means of voice "
          "communication",
          "MC5 - Ground test on aircraft", "ASTM F3061/F3061M-22b", C_ACCEPTED,
          "Ground test record GTR-26-0088, flight test report FTR-26-0121",
          accepted_by="g.rossi", accepted="2026-08-07", dal="C", ata=ATA23,
          compliance="Compliant"),

    _comp("LSS-CERT-COMP-008", "CS 23.2505",
          "Function and installation - audio integrating and fail-to-direct-connect "
          "behaviour",
          "MC4 - Laboratory test", "ASTM F3061/F3061M-22b", C_ACCEPTED,
          "Bench test report BTR-26-0203, LSS-CERT-SWP-006",
          accepted_by="g.rossi", accepted="2026-08-21", dal="D", ata=ATA23,
          compliance="Compliant"),

    _comp("LSS-CERT-COMP-009", "CS 23.2515",
          "Electrical and electronic system lightning protection - external antennas",
          "MC8 - Equipment qualification", "ASTM F3061/F3061M-22b", C_ACCEPTED,
          "LSS-CERT-EMI-002, lightning direct effects report LDE-26-0017",
          accepted_by="g.rossi", accepted="2026-07-24", ata=ATA23,
          compliance="Compliant with limitation",
          notes="Compliant with the installation limitation recorded in "
                "LSS-CERT-EMI-002. The limitation is enforced in the audio panel "
                "software, so it is traceable to a requirement rather than resting on "
                "a note in a report."),

    _comp("LSS-CERT-COMP-010", "CS 23.2240",
          "Structural durability - damage tolerance of the antenna doubler cut-out in "
          "the pressure shell",
          "MC2 - Calculation / analysis", "ASTM F3114-21", C_FINDING,
          "Damage tolerance analysis DTA-26-0031, coupon fatigue test CFT-26-0012",
          findings=1, ata=ATA23, compliance="In work",
          loi="Authority reviewed and accepted",
          notes="One open finding. The authority has asked for the inspection threshold "
                "to be substantiated against the fatigue spectrum actually used rather "
                "than the generic spectrum, which means re-running the analysis. This "
                "is the demo's example of a finding sitting open on the board."),

    _comp("LSS-CERT-COMP-011", "CS 23.2530",
          "External and cockpit lighting - static discharger bonding",
          "MC7 - Design inspection / audit", "ASTM F3061/F3061M-22b", C_ACCEPTED,
          "Bonding verification record BVR-26-0054",
          accepted_by="g.rossi", accepted="2026-09-04", ata=ATA23,
          compliance="Compliant"),

    _comp("LSS-CERT-COMP-012", "CS 23.2510(a)",
          "Software development assurance - ECS controller software level C",
          "MC1 - Design review", "ASTM F3061/F3061M-22b", C_SUBMITTED,
          "LSS-CERT-SWP-004, LSS-CERT-SWP-005",
          dal="C", ata=ATA21, compliance="In work",
          loi="Authority reviewed and accepted",
          notes="Accomplishment summary submitted for version 2.1.0. The authority "
                "retains involvement for software at level C on this programme."),

    _comp("LSS-CERT-COMP-013", "CS 23.2510(b)",
          "Airborne electronic hardware development assurance - audio matrix CPLD",
          "MC1 - Design review", "ASTM F3061/F3061M-22b", C_ACCEPTED,
          "LSS-CERT-SWP-003, LSS-CERT-SWP-007",
          accepted_by="g.rossi", accepted="2026-09-11", dal="D", ata=ATA23,
          compliance="Compliant"),

    _comp("LSS-CERT-COMP-014", "CS 23.2270",
          "Emergency conditions - occupant protection under the 16g longitudinal "
          "condition",
          "MC4 - Laboratory test", "ASTM F3083/F3083M-20a", C_SUBMITTED,
          "LSS-CERT-QUAL-001, LSS-CERT-QUAL-002, LSS-CERT-SAFE-005",
          findings=0, ata=ATA25, compliance="In work",
          notes="The pilot seat test is released; the passenger seat test is still in "
                "airworthiness sign-off, so this item cannot be accepted yet. The "
                "analysis covering the remaining seat positions is validated against "
                "the pilot seat test."),

    _comp("LSS-CERT-COMP-015", "CS 23.2270(e)",
          "Equivalent safety finding - passenger seat orientation during taxi, take-off "
          "and landing",
          "MC4 - Laboratory test", "ASTM F3083/F3083M-20a", C_SUBMITTED,
          "LSS-CERT-QUAL-002, interlock functional test IFT-26-0007",
          findings=0, ata=ATA25, compliance="Equivalent safety finding",
          loi="Authority reviewed and accepted",
          notes="Equivalent safety finding sought under certification review item "
                "CRI-25-002. Submitted, awaiting the authority position. The swivel "
                "interlock added in revision B of the seat is the compensating feature."),

    _comp("LSS-CERT-COMP-016", "CS 23.2325",
          "Fire protection - cabin interior material flammability",
          "MC4 - Laboratory test", "ASTM F3083/F3083M-20a", C_ACCEPTED,
          "LSS-CERT-QUAL-006, LSS-CERT-QUAL-008, LSS-CERT-QUAL-009",
          accepted_by="g.rossi", accepted="2026-08-28", ata=ATA25,
          compliance="Compliant"),

    _comp("LSS-CERT-COMP-017", "CS 23.2325(b)",
          "Fire protection - heat release and smoke density of large-area lining panels",
          "MC4 - Laboratory test", "ASTM F3083/F3083M-20a", C_ACCEPTED,
          "LSS-CERT-QUAL-008",
          accepted_by="g.rossi", accepted="2026-08-28", ata=ATA25,
          compliance="Compliant"),

    _comp("LSS-CERT-COMP-018", "CS 23.2325(c)",
          "Fire protection - galley and lavatory monument materials and waste stowage",
          "MC4 - Laboratory test", "ASTM F3083/F3083M-20a", C_ACCEPTED,
          "LSS-CERT-QUAL-010",
          accepted_by="g.rossi", accepted="2026-09-18", ata=ATA25,
          compliance="Compliant"),

    _comp("LSS-CERT-COMP-019", "CS 23.2270(d)",
          "Emergency conditions - retention of items of mass in the baggage compartment",
          "MC4 - Laboratory test", "ASTM F3083/F3083M-20a", C_ACCEPTED,
          "Baggage restraint test report BRT-26-0021",
          accepted_by="g.rossi", accepted="2026-07-10", ata=ATA25,
          compliance="Compliant"),

    _comp("LSS-CERT-COMP-020", "CS 23.2340",
          "Emergency equipment - provision, accessibility and stowage",
          "MC7 - Design inspection / audit", "ASTM F3083/F3083M-20a", C_ACCEPTED,
          "Cabin safety inspection record CSI-26-0033",
          accepted_by="g.rossi", accepted="2026-09-25", ata=ATA25,
          compliance="Compliant"),

    _comp("LSS-CERT-COMP-021", "CS 23.2325(d)",
          "Fire protection - thermal and acoustic insulation flame propagation",
          "MC4 - Laboratory test", "ASTM F3083/F3083M-20a", C_ACCEPTED,
          "LSS-CERT-QUAL-011",
          accepted_by="g.rossi", accepted="2026-09-11", ata=ATA25,
          compliance="Compliant"),

    _comp("LSS-CERT-COMP-022", "CS 23.2335",
          "Cabin interior - occupant egress path with the forward divider installed",
          "MC7 - Design inspection / audit", "ASTM F3083/F3083M-20a", C_PLANNED,
          "Not yet identified",
          ata=ATA25, compliance="Not started",
          loi="Authority notified",
          notes="Raised by certification review item CRI-25-004 against the customer "
                "divider variant. Planned, with no method yet agreed, because the "
                "divider design is still in review. This is the demo's example of the "
                "left-hand lane of the compliance board."),

    _comp("LSS-CERT-COMP-023", "CS 23.2530(b)",
          "Cabin data network security - protection against unauthorised access",
          "MC1 - Design review", "Special condition SC-23-002", C_METHOD,
          "Security assessment plan SAP-26-0004",
          ata=ATA23, compliance="In work",
          loi="Authority witnessed",
          notes="Against special condition SC-23-002. The means of compliance has been "
                "agreed with the authority but the evidence has not started."),
]


ALL_DOCUMENTS = (DRAWINGS + SPECIFICATIONS + INTERFACE_DOCS + CERT_PLANS
                 + SAFETY_ASSESSMENTS + QUAL_DOCS + EMI_REPORTS + SW_PLANS
                 + COMPLIANCE_ITEMS)
