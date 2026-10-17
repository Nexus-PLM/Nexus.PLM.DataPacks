"""The NX-200 requirement set, its trace links and its baseline.

Six levels, each a concrete company type under the matching out-of-the-box abstract level:

    AircraftRequirement   LSS-REQ-ACFT-nnnn   what the aeroplane must do
    OperatorRequirement   LSS-REQ-OPS-nnnn    what a launch operator asked for
    CertRequirement       LSS-REQ-CERT-nnnn   what the certification basis demands
    SystemRequirement     LSS-REQ-SYS-nnnn    allocated to one ATA system
    SubsystemRequirement  LSS-REQ-SUB-nnnn    allocated inside a system
    ComponentRequirement  LSS-REQ-CMP-nnnn    becomes a spec for one item

The tree is held by `parentPlmId`, so the Requirements app renders it as a hierarchy.
Trace links are separate objects and carry the cross-cutting relationships the hierarchy
cannot: which part implements a requirement, which test verifies it, which compliance item
it feeds, and which requirements a safety assessment derived.

Two things here are the point of the whole demo for a certification audience:

* A requirement with no parent and `derivedRequirement` true is an ARP4754A derived
  requirement. It did not come down from a higher level - it came out of the safety
  assessment - and the standard requires it to be fed back into that assessment. Holding a
  flag means the set can be listed and reviewed, rather than rediscovered.
* A trace link pinned to a target revision goes SUSPECT when that target is revised. That
  is the mechanism that answers "what does this change break?" without anyone remembering.
"""

from lightjet_data import ATA21, ATA23, ATA25, PROGRAMME, ROOT_FOLDER, T

R_DRAFT, R_REVIEW, R_APPROVED, R_IMPL, R_VERIFIED = (
    "Draft", "In Review", "Approved", "Implemented", "Verified")

FREQ = f"{ROOT_FOLDER}/Certification/Certification Programme"


def req(level, pn, title, body, status, attrs, parent=None, folder=None, notes=None):
    """One requirement. `level` is the concrete type stem."""
    base = {
        "title": title,
        "body": body,
        "programmeCode": PROGRAMME,
        "allocationStatus": "Allocated",
        "verificationStatus": "Not verified",
        "certificationCredit": False,
        "derivedRequirement": False,
        "volatilityRisk": "Stable",
    }
    base.update(attrs)
    if parent:
        base["parentPlmId"] = parent          # resolved to a real id by the loader
    return {
        "type": f"{T}{level}", "pn": pn, "description": title, "status": status,
        "attrs": base, "parent": parent, "folder": folder or FREQ, "notes": notes,
        "revision": "A", "history": [("A", status)],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Aircraft level
# ─────────────────────────────────────────────────────────────────────────────

REQUIREMENTS = [
    req("AircraftRequirement", "LSS-REQ-ACFT-0001",
        "Cabin altitude shall not exceed 2 400 m at maximum operating altitude",
        "With the aeroplane at its maximum operating altitude of 13 700 m (45 000 ft) and "
        "the environmental control system operating normally, cabin pressure altitude "
        "shall not exceed 2 400 m (8 000 ft).",
        R_APPROVED,
        {"requirementType": "Performance", "priority": "Critical",
         "rationale": "Cabin altitude is the headline comfort and physiological "
                      "requirement for the class and is quoted in the sales "
                      "specification. It sizes the pressurisation system and drives the "
                      "fuselage differential pressure.",
         "source": "NX-200 aircraft specification, issue 4",
         "acceptanceCriteria": "Demonstrated by flight test at maximum operating "
                               "altitude with the cabin altitude recorded for not less "
                               "than 30 minutes in stabilised cruise.",
         "verificationMethod": "Test", "safetyDAL": "Not Applicable",
         "ataChapter": ATA21, "requirementOwner": "r.achebe",
         "designMissionProfile": "1 850 km stage length, two crew and five passengers",
         "performanceTarget": "2 400 m maximum at 13 700 m",
         "marketDriver": "Comfort parity with the segment leader",
         "verificationStatus": "In verification",
         "certificationCredit": True,
         "complianceItemRef": "LSS-CERT-COMP-001"}),

    req("AircraftRequirement", "LSS-REQ-ACFT-0002",
        "The cabin shall provide clear air-to-ground and air-to-air voice communication "
        "throughout the operating envelope",
        "The aeroplane shall provide two independent means of air-to-ground voice "
        "communication and one satellite voice capability, usable from either crew "
        "station throughout the certified operating envelope.",
        R_APPROVED,
        {"requirementType": "Functional", "priority": "Critical",
         "rationale": "Two independent communication means is both an operational "
                      "necessity and a condition of the intended operations.",
         "source": "NX-200 aircraft specification, issue 4",
         "acceptanceCriteria": "Ground and flight test demonstration of range and "
                               "intelligibility on each transceiver independently.",
         "verificationMethod": "Test", "safetyDAL": "DAL-C",
         "ataChapter": ATA23, "requirementOwner": "r.achebe",
         "performanceTarget": "Two independent VHF plus satellite voice",
         "verificationStatus": "Verified",
         "verificationEvidenceRef": "LSS-CERT-COMP-007",
         "certificationCredit": True,
         "complianceItemRef": "LSS-CERT-COMP-007"}),

    req("AircraftRequirement", "LSS-REQ-ACFT-0003",
        "The cabin interior shall seat seven occupants and survive the emergency landing "
        "conditions",
        "The cabin shall provide two crew and five passenger places. Every occupant place "
        "and its supporting structure shall withstand the emergency landing conditions of "
        "the certification basis without injurious occupant deceleration or loss of "
        "restraint.",
        R_APPROVED,
        {"requirementType": "Safety", "priority": "Critical",
         "rationale": "Occupant survivability in a survivable impact is the single "
                      "largest body of substantiation in the cabin and sizes the seat "
                      "track, floor beams and seat structure together.",
         "source": "NX-200 aircraft specification, issue 4",
         "acceptanceCriteria": "Dynamic test of the critical seat installation to the "
                               "16g longitudinal condition, with analysis for the "
                               "remaining positions validated against the test.",
         "verificationMethod": "Test", "safetyDAL": "Not Applicable",
         "ataChapter": ATA25, "requirementOwner": "p.lindqvist",
         "performanceTarget": "Seven occupant places, 16g longitudinal",
         "verificationStatus": "In verification",
         "certificationCredit": True,
         "complianceItemRef": "LSS-CERT-COMP-014"}),

    req("AircraftRequirement", "LSS-REQ-ACFT-0004",
        "Cabin interior materials shall not contribute materially to an in-flight fire",
        "Materials used in the cabin interior shall meet the flammability, heat release "
        "and smoke density criteria of the certification basis appropriate to their "
        "surface area and location.",
        R_APPROVED,
        {"requirementType": "Safety", "priority": "Critical",
         "rationale": "Interior flammability is the requirement that most constrains "
                      "material choice, and a late material substitution without "
                      "re-test is the most common cause of a cabin certification delay.",
         "source": "Certification basis, CS 23.853 and Appendix F",
         "acceptanceCriteria": "Laboratory test of each material to the applicable "
                               "Appendix F part, traceable to the part it is used on.",
         "verificationMethod": "Test", "safetyDAL": "Not Applicable",
         "ataChapter": ATA25, "requirementOwner": "g.rossi",
         "verificationStatus": "In verification",
         "certificationCredit": True,
         "complianceItemRef": "LSS-CERT-COMP-016"}),

    # ── Operator level ──────────────────────────────────────────────────────
    req("OperatorRequirement", "LSS-REQ-OPS-0001",
        "Launch operator requires satellite voice and data at every seat",
        "Meridian Executive Charter requires satellite voice available from every "
        "passenger place and a data service sufficient for cabin messaging.",
        R_APPROVED,
        {"requirementType": "Operational", "priority": "High",
         "rationale": "Charter operation into regions without reliable VHF coverage.",
         "source": "Meridian Executive Charter letter of intent, 3 February 2026",
         "acceptanceCriteria": "Demonstration of satellite voice from each place and a "
                               "sustained 88 kbit/s data link.",
         "verificationMethod": "Demonstration", "safetyDAL": "Not Applicable",
         "ataChapter": ATA23, "requirementOwner": "f.mbeki",
         "operatorName": "Meridian Executive Charter", "fleetSize": 6,
         "contractualCommitment": True, "negotiationStatus": "Agreed",
         "verificationStatus": "Verification planned"}),

    req("OperatorRequirement", "LSS-REQ-OPS-0004",
        "Launch operator requires a forward cabin divider with credenza",
        "Meridian Executive Charter requires a forward divider incorporating a credenza "
        "and coat stowage, as an approved interior variant.",
        R_REVIEW,
        {"requirementType": "Operational", "priority": "Medium",
         "rationale": "Differentiates the charter cabin and is a condition of the "
                      "launch order for airframes 004 onward.",
         "source": "Meridian Executive Charter cabin review, 18 June 2026",
         "acceptanceCriteria": "Approved interior variant with flammability "
                               "substantiation and a weight and balance entry.",
         "verificationMethod": "Inspection", "safetyDAL": "Not Applicable",
         "ataChapter": ATA25, "requirementOwner": "f.mbeki",
         "operatorName": "Meridian Executive Charter", "fleetSize": 6,
         "contractualCommitment": False, "negotiationStatus": "Under negotiation",
         "volatilityRisk": "Under negotiation",
         "allocationStatus": "Partially allocated",
         "verificationStatus": "Not verified"},
        notes="Still in review: the heat release and smoke density testing for the "
              "divider has not been completed, so the requirement cannot be approved "
              "with a verification method that is known to be achievable."),

    # ── Certification level ─────────────────────────────────────────────────
    req("CertRequirement", "LSS-REQ-CERT-0001",
        "CS 23.2525 - Pressurised cabin, system design and analysis",
        "The pressurisation system shall be designed and substantiated so that no single "
        "failure or probable combination of failures results in a cabin pressure altitude "
        "exceeding the limits of the certification basis.",
        R_APPROVED,
        {"requirementType": "Certification", "priority": "Critical",
         "rationale": "Direct requirement of the certification basis.",
         "source": "CS-23 Amendment 5",
         "acceptanceCriteria": "System safety assessment showing the hazardous failure "
                               "condition is extremely remote, supported by test.",
         "verificationMethod": "Analysis", "safetyDAL": "DAL-B",
         "regulatoryReference": "CS 23.2525",
         "regulationParagraph": "CS 23.2525",
         "certificationBasis": "CS-23 Amdt 5 + ASTM F44 MoC",
         "consensusStandardRef": "ASTM F3061/F3061M-22b",
         "meansOfCompliance": "MC3 - Safety assessment",
         "ataChapter": ATA21, "requirementOwner": "g.rossi",
         "certificationCredit": True,
         "complianceItemRef": "LSS-CERT-COMP-002",
         "safetyAssessmentRef": "LSS-CERT-SAFE-002",
         "verificationStatus": "In verification"}),

    req("CertRequirement", "LSS-REQ-CERT-0002",
        "CS 23.2320 - Occupant physical environment",
        "The aeroplane shall provide the occupants with a physical environment that "
        "protects them from the effects of altitude, temperature and contamination.",
        R_APPROVED,
        {"requirementType": "Certification", "priority": "Critical",
         "rationale": "Direct requirement of the certification basis.",
         "source": "CS-23 Amendment 5",
         "acceptanceCriteria": "Flight test of cabin altitude, temperature and air "
                               "quality across the envelope.",
         "verificationMethod": "Test", "safetyDAL": "Not Applicable",
         "regulatoryReference": "CS 23.2320",
         "regulationParagraph": "CS 23.2320",
         "certificationBasis": "CS-23 Amdt 5 + ASTM F44 MoC",
         "consensusStandardRef": "ASTM F3061/F3061M-22b",
         "meansOfCompliance": "MC6 - Flight test",
         "ataChapter": ATA21, "requirementOwner": "g.rossi",
         "certificationCredit": True,
         "complianceItemRef": "LSS-CERT-COMP-001",
         "verificationStatus": "In verification"}),

    req("CertRequirement", "LSS-REQ-CERT-0003",
        "CS 23.2270 - Emergency conditions, occupant restraint and retention of items",
        "Each occupant shall be protected under the emergency landing conditions, and "
        "items of mass shall be retained so that they do not present a hazard.",
        R_APPROVED,
        {"requirementType": "Certification", "priority": "Critical",
         "rationale": "Direct requirement of the certification basis. Governs the seat, "
                      "the restraint, the seat track and the baggage restraint together.",
         "source": "CS-23 Amendment 5",
         "acceptanceCriteria": "Dynamic test of the critical installation plus analysis "
                               "validated by that test.",
         "verificationMethod": "Test", "safetyDAL": "Not Applicable",
         "regulatoryReference": "CS 23.2270",
         "regulationParagraph": "CS 23.2270",
         "certificationBasis": "CS-23 Amdt 5 + ASTM F44 MoC",
         "consensusStandardRef": "ASTM F3083/F3083M-20a",
         "meansOfCompliance": "MC4 - Laboratory test",
         "ataChapter": ATA25, "requirementOwner": "g.rossi",
         "certificationCredit": True,
         "complianceItemRef": "LSS-CERT-COMP-014",
         "verificationStatus": "In verification"}),

    req("CertRequirement", "LSS-REQ-CERT-0004",
        "CS 23.2325 - Fire protection, cabin interior materials",
        "Cabin interior materials shall meet the flammability criteria appropriate to "
        "their use, and the compartment interiors shall be constructed of materials that "
        "meet the applicable test criteria.",
        R_APPROVED,
        {"requirementType": "Certification", "priority": "Critical",
         "rationale": "Direct requirement of the certification basis.",
         "source": "CS-23 Amendment 5, Appendix F",
         "acceptanceCriteria": "Laboratory test of each material to the applicable "
                               "Appendix F part, with the result traceable to the part.",
         "verificationMethod": "Test", "safetyDAL": "Not Applicable",
         "regulatoryReference": "CS 23.2325",
         "regulationParagraph": "CS 23.2325",
         "certificationBasis": "CS-23 Amdt 5 + ASTM F44 MoC",
         "consensusStandardRef": "ASTM F3083/F3083M-20a",
         "meansOfCompliance": "MC4 - Laboratory test",
         "ataChapter": ATA25, "requirementOwner": "g.rossi",
         "certificationCredit": True,
         "complianceItemRef": "LSS-CERT-COMP-016",
         "verificationStatus": "In verification"}),

    req("CertRequirement", "LSS-REQ-CERT-0005",
        "Equivalent safety finding - passenger seat orientation during taxi, take-off "
        "and landing",
        "An equivalent safety finding is sought to permit a swivelling club seat, on the "
        "basis of a mechanical interlock that holds the seat in the forward-facing "
        "position whenever the seat belt sign is illuminated.",
        R_APPROVED,
        {"requirementType": "Certification", "priority": "High",
         "rationale": "The club four arrangement is a commercial requirement and a "
                      "swivelling seat cannot meet the literal orientation requirement. "
                      "The interlock provides an equivalent level of safety.",
         "source": "Certification review item CRI-25-002",
         "acceptanceCriteria": "Authority acceptance of the equivalent safety finding, "
                               "supported by a test of the interlock and the dynamic "
                               "test in the forward-facing position.",
         "verificationMethod": "Test", "safetyDAL": "Not Applicable",
         "regulatoryReference": "CS 23.2270(e)",
         "regulationParagraph": "CS 23.2270(e)",
         "certificationBasis": "CS-23 Amdt 5 + ASTM F44 MoC",
         "meansOfCompliance": "MC4 - Laboratory test",
         "equivalentSafetyFinding": True,
         "ataChapter": ATA25, "requirementOwner": "g.rossi",
         "certificationCredit": True,
         "complianceItemRef": "LSS-CERT-COMP-015",
         "verificationStatus": "In verification",
         "volatilityRisk": "Awaiting authority position"},
        notes="Equivalent safety finding, not a deviation. The interlock in revision B "
              "of the passenger seat exists because of this finding, which is why "
              "LSS-ECO-00001 changed the seat."),

    # ── System level ────────────────────────────────────────────────────────
    req("SystemRequirement", "LSS-REQ-SYS-0001",
        "The environmental control system shall maintain cabin altitude at or below "
        "2 400 m",
        "The environmental control system shall maintain cabin pressure altitude at or "
        "below 2 400 m with the aeroplane at 13 700 m, and shall limit cabin rate of "
        "change to 150 m per minute in climb and 90 m per minute in descent.",
        R_IMPL,
        {"requirementType": "Performance", "priority": "Critical",
         "rationale": "Allocation of the aircraft cabin altitude requirement to the "
                      "system that delivers it, with the rate-of-change limits that make "
                      "it comfortable rather than merely compliant.",
         "source": "LSS-REQ-ACFT-0001",
         "acceptanceCriteria": "Flight test record of cabin altitude and rate of change "
                               "through a full climb and descent profile.",
         "verificationMethod": "Test", "safetyDAL": "DAL-C",
         "ataChapter": ATA21, "requirementOwner": "r.achebe",
         "systemName": "Environmental control and pressurisation",
         "functionalHazardRef": "LSS-CERT-SAFE-001",
         "failureEffectClassification": "Major",
         "redundancyRequirement": "Dual independent",
         "verificationStatus": "In verification",
         "verificationEvidenceRef": "LSS-CERT-COMP-001",
         "certificationCredit": True,
         "complianceItemRef": "LSS-CERT-COMP-001",
         "safetyAssessmentRef": "LSS-CERT-SAFE-001"},
        parent="LSS-REQ-ACFT-0001"),

    req("SystemRequirement", "LSS-REQ-SYS-0002",
        "No single failure of the pressurisation system shall result in a hazardous "
        "cabin pressure condition",
        "No single failure, and no probable combination of failures, of the "
        "pressurisation control system shall result in cabin pressure altitude exceeding "
        "4 600 m or in cabin differential pressure exceeding the structural limit.",
        R_IMPL,
        {"requirementType": "Safety", "priority": "Critical",
         "rationale": "The hazardous failure condition identified in the functional "
                      "hazard assessment. Drives the dual channel controller, the "
                      "independent safety valve and design assurance level B.",
         "source": "LSS-REQ-CERT-0001 and LSS-CERT-SAFE-001",
         "acceptanceCriteria": "System safety assessment showing the condition is "
                               "extremely remote, at or below 1E-7 per flight hour, with "
                               "failure modes confirmed by test.",
         "verificationMethod": "Analysis", "safetyDAL": "DAL-B",
         "ataChapter": ATA21, "requirementOwner": "r.achebe",
         "systemName": "Environmental control and pressurisation",
         "functionalHazardRef": "LSS-CERT-SAFE-001",
         "failureEffectClassification": "Hazardous / Severe-Major",
         "redundancyRequirement": "Fail-safe",
         "verificationStatus": "In verification",
         "certificationCredit": True,
         "complianceItemRef": "LSS-CERT-COMP-002",
         "safetyAssessmentRef": "LSS-CERT-SAFE-002"},
        parent="LSS-REQ-CERT-0001"),

    req("SystemRequirement", "LSS-REQ-SYS-0003",
        "The communications system shall provide two independent VHF transceivers and "
        "satellite voice",
        "The communications system shall provide two VHF transceivers on independent "
        "power sources and independent antennas, with 8.33 kHz channel spacing, plus one "
        "satellite voice terminal.",
        R_VERIFIED,
        {"requirementType": "Functional", "priority": "Critical",
         "rationale": "Allocation of the aircraft communication requirement. Independence "
                      "of power and antenna is what makes the two means genuinely "
                      "independent rather than nominally so.",
         "source": "LSS-REQ-ACFT-0002",
         "acceptanceCriteria": "Ground test of each transceiver with the other powered "
                               "down, followed by flight test of range.",
         "verificationMethod": "Test", "safetyDAL": "DAL-C",
         "ataChapter": ATA23, "requirementOwner": "r.achebe",
         "systemName": "Communications",
         "failureEffectClassification": "Major",
         "redundancyRequirement": "Dual independent",
         "verificationStatus": "Verified",
         "verificationEvidenceRef": "LSS-CERT-COMP-007",
         "certificationCredit": True,
         "complianceItemRef": "LSS-CERT-COMP-007"},
        parent="LSS-REQ-ACFT-0002"),

    req("SystemRequirement", "LSS-REQ-SYS-0004",
        "The cabin interior shall withstand the 16g longitudinal emergency landing "
        "condition",
        "Every occupant place, its restraint and its attachment to primary structure "
        "shall withstand the 16g longitudinal dynamic condition without failure of the "
        "restraint, injurious loads on the occupant, or separation of the seat from the "
        "floor.",
        R_IMPL,
        {"requirementType": "Safety", "priority": "Critical",
         "rationale": "Allocation of the aircraft occupant protection requirement to the "
                      "interior. The load path runs seat to fitting to track to floor "
                      "beam, so the requirement has to be owned at system level rather "
                      "than by the seat alone.",
         "source": "LSS-REQ-ACFT-0003 and LSS-REQ-CERT-0003",
         "acceptanceCriteria": "Dynamic test of the critical seat installation, with the "
                               "remaining positions covered by analysis validated "
                               "against that test.",
         "verificationMethod": "Test", "safetyDAL": "Not Applicable",
         "ataChapter": ATA25, "requirementOwner": "p.lindqvist",
         "systemName": "Equipment and furnishings",
         "failureEffectClassification": "Hazardous / Severe-Major",
         "redundancyRequirement": "None",
         "verificationStatus": "In verification",
         "verificationEvidenceRef": "LSS-CERT-QUAL-001",
         "certificationCredit": True,
         "complianceItemRef": "LSS-CERT-COMP-014"},
        parent="LSS-REQ-CERT-0003"),

    req("SystemRequirement", "LSS-REQ-SYS-0005",
        "Cabin interior materials shall meet the applicable Appendix F criteria",
        "Every cabin interior material shall be tested to the Appendix F part applicable "
        "to its location and surface area, and the result shall be traceable to the part "
        "number and material batch it covers.",
        R_IMPL,
        {"requirementType": "Safety", "priority": "Critical",
         "rationale": "Allocation of the aircraft fire protection requirement. The "
                      "traceability half is as important as the test half: an untraceable "
                      "pass is not evidence.",
         "source": "LSS-REQ-ACFT-0004 and LSS-REQ-CERT-0004",
         "acceptanceCriteria": "A test report per material, referenced from the part that "
                               "uses it, with the batch recorded.",
         "verificationMethod": "Test", "safetyDAL": "Not Applicable",
         "ataChapter": ATA25, "requirementOwner": "g.rossi",
         "systemName": "Equipment and furnishings",
         "failureEffectClassification": "Major",
         "redundancyRequirement": "None",
         "verificationStatus": "In verification",
         "certificationCredit": True,
         "complianceItemRef": "LSS-CERT-COMP-016"},
        parent="LSS-REQ-CERT-0004"),

    # ── Subsystem level ─────────────────────────────────────────────────────
    req("SubsystemRequirement", "LSS-REQ-SUB-0001",
        "The pressurisation control subsystem shall be dual channel with independent "
        "sensing",
        "The cabin pressure controller shall provide two control channels with "
        "independent pressure sensing, automatic changeover on channel failure, and a "
        "manual mode available to the crew.",
        R_IMPL,
        {"requirementType": "Design", "priority": "Critical",
         "rationale": "Derived from the single-failure requirement. Independent sensing "
                      "is the part that is easy to lose in a cost reduction and is the "
                      "reason the requirement is written down separately.",
         "source": "LSS-REQ-SYS-0002",
         "acceptanceCriteria": "Failure mode test of channel changeover and manual mode, "
                               "with the sensing independence confirmed by inspection.",
         "verificationMethod": "Test", "safetyDAL": "DAL-B",
         "ataChapter": ATA21, "requirementOwner": "r.achebe",
         "subsystemLabel": "Pressurisation control", "ataSubject": "21-30",
         "interfaceDocumentRef": "LSS-ICD-001",
         "verificationStatus": "In verification",
         "complianceItemRef": "LSS-CERT-COMP-002",
         "safetyAssessmentRef": "LSS-CERT-SAFE-002"},
        parent="LSS-REQ-SYS-0002"),

    req("SubsystemRequirement", "LSS-REQ-SUB-0002",
        "An independent cabin pressure safety valve shall limit maximum differential "
        "pressure",
        "A cabin pressure safety valve, independent of the outflow valve and of the "
        "pressurisation controller, shall limit cabin differential pressure to the "
        "structural design value with no electrical power available.",
        R_IMPL,
        {"requirementType": "Safety", "priority": "Critical",
         "rationale": "This is an ARP4754A derived requirement. It did not come down "
                      "from the aircraft specification - it came out of the preliminary "
                      "system safety assessment, which found that the catastrophic "
                      "overpressure case needs a means of protection that shares nothing "
                      "with the normal control path.",
         "source": "LSS-CERT-SAFE-001, preliminary system safety assessment",
         "acceptanceCriteria": "Test of the safety valve cracking pressure and flow "
                               "capacity with no electrical power applied.",
         "verificationMethod": "Test", "safetyDAL": "Not Applicable",
         "ataChapter": ATA21, "requirementOwner": "r.achebe",
         "subsystemLabel": "Pressurisation protection", "ataSubject": "21-30",
         "derivedRequirement": True,
         "verificationStatus": "Verified",
         "verificationEvidenceRef": "LSS-CERT-QUAL-005",
         "complianceItemRef": "LSS-CERT-COMP-003",
         "safetyAssessmentRef": "LSS-CERT-SAFE-001",
         "certificationCredit": True},
        notes="Derived requirement under ARP4754A: no parent requirement, so it is fed "
              "back into the safety assessment rather than traced upward. This is the "
              "object to open when asked how derived requirements are controlled."),

    req("SubsystemRequirement", "LSS-REQ-SUB-0003",
        "The audio integrating subsystem shall allow either crew station to select "
        "either transceiver",
        "The audio control panel shall allow each crew station independently to select "
        "transmit and receive on either VHF transceiver or the satellite terminal, and "
        "shall fail to a direct-connect mode on loss of panel power.",
        R_VERIFIED,
        {"requirementType": "Functional", "priority": "High",
         "rationale": "The fail-to-direct-connect behaviour is what keeps the two "
                      "independent transceivers independent when the panel between them "
                      "fails.",
         "source": "LSS-REQ-SYS-0003",
         "acceptanceCriteria": "Bench and aircraft test of every selection combination, "
                               "plus a panel power removal test.",
         "verificationMethod": "Test", "safetyDAL": "DAL-D",
         "ataChapter": ATA23, "requirementOwner": "d.okonjo",
         "subsystemLabel": "Audio integrating", "ataSubject": "23-50",
         "interfaceDocumentRef": "LSS-ICD-002",
         "verificationStatus": "Verified",
         "verificationEvidenceRef": "LSS-CERT-COMP-008",
         "complianceItemRef": "LSS-CERT-COMP-008"},
        parent="LSS-REQ-SYS-0003"),

    req("SubsystemRequirement", "LSS-REQ-SUB-0004",
        "Seat installation load paths shall be fail safe to the floor structure",
        "The seat track fittings and their attachment to the floor beams shall provide "
        "multiple load paths such that failure of any single fitting does not release the "
        "seat under the emergency landing condition.",
        R_IMPL,
        {"requirementType": "Design", "priority": "Critical",
         "rationale": "Allocated from the 16g requirement. Fail safety at the fitting is "
                      "cheaper than qualifying every fitting as a safe-life part.",
         "source": "LSS-REQ-SYS-0004",
         "acceptanceCriteria": "Static test to ultimate load with one fitting removed, "
                               "plus damage tolerance analysis.",
         "verificationMethod": "Test", "safetyDAL": "Not Applicable",
         "ataChapter": ATA25, "requirementOwner": "p.lindqvist",
         "subsystemLabel": "Seat attachment", "ataSubject": "25-10",
         "verificationStatus": "In verification",
         "complianceItemRef": "LSS-CERT-COMP-014"},
        parent="LSS-REQ-SYS-0004"),

    req("SubsystemRequirement", "LSS-REQ-SUB-0005",
        "Large-area cabin lining panels shall meet the heat release and smoke density "
        "criteria",
        "Cabin lining panels whose exposed surface area exceeds the threshold of the "
        "certification basis shall meet a peak heat release of not more than 65 kW per "
        "square metre, a total heat release of not more than 65 kW-minutes per square "
        "metre, and a specific optical smoke density of not more than 200.",
        R_IMPL,
        {"requirementType": "Safety", "priority": "Critical",
         "rationale": "Allocated from the interior materials requirement. The 65/65 and "
                      "Ds 200 numbers are written into the requirement so a supplier "
                      "cannot read them out of a reference and get them wrong.",
         "source": "LSS-REQ-SYS-0005",
         "acceptanceCriteria": "Appendix F Part IV and Part V laboratory tests on "
                               "production-representative panels.",
         "verificationMethod": "Test", "safetyDAL": "Not Applicable",
         "ataChapter": ATA25, "requirementOwner": "g.rossi",
         "subsystemLabel": "Cabin lining", "ataSubject": "25-20",
         "verificationStatus": "In verification",
         "verificationEvidenceRef": "LSS-CERT-QUAL-008",
         "complianceItemRef": "LSS-CERT-COMP-017"},
        parent="LSS-REQ-SYS-0005"),

    # ── Component level ─────────────────────────────────────────────────────
    req("ComponentRequirement", "LSS-REQ-CMP-0001",
        "Cabin pressure controller - dual channel, ETSO authorised, DAL B",
        "The cabin pressure controller shall be a dual channel digital unit holding an "
        "ETSO authorisation, developed to design assurance level B, qualified to DO-160G "
        "for the categories of the installation, and shall provide automatic changeover "
        "and a manual crew mode.",
        R_VERIFIED,
        {"requirementType": "Interface", "priority": "Critical",
         "rationale": "This requirement is the procurement specification for the "
                      "controller. It is written at component level so it can be flowed "
                      "down to the supplier verbatim.",
         "source": "LSS-REQ-SUB-0001",
         "acceptanceCriteria": "ETSO authorisation on file, DO-160G qualification report "
                               "accepted, and bench test of changeover and manual mode.",
         "verificationMethod": "Test", "safetyDAL": "DAL-B",
         "ataChapter": ATA21, "requirementOwner": "r.achebe",
         "componentLabel": "Cabin pressure controller",
         "targetPartNumber": "LSS-V-00004",
         "do160CategoryRequired": "A2, B, S(B), U, Z, B, A, X, X, F, Z, T, W(T), AB",
         "supplierFlowdown": True,
         "procurementSpecRef": "LSS-SPEC-PRO-001",
         "verificationStatus": "Verified",
         "verificationEvidenceRef": "LSS-CERT-QUAL-004",
         "complianceItemRef": "LSS-CERT-COMP-002"},
        parent="LSS-REQ-SUB-0001"),

    req("ComponentRequirement", "LSS-REQ-CMP-0002",
        "Cabin pressure safety valve - mechanical, no electrical power required",
        "The cabin pressure safety valve shall be wholly mechanical, shall crack at "
        "0.62 bar differential plus or minus 0.02 bar, and shall provide the flow "
        "capacity to limit differential pressure with the outflow valve failed closed and "
        "no electrical power available.",
        R_VERIFIED,
        {"requirementType": "Physical", "priority": "Critical",
         "rationale": "Flows down the derived requirement for an independent means of "
                      "overpressure protection. Wholly mechanical is the point: anything "
                      "electrical shares a failure mode with the control path.",
         "source": "LSS-REQ-SUB-0002",
         "acceptanceCriteria": "Cracking pressure and flow capacity test with no power "
                               "applied and the outflow valve failed closed.",
         "verificationMethod": "Test", "safetyDAL": "Not Applicable",
         "ataChapter": ATA21, "requirementOwner": "m.sandoval",
         "componentLabel": "Cabin pressure safety valve",
         "targetPartNumber": "LSS-V-00006",
         "supplierFlowdown": True,
         "procurementSpecRef": "LSS-SPEC-PRO-002",
         "verificationStatus": "Verified",
         "verificationEvidenceRef": "LSS-CERT-QUAL-005",
         "complianceItemRef": "LSS-CERT-COMP-003"},
        parent="LSS-REQ-SUB-0002"),

    req("ComponentRequirement", "LSS-REQ-CMP-0003",
        "VHF transceiver - 8.33 kHz, TSO authorised, DAL C",
        "Each VHF transceiver shall hold a TSO authorisation, support 8.33 kHz channel "
        "spacing, be developed to design assurance level C, and be qualified to DO-160G "
        "for the forward avionics bay environment.",
        R_VERIFIED,
        {"requirementType": "Interface", "priority": "Critical",
         "rationale": "Procurement specification for the transceiver.",
         "source": "LSS-REQ-SYS-0003",
         "acceptanceCriteria": "TSO authorisation on file and DO-160G qualification "
                               "report accepted.",
         "verificationMethod": "Inspection", "safetyDAL": "DAL-C",
         "ataChapter": ATA23, "requirementOwner": "d.okonjo",
         "componentLabel": "VHF transceiver",
         "targetPartNumber": "LSS-V-00010",
         "do160CategoryRequired": "A2, B, S(A), U, Z, B, A, X, X, F, Z, T, W(T), AB",
         "supplierFlowdown": True,
         "procurementSpecRef": "LSS-SPEC-PRO-003",
         "verificationStatus": "Verified",
         "complianceItemRef": "LSS-CERT-COMP-007"},
        parent="LSS-REQ-SYS-0003"),

    req("ComponentRequirement", "LSS-REQ-CMP-0004",
        "VHF antenna doubler - damage tolerant, pressure boundary",
        "The VHF antenna doubler shall restore the strength and damage tolerance of the "
        "pressurised shell at the antenna cut-out, with an inspection threshold and "
        "interval consistent with the maintenance programme.",
        R_IMPL,
        {"requirementType": "Physical", "priority": "Critical",
         "rationale": "A cut-out in the pressure shell is a fatigue and damage tolerance "
                      "problem, not an antenna mounting problem. Written as its own "
                      "requirement so the structural work is not lost inside an avionics "
                      "installation.",
         "source": "LSS-REQ-SYS-0003",
         "acceptanceCriteria": "Damage tolerance analysis with an inspection threshold, "
                               "supported by coupon fatigue test.",
         "verificationMethod": "Analysis", "safetyDAL": "Not Applicable",
         "ataChapter": ATA23, "requirementOwner": "p.lindqvist",
         "componentLabel": "VHF antenna doubler",
         "targetPartNumber": "LSS-23-0001",
         "supplierFlowdown": False,
         "verificationStatus": "In verification",
         "complianceItemRef": "LSS-CERT-COMP-010"},
        parent="LSS-REQ-SYS-0003"),

    req("ComponentRequirement", "LSS-REQ-CMP-0005",
        "Passenger seat - 16g dynamic, swivel interlock, fire blocked cushions",
        "The passenger club seat shall be substantiated to the 16g longitudinal dynamic "
        "condition in the forward-facing position, shall incorporate a swivel interlock "
        "that holds the forward-facing position whenever the seat belt sign is "
        "illuminated, and shall use fire blocked cushions meeting the Appendix F Part II "
        "oil burner criteria.",
        R_IMPL,
        {"requirementType": "Physical", "priority": "Critical",
         "rationale": "Combines the occupant protection requirement, the equivalent "
                      "safety finding on seat orientation and the cushion flammability "
                      "requirement into one specification the seat supplier can build to.",
         "source": "LSS-REQ-SUB-0004 and LSS-REQ-CERT-0005",
         "acceptanceCriteria": "Dynamic test report, interlock functional test, and "
                               "cushion oil burner test report.",
         "verificationMethod": "Test", "safetyDAL": "Not Applicable",
         "ataChapter": ATA25, "requirementOwner": "m.sandoval",
         "componentLabel": "Passenger club seat",
         "targetPartNumber": "LSS-F-00010",
         "supplierFlowdown": True,
         "procurementSpecRef": "LSS-SPEC-PRO-004",
         "verificationStatus": "In verification",
         "verificationEvidenceRef": "LSS-CERT-QUAL-002",
         "complianceItemRef": "LSS-CERT-COMP-015"},
        parent="LSS-REQ-SUB-0004"),

    req("ComponentRequirement", "LSS-REQ-CMP-0006",
        "Sidewall panel - 65/65 heat release and Ds 200 smoke density",
        "The forward sidewall panels shall meet a peak and total heat release of not more "
        "than 65 kW per square metre and 65 kW-minutes per square metre respectively, and "
        "a specific optical smoke density of not more than 200, as built with the "
        "production decorative finish.",
        R_IMPL,
        {"requirementType": "Physical", "priority": "Critical",
         "rationale": "As built with the production finish is the operative phrase: the "
                      "substrate passes easily and the decorative layer is what fails.",
         "source": "LSS-REQ-SUB-0005",
         "acceptanceCriteria": "Appendix F Part IV and Part V test reports on panels "
                               "carrying the production finish and adhesive.",
         "verificationMethod": "Test", "safetyDAL": "Not Applicable",
         "ataChapter": ATA25, "requirementOwner": "m.sandoval",
         "componentLabel": "Forward sidewall panel",
         "targetPartNumber": "LSS-F-00020",
         "supplierFlowdown": True,
         "procurementSpecRef": "LSS-SPEC-PRO-005",
         "verificationStatus": "In verification",
         "verificationEvidenceRef": "LSS-CERT-QUAL-008",
         "complianceItemRef": "LSS-CERT-COMP-017"},
        parent="LSS-REQ-SUB-0005"),

    req("ComponentRequirement", "LSS-REQ-CMP-0007",
        "ECS controller software - DO-178C level C with verification independence",
        "The environmental control system controller software shall be developed and "
        "verified to DO-178C level C, with verification independence for the objectives "
        "the standard requires it for at that level, and shall be field loadable under "
        "configuration control.",
        R_IMPL,
        {"requirementType": "Design", "priority": "High",
         "rationale": "Level C follows from the major failure effect of the temperature "
                      "control function. Field loadability is an operational convenience "
                      "that brings a configuration control obligation with it.",
         "source": "LSS-REQ-SYS-0001",
         "acceptanceCriteria": "Software accomplishment summary accepted, with the "
                               "configuration index identifying the released load.",
         "verificationMethod": "Analysis", "safetyDAL": "DAL-C",
         "ataChapter": ATA21, "requirementOwner": "r.achebe",
         "componentLabel": "ECS controller software",
         "targetPartNumber": "LSS-SW-0001",
         "supplierFlowdown": False,
         "verificationStatus": "In verification",
         "verificationEvidenceRef": "LSS-CERT-SWP-004",
         "complianceItemRef": "LSS-CERT-COMP-012"},
        parent="LSS-REQ-SYS-0001"),

    req("ComponentRequirement", "LSS-REQ-CMP-0008",
        "Bleed duct assembly - titanium, pressure boundary, penetrant inspected",
        "The bleed air supply duct assembly shall be titanium, shall contain bleed air at "
        "the maximum engine bleed temperature and pressure, and every weld shall be "
        "penetrant inspected to the process specification.",
        R_IMPL,
        {"requirementType": "Physical", "priority": "High",
         "rationale": "Hot, pressurised and inside the pack bay next to the firewall. "
                      "The penetrant requirement is called out at requirement level "
                      "because it is the one inspection a cost reduction tends to remove.",
         "source": "LSS-REQ-SYS-0001",
         "acceptanceCriteria": "Proof pressure test at temperature plus penetrant "
                               "inspection records for every weld.",
         "verificationMethod": "Test", "safetyDAL": "Not Applicable",
         "ataChapter": ATA21, "requirementOwner": "m.sandoval",
         "componentLabel": "Bleed air supply duct assembly",
         "targetPartNumber": "LSS-21-0001",
         "supplierFlowdown": False,
         "verificationStatus": "In verification",
         "complianceItemRef": "LSS-CERT-COMP-005"},
        parent="LSS-REQ-SYS-0001"),
]


# ─────────────────────────────────────────────────────────────────────────────
# Trace links
# ─────────────────────────────────────────────────────────────────────────────
# `implements` runs requirement -> part. `verified-by` runs requirement -> the document
# holding the evidence. `satisfied-by` runs requirement -> compliance item. `derived-from`
# records that a derived requirement came out of a safety assessment rather than from a
# parent. `traces-to` is the catch-all for an allocation the hierarchy does not express.
#
# A link whose target is pinned to a revision goes suspect when that target is revised,
# which is how a change impact assessment stops depending on anybody's memory. The links
# onto the two items that carry real revision history - LSS-21-0004 at revision B and
# LSS-F-00010 at revision B - are the ones to look at when demonstrating that.

def trace(source, target, link_type, note=None, pin=False):
    return {"source": source, "target": target, "type": link_type,
            "note": note, "pin": pin}


TRACE_LINKS = [
    # Aircraft -> certification basis
    trace("LSS-REQ-ACFT-0001", "LSS-REQ-CERT-0002", "traces-to",
          "Cabin altitude is how the occupant physical environment requirement is met."),
    trace("LSS-REQ-ACFT-0003", "LSS-REQ-CERT-0003", "traces-to",
          "Occupant protection traces to the emergency conditions paragraph."),
    trace("LSS-REQ-ACFT-0004", "LSS-REQ-CERT-0004", "traces-to",
          "Interior materials trace to the fire protection paragraph."),
    trace("LSS-REQ-OPS-0001", "LSS-REQ-SYS-0003", "traces-to",
          "Operator satellite requirement allocated to the communications system."),
    trace("LSS-REQ-OPS-0004", "LSS-REQ-SUB-0005", "traces-to",
          "The customer divider has to meet the same lining panel criteria."),

    # Derived requirement, fed back into the safety assessment
    trace("LSS-REQ-SUB-0002", "LSS-CERT-SAFE-001", "derived-from",
          "ARP4754A derived requirement: raised by the preliminary system safety "
          "assessment, not allocated from a parent requirement."),

    # Requirement -> implementing item
    trace("LSS-REQ-SYS-0001", "LSS-21-INST-001", "implements"),
    trace("LSS-REQ-SYS-0002", "LSS-V-00004", "implements"),
    trace("LSS-REQ-SUB-0001", "LSS-V-00004", "implements"),
    trace("LSS-REQ-SUB-0002", "LSS-V-00006", "implements",
          "The independent mechanical safety valve."),
    trace("LSS-REQ-CMP-0001", "LSS-V-00004", "implements"),
    trace("LSS-REQ-CMP-0002", "LSS-V-00006", "implements"),
    trace("LSS-REQ-CMP-0008", "LSS-21-0001", "implements"),
    trace("LSS-REQ-CMP-0008", "LSS-21-0004", "implements", pin=True,
          note="Pinned to the coupling revision the proof pressure test was run on. "
               "Revision B changed the clamp band thickness, so this link is suspect "
               "until the test credit is reassessed."),
    trace("LSS-REQ-CMP-0007", "LSS-SW-0001", "implements", pin=True,
          note="Pinned: the software level C substantiation is against a specific "
               "configuration index."),
    trace("LSS-REQ-SYS-0003", "LSS-23-INST-001", "implements"),
    trace("LSS-REQ-SUB-0003", "LSS-E-00010", "implements"),
    trace("LSS-REQ-CMP-0003", "LSS-V-00010", "implements"),
    trace("LSS-REQ-CMP-0004", "LSS-23-0001", "implements"),
    trace("LSS-REQ-SYS-0004", "LSS-25-INST-001", "implements"),
    trace("LSS-REQ-SUB-0004", "LSS-25-0001", "implements"),
    trace("LSS-REQ-SUB-0004", "LSS-25-0003", "implements"),
    trace("LSS-REQ-CMP-0005", "LSS-F-00010", "implements", pin=True,
          note="Pinned to the seat revision the dynamic test was run on. Revision B "
               "added the swivel interlock, so the link is suspect until the delta "
               "assessment confirms the test credit still stands."),
    trace("LSS-REQ-CMP-0006", "LSS-F-00020", "implements"),
    trace("LSS-REQ-CMP-0006", "LSS-F-00021", "implements"),
    trace("LSS-REQ-SUB-0005", "LSS-F-00030", "implements"),
    trace("LSS-REQ-SYS-0005", "LSS-F-00100", "implements"),
    trace("LSS-REQ-CERT-0005", "LSS-F-00010", "implements",
          "The swivel interlock in revision B exists because of this equivalent safety "
          "finding."),

    # Requirement -> verification evidence
    trace("LSS-REQ-ACFT-0001", "LSS-CERT-COMP-001", "verified-by"),
    trace("LSS-REQ-SYS-0001", "LSS-CERT-COMP-001", "verified-by"),
    trace("LSS-REQ-SYS-0002", "LSS-CERT-SAFE-002", "verified-by"),
    trace("LSS-REQ-SUB-0002", "LSS-CERT-QUAL-005", "verified-by"),
    trace("LSS-REQ-CMP-0002", "LSS-CERT-QUAL-005", "verified-by"),
    trace("LSS-REQ-CMP-0001", "LSS-CERT-QUAL-004", "verified-by"),
    trace("LSS-REQ-ACFT-0002", "LSS-CERT-COMP-007", "verified-by"),
    trace("LSS-REQ-SYS-0003", "LSS-CERT-COMP-007", "verified-by"),
    trace("LSS-REQ-SUB-0003", "LSS-CERT-COMP-008", "verified-by"),
    trace("LSS-REQ-CMP-0004", "LSS-CERT-COMP-010", "verified-by"),
    trace("LSS-REQ-SYS-0004", "LSS-CERT-QUAL-001", "verified-by"),
    trace("LSS-REQ-CMP-0005", "LSS-CERT-QUAL-002", "verified-by"),
    trace("LSS-REQ-SUB-0005", "LSS-CERT-QUAL-008", "verified-by"),
    trace("LSS-REQ-CMP-0006", "LSS-CERT-QUAL-008", "verified-by"),
    trace("LSS-REQ-SYS-0005", "LSS-CERT-QUAL-009", "verified-by"),
    trace("LSS-REQ-CMP-0007", "LSS-CERT-SWP-004", "verified-by"),
    trace("LSS-REQ-ACFT-0003", "LSS-CERT-COMP-014", "verified-by"),
    trace("LSS-REQ-ACFT-0004", "LSS-CERT-COMP-016", "verified-by"),

    # Requirement -> compliance item
    trace("LSS-REQ-CERT-0001", "LSS-CERT-COMP-002", "satisfied-by"),
    trace("LSS-REQ-CERT-0002", "LSS-CERT-COMP-001", "satisfied-by"),
    trace("LSS-REQ-CERT-0003", "LSS-CERT-COMP-014", "satisfied-by"),
    trace("LSS-REQ-CERT-0004", "LSS-CERT-COMP-016", "satisfied-by"),
    trace("LSS-REQ-CERT-0005", "LSS-CERT-COMP-015", "satisfied-by"),
    trace("LSS-REQ-SUB-0002", "LSS-CERT-COMP-003", "satisfied-by"),

    # A conflict worth showing: the operator divider and the weight requirement
    trace("LSS-REQ-OPS-0004", "LSS-REQ-ACFT-0003", "conflicts-with",
          "The forward divider reduces the clear path to the forward occupant places. "
          "Resolution is tracked on certification review item CRI-25-004."),
]


# ─────────────────────────────────────────────────────────────────────────────
# Baseline
# ─────────────────────────────────────────────────────────────────────────────
# One baseline, taken at the point the certification programme plan was issued. A baseline
# is what makes "what changed since we agreed the requirements?" answerable, and the compare
# view is the fastest way to show auditability to a certification audience.

BASELINES = [
    {
        "name": "NX-200 requirements baseline at certification plan issue 3",
        "scope": None,
        "notes": "Taken on issue of certification programme plan LSS-CERT-PLAN-001 "
                 "revision C, 2026-05-14. Everything agreed with the authority at the "
                 "level-of-involvement meeting is in this baseline, so a later compare "
                 "shows exactly what has moved since.",
    },
]
