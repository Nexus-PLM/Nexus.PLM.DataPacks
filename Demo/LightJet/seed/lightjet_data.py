"""The NX-200 demo content: items, structure, documents, requirements, changes, records.

Everything here is declarative. `seed_lightjet.py` walks it and creates it through the
Engine's REST API; `--dry-run` walks it without a server and checks it holds together -
every bill-of-materials child exists, every trace link has two real ends, every attribute
name is declared on the type it is being set on, and every part number matches the pattern
its type's numbering schema would mint.

Part numbers are explicit rather than left to the numbering service. A demo script has to be
able to say "open LSS-21-0014" and have it be there, and a reproducible dataset cannot
depend on what a site's counters happen to be sitting at. The numbers still follow the
schemas exactly, which the dry run checks.

The aircraft is a fictional seven-seat light jet. Certification basis is CS-23 Amendment 5
with ASTM F44 consensus standards as the accepted means of compliance, which is the right
basis for this class since CS-23 Amdt 5 and 14 CFR Part 23 Amdt 64 replaced the prescriptive
rules with safety objectives met through those standards. The design organisation holds a
Part 21 Subpart J approval, so type design data is released under the 21A.263 privilege
rather than sent to the authority item by item. Suppliers, operators and people are invented.
"""

PROGRAMME = "NX-200"
AIRCRAFT = "NX-200 Light Jet"
ROOT_FOLDER = f"{AIRCRAFT}"

T = "n5LightSpeedSystems"

# Lifecycle states, by the set a type uses. Named here so the content reads in domain terms.
S_WORK, S_DESIGN, S_STRESS, S_SIGN, S_REL, S_SUPER = (
    "In Work", "In Design Review", "In Stress Review", "Airworthiness Sign-off",
    "Released", "Superseded")
Q_OPEN, Q_REVIEW, Q_DISP, Q_CLOSED = "Open", "Under Review", "Dispositioned", "Closed"
C_PLANNED, C_METHOD, C_EVIDENCE, C_SUBMITTED, C_ACCEPTED, C_FINDING, C_CLOSED = (
    "Planned", "Method Agreed", "Evidence in Work", "Submitted", "Accepted",
    "Finding Open", "Closed")
P_DRAFT, P_REVIEW, P_ISSUED = "Draft", "In Review", "Issued"
R_DRAFT, R_REVIEW, R_APPROVED, R_IMPL, R_VERIFIED = (
    "Draft", "In Review", "Approved", "Implemented", "Verified")
SUP_ACTIVE, SUP_DRAFT, SUP_REVIEW = "Active", "Draft", "In Review"


# ─────────────────────────────────────────────────────────────────────────────
# People and organisations
# ─────────────────────────────────────────────────────────────────────────────
# Usernames only - the loader never sets a password for an existing account and creates a
# new one with the site's standard demo password. Group membership is what the workflows and
# the security model actually turn on.

USERS = [
    # username,        display name,        role,     groups
    ("l.harkness", "Lena Harkness", "Admin",
     ["LSS Airworthiness and Certification", "LSS Change Control Board"]),
    ("d.okonjo", "Daniel Okonjo", "User",
     ["LSS Design Engineering", "LSS Change Control Board"]),
    ("m.sandoval", "Mira Sandoval", "User", ["LSS Design Engineering"]),
    ("p.lindqvist", "Petra Lindqvist", "User", ["LSS Stress and Loads"]),
    ("r.achebe", "Rotimi Achebe", "User", ["LSS Systems Engineering"]),
    ("s.vanderberg", "Sanne van der Berg", "User",
     ["LSS Systems Engineering", "LSS Change Control Board"]),
    ("k.tanaka", "Kenji Tanaka", "User",
     ["LSS Quality Assurance", "LSS Material Review Board"]),
    ("a.novak", "Anja Novak", "User",
     ["LSS Quality Assurance", "LSS Material Review Board"]),
    ("t.brennan", "Tom Brennan", "User", ["LSS Manufacturing Engineering"]),
    ("y.cheng", "Yuan Cheng", "User", ["LSS Supply Chain"]),
    ("f.mbeki", "Faith Mbeki", "User", ["LSS Customer Support"]),
    ("g.rossi", "Giulia Rossi", "User",
     ["LSS Airworthiness and Certification", "LSS Material Review Board"]),
]

SUPPLIERS = [
    # name,                       cage,    country, scope
    ("Meridian Air Systems", "K4821", "United States",
     "Air cycle machines, heat exchangers, pressurisation control"),
    ("Thorne Avionics", "L7730", "United Kingdom",
     "VHF and satellite communications, audio integrating equipment"),
    ("Caldera Seating", "F2914", "Italy",
     "16g dynamically tested seating and restraint systems"),
    ("Volant Composites", "H5508", "Germany",
     "Composite sandwich panels, cabin monuments, interior trim"),
    ("Arclight Interconnect", "M1172", "United States",
     "Wiring harnesses, connectors, EWIS assembly"),
    ("Pyrosafe Materials", "N6643", "France",
     "Flame-retardant textiles, sealants and adhesives"),
]


def vendor_rep(num, name, company, role, email, cage, nda, nda_exp, brief):
    return {
        "type": f"{T}VendorRep", "pn": num, "description": name,
        "status": SUP_ACTIVE, "folder": f"{ROOT_FOLDER}/Quality Records/Supplier Approval",
        "attrs": {
            "companyName": company, "contactRole": role, "emailAddress": email,
            "supplierCageCode": cage, "ndaOnFile": nda, "ndaExpiryDate": nda_exp,
            "exportBriefingDate": brief, "siteAccessAuthorised": nda,
            "recordOwnerFunction": "Supply Chain", "programmeCode": PROGRAMME,
        },
    }


VENDOR_REPS = [
    vendor_rep("NX00100001", "Alan Pretorius - Meridian Air Systems",
               "Meridian Air Systems", "Programme manager",
               "a.pretorius@meridian-air.example", "K4821", True,
               "2027-03-31", "2026-02-11"),
    vendor_rep("NX00100002", "Yasmin Haddad - Thorne Avionics",
               "Thorne Avionics", "Design engineer",
               "y.haddad@thorne-avionics.example", "L7730", True,
               "2027-09-30", "2026-01-20"),
    vendor_rep("NX00100003", "Marco Bellini - Caldera Seating",
               "Caldera Seating", "Quality representative",
               "m.bellini@caldera-seating.example", "F2914", True,
               "2026-11-30", "2026-04-02"),
    vendor_rep("NX00100004", "Ingrid Vogt - Volant Composites",
               "Volant Composites", "Account manager",
               "i.vogt@volant-composites.example", "H5508", False,
               None, None),
    vendor_rep("NX00100005", "Dev Ramanathan - Arclight Interconnect",
               "Arclight Interconnect", "Delegated inspector",
               "d.ramanathan@arclight-ic.example", "M1172", True,
               "2028-01-31", "2026-03-18"),
]


# ─────────────────────────────────────────────────────────────────────────────
# Item helpers
# ─────────────────────────────────────────────────────────────────────────────

def item(type_stem, pn, description, status, attrs, folder=None, revision="A",
         notes=None, history=None):
    """One PLM item. `history` lists earlier revisions, oldest first."""
    return {
        "type": f"{T}{type_stem}", "pn": pn, "description": description,
        "status": status, "revision": revision, "attrs": attrs,
        "folder": folder, "notes": notes, "history": history or [],
    }


def common(ata, chapter_label, owner, maturity="Detail design", **extra):
    base = {
        "programmeCode": PROGRAMME,
        "ataChapter": chapter_label,
        "ataSubject": ata,
        "designResponsibleOrg": "LSS Design Engineering",
        "engineeringOwner": owner,
        "itemMaturity": maturity,
        "exportJurisdiction": "None",
        "exportClassification": "Not controlled",
    }
    base.update(extra)
    return base


ATA21 = "21 Air Conditioning"
ATA23 = "23 Communications"
ATA25 = "25 Equipment / Furnishings"

F21 = f"{ROOT_FOLDER}/Product Structure/ATA 21 Air Conditioning"
F23 = f"{ROOT_FOLDER}/Product Structure/ATA 23 Communications"
F25 = f"{ROOT_FOLDER}/Product Structure/ATA 25 Equipment and Furnishings"


# ─────────────────────────────────────────────────────────────────────────────
# ATA 21 - Air Conditioning and Pressurisation
# ─────────────────────────────────────────────────────────────────────────────
# A bleed-air bootstrap environmental control system: engine bleed through a shutoff and
# pressure-regulating valve, a primary heat exchanger, an air cycle machine, a water
# separator, cabin distribution, and a digital controller with its own DO-178C software.
# Pressurisation is a separate subsystem on the same chapter: outflow valve, cabin pressure
# controller, and the safety valve that is the last line of defence.

ITEMS_21 = [
    item("Installation", "LSS-21-INST-001",
         "Environmental control system installation, NX-200",
         S_REL,
         common("21-00", ATA21, "r.achebe", "Certified",
                airworthinessClassification="Essential",
                failureEffectClassification="Major",
                certificationBasis="CS-23 Amdt 5 + ASTM F44 MoC",
                designAssuranceLevel="C",
                massKg=86.4, massStatus="Weighed",
                cgStationMm=4120, cgButtlineMm=0, cgWaterlineMm=1180,
                doaApprovalReference="EASA.21J.0742",
                complianceItemRefs="LSS-CERT-COMP-001, LSS-CERT-COMP-004",
                installationZone="Zone 130 - aft equipment bay",
                systemInstalled="Environmental control and pressurisation",
                torqueSpecificationRef="LSS-SPEC-PRC-004",
                sealantSpecification="LSS-CM-0001",
                riggingProcedureRef="LSS-SPEC-PRC-011",
                installationManHours=38,
                clearanceRequirementMm=12,
                drawingNumber="LSS-DWG-21-0001",
                cadModelReference="NX200-ECS-INST-ASM",
                firstArticleRequired=True),
         folder=f"{F21}/21-00 Air Conditioning - General",
         history=[("A", S_REL)],
         notes="Installation released under DOA privilege 21A.263 on 14 May 2026. "
               "Mass is the weighed figure from airframe 002, superseding the calculated "
               "estimate of 84.1 kg."),

    item("AircraftPart", "LSS-21-0001",
         "Bleed air supply duct assembly, engine to pack",
         S_REL,
         common("21-10", ATA21, "m.sandoval", "Certified",
                partCategory="Sub-assembly",
                airworthinessClassification="Essential",
                failureEffectClassification="Major",
                primaryMaterial="Titanium Ti-6Al-4V",
                materialForm="Tube",
                materialSpecification="AMS 4911",
                massKg=4.82, massStatus="Weighed",
                ndtRequirement="Fluorescent penetrant",
                specialProcesses="Welding (AWS D17.1), penetrant inspection",
                processSpecificationRefs="LSS-PS-0001, LSS-PS-0003",
                fatigueCritical=False,
                pressureBoundary=True,
                drawingNumber="LSS-DWG-21-0002",
                cadModelReference="NX200-21-0001-ASM",
                interchangeability="Fully interchangeable",
                fireProtectionRequirement="None"),
         folder=f"{F21}/21-10 Compression",
         history=[("A", S_REL)]),

    item("AircraftPart", "LSS-21-0002",
         "Bleed duct, forward section",
         S_REL,
         common("21-10", ATA21, "m.sandoval", "Certified",
                partCategory="Tube / duct",
                primaryMaterial="Titanium Ti-6Al-4V",
                materialForm="Tube", materialSpecification="AMS 4911",
                massKg=1.94, massStatus="Weighed",
                ndtRequirement="Fluorescent penetrant",
                pressureBoundary=True,
                drawingNumber="LSS-DWG-21-0003",
                airworthinessClassification="Essential"),
         folder=f"{F21}/21-10 Compression", history=[("A", S_REL)]),

    item("AircraftPart", "LSS-21-0003",
         "Bleed duct, aft section",
         S_REL,
         common("21-10", ATA21, "m.sandoval", "Certified",
                partCategory="Tube / duct",
                primaryMaterial="Titanium Ti-6Al-4V",
                materialForm="Tube", materialSpecification="AMS 4911",
                massKg=2.31, massStatus="Weighed",
                ndtRequirement="Fluorescent penetrant",
                pressureBoundary=True,
                drawingNumber="LSS-DWG-21-0004",
                airworthinessClassification="Essential"),
         folder=f"{F21}/21-10 Compression", history=[("A", S_REL)]),

    # Revision B exists because an ECO changed it. This is the object the change story and
    # the nonconformance story both land on, so it carries real revision history.
    item("AircraftPart", "LSS-21-0004",
         "Duct coupling, V-band, 50 mm",
         S_REL,
         common("21-10", ATA21, "m.sandoval", "Certified",
                partCategory="Machined",
                primaryMaterial="Stainless steel 321",
                materialForm="Bar", materialSpecification="AMS 5510",
                massKg=0.34, massStatus="Weighed",
                ndtRequirement="None",
                pressureBoundary=True,
                drawingNumber="LSS-DWG-21-0005",
                airworthinessClassification="Essential",
                interchangeability="Fully interchangeable",
                processSpecificationRefs="LSS-PS-0002"),
         folder=f"{F21}/21-10 Compression", revision="B",
         history=[("A", S_SUPER), ("B", S_REL)],
         notes="Revision B raises the clamp band thickness from 1.2 mm to 1.6 mm after "
               "three in-service loosening reports. Implemented by LSS-ECO-00004 and "
               "notified by LSS-ECN-00004."),

    item("AircraftPart", "LSS-21-0005",
         "Primary heat exchanger mount assembly",
         S_REL,
         common("21-50", ATA21, "p.lindqvist", "Certified",
                partCategory="Sub-assembly",
                primaryMaterial="Aluminium 7075-T7351",
                materialForm="Plate", materialSpecification="AMS 4078",
                massKg=3.18, massStatus="Calculated",
                ndtRequirement="Fluorescent penetrant",
                fatigueCritical=True,
                damageToleranceCategory="Damage tolerant",
                drawingNumber="LSS-DWG-21-0006",
                airworthinessClassification="Essential",
                failureEffectClassification="Major"),
         folder=f"{F21}/21-50 Cooling", history=[("A", S_REL)]),

    item("AircraftPart", "LSS-21-0006", "Heat exchanger mount bracket, LH", S_REL,
         common("21-50", ATA21, "p.lindqvist", "Certified",
                partCategory="Machined", primaryMaterial="Aluminium 7075-T7351",
                materialForm="Plate", materialSpecification="AMS 4078",
                massKg=0.91, massStatus="Weighed", ndtRequirement="Fluorescent penetrant",
                fatigueCritical=True, damageToleranceCategory="Damage tolerant",
                surfaceTreatment="Chromic acid anodise to MIL-A-8625 Type I",
                processSpecificationRefs="LSS-PS-0004",
                drawingNumber="LSS-DWG-21-0007"),
         folder=f"{F21}/21-50 Cooling", history=[("A", S_REL)]),

    item("AircraftPart", "LSS-21-0007", "Heat exchanger mount bracket, RH", S_REL,
         common("21-50", ATA21, "p.lindqvist", "Certified",
                partCategory="Machined", primaryMaterial="Aluminium 7075-T7351",
                materialForm="Plate", materialSpecification="AMS 4078",
                massKg=0.91, massStatus="Weighed", ndtRequirement="Fluorescent penetrant",
                fatigueCritical=True, damageToleranceCategory="Damage tolerant",
                surfaceTreatment="Chromic acid anodise to MIL-A-8625 Type I",
                processSpecificationRefs="LSS-PS-0004",
                drawingNumber="LSS-DWG-21-0007"),
         folder=f"{F21}/21-50 Cooling", history=[("A", S_REL)]),

    item("AircraftPart", "LSS-21-0008", "Cabin air distribution manifold", S_REL,
         common("21-20", ATA21, "m.sandoval", "Certified",
                partCategory="Sub-assembly",
                primaryMaterial="Glass/epoxy laminate",
                materialForm="Prepreg", materialSpecification="LSS-SPEC-MAT-003",
                massKg=2.64, massStatus="Weighed",
                ndtRequirement="Ultrasonic",
                specialProcesses="Composite layup and cure (NADCAP Composites)",
                processSpecificationRefs="LSS-PS-0005",
                drawingNumber="LSS-DWG-21-0008",
                fireProtectionRequirement=
                "CS 23.853 / Appendix F Part I - vertical burn",
                airworthinessClassification="Non-Essential"),
         folder=f"{F21}/21-20 Distribution", history=[("A", S_REL)]),

    item("AircraftPart", "LSS-21-0009", "Distribution manifold shell, composite", S_REL,
         common("21-20", ATA21, "m.sandoval", "Certified",
                partCategory="Composite laminate",
                primaryMaterial="Glass/epoxy laminate",
                materialForm="Prepreg", materialSpecification="LSS-SPEC-MAT-003",
                massKg=1.88, massStatus="Weighed", ndtRequirement="Ultrasonic",
                processSpecificationRefs="LSS-PS-0005",
                drawingNumber="LSS-DWG-21-0009",
                fireProtectionRequirement=
                "CS 23.853 / Appendix F Part I - vertical burn"),
         folder=f"{F21}/21-20 Distribution", history=[("A", S_REL)]),

    item("AircraftPart", "LSS-21-0010", "Cabin air outlet nozzle, adjustable", S_REL,
         common("21-20", ATA21, "m.sandoval", "In production",
                partCategory="Moulded", primaryMaterial="PEI (Ultem 1000)",
                materialSpecification="LSS-SPEC-MAT-007",
                massKg=0.062, massStatus="Weighed", ndtRequirement="None",
                drawingNumber="LSS-DWG-21-0010",
                fireProtectionRequirement=
                "CS 23.853 / Appendix F Part I - vertical burn",
                airworthinessClassification="Non-Essential"),
         folder=f"{F21}/21-20 Distribution", history=[("A", S_REL)]),

    item("AircraftPart", "LSS-21-0011", "Outflow valve installation bracket", S_REL,
         common("21-30", ATA21, "p.lindqvist", "Certified",
                partCategory="Machined", primaryMaterial="Aluminium 2024-T351",
                materialForm="Plate", materialSpecification="AMS 4037",
                massKg=0.76, massStatus="Weighed",
                ndtRequirement="Fluorescent penetrant",
                fatigueCritical=True, pressureBoundary=True,
                damageToleranceCategory="Damage tolerant",
                drawingNumber="LSS-DWG-21-0011",
                airworthinessClassification="Flight Safety Critical",
                failureEffectClassification="Hazardous / Severe-Major"),
         folder=f"{F21}/21-30 Pressurisation Control", history=[("A", S_REL)]),

    # In work, not released: the live design the demo can open and edit.
    item("AircraftPart", "LSS-21-0012",
         "Ram air inlet scoop, redesigned for improved pressure recovery",
         S_DESIGN,
         common("21-50", ATA21, "m.sandoval", "Detail design",
                partCategory="Composite laminate",
                primaryMaterial="Carbon/epoxy laminate",
                materialForm="Prepreg", materialSpecification="LSS-SPEC-MAT-001",
                massKg=1.42, massStatus="Calculated", ndtRequirement="Ultrasonic",
                processSpecificationRefs="LSS-PS-0005",
                drawingNumber="LSS-DWG-21-0012",
                airworthinessClassification="Non-Essential",
                firstArticleRequired=True),
         folder=f"{F21}/21-50 Cooling", history=[("A", S_DESIGN)],
         notes="Raised by LSS-ECR-00002 to recover the 3.1 kPa pack inlet pressure "
               "shortfall measured in ground test. Awaiting stress sign-off on the "
               "revised attachment."),

    item("AircraftPart", "LSS-21-0013", "Condenser drain line and check valve mount",
         S_REL,
         common("21-70", ATA21, "m.sandoval", "Certified",
                partCategory="Tube / duct", primaryMaterial="Aluminium 6061-T6",
                materialForm="Tube", materialSpecification="AMS 4083",
                massKg=0.41, massStatus="Weighed", ndtRequirement="None",
                drawingNumber="LSS-DWG-21-0013",
                airworthinessClassification="Non-Essential"),
         folder=f"{F21}/21-70 Moisture and Air Contamination Control",
         history=[("A", S_REL)]),

    item("AircraftPart", "LSS-21-0014",
         "Pack bay firewall penetration seal plate",
         S_REL,
         common("21-00", ATA21, "m.sandoval", "Certified",
                partCategory="Sheet metal", primaryMaterial="Titanium Ti-6Al-4V",
                materialForm="Sheet", materialSpecification="AMS 4911",
                massKg=0.58, massStatus="Weighed", ndtRequirement="None",
                drawingNumber="LSS-DWG-21-0014",
                airworthinessClassification="Essential",
                failureEffectClassification="Hazardous / Severe-Major",
                fireProtectionRequirement=
                "CS 23.863 flammable fluid fire protection"),
         folder=f"{F21}/21-00 Air Conditioning - General", history=[("A", S_REL)]),

    item("ElectricalPart", "LSS-E-00001",
         "Environmental control system controller, dual channel",
         S_REL,
         common("21-60", ATA21, "r.achebe", "Certified",
                electricalFunction="Data concentrator",
                nominalVoltage=28, currentRating=3.5, powerConsumption=42,
                do160Revision="DO-160G",
                do160Categories="A2, D1, S(B), U, Z, B, A, X, X, F, Z, T, W(T), AB",
                hirfCategory="Category B",
                lightningZone="Interior - induced only",
                bondingRequirement="Class R bond to structure, 2.5 milliohm maximum",
                loadableSoftwareRef="LSS-SW-0001",
                mtbfHours=22000,
                massKg=1.86, massStatus="Weighed",
                airworthinessClassification="Essential",
                failureEffectClassification="Major",
                designAssuranceLevel="C",
                certificationBasis="CS-23 Amdt 5 + ASTM F44 MoC",
                drawingNumber="LSS-DWG-21-0015",
                serialisedItem=True,
                complianceItemRefs="LSS-CERT-COMP-004, LSS-CERT-COMP-012"),
         folder=f"{F21}/21-60 Temperature Control", history=[("A", S_REL)]),

    item("SoftwareItem", "LSS-SW-0001",
         "Environmental control system controller software",
         S_REL,
         {"programmeCode": PROGRAMME, "ataChapter": ATA21, "ataSubject": "21-60",
          "designResponsibleOrg": "LSS Design Engineering",
          "engineeringOwner": "r.achebe", "itemMaturity": "Certified",
          "exportJurisdiction": "EAR", "exportClassification": "EAR99",
          "softwarePartNumber": "LSS-SW-0001-02", "softwareVersion": "2.1.0",
          "do178cLevel": "C", "designAssuranceLevel": "C",
          "psacReference": "LSS-CERT-SWP-001",
          "sasReference": "LSS-CERT-SWP-004",
          "sciReference": "LSS-CERT-SWP-005",
          "objectCodeVerification": False,
          "verificationIndependence": True,
          "toolQualificationRefs": "Compiler (TQL-5), coverage analyser (TQL-5)",
          "fieldLoadable": True, "partitioningRequired": False,
          "targetProcessor": "PowerPC e200z4", "sourceLinesOfCode": 41200,
          "airworthinessClassification": "Essential",
          "failureEffectClassification": "Major",
          "certificationBasis": "CS-23 Amdt 5 + ASTM F44 MoC",
          "typeDesignData": True},
         folder=f"{ROOT_FOLDER}/Certification/Software and Electronic Hardware",
         revision="C",
         history=[("A", S_SUPER), ("B", S_SUPER), ("C", S_REL)],
         notes="Level C. Version 2.1.0 closes the cabin temperature oscillation reported "
               "in LSS-PR-00002. Field loadable, so a change needs a service bulletin as "
               "well as an engineering change notice."),

    item("Harness", "LSS-W21-001", "Environmental control system control harness", S_REL,
         common("21-60", ATA21, "d.okonjo", "Certified",
                wireSpecification="BMS 13-48 Type 5 Class 1",
                gaugeRange="20 to 12 AWG",
                connectorSpecifications="MIL-DTL-38999 Series III, size 13 and 17",
                shieldingClass="Twisted shielded pair",
                routeZone="Zone 130 to Zone 220, upper left raceway",
                separationCategory="Category 2 - redundant systems separated",
                harnessLengthMm=4820, circuitCount=38,
                ewisZonalInspectionRef="LSS-SPEC-TST-009",
                massKg=3.42, massStatus="Weighed",
                drawingNumber="LSS-DWG-21-0016",
                airworthinessClassification="Essential"),
         folder=f"{F21}/21-60 Temperature Control", history=[("A", S_REL)]),

    item("VendorPart", "LSS-V-00001", "Bleed air shutoff and pressure regulating valve",
         S_REL,
         {"programmeCode": PROGRAMME, "ataChapter": ATA21, "ataSubject": "21-10",
          "designResponsibleOrg": "Supplier design authority",
          "engineeringOwner": "m.sandoval", "itemMaturity": "Certified",
          "exportJurisdiction": "EAR", "exportClassification": "EAR99",
          "supplierName": "Meridian Air Systems",
          "supplierPartNumber": "MAS-4412-003", "supplierCageCode": "K4821",
          "approvalBasis": "Approved as part of type design",
          "sourceApprovalStatus": "Approved - single source",
          "obsolescenceStatus": "Active",
          "counterfeitRiskLevel": "Low - franchised distributor only",
          "authorisedDistributors": "Meridian Air Systems direct only",
          "reachSvhcStatus": "No SVHC above threshold",
          "rohsStatus": "Exempt - aerospace",
          "conflictMineralsStatus": "CMRT received",
          "leadTimeWeeks": 26, "massKg": 2.74, "massStatus": "Weighed",
          "airworthinessClassification": "Essential",
          "failureEffectClassification": "Major",
          "certificationBasis": "CS-23 Amdt 5 + ASTM F44 MoC",
          "serialisedItem": True, "typeDesignData": True,
          "buyMakeFlag": "Buy", "supplierUnitPrice": 14250, "costCurrency": "USD"},
         folder=f"{F21}/21-10 Compression", history=[("A", S_REL)]),

    item("VendorPart", "LSS-V-00002", "Air cycle machine, bootstrap, 1.8 kg/min", S_REL,
         {"programmeCode": PROGRAMME, "ataChapter": ATA21, "ataSubject": "21-50",
          "designResponsibleOrg": "Supplier design authority",
          "engineeringOwner": "r.achebe", "itemMaturity": "Certified",
          "exportJurisdiction": "EAR", "exportClassification": "ECCN 9A991.d",
          "supplierName": "Meridian Air Systems",
          "supplierPartNumber": "MAS-7730-011", "supplierCageCode": "K4821",
          "approvalBasis": "Approved as part of type design",
          "sourceApprovalStatus": "Approved - single source",
          "obsolescenceStatus": "Active",
          "counterfeitRiskLevel": "Low - franchised distributor only",
          "reachSvhcStatus": "No SVHC above threshold",
          "rohsStatus": "Exempt - aerospace",
          "conflictMineralsStatus": "CMRT received",
          "leadTimeWeeks": 38, "massKg": 11.9, "massStatus": "Weighed",
          "airworthinessClassification": "Essential",
          "failureEffectClassification": "Major",
          "lifeLimitedPart": True, "lifeLimitHours": 20000,
          "serialisedItem": True, "typeDesignData": True,
          "buyMakeFlag": "Buy", "supplierUnitPrice": 68400, "costCurrency": "USD"},
         folder=f"{F21}/21-50 Cooling", history=[("A", S_REL)],
         notes="Life limited to 20 000 flight hours. Overhaul interval and life limit are "
               "published in the airworthiness limitations section."),

    item("VendorPart", "LSS-V-00003", "Water separator and coalescer", S_REL,
         {"programmeCode": PROGRAMME, "ataChapter": ATA21, "ataSubject": "21-70",
          "designResponsibleOrg": "Supplier design authority",
          "engineeringOwner": "m.sandoval", "itemMaturity": "Certified",
          "exportJurisdiction": "None", "exportClassification": "Not controlled",
          "supplierName": "Meridian Air Systems",
          "supplierPartNumber": "MAS-2208-004", "supplierCageCode": "K4821",
          "approvalBasis": "Approved as part of type design",
          "sourceApprovalStatus": "Approved",
          "obsolescenceStatus": "Not recommended for new design",
          "counterfeitRiskLevel": "Low - franchised distributor only",
          "reachSvhcStatus": "SVHC declared",
          "rohsStatus": "Exempt - aerospace",
          "conflictMineralsStatus": "CMRT outstanding",
          "leadTimeWeeks": 18, "massKg": 1.64, "massStatus": "Weighed",
          "airworthinessClassification": "Non-Essential",
          "typeDesignData": True, "buyMakeFlag": "Buy"},
         folder=f"{F21}/21-70 Moisture and Air Contamination Control",
         history=[("A", S_REL)],
         notes="Supplier has flagged this part not recommended for new design. A SVHC "
               "declaration is on file against the coalescer media."),

    item("VendorPart", "LSS-V-00004", "Cabin pressure controller, digital, dual channel",
         S_REL,
         {"programmeCode": PROGRAMME, "ataChapter": ATA21, "ataSubject": "21-30",
          "designResponsibleOrg": "Supplier design authority",
          "engineeringOwner": "r.achebe", "itemMaturity": "Certified",
          "exportJurisdiction": "EAR", "exportClassification": "EAR99",
          "supplierName": "Meridian Air Systems",
          "supplierPartNumber": "MAS-9901-007", "supplierCageCode": "K4821",
          "approvalBasis": "EASA ETSO authorisation",
          "tsoEtsoReference": "ETSO-C2d",
          "sourceApprovalStatus": "Approved - single source",
          "obsolescenceStatus": "Active",
          "counterfeitRiskLevel": "Low - franchised distributor only",
          "reachSvhcStatus": "No SVHC above threshold",
          "rohsStatus": "Exempt - aerospace",
          "conflictMineralsStatus": "CMRT received",
          "leadTimeWeeks": 30, "massKg": 1.21, "massStatus": "Weighed",
          "airworthinessClassification": "Flight Safety Critical",
          "failureEffectClassification": "Hazardous / Severe-Major",
          "designAssuranceLevel": "B",
          "serialisedItem": True, "typeDesignData": True,
          "buyMakeFlag": "Buy", "supplierUnitPrice": 31900, "costCurrency": "USD"},
         folder=f"{F21}/21-30 Pressurisation Control", history=[("A", S_REL)]),

    item("VendorPart", "LSS-V-00005", "Outflow valve, electro-pneumatic", S_REL,
         {"programmeCode": PROGRAMME, "ataChapter": ATA21, "ataSubject": "21-30",
          "designResponsibleOrg": "Supplier design authority",
          "engineeringOwner": "m.sandoval", "itemMaturity": "Certified",
          "exportJurisdiction": "None", "exportClassification": "Not controlled",
          "supplierName": "Meridian Air Systems",
          "supplierPartNumber": "MAS-5540-002", "supplierCageCode": "K4821",
          "approvalBasis": "Approved as part of type design",
          "sourceApprovalStatus": "Approved",
          "obsolescenceStatus": "Active",
          "counterfeitRiskLevel": "Low - franchised distributor only",
          "reachSvhcStatus": "No SVHC above threshold",
          "rohsStatus": "Exempt - aerospace",
          "conflictMineralsStatus": "CMRT received",
          "leadTimeWeeks": 22, "massKg": 2.08, "massStatus": "Weighed",
          "airworthinessClassification": "Flight Safety Critical",
          "failureEffectClassification": "Hazardous / Severe-Major",
          "serialisedItem": True, "typeDesignData": True, "buyMakeFlag": "Buy"},
         folder=f"{F21}/21-30 Pressurisation Control", history=[("A", S_REL)]),

    item("VendorPart", "LSS-V-00006", "Cabin pressure safety valve, dual", S_REL,
         {"programmeCode": PROGRAMME, "ataChapter": ATA21, "ataSubject": "21-30",
          "designResponsibleOrg": "Supplier design authority",
          "engineeringOwner": "m.sandoval", "itemMaturity": "Certified",
          "exportJurisdiction": "None", "exportClassification": "Not controlled",
          "supplierName": "Meridian Air Systems",
          "supplierPartNumber": "MAS-5541-001", "supplierCageCode": "K4821",
          "approvalBasis": "Approved as part of type design",
          "sourceApprovalStatus": "Approved",
          "obsolescenceStatus": "Active",
          "counterfeitRiskLevel": "Low - franchised distributor only",
          "reachSvhcStatus": "No SVHC above threshold",
          "rohsStatus": "Exempt - aerospace",
          "conflictMineralsStatus": "CMRT received",
          "leadTimeWeeks": 20, "massKg": 1.48, "massStatus": "Weighed",
          "airworthinessClassification": "Flight Safety Critical",
          "failureEffectClassification": "Catastrophic",
          "serialisedItem": True, "typeDesignData": True, "buyMakeFlag": "Buy"},
         folder=f"{F21}/21-30 Pressurisation Control", history=[("A", S_REL)],
         notes="The last line of defence against cabin overpressure. Failure effect is "
               "catastrophic, so the installation is substantiated by LSS-CERT-SAFE-002."),

    item("VendorPart", "LSS-V-00007", "Primary heat exchanger, air to air", S_REL,
         {"programmeCode": PROGRAMME, "ataChapter": ATA21, "ataSubject": "21-50",
          "designResponsibleOrg": "Supplier design authority",
          "engineeringOwner": "r.achebe", "itemMaturity": "Certified",
          "exportJurisdiction": "None", "exportClassification": "Not controlled",
          "supplierName": "Meridian Air Systems",
          "supplierPartNumber": "MAS-6612-008", "supplierCageCode": "K4821",
          "approvalBasis": "Approved as part of type design",
          "sourceApprovalStatus": "Approved",
          "obsolescenceStatus": "Active",
          "counterfeitRiskLevel": "Low - franchised distributor only",
          "reachSvhcStatus": "No SVHC above threshold",
          "rohsStatus": "Exempt - aerospace",
          "conflictMineralsStatus": "CMRT received",
          "leadTimeWeeks": 34, "massKg": 8.6, "massStatus": "Weighed",
          "airworthinessClassification": "Essential",
          "typeDesignData": True, "buyMakeFlag": "Buy"},
         folder=f"{F21}/21-50 Cooling", history=[("A", S_REL)]),

    item("AeroStdPart", "LSS-STD-00001", "Clamp, V-band coupling, 50 mm", S_REL,
         {"programmeCode": PROGRAMME, "ataChapter": ATA21, "ataSubject": "21-10",
          "designResponsibleOrg": "Industry standard",
          "engineeringOwner": "t.brennan", "itemMaturity": "In production",
          "exportJurisdiction": "None", "exportClassification": "Not controlled",
          "standardFamily": "MS", "standardNumber": "MS27020-8",
          "standardBody": "NASM / NAS", "fastenerType": "Clamp",
          "gradeClass": "Corrosion resistant steel",
          "platingFinish": "Passivated per AMS 2700",
          "installationTorque": 5.6,
          "lockingFeature": "Self-locking nut",
          "qualifiedProductsList": True,
          "massKg": 0.084, "massStatus": "Weighed",
          "airworthinessClassification": "Standard Part", "typeDesignData": True},
         folder=f"{F21}/21-10 Compression", history=[("A", S_REL)]),

    item("AeroStdPart", "LSS-STD-00002", "Bolt, hex head, close tolerance, 1/4-28", S_REL,
         {"programmeCode": PROGRAMME, "ataChapter": "20 Standard Practices - Airframe",
          "ataSubject": "20-10", "designResponsibleOrg": "Industry standard",
          "engineeringOwner": "t.brennan", "itemMaturity": "In production",
          "exportJurisdiction": "None", "exportClassification": "Not controlled",
          "standardFamily": "NAS", "standardNumber": "NAS6204-10",
          "standardBody": "Aerospace Industries Association",
          "fastenerType": "Bolt", "gradeClass": "Alloy steel, 160 ksi",
          "threadSpecification": "1/4-28 UNJF-3A",
          "platingFinish": "Cadmium plate per AMS-QQ-P-416 Type II Class 2",
          "installationTorque": 9.0,
          "lockingFeature": "Self-locking nut",
          "qualifiedProductsList": True,
          "massKg": 0.012, "massStatus": "Weighed",
          "airworthinessClassification": "Standard Part", "typeDesignData": True},
         folder=f"{ROOT_FOLDER}/Product Structure/ATA 20 Standard Practices - Airframe",
         history=[("A", S_REL)]),

    item("AeroStdPart", "LSS-STD-00003", "Nut, self-locking, hex, 1/4-28", S_REL,
         {"programmeCode": PROGRAMME, "ataChapter": "20 Standard Practices - Airframe",
          "ataSubject": "20-10", "designResponsibleOrg": "Industry standard",
          "engineeringOwner": "t.brennan", "itemMaturity": "In production",
          "exportJurisdiction": "None", "exportClassification": "Not controlled",
          "standardFamily": "NAS", "standardNumber": "NAS1291-4",
          "standardBody": "Aerospace Industries Association",
          "fastenerType": "Nut", "gradeClass": "Corrosion resistant steel",
          "threadSpecification": "1/4-28 UNJF-3B",
          "lockingFeature": "Self-locking nut",
          "qualifiedProductsList": True,
          "massKg": 0.006, "massStatus": "Weighed",
          "airworthinessClassification": "Standard Part", "typeDesignData": True},
         folder=f"{ROOT_FOLDER}/Product Structure/ATA 20 Standard Practices - Airframe",
         history=[("A", S_REL)]),

    item("Consumable", "LSS-CM-0001",
         "Sealant, polysulphide, fuel and pressure resistant, Class B-2", SUP_ACTIVE,
         {"programmeCode": PROGRAMME, "ataChapter": "20 Standard Practices - Airframe",
          "ataSubject": "20-30", "designResponsibleOrg": "Industry standard",
          "engineeringOwner": "t.brennan", "itemMaturity": "In production",
          "exportJurisdiction": "None", "exportClassification": "Not controlled",
          "consumableClass": "Sealant", "specification": "AMS 3277 Class B-2",
          "manufacturer": "Pyrosafe Materials", "shelfLifeMonths": 9,
          "storageConditions": "4 to 27 degrees C, original sealed container",
          "cureSchedule": "72 hours at 25 degrees C and 50 percent RH",
          "mixRatio": "100:10 by weight, base to accelerator",
          "potLifeMinutes": 120,
          "hazardClassification": "UN3334, aviation regulated liquid",
          "safetyDataSheetRef": "SDS-PYR-3277-B2",
          "batchTraceabilityRequired": True,
          "recordOwnerFunction": "Manufacturing", "controlledItem": True,
          "typeDesignData": False},
         folder=f"{ROOT_FOLDER}/Production/Consumable Materials"),

    item("Tooling", "LSS-TL-0001",
         "Assembly jig, environmental control system pack bay", SUP_ACTIVE,
         {"programmeCode": PROGRAMME, "ataChapter": ATA21, "ataSubject": "21-00",
          "designResponsibleOrg": "LSS Design Engineering",
          "engineeringOwner": "t.brennan", "itemMaturity": "In production",
          "exportJurisdiction": "None", "exportClassification": "Not controlled",
          "toolType": "Assembly jig", "toolClass": "Hard tool - production",
          "calibrationRequired": True, "calibrationInterval": 12,
          "calibrationDueDate": "2027-02-28",
          "calibrationCertificateRef": "CAL-2026-0418",
          "locationCode": "Bay 3, Station 140", "custodian": "t.brennan",
          "qualifiedForParts": "LSS-21-INST-001, LSS-21-0001, LSS-21-0005",
          "toolProvingRecordRef": "TPR-2026-0071",
          "recordOwnerFunction": "Manufacturing", "controlledItem": True,
          "typeDesignData": False},
         folder=f"{ROOT_FOLDER}/Production/Tooling and GSE"),

    item("Tooling", "LSS-TL-0002",
         "Check fixture, bleed duct assembly LSS-21-0001", "Restricted",
         {"programmeCode": PROGRAMME, "ataChapter": ATA21, "ataSubject": "21-10",
          "designResponsibleOrg": "LSS Design Engineering",
          "engineeringOwner": "t.brennan", "itemMaturity": "In production",
          "exportJurisdiction": "None", "exportClassification": "Not controlled",
          "toolType": "Check fixture", "toolClass": "Hard tool - production",
          "calibrationRequired": True, "calibrationInterval": 6,
          "calibrationDueDate": "2026-09-30",
          "calibrationCertificateRef": "CAL-2026-0119",
          "locationCode": "Inspection room 1", "custodian": "k.tanaka",
          "qualifiedForParts": "LSS-21-0001, LSS-21-0002, LSS-21-0003",
          "toolProvingRecordRef": "TPR-2026-0044",
          "recordOwnerFunction": "Quality", "controlledItem": True,
          "typeDesignData": False},
         folder=f"{ROOT_FOLDER}/Production/Tooling and GSE",
         notes="Restricted: calibration lapsed on 30 September 2026. Quarantined pending "
               "recalibration. Inspections taken with it between 30 September and "
               "quarantine are under review in LSS-NCR-00006."),
]
