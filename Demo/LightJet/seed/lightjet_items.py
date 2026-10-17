"""NX-200 items for ATA 23 Communications and ATA 25 Equipment and Furnishings.

ATA 23 is a light-jet communications fit: dual VHF, a satellite terminal, an audio
integrating panel with its own DO-178C software and DO-254 programmable hardware, a cockpit
voice recorder, the antennas and their structural doublers, static dischargers, and the two
harnesses that join them. Subchapter numbering follows iSpec 2200, so speech communications
is 23-10, satellite 23-15, audio integrating 23-50, static discharging 23-60 and audio and
video monitoring 23-70.

ATA 25 is the cabin: crew and passenger seating substantiated to the 16g dynamic condition,
sidewalls and ceiling panels substantiated against the Appendix F heat-release and smoke
criteria, seat cushions against the Part II oil-burner test, carpets and soft goods against
the Part I vertical burn, a galley and lavatory monument, emergency equipment stowage and
the seat track fittings that carry it all into the floor structure.

The flammability basis on each item is the real differentiator in this chapter, and it is
the thing a certification engineer will look for first in a demo.
"""

from lightjet_data import (
    ATA23, ATA25, F23, F25, PROGRAMME, ROOT_FOLDER, S_DESIGN, S_REL, S_SIGN, S_SUPER,
    S_WORK, SUP_ACTIVE, T, common, item,
)

APPF_I_12 = "Appendix F Part I - 12 second vertical"
APPF_I_60 = "Appendix F Part I - 60 second vertical"
APPF_II = "Appendix F Part II - seat cushion oil burner"
APPF_IV = "Appendix F Part IV - heat release (OSU 65/65)"
APPF_V = "Appendix F Part V - smoke density (Ds 200)"
DYN_23 = "CS 23.562 - 16g dynamic"
TSO_SEAT = "TSO-C127b seat"


def _vendor(pn, desc, ata, sub, folder, supplier, spn, cage, mass, extra=None,
            status=S_REL, history=None, notes=None, ata_label=None):
    attrs = {
        "programmeCode": PROGRAMME, "ataChapter": ata_label or ata, "ataSubject": sub,
        "designResponsibleOrg": "Supplier design authority",
        "engineeringOwner": "r.achebe", "itemMaturity": "Certified",
        "exportJurisdiction": "None", "exportClassification": "Not controlled",
        "supplierName": supplier, "supplierPartNumber": spn,
        "supplierCageCode": cage,
        "approvalBasis": "Approved as part of type design",
        "sourceApprovalStatus": "Approved",
        "obsolescenceStatus": "Active",
        "counterfeitRiskLevel": "Low - franchised distributor only",
        "reachSvhcStatus": "No SVHC above threshold",
        "rohsStatus": "Exempt - aerospace",
        "conflictMineralsStatus": "CMRT received",
        "massKg": mass, "massStatus": "Weighed",
        "airworthinessClassification": "Non-Essential",
        "typeDesignData": True, "buyMakeFlag": "Buy",
    }
    attrs.update(extra or {})
    return item("VendorPart", pn, desc, status, attrs, folder=folder,
                history=history or [("A", S_REL)], notes=notes)


# ─────────────────────────────────────────────────────────────────────────────
# ATA 23 - Communications
# ─────────────────────────────────────────────────────────────────────────────

ITEMS_23 = [
    item("Installation", "LSS-23-INST-001",
         "Communications system installation, NX-200",
         S_REL,
         common("23-00", ATA23, "r.achebe", "Certified",
                airworthinessClassification="Essential",
                failureEffectClassification="Major",
                certificationBasis="CS-23 Amdt 5 + ASTM F44 MoC",
                designAssuranceLevel="C",
                massKg=31.8, massStatus="Weighed",
                cgStationMm=2240, cgButtlineMm=0, cgWaterlineMm=1460,
                doaApprovalReference="EASA.21J.0742",
                complianceItemRefs="LSS-CERT-COMP-007, LSS-CERT-COMP-008",
                installationZone="Zone 220 - forward avionics bay and flight compartment",
                systemInstalled="VHF, satellite and intercom communications",
                torqueSpecificationRef="LSS-SPEC-PRC-004",
                riggingProcedureRef="LSS-SPEC-PRC-012",
                installationManHours=22,
                drawingNumber="LSS-DWG-23-0001",
                cadModelReference="NX200-COM-INST-ASM"),
         folder=f"{F23}/23-00 Communications - General", history=[("A", S_REL)]),

    item("ElectricalPart", "LSS-E-00010",
         "Audio control panel, three-place, dual transceiver",
         S_REL,
         common("23-50", ATA23, "d.okonjo", "Certified",
                electricalFunction="Audio / radio equipment",
                nominalVoltage=28, currentRating=1.2, powerConsumption=18,
                do160Revision="DO-160G",
                do160Categories="A2, B, S(A), U, Z, B, A, X, X, F, Z, T, W(T), AB",
                hirfCategory="Category B",
                lightningZone="Interior - induced only",
                bondingRequirement="Class R bond, 2.5 milliohm maximum",
                loadableSoftwareRef="LSS-SW-0002",
                mtbfHours=31000, massKg=0.94, massStatus="Weighed",
                airworthinessClassification="Essential",
                failureEffectClassification="Major",
                designAssuranceLevel="D",
                certificationBasis="CS-23 Amdt 5 + ASTM F44 MoC",
                drawingNumber="LSS-DWG-23-0002",
                serialisedItem=True,
                complianceItemRefs="LSS-CERT-COMP-008"),
         folder=f"{F23}/23-50 Audio Integrating", history=[("A", S_REL)]),

    item("SoftwareItem", "LSS-SW-0002", "Audio control panel software", S_REL,
         {"programmeCode": PROGRAMME, "ataChapter": ATA23, "ataSubject": "23-50",
          "designResponsibleOrg": "LSS Design Engineering",
          "engineeringOwner": "d.okonjo", "itemMaturity": "Certified",
          "exportJurisdiction": "EAR", "exportClassification": "EAR99",
          "softwarePartNumber": "LSS-SW-0002-01", "softwareVersion": "1.4.2",
          "do178cLevel": "D", "designAssuranceLevel": "D",
          "psacReference": "LSS-CERT-SWP-002",
          "sasReference": "LSS-CERT-SWP-006",
          "objectCodeVerification": False, "verificationIndependence": False,
          "fieldLoadable": False, "partitioningRequired": False,
          "targetProcessor": "ARM Cortex-M7", "sourceLinesOfCode": 11400,
          "airworthinessClassification": "Essential",
          "failureEffectClassification": "Major",
          "certificationBasis": "CS-23 Amdt 5 + ASTM F44 MoC",
          "typeDesignData": True},
         folder=f"{ROOT_FOLDER}/Certification/Software and Electronic Hardware",
         history=[("A", S_REL)]),

    item("AehItem", "LSS-HW-0001",
         "Audio matrix programmable logic device, audio control panel", S_REL,
         {"programmeCode": PROGRAMME, "ataChapter": ATA23, "ataSubject": "23-50",
          "designResponsibleOrg": "LSS Design Engineering",
          "engineeringOwner": "d.okonjo", "itemMaturity": "Certified",
          "exportJurisdiction": "EAR", "exportClassification": "EAR99",
          "hardwarePartNumber": "LSS-HW-0001-01", "hardwareVersion": "B",
          "do254Level": "D", "complexityClassification": "Simple",
          "deviceType": "CPLD", "deviceFamily": "Altera MAX 10",
          "phacReference": "LSS-CERT-SWP-003",
          "hasReference": "LSS-CERT-SWP-007",
          "hdlLanguage": "VHDL", "elaborationToolsQualified": False,
          "airworthinessClassification": "Essential",
          "designAssuranceLevel": "D",
          "certificationBasis": "CS-23 Amdt 5 + ASTM F44 MoC",
          "typeDesignData": True},
         folder=f"{ROOT_FOLDER}/Certification/Software and Electronic Hardware",
         history=[("A", S_REL)],
         notes="Classified simple under DO-254, so substantiation is by test coverage of "
               "all input combinations rather than the full objective set."),

    item("ElectricalPart", "LSS-E-00011", "Antenna, VHF communications, blade", S_REL,
         common("23-10", ATA23, "d.okonjo", "Certified",
                electricalFunction="Antenna",
                do160Revision="DO-160G",
                do160Categories="A2, C, S(C), U, Z, B, D, X, X, F, Z, T, W(T), AB",
                hirfCategory="Category A",
                lightningZone="Zone 1A",
                bondingRequirement="Direct metal-to-metal bond through doubler, "
                                   "2.5 milliohm maximum",
                massKg=0.42, massStatus="Weighed",
                airworthinessClassification="Essential",
                drawingNumber="LSS-DWG-23-0003",
                complianceItemRefs="LSS-CERT-COMP-009"),
         folder=f"{F23}/23-10 Speech Communications", history=[("A", S_REL)],
         notes="External, so it sits in lightning Zone 1A and the direct-effects "
               "substantiation in LSS-CERT-QUAL-004 applies."),

    item("AircraftPart", "LSS-23-0001",
         "Antenna doubler, VHF communications, upper fuselage", S_REL,
         common("23-10", ATA23, "p.lindqvist", "Certified",
                partCategory="Sheet metal",
                primaryMaterial="Aluminium 2024-T3",
                materialForm="Sheet", materialSpecification="AMS 4037",
                massKg=0.28, massStatus="Weighed",
                ndtRequirement="Eddy current",
                fatigueCritical=True, pressureBoundary=True,
                damageToleranceCategory="Damage tolerant",
                surfaceTreatment="Alodine 1200 per MIL-DTL-5541 Class 1A",
                processSpecificationRefs="LSS-PS-0004",
                drawingNumber="LSS-DWG-23-0004",
                airworthinessClassification="Flight Safety Critical",
                failureEffectClassification="Hazardous / Severe-Major"),
         folder=f"{F23}/23-10 Speech Communications", history=[("A", S_REL)],
         notes="Fatigue critical and part of the pressure boundary: it is a cut-out in "
               "the pressurised shell. Damage tolerance substantiation is in "
               "LSS-CERT-COMP-010."),

    item("AircraftPart", "LSS-23-0002", "Avionics tray, communications equipment", S_REL,
         common("23-00", ATA23, "m.sandoval", "Certified",
                partCategory="Sheet metal",
                primaryMaterial="Aluminium 6061-T6",
                materialForm="Sheet", materialSpecification="AMS 4027",
                massKg=1.12, massStatus="Weighed", ndtRequirement="None",
                surfaceTreatment="Alodine 1200 per MIL-DTL-5541 Class 1A",
                drawingNumber="LSS-DWG-23-0005",
                airworthinessClassification="Non-Essential",
                fireProtectionRequirement="None"),
         folder=f"{F23}/23-00 Communications - General", history=[("A", S_REL)]),

    item("ElectricalPart", "LSS-E-00012", "Static discharger set, wing and empennage",
         S_REL,
         common("23-60", ATA23, "d.okonjo", "Certified",
                electricalFunction="Protection device",
                do160Revision="DO-160G",
                do160Categories="A2, C, S(C), U, Z, B, D, X, X, F, Z, T, X, AB",
                hirfCategory="Not applicable",
                lightningZone="Zone 1B",
                bondingRequirement="Bonded to structure, 0.1 ohm maximum per discharger",
                massKg=0.31, massStatus="Weighed",
                airworthinessClassification="Non-Essential",
                drawingNumber="LSS-DWG-23-0006"),
         folder=f"{F23}/23-60 Static Discharging", history=[("A", S_REL)]),

    item("Harness", "LSS-W23-001", "Communications coaxial harness", S_REL,
         common("23-10", ATA23, "d.okonjo", "Certified",
                wireSpecification="M17/128-RG400 double shielded coaxial",
                gaugeRange="RG400 equivalent",
                connectorSpecifications="TNC and BNC, MIL-PRF-39012",
                shieldingClass="Double braid",
                routeZone="Zone 220 to Zone 310, overhead raceway",
                separationCategory="Category 2 - redundant systems separated",
                harnessLengthMm=6140, circuitCount=6,
                ewisZonalInspectionRef="LSS-SPEC-TST-009",
                massKg=2.18, massStatus="Weighed",
                drawingNumber="LSS-DWG-23-0007",
                airworthinessClassification="Essential"),
         folder=f"{F23}/23-10 Speech Communications", history=[("A", S_REL)]),

    item("Harness", "LSS-W23-002", "Flight compartment audio harness", S_REL,
         common("23-50", ATA23, "d.okonjo", "Certified",
                wireSpecification="BMS 13-48 Type 5 Class 1",
                gaugeRange="24 to 20 AWG",
                connectorSpecifications="MIL-DTL-38999 Series III size 11 and 13",
                shieldingClass="Twisted shielded pair",
                routeZone="Zone 220, instrument panel to overhead",
                separationCategory="Category 3 - no separation requirement",
                harnessLengthMm=3280, circuitCount=44,
                ewisZonalInspectionRef="LSS-SPEC-TST-009",
                massKg=1.76, massStatus="Weighed",
                drawingNumber="LSS-DWG-23-0008",
                airworthinessClassification="Essential"),
         folder=f"{F23}/23-50 Audio Integrating", history=[("A", S_REL)]),

    _vendor("LSS-V-00010", "VHF communications transceiver, 8.33 kHz", ATA23, "23-10",
            f"{F23}/23-10 Speech Communications", "Thorne Avionics",
            "TAV-VHF-2200", "L7730", 2.34,
            extra={"approvalBasis": "FAA TSO authorisation",
                   "tsoEtsoReference": "TSO-C169a",
                   "sourceApprovalStatus": "Approved - single source",
                   "airworthinessClassification": "Essential",
                   "failureEffectClassification": "Major",
                   "designAssuranceLevel": "C",
                   "serialisedItem": True, "leadTimeWeeks": 24,
                   "supplierUnitPrice": 11800, "costCurrency": "USD",
                   "exportJurisdiction": "EAR", "exportClassification": "EAR99"}),

    _vendor("LSS-V-00011", "Satellite communications terminal, Iridium Certus 100",
            ATA23, "23-15", f"{F23}/23-15 Satellite Communications",
            "Thorne Avionics", "TAV-SAT-4410", "L7730", 3.86,
            extra={"approvalBasis": "EASA ETSO authorisation",
                   "tsoEtsoReference": "ETSO-2C517",
                   "sourceApprovalStatus": "Approved - single source",
                   "airworthinessClassification": "Non-Essential",
                   "serialisedItem": True, "leadTimeWeeks": 32,
                   "supplierUnitPrice": 24600, "costCurrency": "USD",
                   "exportJurisdiction": "EAR",
                   "exportClassification": "ECCN 7A994",
                   "obsolescenceStatus": "Active"},
            notes="Export classified ECCN 7A994. Drawings and interface data may not be "
                  "released to a vendor representative without a current export briefing "
                  "on file."),

    _vendor("LSS-V-00012", "Cockpit voice recorder, 25 hour solid state",
            ATA23, "23-70", f"{F23}/23-70 Audio and Video Monitoring",
            "Thorne Avionics", "TAV-CVR-9120", "L7730", 4.22,
            extra={"approvalBasis": "FAA TSO authorisation",
                   "tsoEtsoReference": "TSO-C123c",
                   "sourceApprovalStatus": "Approved - single source",
                   "airworthinessClassification": "Essential",
                   "failureEffectClassification": "Minor",
                   "serialisedItem": True, "leadTimeWeeks": 28,
                   "supplierUnitPrice": 38200, "costCurrency": "USD",
                   "exportJurisdiction": "EAR", "exportClassification": "EAR99"},
            notes="Crash survivable. The underwater locating beacon fitted to it is a "
                  "life limited item with a six year battery life."),

    _vendor("LSS-V-00013", "Underwater locating beacon, CVR mounted",
            ATA23, "23-70", f"{F23}/23-70 Audio and Video Monitoring",
            "Thorne Avionics", "TAV-ULB-0410", "L7730", 0.19,
            extra={"approvalBasis": "FAA TSO authorisation",
                   "tsoEtsoReference": "TSO-C121c",
                   "sourceApprovalStatus": "Approved",
                   "airworthinessClassification": "Essential",
                   "lifeLimitedPart": True, "lifeLimitHours": 0,
                   "serialisedItem": True, "leadTimeWeeks": 12,
                   "exportJurisdiction": "None",
                   "exportClassification": "Not controlled"},
            notes="Battery life limited to six calendar years, which is a calendar limit "
                  "rather than a flight hour limit. Listed in the airworthiness "
                  "limitations section and tracked per serial number."),

    _vendor("LSS-V-00014", "Antenna, satellite communications, low gain",
            ATA23, "23-15", f"{F23}/23-15 Satellite Communications",
            "Thorne Avionics", "TAV-SAT-ANT-210", "L7730", 1.08,
            extra={"approvalBasis": "EASA ETSO authorisation",
                   "tsoEtsoReference": "ETSO-2C517",
                   "sourceApprovalStatus": "Approved",
                   "airworthinessClassification": "Non-Essential",
                   "exportJurisdiction": "EAR",
                   "exportClassification": "ECCN 7A994"}),

    _vendor("LSS-V-00015", "Headset jack panel assembly, crew station",
            ATA23, "23-50", f"{F23}/23-50 Audio Integrating",
            "Thorne Avionics", "TAV-JCK-1120", "L7730", 0.22,
            extra={"sourceApprovalStatus": "Approved",
                   "airworthinessClassification": "Non-Essential",
                   "obsolescenceStatus": "Last time buy announced",
                   "lastTimeBuyDate": "2027-03-31",
                   "counterfeitRiskLevel": "Medium - broker used",
                   "leadTimeWeeks": 16},
            notes="Last time buy announced for 31 March 2027. Obsolescence case "
                  "LSS-ECR-00003 is open to qualify a replacement."),

    item("Harness", "LSS-W23-003",
         "Satellite communications RF and data harness", S_SIGN,
         common("23-15", ATA23, "d.okonjo", "Detail design",
                wireSpecification="M17/113-RG316 and BMS 13-48 Type 5",
                gaugeRange="24 to 22 AWG",
                connectorSpecifications="TNC, MIL-DTL-38999 Series III size 11",
                shieldingClass="Overall shield",
                routeZone="Zone 310, aft pressure bulkhead to avionics bay",
                separationCategory="Category 3 - no separation requirement",
                harnessLengthMm=5410, circuitCount=14,
                massKg=1.94, massStatus="Calculated",
                drawingNumber="LSS-DWG-23-0009",
                airworthinessClassification="Non-Essential",
                exportJurisdiction="EAR", exportClassification="ECCN 7A994"),
         folder=f"{F23}/23-15 Satellite Communications", history=[("A", S_SIGN)],
         notes="Awaiting airworthinesss sign-off. This harness is the demo's example of "
               "a card sitting in the sign-off lane of the type design release board."),
]


# ─────────────────────────────────────────────────────────────────────────────
# ATA 25 - Equipment and Furnishings
# ─────────────────────────────────────────────────────────────────────────────

def _interior(pn, desc, sub, folder, category, zone, mass, flam, extra=None,
              status=S_REL, history=None, notes=None, revision="A", owner="m.sandoval"):
    attrs = common(sub, ATA25, owner, "Certified",
                   furnishingCategory=category, interiorZone=zone,
                   flammabilityTest=flam,
                   massKg=mass, massStatus="Weighed",
                   airworthinessClassification="Non-Essential",
                   certificationBasis="CS-23 Amdt 5 + ASTM F44 MoC",
                   fireProtectionRequirement=(
                       "Appendix F Part II - seat cushion oil burner"
                       if flam == APPF_II else
                       "Appendix F Part IV - heat release"
                       if flam == APPF_IV else
                       "CS 23.853 / Appendix F Part I - vertical burn"),
                   occupantSafetyBasis="Not applicable",
                   customerConfigurable=False, completionCentreFit=False)
    attrs.update(extra or {})
    return item("InteriorPart", pn, desc, status, attrs, folder=folder,
                revision=revision, history=history or [("A", S_REL)], notes=notes)


ITEMS_25 = [
    item("Installation", "LSS-25-INST-001",
         "Cabin interior installation, seven place, standard configuration",
         S_REL,
         common("25-00", ATA25, "m.sandoval", "Certified",
                airworthinessClassification="Non-Essential",
                certificationBasis="CS-23 Amdt 5 + ASTM F44 MoC",
                massKg=214.6, massStatus="Weighed",
                cgStationMm=3180, cgButtlineMm=0, cgWaterlineMm=1240,
                doaApprovalReference="EASA.21J.0742",
                complianceItemRefs="LSS-CERT-COMP-014, LSS-CERT-COMP-016, "
                                   "LSS-CERT-COMP-018",
                installationZone="Zone 200 and 300 - pressurised cabin",
                systemInstalled="Seating, furnishings, emergency equipment",
                torqueSpecificationRef="LSS-SPEC-PRC-004",
                installationManHours=142,
                drawingNumber="LSS-DWG-25-0001",
                cadModelReference="NX200-INT-INST-ASM",
                fireProtectionRequirement=
                "Appendix F Part IV - heat release"),
         folder=f"{F25}/25-00 Equipment and Furnishings - General",
         history=[("A", S_REL)]),

    # ── Flight compartment, 25-10 ────────────────────────────────────────────
    item("InteriorPart", "LSS-F-00001",
         "Pilot seat assembly, 16g, fore/aft and recline adjustable",
         S_REL,
         common("25-10", ATA25, "m.sandoval", "Certified",
                furnishingCategory="Seat",
                interiorZone="Flight compartment",
                flammabilityTest=APPF_I_12,
                occupantSafetyBasis=DYN_23,
                dynamicTestReportRef="LSS-CERT-QUAL-001",
                flammabilityTestReportRef="LSS-CERT-QUAL-006",
                upholsteryMaterial="Wool/nylon blend, FR treated",
                colourTrimCode="TRM-GRA-01",
                massKg=18.4, massStatus="Weighed",
                airworthinessClassification="Essential",
                failureEffectClassification="Major",
                certificationBasis="CS-23 Amdt 5 + ASTM F44 MoC",
                fireProtectionRequirement=
                "Appendix F Part II - seat cushion oil burner",
                drawingNumber="LSS-DWG-25-0002",
                customerConfigurable=False,
                complianceItemRefs="LSS-CERT-COMP-014, LSS-CERT-COMP-015"),
         folder=f"{F25}/25-10 Flight Compartment", history=[("A", S_REL)],
         notes="Substantiated to the CS 23.562 16g dynamic condition. The dynamic test "
               "report LSS-CERT-QUAL-001 covers the critical seat position; the yawed "
               "test demonstrated restraint retention in the same run."),

    _interior("LSS-F-00002", "Seat cushion, pilot seat, bottom", "25-10",
              f"{F25}/25-10 Flight Compartment", "Seat cushion",
              "Flight compartment", 1.64, APPF_II,
              extra={"flammabilityTestReportRef": "LSS-CERT-QUAL-007",
                     "upholsteryMaterial": "Wool/nylon blend over FR foam with "
                                           "fire blocking layer",
                     "colourTrimCode": "TRM-GRA-01",
                     "drawingNumber": "LSS-DWG-25-0003",
                     "complianceItemRefs": "LSS-CERT-COMP-015"},
              notes="Seat cushions must pass the Appendix F Part II oil burner test as "
                    "well as the Part I vertical burn, which is why the fire blocking "
                    "layer is called out on the drawing and not left to the supplier."),

    _interior("LSS-F-00003", "Seat cushion, pilot seat, back", "25-10",
              f"{F25}/25-10 Flight Compartment", "Seat cushion",
              "Flight compartment", 1.18, APPF_II,
              extra={"flammabilityTestReportRef": "LSS-CERT-QUAL-007",
                     "upholsteryMaterial": "Wool/nylon blend over FR foam with "
                                           "fire blocking layer",
                     "colourTrimCode": "TRM-GRA-01",
                     "drawingNumber": "LSS-DWG-25-0003"}),

    item("AircraftPart", "LSS-25-0001",
         "Seat track fitting, flight compartment, machined", S_REL,
         common("25-10", ATA25, "p.lindqvist", "Certified",
                partCategory="Machined",
                primaryMaterial="Aluminium 7075-T7351",
                materialForm="Bar", materialSpecification="AMS 4124",
                massKg=0.22, massStatus="Weighed",
                ndtRequirement="Fluorescent penetrant",
                fatigueCritical=True,
                damageToleranceCategory="Fail safe - multiple load path",
                surfaceTreatment="Chromic acid anodise to MIL-A-8625 Type I",
                processSpecificationRefs="LSS-PS-0004",
                drawingNumber="LSS-DWG-25-0004",
                airworthinessClassification="Flight Safety Critical",
                failureEffectClassification="Hazardous / Severe-Major",
                complianceItemRefs="LSS-CERT-COMP-014"),
         folder=f"{F25}/25-10 Flight Compartment", history=[("A", S_REL)],
         notes="Carries the 16g seat reaction into the floor beam. Flight safety "
               "critical: the fitting is the load path the seat substantiation assumes."),

    # ── Passenger compartment, 25-20 ─────────────────────────────────────────
    item("InteriorPart", "LSS-F-00010",
         "Passenger seat assembly, club four, 16g, swivel and track",
         S_REL,
         common("25-20", ATA25, "m.sandoval", "Certified",
                furnishingCategory="Seat", interiorZone="Passenger compartment",
                flammabilityTest=APPF_I_12,
                occupantSafetyBasis=DYN_23,
                dynamicTestReportRef="LSS-CERT-QUAL-002",
                flammabilityTestReportRef="LSS-CERT-QUAL-006",
                upholsteryMaterial="Aniline leather, FR treated",
                colourTrimCode="TRM-TAN-04",
                massKg=22.8, massStatus="Weighed",
                airworthinessClassification="Essential",
                failureEffectClassification="Major",
                certificationBasis="CS-23 Amdt 5 + ASTM F44 MoC",
                fireProtectionRequirement=
                "Appendix F Part II - seat cushion oil burner",
                drawingNumber="LSS-DWG-25-0005",
                customerConfigurable=True, completionCentreFit=True,
                complianceItemRefs="LSS-CERT-COMP-014, LSS-CERT-COMP-015"),
         folder=f"{F25}/25-20 Passenger Compartment", revision="B",
         history=[("A", S_SUPER), ("B", S_REL)],
         notes="Revision B adds the swivel lock interlock required by the equivalent "
               "safety finding on seat orientation during taxi, take-off and landing. "
               "Implemented by LSS-ECO-00001."),

    _interior("LSS-F-00011", "Seat cushion set, passenger club seat", "25-20",
              f"{F25}/25-20 Passenger Compartment", "Seat cushion",
              "Passenger compartment", 3.42, APPF_II,
              extra={"flammabilityTestReportRef": "LSS-CERT-QUAL-007",
                     "upholsteryMaterial": "Aniline leather over FR foam with "
                                           "fire blocking layer",
                     "colourTrimCode": "TRM-TAN-04",
                     "drawingNumber": "LSS-DWG-25-0006",
                     "customerConfigurable": True}),

    _interior("LSS-F-00020", "Sidewall panel, LH forward", "25-20",
              f"{F25}/25-20 Passenger Compartment", "Sidewall panel",
              "Passenger compartment", 4.18, APPF_IV,
              extra={"flammabilityTestReportRef": "LSS-CERT-QUAL-008",
                     "upholsteryMaterial": "Suede-effect polyester over Nomex "
                                           "honeycomb sandwich",
                     "colourTrimCode": "TRM-TAN-04",
                     "drawingNumber": "LSS-DWG-25-0007",
                     "customerConfigurable": True, "completionCentreFit": True,
                     "complianceItemRefs": "LSS-CERT-COMP-016, LSS-CERT-COMP-017"},
              notes="Large surface area panel, so the Appendix F Part IV heat release "
                    "and Part V smoke density criteria both apply. The 65/65 heat "
                    "release result is in LSS-CERT-QUAL-008."),

    _interior("LSS-F-00021", "Sidewall panel, RH forward", "25-20",
              f"{F25}/25-20 Passenger Compartment", "Sidewall panel",
              "Passenger compartment", 4.18, APPF_IV,
              extra={"flammabilityTestReportRef": "LSS-CERT-QUAL-008",
                     "upholsteryMaterial": "Suede-effect polyester over Nomex "
                                           "honeycomb sandwich",
                     "colourTrimCode": "TRM-TAN-04",
                     "drawingNumber": "LSS-DWG-25-0007",
                     "customerConfigurable": True, "completionCentreFit": True}),

    _interior("LSS-F-00030", "Ceiling panel assembly, cabin", "25-20",
              f"{F25}/25-20 Passenger Compartment", "Ceiling panel",
              "Passenger compartment", 6.24, APPF_IV,
              extra={"flammabilityTestReportRef": "LSS-CERT-QUAL-008",
                     "upholsteryMaterial": "Nomex honeycomb sandwich with "
                                           "decorative laminate",
                     "colourTrimCode": "TRM-WHT-02",
                     "drawingNumber": "LSS-DWG-25-0008",
                     "complianceItemRefs": "LSS-CERT-COMP-016"}),

    _interior("LSS-F-00040", "Carpet set, cabin and vestibule", "25-20",
              f"{F25}/25-20 Passenger Compartment", "Carpet",
              "Passenger compartment", 8.92, APPF_I_12,
              extra={"flammabilityTestReportRef": "LSS-CERT-QUAL-009",
                     "upholsteryMaterial": "Wool pile with FR backing",
                     "colourTrimCode": "TRM-TAN-04",
                     "drawingNumber": "LSS-DWG-25-0009",
                     "customerConfigurable": True, "completionCentreFit": True}),

    _interior("LSS-F-00080", "Window shade assembly, cabin", "25-20",
              f"{F25}/25-20 Passenger Compartment", "Window shade",
              "Passenger compartment", 0.38, APPF_I_12,
              extra={"flammabilityTestReportRef": "LSS-CERT-QUAL-009",
                     "colourTrimCode": "TRM-TAN-04",
                     "drawingNumber": "LSS-DWG-25-0010",
                     "customerConfigurable": True}),

    item("AircraftPart", "LSS-25-0002",
         "Floor panel, cabin, composite sandwich", S_REL,
         common("25-20", ATA25, "p.lindqvist", "Certified",
                partCategory="Composite sandwich",
                primaryMaterial="Carbon/epoxy face sheets, Nomex core",
                materialForm="Prepreg", materialSpecification="LSS-SPEC-MAT-002",
                massKg=5.86, massStatus="Weighed",
                ndtRequirement="Ultrasonic",
                specialProcesses="Composite layup and cure (NADCAP Composites)",
                processSpecificationRefs="LSS-PS-0005",
                fatigueCritical=False,
                drawingNumber="LSS-DWG-25-0011",
                airworthinessClassification="Essential",
                fireProtectionRequirement=
                "CS 23.853 / Appendix F Part I - vertical burn",
                complianceItemRefs="LSS-CERT-COMP-016"),
         folder=f"{F25}/25-20 Passenger Compartment", history=[("A", S_REL)]),

    item("AircraftPart", "LSS-25-0003",
         "Seat track fitting, cabin, machined", S_REL,
         common("25-20", ATA25, "p.lindqvist", "Certified",
                partCategory="Machined",
                primaryMaterial="Aluminium 7075-T7351",
                materialForm="Bar", materialSpecification="AMS 4124",
                massKg=0.26, massStatus="Weighed",
                ndtRequirement="Fluorescent penetrant",
                fatigueCritical=True,
                damageToleranceCategory="Fail safe - multiple load path",
                surfaceTreatment="Chromic acid anodise to MIL-A-8625 Type I",
                processSpecificationRefs="LSS-PS-0004",
                drawingNumber="LSS-DWG-25-0012",
                airworthinessClassification="Flight Safety Critical",
                failureEffectClassification="Hazardous / Severe-Major",
                complianceItemRefs="LSS-CERT-COMP-014"),
         folder=f"{F25}/25-20 Passenger Compartment", history=[("A", S_REL)]),

    # ── Galley, lavatory, cargo, emergency, insulation ───────────────────────
    _interior("LSS-F-00050", "Galley monument, forward, refreshment centre", "25-30",
              f"{F25}/25-30 Galley", "Cabinet", "Galley", 24.6, APPF_IV,
              extra={"flammabilityTestReportRef": "LSS-CERT-QUAL-010",
                     "upholsteryMaterial": "Decorative laminate over Nomex sandwich",
                     "colourTrimCode": "TRM-WAL-07",
                     "drawingNumber": "LSS-DWG-25-0013",
                     "customerConfigurable": True, "completionCentreFit": True,
                     "complianceItemRefs": "LSS-CERT-COMP-018"},
              notes="Customer configurable and fitted at the completion centre. Three "
                    "approved variants exist; the mass and centre of gravity entry in "
                    "the weight and balance report depends on which is fitted."),

    _interior("LSS-F-00060", "Lavatory module, aft, with vanity", "25-40",
              f"{F25}/25-40 Lavatories", "Cabinet", "Lavatory", 31.2, APPF_IV,
              extra={"flammabilityTestReportRef": "LSS-CERT-QUAL-010",
                     "colourTrimCode": "TRM-WHT-02",
                     "drawingNumber": "LSS-DWG-25-0014",
                     "customerConfigurable": True, "completionCentreFit": True,
                     "complianceItemRefs": "LSS-CERT-COMP-018"}),

    _interior("LSS-F-00070", "Baggage restraint net, aft compartment", "25-50",
              f"{F25}/25-50 Cargo and Baggage Compartments", "Stowage",
              "Baggage compartment", 1.84, APPF_I_12,
              extra={"flammabilityTestReportRef": "LSS-CERT-QUAL-009",
                     "drawingNumber": "LSS-DWG-25-0015",
                     "complianceItemRefs": "LSS-CERT-COMP-019"},
              notes="Restrains baggage against the 9g forward emergency landing "
                    "condition. The net, its attachments and the compartment liner are "
                    "substantiated together."),

    _interior("LSS-F-00090", "Emergency equipment stowage, cabin", "25-60",
              f"{F25}/25-60 Emergency Equipment", "Stowage",
              "Passenger compartment", 2.12, APPF_I_12,
              extra={"flammabilityTestReportRef": "LSS-CERT-QUAL-009",
                     "drawingNumber": "LSS-DWG-25-0016",
                     "airworthinessClassification": "Essential",
                     "complianceItemRefs": "LSS-CERT-COMP-020"},
              notes="Holds the portable fire extinguisher, first aid kit and emergency "
                    "locator transmitter. Accessibility is part of the compliance "
                    "demonstration, so the installation drawing controls the location."),

    _interior("LSS-F-00100", "Thermal and acoustic insulation blanket set, cabin",
              "25-80", f"{F25}/25-80 Insulation", "Soft goods",
              "Passenger compartment", 11.4, APPF_I_12,
              extra={"flammabilityTestReportRef": "LSS-CERT-QUAL-011",
                     "drawingNumber": "LSS-DWG-25-0017",
                     "complianceItemRefs": "LSS-CERT-COMP-021"},
              notes="Flame propagation resistance of the blanket covering is the "
                    "governing requirement, not just the vertical burn of the batting."),

    # In-work interior item, so the demo has a live design in ATA 25 too.
    _interior("LSS-F-00110", "Divider and credenza, forward cabin, customer variant",
              "25-20", f"{F25}/25-20 Passenger Compartment", "Divider",
              "Cabinetry / monument", 16.8, APPF_IV,
              status=S_DESIGN, history=[("A", S_DESIGN)],
              extra={"colourTrimCode": "TRM-WAL-07",
                     "drawingNumber": "LSS-DWG-25-0018",
                     "customerConfigurable": True, "completionCentreFit": True,
                     "itemMaturity": "Detail design", "massStatus": "Calculated"},
              notes="Raised by operator requirement LSS-REQ-OPS-0004. Heat release and "
                    "smoke density testing is not yet complete, so it cannot progress "
                    "past design review."),

    _vendor("LSS-V-00020", "Seat belt and shoulder harness, four point",
            ATA25, "25-10", f"{F25}/25-10 Flight Compartment",
            "Caldera Seating", "CAL-RST-4410", "F2914", 1.42,
            extra={"approvalBasis": "FAA TSO authorisation",
                   "tsoEtsoReference": "TSO-C114",
                   "sourceApprovalStatus": "Approved",
                   "airworthinessClassification": "Essential",
                   "failureEffectClassification": "Major",
                   "serialisedItem": True, "leadTimeWeeks": 14,
                   "engineeringOwner": "m.sandoval"}),

    _vendor("LSS-V-00021", "Seat recline and swivel mechanism",
            ATA25, "25-20", f"{F25}/25-20 Passenger Compartment",
            "Caldera Seating", "CAL-MEC-2280", "F2914", 3.68,
            extra={"sourceApprovalStatus": "Approved",
                   "airworthinessClassification": "Essential",
                   "leadTimeWeeks": 20, "engineeringOwner": "m.sandoval"}),

    _vendor("LSS-V-00022", "Composite sandwich panel blank, Nomex core",
            ATA25, "25-20", f"{F25}/25-20 Passenger Compartment",
            "Volant Composites", "VOL-PNL-1140", "H5508", 2.96,
            extra={"sourceApprovalStatus": "Approved",
                   "airworthinessClassification": "Non-Essential",
                   "leadTimeWeeks": 12, "engineeringOwner": "m.sandoval",
                   "conflictMineralsStatus": "CMRT outstanding"}),

    _vendor("LSS-V-00023", "Flame retardant upholstery leather, aniline",
            ATA25, "25-20", f"{F25}/25-20 Passenger Compartment",
            "Pyrosafe Materials", "PYR-LTH-0820", "N6643", 0.62,
            extra={"sourceApprovalStatus": "Approved",
                   "airworthinessClassification": "Non-Essential",
                   "leadTimeWeeks": 8, "engineeringOwner": "m.sandoval",
                   "reachSvhcStatus": "SVHC declared"},
            notes="A SVHC is declared against the tanning process. Supply chain holds "
                  "the declaration; the substitution case is tracked on the board."),

    item("Consumable", "LSS-CM-0010",
         "Adhesive, film, 120 degrees C cure, structural", SUP_ACTIVE,
         {"programmeCode": PROGRAMME, "ataChapter": ATA25, "ataSubject": "25-20",
          "designResponsibleOrg": "Industry standard",
          "engineeringOwner": "t.brennan", "itemMaturity": "In production",
          "exportJurisdiction": "None", "exportClassification": "Not controlled",
          "consumableClass": "Adhesive - film", "specification": "LSS-SPEC-MAT-005",
          "manufacturer": "Pyrosafe Materials", "shelfLifeMonths": 12,
          "storageConditions": "Minus 18 degrees C, sealed; 30 days out-time maximum",
          "cureSchedule": "60 minutes at 120 degrees C, 0.28 MPa",
          "hazardClassification": "Not dangerous goods",
          "safetyDataSheetRef": "SDS-PYR-AF163",
          "batchTraceabilityRequired": True,
          "recordOwnerFunction": "Manufacturing", "controlledItem": True,
          "typeDesignData": False},
         folder=f"{ROOT_FOLDER}/Production/Consumable Materials"),

    item("Tooling", "LSS-TL-0010",
         "Bond fixture, cabin floor panel LSS-25-0002", SUP_ACTIVE,
         {"programmeCode": PROGRAMME, "ataChapter": ATA25, "ataSubject": "25-20",
          "designResponsibleOrg": "LSS Design Engineering",
          "engineeringOwner": "t.brennan", "itemMaturity": "In production",
          "exportJurisdiction": "None", "exportClassification": "Not controlled",
          "toolType": "Bond fixture", "toolClass": "Hard tool - production",
          "calibrationRequired": True, "calibrationInterval": 12,
          "calibrationDueDate": "2027-05-31",
          "calibrationCertificateRef": "CAL-2026-0502",
          "locationCode": "Composite shop, autoclave 2",
          "custodian": "t.brennan",
          "qualifiedForParts": "LSS-25-0002",
          "toolProvingRecordRef": "TPR-2026-0088",
          "recordOwnerFunction": "Manufacturing", "controlledItem": True,
          "typeDesignData": False},
         folder=f"{ROOT_FOLDER}/Production/Tooling and GSE"),
]
