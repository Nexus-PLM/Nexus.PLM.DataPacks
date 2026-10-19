"""The test and analysis reports that compliance items rest on.

The FAA DER agent refused to accept the certification position and gave the reason: a
large part of the compliance checklist cited evidence that did not exist. Ground test
record GTR-26-0088, firewall penetration test FWT-26-0009, lightning direct effects
LDE-26-0017 - names in a text field, with no object behind any of them, on compliance
items already marked Accepted.

She was right, and it is the worst kind of wrong for a demonstration to an aviation
audience, because it is precisely the failure the system is supposed to prevent. An
accepted compliance item whose evidence is a string is not evidence of compliance; it is
a claim about one.

So the reports exist now, as objects, with their result, their configuration, their
laboratory and their dates - and the compliance items reference them as LINKS, so the
chain from a requirement to the thing that proves it is navigable rather than retyped.

Two are deliberately NOT created, and that is the point of them:

* `DTA-26-0031` and `CFT-26-0012` - the damage tolerance analysis and coupon fatigue test
  behind LSS-CERT-COMP-010. That item carries an OPEN authority finding: the authority
  asked for the analysis to be re-run against the fatigue spectrum actually used. The
  evidence genuinely does not exist yet, and inventing it would hide the finding.
* `IFT-26-0007` - the swivel interlock functional test behind the equivalent safety
  finding LSS-CERT-COMP-015, which is Submitted and awaiting the authority position.

A demo where every box is ticked teaches nobody anything.
"""

from lightjet_data import PROGRAMME, ROOT_FOLDER, T

RELEASED, SIGNOFF = "Released", "Airworthiness Sign-off"
F_QUAL = f"{ROOT_FOLDER}/Certification/Equipment Qualification"

LAB_NORTHGATE = "Northgate Environmental Test Laboratory"
LAB_ACC = "ISO/IEC 17025 accredited, UKAS 4471"


def evidence(pn, title, legacy, sections, categories, lab, accreditation,
             start, end, specimens, result, author, pages, notes,
             regulations=None, status=RELEASED, deviations=None, plan=None):
    """One test or analysis report, as the object a compliance item points at."""
    return {
        "type": f"{T}QualTestReport", "pn": pn, "description": title,
        "status": status, "revision": "A", "history": [("A", status)],
        "folder": F_QUAL, "notes": notes,
        "file": f"{pn}.docx",
        "attrs": {
            "programmeCode": PROGRAMME,
            "authorName": author, "checkedBy": "s.vanderberg",
            "approvedBy": "l.harkness" if status == RELEASED else None,
            "issueDate": end, "pageCount": pages,
            "retentionClass": "Type design - life of type",
            "confidentiality": "Internal",
            "certificationBasis": "CS-23 Amdt 5 + ASTM F44 MoC",
            "certificationAuthority": "EASA",
            "approvalRoute": "DOA privilege (21A.263)",
            "doaApprovalReference": "EASA.21J.0742",
            "complianceRegulations": regulations,
            "meansOfCompliance": "MC4 - Laboratory test",
            "do160Revision": "DO-160G",
            "do160Sections": sections,
            "environmentalCategories": categories,
            # The laboratory's own reference, kept because that is what appears on the
            # paperwork the laboratory issues and what an auditor will ask to match.
            # The laboratory's own reference, which is what appears on the
            # paperwork it issues and what an auditor asks to match.
            "testPlanReference": plan or legacy,
            "testLaboratory": lab, "labAccreditation": accreditation,
            "testStartDate": start, "testEndDate": end,
            "specimenSerialNumbers": specimens,
            "testResult": result,
            "deviationReferences": deviations,
            "retestRequired": False,
        },
    }


EVIDENCE = [
    evidence(
        "LSS-CERT-QUAL-013",
        "Ground test record - communications system installed performance",
        "GTR-26-0088", "20 Radio Frequency Susceptibility",
        "Installed system ground test; not a DO-160 category test",
        "Light Speed Systems flight test, Cranfield", "Part 21 Subpart J DOA privilege",
        "2026-07-28", "2026-08-04", "Airframe 002, G-MECA",
        "Pass", "d.okonjo", 46, regulations="CS 23.2500",
        notes="Each VHF transceiver exercised with the other powered down, which is what "
              "makes the two means genuinely independent rather than nominally so. Range "
              "and intelligibility recorded at four bearings."),

    evidence(
        "LSS-CERT-QUAL-014",
        "Flight test report - communications range and intelligibility",
        "FTR-26-0121", "20 Radio Frequency Susceptibility",
        "In-flight measurement; not a laboratory category test",
        "Light Speed Systems flight test, Cranfield", "Part 21 Subpart J DOA privilege",
        "2026-08-11", "2026-08-19", "Airframe 001, G-NXPA",
        "Pass", "d.okonjo", 72, regulations="CS 23.2500",
        notes="Flown on the prototype, which is on a permit to fly. The credit is "
              "valid because the communications installation on airframe 001 is the same "
              "revision as the production standard - confirmed from the as-built."),

    evidence(
        "LSS-CERT-QUAL-015",
        "Firewall penetration fire test report - pack bay seal plate",
        "FWT-26-0009", "26 Fire, Flammability",
        "ISO 2685 flame, 1100 degrees C for 15 minutes",
        "Northgate Fire Test Laboratory", LAB_ACC,
        "2026-06-08", "2026-06-19", "LSS-21-0014 S/N 0004 with AMS 3277 sealant",
        "Pass", "m.sandoval", 58, regulations="CS 23.2440",
        notes="THE REPORT WAVE 3 TURNS ON. The specimen was the titanium seal plate "
              "sealed with polysulphide AMS 3277 - the joint and the sealant that are "
              "now suspected of causing in-service corrosion. If the joint detail or the "
              "sealant changes, this credit is against a configuration that no longer "
              "exists, and LSS-CERT-COMP-006 goes with it."),

    evidence(
        "LSS-CERT-QUAL-016",
        "Lightning direct effects test report - VHF antenna and doubler",
        "LDE-26-0017", "23 Lightning Direct Effects",
        "Zone 1A, waveforms A, B, C and D",
        LAB_NORTHGATE, LAB_ACC,
        "2026-07-01", "2026-07-15", "LSS-E-00011 and LSS-23-0001 S/N 0002",
        "Pass with deviation", "d.okonjo", 94, regulations="CS 23.2515",
        deviations="DEV-LDE-0017-01",
        notes="Waveform D applied at 95 percent of the Zone 1A level; the generator "
              "could not reach full amplitude on the day. Accepted because the margin on "
              "waveforms A and B was large and the failure mode is arc attachment, not "
              "cumulative. The deviation is named on LSS-CERT-COMP-009."),

    evidence(
        "LSS-CERT-QUAL-017",
        "Bonding verification record - static dischargers and antenna earths",
        "BVR-26-0054", "23 Lightning Direct Effects",
        "DC resistance measurement, installed",
        "Light Speed Systems production test", "Part 21 Subpart G POA",
        "2026-08-24", "2026-08-28", "Airframe 002, all bonding points",
        "Pass", "d.okonjo", 24, regulations="CS 23.2530",
        notes="Every bond measured installed, not on the bench. Antenna earth 1.8 "
              "milliohm against a 2.5 milliohm requirement; dischargers all below "
              "0.1 ohm."),

    evidence(
        "LSS-CERT-QUAL-018",
        "Bench test report - audio integrating selection and fail-to-direct-connect",
        "BTR-26-0203", "16 Power Input",
        "Functional bench test with controlled power removal",
        "Light Speed Systems avionics laboratory", "Part 21 Subpart J DOA privilege",
        "2026-08-10", "2026-08-17", "LSS-E-00010 S/N 0003",
        "Pass", "d.okonjo", 38, regulations="CS 23.2505",
        notes="Every selection combination exercised, then panel power removed. The "
              "panel falls back to a direct connection between crew station and "
              "transceiver, which is what keeps the two independent transceivers "
              "independent when the panel between them fails."),

    evidence(
        "LSS-CERT-QUAL-019",
        "Proof pressure test record - bleed air duct assembly",
        "PPT-26-0042", "4 Temperature and Altitude",
        "Proof pressure at maximum bleed temperature",
        "Light Speed Systems production test", "Part 21 Subpart G POA",
        "2026-05-26", "2026-06-04", "LSS-21-0001 S/N 0003 and 0005",
        "Pass", "m.sandoval", 32, regulations="CS 23.2430",
        notes="Held at 1.5 times maximum working pressure at temperature. Every weld "
              "penetrant inspected before and after; no indications. This is the record "
              "the delta first article on the revision B coupling has to be read "
              "against."),

    evidence(
        "LSS-CERT-QUAL-020",
        "Baggage restraint test report - 9g forward emergency landing condition",
        "BRT-26-0021", "7 Operational Shock and Crash Safety",
        "Static 9g forward with maximum rated baggage load",
        "Calspan Dynamic Test Services", "ISO/IEC 17025 accredited",
        "2026-06-22", "2026-06-26", "LSS-F-00070 with the compartment liner",
        "Pass", "p.lindqvist", 41, regulations="CS 23.2270(d)",
        notes="The net, its attachments and the compartment liner tested together, "
              "because a net that holds while its attachment tears out of the liner has "
              "proved nothing."),

    evidence(
        "LSS-CERT-QUAL-021",
        "Cabin safety inspection record - emergency equipment provision and access",
        "CSI-26-0033", "26 Fire, Flammability",
        "Design inspection against the cabin safety requirements",
        "Light Speed Systems airworthiness", "Part 21 Subpart J DOA privilege",
        "2026-09-14", "2026-09-22", "Airframe 002 cabin, as fitted",
        "Pass", "g.rossi", 28, regulations="CS 23.2340",
        notes="Accessibility is part of the requirement, not a detail of it - an "
              "extinguisher that cannot be reached from a seated position has not been "
              "provided. Reach measured from every occupant place."),

    evidence(
        "LSS-CERT-QUAL-022",
        "Flight test report - cabin altitude and environmental performance",
        "FTR-26-0114", "4 Temperature and Altitude",
        "In-flight measurement through a full climb and descent profile",
        "Light Speed Systems flight test, Cranfield", "Part 21 Subpart J DOA privilege",
        "2026-09-02", "2026-09-16", "Airframe 002, G-MECA",
        "Pass", "r.achebe", 86, regulations="CS 23.2320", status=SIGNOFF,
        notes="Cabin altitude 2 310 m at 13 700 m against a 2 400 m requirement, held "
              "for 34 minutes in stabilised cruise. IN AIRWORTHINESS SIGN-OFF, NOT "
              "RELEASED - and the DER's point stands: this was flown with the GLASS ram "
              "air scoop fitted. If the carbon scoop changes pack inlet pressure, the "
              "margin this report demonstrates was measured on a configuration that is "
              "being changed."),
]


# ─────────────────────────────────────────────────────────────────────────────
# Compliance item → the evidence it rests on, as links rather than text
# ─────────────────────────────────────────────────────────────────────────────

EVIDENCE_LINKS = [
    ("LSS-CERT-COMP-007", "LSS-CERT-QUAL-013", "Installed ground test."),
    ("LSS-CERT-COMP-007", "LSS-CERT-QUAL-014", "Flight test range and intelligibility."),
    ("LSS-CERT-COMP-006", "LSS-CERT-QUAL-015",
     "Firewall penetration fire test, run on the joint as currently designed and sealed."),
    ("LSS-CERT-COMP-009", "LSS-CERT-QUAL-016",
     "Lightning direct effects. Pass with deviation on waveform D amplitude."),
    ("LSS-CERT-COMP-011", "LSS-CERT-QUAL-017", "Installed bonding measurements."),
    ("LSS-CERT-COMP-008", "LSS-CERT-QUAL-018", "Audio integrating functional test."),
    ("LSS-CERT-COMP-005", "LSS-CERT-QUAL-019", "Proof pressure at temperature."),
    ("LSS-CERT-COMP-019", "LSS-CERT-QUAL-020", "Baggage restraint static test."),
    ("LSS-CERT-COMP-020", "LSS-CERT-QUAL-021", "Cabin safety design inspection."),
    ("LSS-CERT-COMP-001", "LSS-CERT-QUAL-022",
     "Flight test of cabin altitude. Not yet released, which is why this compliance "
     "item is Submitted rather than Accepted."),
    # The part the report is about, so the chain runs both ways.
    ("LSS-21-0014", "LSS-CERT-QUAL-015",
     "The firewall penetration test was run on this plate and its sealant."),
    ("LSS-23-0001", "LSS-CERT-QUAL-016", "Lightning direct effects on the doubler."),
    ("LSS-21-0001", "LSS-CERT-QUAL-019", "Proof pressure test of this assembly."),
    ("LSS-F-00070", "LSS-CERT-QUAL-020", "Baggage restraint test."),
    ("LSS-E-00010", "LSS-CERT-QUAL-018", "Audio panel bench test."),
    ("LSS-21-INST-001", "LSS-CERT-QUAL-022", "Cabin altitude flight test."),
]

# The compliance items whose evidenceDocumentRefs should now name the object rather than
# the laboratory's own reference. The laboratory reference survives on the report itself.
EVIDENCE_REF_UPDATES = {
    "LSS-CERT-COMP-001": "LSS-CERT-QUAL-022, LSS-CERT-SAFE-001",
    "LSS-CERT-COMP-005": "LSS-CERT-QUAL-019, LSS-PS-0001",
    "LSS-CERT-COMP-006": "LSS-CERT-QUAL-015",
    "LSS-CERT-COMP-007": "LSS-CERT-QUAL-013, LSS-CERT-QUAL-014",
    "LSS-CERT-COMP-008": "LSS-CERT-QUAL-018, LSS-CERT-SWP-006",
    "LSS-CERT-COMP-009": "LSS-CERT-EMI-002, LSS-CERT-QUAL-016",
    "LSS-CERT-COMP-011": "LSS-CERT-QUAL-017",
    "LSS-CERT-COMP-019": "LSS-CERT-QUAL-020",
    "LSS-CERT-COMP-020": "LSS-CERT-QUAL-021",
    # Left naming documents that do not exist, on purpose: the authority finding is open
    # and the evidence has genuinely not been produced.
    "LSS-CERT-COMP-010": "Damage tolerance analysis DTA-26-0031 and coupon fatigue test "
                         "CFT-26-0012 - NOT YET PRODUCED. The authority has asked for the "
                         "analysis to be re-run against the fatigue spectrum actually "
                         "used. This finding is open and the evidence does not exist.",
    "LSS-CERT-COMP-015": "Interlock functional test IFT-26-0007 - NOT YET PRODUCED. "
                         "Awaiting the authority position on the equivalent safety "
                         "finding before the test is run.",
}
