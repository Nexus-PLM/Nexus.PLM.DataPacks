"""The NX-200 type tree: eight abstract bases and twenty-four concrete types.

The abstract bases already exist in the installer payload as empty stubs. This module fills
them, so a site that has them sees a Modified diff on the bases and New on everything else,
rather than a parallel aviation hierarchy standing next to the one it already had.

    ItemsBase (OOTB)
    +- n5LightSpeedSystemsItemBase                     programme, ATA, export control
       +- n5LightSpeedSystemsTypeDesignItemBase        airworthiness, DAL, mass, life limits
       |  +- n5LightSpeedSystemsEngBase                CAD, drawing, GD&T, interchangeability
       |  |  +- AircraftPart  ElectricalPart  InteriorPart  Installation  Harness
       |  +- AeroStdPart  VendorPart  SoftwareItem  AehItem
       +- n5LightSpeedSystemsNonTypeDesignItemBase
          +- VendorRep  Tooling  Consumable

    DocumentsBase (OOTB)
    +- n5LightSpeedSystemsDocumentsBase                issue, author, retention, confidentiality
       +- n5LightSpeedSystemsTypeDesignDocumentsBase   cert basis, means of compliance, CRI
       |  +- Drawing  Specification  Icd  ComplianceReport  QualTestPlan  QualTestReport
       |     SafetyAssessment  SwPlan  PrjSpecificCertPlan  EMICAR
       +- n5LightSpeedSystemsNonTypeDesignDocumentsBase  AS9100D clause, record owner
          +- FaiReport  Ncr  CofC  AirworthinessRelease  ServiceBulletin  ProcessSpec
             SupplierQualRecord
"""

from aviation_model import (
    AIRWORTHINESS_CLASS, AS9100D_CLAUSES, ATA_CHAPTERS_IN_SCOPE, CERTIFICATE_STATES,
    CERT_BASIS, COMPLIANCE_STATES, CONFIDENTIALITY, DAL, DO160_SECTIONS, EXPORT_CLASS,
    EXPORT_JURISDICTION, FAILURE_EFFECT, MEANS_OF_COMPLIANCE, NADCAP_FAMILIES,
    PUBLICATION_STATES, QUALITY_STATES, RETENTION, SUPPORT_STATES, TYPE_DESIGN_STATES,
    WF_COMPLIANCE, WF_FAI, WF_MRB, WF_PUBLICATION, WF_SUPPLIER, WF_TYPE_DESIGN,
    a, states, t,
)

# Every ATA chapter the NX-200 structure uses, chapter level. The three in scope for this
# demo are built out to subchapter level in the classification tree.
ATA_ALL = [
    "05 Time Limits / Maintenance Checks", "06 Dimensions and Areas",
    "20 Standard Practices - Airframe", "21 Air Conditioning",
    "22 Auto Flight", "23 Communications", "24 Electrical Power",
    "25 Equipment / Furnishings", "26 Fire Protection", "27 Flight Controls",
    "28 Fuel", "29 Hydraulic Power", "30 Ice and Rain Protection",
    "31 Indicating / Recording Systems", "32 Landing Gear", "33 Lights",
    "34 Navigation", "35 Oxygen", "36 Pneumatic", "38 Water / Waste",
    "49 Airborne Auxiliary Power", "51 Standard Practices - Structures",
    "52 Doors", "53 Fuselage", "54 Nacelles / Pylons", "55 Stabilizers",
    "56 Windows", "57 Wings", "71 Power Plant", "72 Engine",
    "73 Engine Fuel and Control", "74 Ignition", "75 Air", "76 Engine Controls",
    "77 Engine Indicating", "78 Exhaust", "79 Oil", "80 Starting",
]

PROGRAMMES = ["NX-200", "NX-200ER", "NX-100 (legacy)", "Common / multi-programme"]


def ty(stem, display, description, base, abstract=False, attributes=None,
       lifecycle=None, numbering=None, actions=None, reactions=None):
    """One type definition, shaped as the Engine's on-disk type JSON expects it."""
    row = {
        "typeName": t(stem) if not base.startswith("__") else t(stem),
        "displayName": display,
        "description": description,
        "version": "1.0.0",
        "relationship": "Derive",
        "baseTypeName": base,
        "abstract": abstract,
        "attributes": attributes or [],
        "rules": [],
        "actions": actions or [],
        "reactions": reactions or [],
    }
    if numbering:
        row["numberingSchemaName"] = numbering
    if lifecycle:
        row["lifecycleStates"] = lifecycle
    return row


def action(name, display, description, workflow_id, available_in):
    return {
        "name": name, "displayName": display, "description": description,
        "workflowDefinitionId": workflow_id, "availableInStatuses": available_in,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Abstract bases
# ─────────────────────────────────────────────────────────────────────────────

ITEM_BASE_ATTRS = [
    a("programmeCode", "Programme", required=True, lov=PROGRAMMES,
      default="NX-200"),
    a("ataChapter", "ATA Chapter", lov=ATA_ALL),
    a("ataSubject", "ATA Subject", lov=None),
    a("designResponsibleOrg", "Design Responsible Organisation",
      lov=["LSS Design Engineering", "LSS Interiors", "Supplier design authority",
           "Licensed from third party", "Industry standard"]),
    a("engineeringOwner", "Engineering Owner"),
    a("itemMaturity", "Maturity",
      lov=["Concept", "Preliminary", "Detail design", "Certified", "In production",
           "Legacy / out of production"], default="Detail design"),
    a("exportJurisdiction", "Export Jurisdiction", lov=EXPORT_JURISDICTION,
      default="None"),
    a("exportClassification", "Export Classification", lov=EXPORT_CLASS,
      default="Not controlled"),
]

TYPE_DESIGN_ITEM_ATTRS = [
    a("typeDesignData", "Type Design Data", kind="Bool", default=True),
    a("certificationBasis", "Certification Basis", lov=CERT_BASIS,
      default="CS-23 Amdt 5 + ASTM F44 MoC"),
    a("airworthinessClassification", "Airworthiness Classification",
      lov=AIRWORTHINESS_CLASS, default="Non-Essential"),
    a("failureEffectClassification", "Failure Effect (ARP4754A)", lov=FAILURE_EFFECT),
    a("designAssuranceLevel", "Design Assurance Level", lov=DAL,
      default="Not applicable"),
    a("doaApprovalReference", "DOA Approval Reference"),
    a("complianceItemRefs", "Compliance Item References"),
    a("serialisedItem", "Serialised", kind="Bool", default=False),
    a("lifeLimitedPart", "Life Limited Part", kind="Bool", default=False),
    a("lifeLimitHours", "Life Limit", kind="Number", unit="FH"),
    a("lifeLimitCycles", "Cycle Limit", kind="Number", unit="FC"),
    a("massKg", "Mass", kind="Number", unit="kg"),
    a("massStatus", "Mass Status",
      lov=["Estimated", "Calculated", "Weighed", "Contractual"], default="Estimated"),
    a("cgStationMm", "CG Station (X)", kind="Number", unit="mm"),
    a("cgButtlineMm", "CG Buttline (Y)", kind="Number", unit="mm"),
    a("cgWaterlineMm", "CG Waterline (Z)", kind="Number", unit="mm"),
    a("materialSpecification", "Material Specification"),
    a("processSpecificationRefs", "Process Specifications"),
    a("fireProtectionRequirement", "Fire Protection Requirement",
      lov=["None", "CS 23.853 / Appendix F Part I - vertical burn",
           "Appendix F Part II - seat cushion oil burner",
           "Appendix F Part IV - heat release",
           "Appendix F Part V - smoke density",
           "CS 23.863 flammable fluid fire protection"], default="None"),
]

ENG_BASE_ATTRS = [
    a("cadModelReference", "CAD Model Reference"),
    a("drawingNumber", "Drawing Number"),
    a("dashNumberVariant", "Dash Number / Variant"),
    a("modelBasedDefinition", "Model Based Definition", kind="Bool", default=False),
    a("geometricTolerancingStandard", "GD&T Standard",
      lov=["ASME Y14.5-2018", "ASME Y14.5-2009", "ISO 1101:2017", "Not applied"],
      default="ASME Y14.5-2018"),
    a("interchangeability", "Interchangeability",
      lov=["Fully interchangeable", "One-way interchangeable",
           "Not interchangeable - rework required", "Replaceable with modification"],
      default="Fully interchangeable"),
    a("firstArticleRequired", "First Article Required", kind="Bool", default=True),
]

NON_TYPE_DESIGN_ITEM_ATTRS = [
    a("typeDesignData", "Type Design Data", kind="Bool", default=False),
    a("recordOwnerFunction", "Owning Function",
      lov=["Quality", "Manufacturing", "Supply Chain", "Customer Support",
           "Airworthiness", "Engineering"]),
    a("controlledItem", "Under Configuration Control", kind="Bool", default=False),
]

DOC_BASE_ATTRS = [
    a("issueDate", "Issue Date", kind="Date"),
    a("authorName", "Author"),
    a("checkedBy", "Checked By"),
    a("approvedBy", "Approved By"),
    a("pageCount", "Pages", kind="Number"),
    a("retentionClass", "Retention Class", lov=RETENTION,
      default="Quality record - 7 years"),
    a("confidentiality", "Confidentiality", lov=CONFIDENTIALITY, default="Internal"),
    a("distributionList", "Distribution"),
    a("supersedesDocument", "Supersedes"),
]

TYPE_DESIGN_DOC_ATTRS = [
    a("typeDesignData", "Type Design Data", kind="Bool", default=True),
    a("certificationBasis", "Certification Basis", lov=CERT_BASIS,
      default="CS-23 Amdt 5 + ASTM F44 MoC"),
    a("complianceRegulations", "Regulation Paragraphs"),
    a("meansOfCompliance", "Means of Compliance", lov=MEANS_OF_COMPLIANCE),
    a("approvalRoute", "Approval Route",
      lov=["DOA privilege (21A.263)", "EASA direct approval",
           "FAA ODA", "FAA ACO direct", "Validation by partner authority"],
      default="DOA privilege (21A.263)"),
    a("certificationReviewItem", "Certification Review Item (CRI)"),
    a("designAssuranceLevel", "Design Assurance Level", lov=DAL,
      default="Not applicable"),
    a("certificationAuthority", "Certification Authority",
      lov=["EASA", "FAA", "TCCA", "ANAC", "CAAC", "UK CAA"], default="EASA"),
    a("doaApprovalReference", "DOA Approval Reference"),
]

NON_TYPE_DESIGN_DOC_ATTRS = [
    a("typeDesignData", "Type Design Data", kind="Bool", default=False),
    a("qmsClause", "AS9100D Clause", lov=AS9100D_CLAUSES),
    a("recordOwnerFunction", "Owning Function",
      lov=["Quality", "Manufacturing", "Supply Chain", "Customer Support",
           "Airworthiness"]),
    a("auditEvidence", "Audit Evidence", kind="Bool", default=True),
    a("objectiveEvidenceRefs", "Objective Evidence References"),
]


ABSTRACT_TYPES = [
    ty("ItemBase", f"{'Light Speed Systems'} Item Base",
       "Abstract base for everything Light Speed Systems makes or manages. Programme, ATA "
       "position and export-control classification live here because every item has them, "
       "whether or not it is type design data.",
       "ItemsBase", abstract=True, attributes=ITEM_BASE_ATTRS,
       lifecycle=states(TYPE_DESIGN_STATES)),

    ty("TypeDesignItemBase", "Type Design Item Base",
       "Abstract base for items that form part of the approved type design. Everything here "
       "is airworthiness-relevant: the certification basis it was approved against, its "
       "failure-effect classification and design assurance level, its mass and centre of "
       "gravity contribution, and any life limit. Changing one of these items is a change to "
       "the type design and goes through the type design release route.",
       t("ItemBase"), abstract=True, attributes=TYPE_DESIGN_ITEM_ATTRS),

    ty("EngBase", "Engineered Item Base",
       "Abstract base for items Light Speed Systems designs itself, as opposed to standard "
       "parts and supplier-designed items. Holds the definition data - CAD reference, drawing "
       "number, tolerancing standard and interchangeability rule.",
       t("TypeDesignItemBase"), abstract=True, attributes=ENG_BASE_ATTRS),

    ty("NonTypeDesignItemBase", "Non Type Design Item Base",
       "Abstract base for items that support production and service but are not part of the "
       "approved type design: tooling, consumables and supplier contacts. These change "
       "without touching the type certificate.",
       t("ItemBase"), abstract=True, attributes=NON_TYPE_DESIGN_ITEM_ATTRS,
       lifecycle=states(SUPPORT_STATES)),

    ty("DocumentsBase", "Light Speed Systems Document Base",
       "Abstract base for every Light Speed Systems document. Authorship, approval, retention "
       "class and confidentiality live here - the fields an auditor asks for whatever the "
       "document is.",
       "DocumentsBase", abstract=True, attributes=DOC_BASE_ATTRS,
       lifecycle=states(TYPE_DESIGN_STATES)),

    ty("TypeDesignDocumentsBase", "Type Design Document Base",
       "Abstract base for documents that are themselves type design data or the evidence "
       "behind it. Carries what the document is compliance for: the regulation paragraphs, "
       "the means of compliance used, the certification review item it answers and the "
       "authority it is shown to.",
       t("DocumentsBase"), abstract=True, attributes=TYPE_DESIGN_DOC_ATTRS),

    ty("NonTypeDesignDocumentsBase", "Quality and Production Record Base",
       "Abstract base for records that evidence the quality management system rather than the "
       "design: first article reports, nonconformances, certificates and supplier approvals. "
       "Each one names the AS9100D clause it is evidence for, which is how an audit sample is "
       "assembled from the data rather than from a folder.",
       t("DocumentsBase"), abstract=True, attributes=NON_TYPE_DESIGN_DOC_ATTRS,
       lifecycle=states(QUALITY_STATES)),
]


# ─────────────────────────────────────────────────────────────────────────────
# Concrete item types
# ─────────────────────────────────────────────────────────────────────────────

RELEASE_ACTION = action(
    "SubmitForRelease", "Submit for release",
    "Starts the type design data release route: design check and stress substantiation in "
    "parallel, then an Airworthiness and Certification signatory.",
    WF_TYPE_DESIGN,
    ["In Work", "In Design Review", "In Stress Review", "Airworthiness Sign-off"],
)

CONCRETE_ITEM_TYPES = [
    ty("AircraftPart", "Aircraft Part",
       "A structural or mechanical part Light Speed Systems designs - ducting, brackets, "
       "machined fittings, composite panels. The workhorse type of the ATA 21 and ATA 25 "
       "structure.",
       t("EngBase"), numbering="n5LssAircraftPart", actions=[RELEASE_ACTION],
       attributes=[
           a("partCategory", "Part Category",
             lov=["Detail part", "Sub-assembly", "Machined", "Sheet metal",
                  "Composite laminate", "Composite sandwich", "Tube / duct",
                  "Casting", "Forging", "Extrusion", "Moulded"],
             default="Detail part"),
           a("primaryMaterial", "Primary Material"),
           a("materialForm", "Material Form",
             lov=["Plate", "Sheet", "Bar", "Tube", "Extrusion", "Forging", "Casting",
                  "Prepreg", "Core", "Film adhesive"]),
           a("heatTreatCondition", "Heat Treat Condition"),
           a("surfaceTreatment", "Surface Treatment"),
           a("ndtRequirement", "NDT Requirement",
             lov=["None", "Fluorescent penetrant", "Radiographic", "Ultrasonic",
                  "Eddy current", "Magnetic particle", "Thermography"],
             default="None"),
           a("specialProcesses", "Special Processes (NADCAP)"),
           a("fatigueCritical", "Fatigue Critical", kind="Bool", default=False),
           a("damageToleranceCategory", "Damage Tolerance Category",
             lov=["Not applicable", "Safe life", "Damage tolerant",
                  "Fail safe - multiple load path"], default="Not applicable"),
           a("pressureBoundary", "Pressure Boundary", kind="Bool", default=False),
       ]),

    ty("ElectricalPart", "Electrical / Avionics Part",
       "An electrical or avionics item Light Speed Systems designs or specifies to its own "
       "requirement - control panels, power distribution, antennas, audio equipment. Carries "
       "the DO-160G qualification position and the HIRF and lightning zone it sits in.",
       t("EngBase"), numbering="n5LssElectricalPart", actions=[RELEASE_ACTION],
       attributes=[
           a("electricalFunction", "Electrical Function",
             lov=["Power generation", "Power distribution", "Control panel",
                  "Sensor / transducer", "Actuator drive", "Antenna",
                  "Audio / radio equipment", "Display", "Lighting",
                  "Protection device", "Data concentrator"]),
           a("nominalVoltage", "Nominal Voltage", kind="Number", unit="V DC"),
           a("currentRating", "Current Rating", kind="Number", unit="A"),
           a("powerConsumption", "Power Consumption", kind="Number", unit="W"),
           a("do160Revision", "DO-160 Revision",
             lov=["DO-160G", "DO-160F", "ED-14G", "Not qualified"],
             default="DO-160G"),
           a("do160Categories", "DO-160 Environmental Categories"),
           a("hirfCategory", "HIRF Category",
             lov=["Not applicable", "Category A", "Category B", "Category C",
                  "Category D", "Category E"], default="Not applicable"),
           a("lightningZone", "Lightning Zone",
             lov=["Zone 1A", "Zone 1B", "Zone 1C", "Zone 2A", "Zone 2B", "Zone 3",
                  "Interior - induced only"], default="Interior - induced only"),
           a("bondingRequirement", "Bonding / Grounding Requirement"),
           a("tsoAuthorisation", "TSO / ETSO Authorisation"),
           a("loadableSoftwareRef", "Loadable Software Reference"),
           a("mtbfHours", "MTBF", kind="Number", unit="FH"),
       ]),

    ty("InteriorPart", "Interior / Furnishing Part",
       "A cabin or flight compartment furnishing - seats, sidewalls, cabinetry, soft goods, "
       "monuments. The ATA 25 workhorse. Flammability and occupant-safety substantiation are "
       "first-class fields because that is what the certification evidence turns on, and "
       "because these are the items a customer reconfigures between aircraft.",
       t("EngBase"), numbering="n5LssInteriorPart", actions=[RELEASE_ACTION],
       attributes=[
           a("interiorZone", "Interior Zone",
             lov=["Flight compartment", "Passenger compartment", "Galley", "Lavatory",
                  "Baggage compartment", "Cabinetry / monument", "Vestibule"]),
           a("furnishingCategory", "Furnishing Category",
             lov=["Seat", "Seat cushion", "Sidewall panel", "Ceiling panel",
                  "Floor panel", "Carpet", "Window shade", "Table", "Cabinet",
                  "Divider", "Soft goods", "Placard", "Stowage"]),
           a("flammabilityTest", "Flammability Test Basis",
             lov=["Appendix F Part I - 12 second vertical",
                  "Appendix F Part I - 60 second vertical",
                  "Appendix F Part I - horizontal",
                  "Appendix F Part II - seat cushion oil burner",
                  "Appendix F Part IV - heat release (OSU 65/65)",
                  "Appendix F Part V - smoke density (Ds 200)",
                  "Not applicable"]),
           a("flammabilityTestReportRef", "Flammability Test Report"),
           a("occupantSafetyBasis", "Occupant Safety Basis",
             lov=["CS 23.562 - 16g dynamic", "CS 25.562 - 16g dynamic",
                  "CS 23.561 static emergency landing", "TSO-C127b seat",
                  "Not applicable"], default="Not applicable"),
           a("dynamicTestReportRef", "Dynamic Test Report"),
           a("upholsteryMaterial", "Upholstery / Facing Material"),
           a("colourTrimCode", "Colour and Trim Code"),
           a("customerConfigurable", "Customer Configurable", kind="Bool",
             default=False),
           a("completionCentreFit", "Completion Centre Fit", kind="Bool",
             default=False),
       ]),

    ty("Installation", "Installation",
       "An ATA installation: the item that puts equipment on the aircraft and owns the "
       "interface to it. Where the routing, clamping, torque and sealing definition lives, "
       "and the level at which a system is signed off as installed.",
       t("EngBase"), numbering="n5LssInstallation", actions=[RELEASE_ACTION],
       attributes=[
           a("installationZone", "Aircraft Zone"),
           a("systemInstalled", "System Installed"),
           a("torqueSpecificationRef", "Torque Specification"),
           a("sealantSpecification", "Sealant Specification"),
           a("riggingProcedureRef", "Rigging / Adjustment Procedure"),
           a("accessPanelRefs", "Access Panels"),
           a("clearanceRequirementMm", "Minimum Clearance", kind="Number", unit="mm"),
           a("installationManHours", "Installation Time", kind="Number", unit="h"),
       ]),

    ty("Harness", "Wiring Harness",
       "A wiring harness or loom. Separation category and route zone are held because EWIS "
       "substantiation depends on them, not on the wire list alone.",
       t("EngBase"), numbering="n5LssHarness", actions=[RELEASE_ACTION],
       attributes=[
           a("wireSpecification", "Wire Specification"),
           a("gaugeRange", "Gauge Range (AWG)"),
           a("connectorSpecifications", "Connector Specifications"),
           a("shieldingClass", "Shielding Class",
             lov=["Unshielded", "Single braid", "Double braid", "Overall shield",
                  "Twisted shielded pair", "Triax"]),
           a("routeZone", "Route Zone"),
           a("separationCategory", "EWIS Separation Category",
             lov=["Category 1 - essential separate route",
                  "Category 2 - redundant systems separated",
                  "Category 3 - no separation requirement"],
             default="Category 3 - no separation requirement"),
           a("harnessLengthMm", "Overall Length", kind="Number", unit="mm"),
           a("circuitCount", "Circuit Count", kind="Number"),
           a("ewisZonalInspectionRef", "EWIS Zonal Inspection Reference"),
       ]),

    ty("AeroStdPart", "Aerospace Standard Part",
       "A standard part procured to an industry designation - AN, MS, NAS, NASM, EN or ISO. "
       "The number carried in partNumber is a site cross-reference; the designation a buyer "
       "actually orders against is standardNumber. A standard part is type design data but "
       "the design authority is the standards body, not Light Speed Systems.",
       t("TypeDesignItemBase"), numbering="n5LssStandardPart",
       attributes=[
           a("standardFamily", "Standard Family",
             lov=["AN", "MS", "NAS", "NASM", "BACB", "EN", "ISO", "DIN", "LN", "SAE"],
             required=True),
           a("standardNumber", "Standard Designation", required=True),
           a("standardBody", "Standards Body",
             lov=["SAE International", "Aerospace Industries Association",
                  "NASM / NAS", "ISO", "CEN / EN", "DIN", "Airbus BACB"]),
           a("fastenerType", "Fastener / Item Type",
             lov=["Bolt", "Screw", "Nut", "Washer", "Rivet", "Pin", "Bearing",
                  "Clamp", "Grommet", "Terminal", "Connector", "Seal", "O-ring",
                  "Insert", "Not a fastener"]),
           a("gradeClass", "Grade / Class"),
           a("threadSpecification", "Thread Specification"),
           a("platingFinish", "Plating / Finish"),
           a("installationTorque", "Installation Torque", kind="Number", unit="Nm"),
           a("lockingFeature", "Locking Feature",
             lov=["None", "Self-locking nut", "Castellated and cotter pin",
                  "Lock washer", "Thread locking compound", "Safety cable"]),
           a("qualifiedProductsList", "On QPL / QML", kind="Bool", default=False),
       ]),

    ty("VendorPart", "Vendor Part",
       "A bought item whose design authority is the supplier. The obsolescence and "
       "counterfeit-risk fields are here because AS9100D 8.1.4 asks the organisation to "
       "control the risk of suspect parts entering the build, and the only way to sample "
       "that in an audit is to hold it as data.",
       t("TypeDesignItemBase"), numbering="n5LssVendorPart",
       actions=[action("RequestSourceApproval", "Request source approval",
                       "Starts the supplier part source approval route.",
                       WF_SUPPLIER,
                       ["In Work", "In Design Review", "Airworthiness Sign-off"])],
       attributes=[
           a("supplierName", "Supplier", required=True),
           a("supplierPartNumber", "Supplier Part Number", required=True),
           a("supplierCageCode", "Supplier CAGE / NSCM Code"),
           a("approvalBasis", "Approval Basis",
             lov=["FAA TSO authorisation", "EASA ETSO authorisation",
                  "FAA PMA", "Approved as part of type design",
                  "Standard part", "Commercial off the shelf"],
             default="Approved as part of type design"),
           a("tsoEtsoReference", "TSO / ETSO Reference"),
           a("sourceApprovalStatus", "Source Approval Status",
             lov=["Not submitted", "Under review", "Approved",
                  "Approved - single source", "Conditional", "Rejected"],
             default="Not submitted"),
           a("alternateApprovedSources", "Alternate Approved Sources"),
           a("obsolescenceStatus", "Obsolescence Status",
             lov=["Active", "Not recommended for new design", "Last time buy announced",
                  "Obsolete - stock only", "Obsolete - no stock"], default="Active"),
           a("lastTimeBuyDate", "Last Time Buy Date", kind="Date"),
           a("counterfeitRiskLevel", "Counterfeit Risk",
             lov=["Low - franchised distributor only", "Medium - broker used",
                  "High - obsolete and broker sourced"],
             default="Low - franchised distributor only"),
           a("authorisedDistributors", "Authorised Distributors"),
           a("reachSvhcStatus", "REACH SVHC Status",
             lov=["No SVHC above threshold", "SVHC declared", "Under assessment",
                  "Not assessed"], default="Not assessed"),
           a("rohsStatus", "RoHS Status",
             lov=["Compliant", "Exempt - aerospace", "Non-compliant", "Not assessed"],
             default="Exempt - aerospace"),
           a("conflictMineralsStatus", "Conflict Minerals Declaration",
             lov=["CMRT received", "CMRT outstanding", "Not applicable"],
             default="CMRT outstanding"),
           a("leadTimeWeeks", "Lead Time", kind="Number", unit="weeks"),
       ]),

    ty("SoftwareItem", "Airborne Software Item",
       "An airborne software configuration item developed and verified to DO-178C. The "
       "assurance level drives which of the standard's objectives apply and whether "
       "verification independence is required, so both are held on the item rather than "
       "buried in the plan.",
       t("TypeDesignItemBase"), numbering="n5LssSoftwareItem", actions=[RELEASE_ACTION],
       attributes=[
           a("softwarePartNumber", "Software Part Number", required=True),
           a("softwareVersion", "Software Version", required=True),
           a("do178cLevel", "DO-178C Software Level", lov=DAL, required=True),
           a("psacReference", "PSAC Reference"),
           a("sasReference", "Software Accomplishment Summary"),
           a("sciReference", "Software Configuration Index"),
           a("objectCodeVerification", "Object Code Verification Required",
             kind="Bool", default=False),
           a("verificationIndependence", "Verification Independence Required",
             kind="Bool", default=False),
           a("toolQualificationRefs", "Qualified Tools (DO-330)"),
           a("fieldLoadable", "Field Loadable Software", kind="Bool", default=False),
           a("partitioningRequired", "Partitioning Required", kind="Bool",
             default=False),
           a("targetProcessor", "Target Processor"),
           a("sourceLinesOfCode", "Source Lines of Code", kind="Number"),
       ]),

    ty("AehItem", "Airborne Electronic Hardware Item",
       "A programmable electronic hardware item developed to DO-254. Complex devices carry "
       "the full objective set; simple ones are substantiated by test alone, so the "
       "classification is a required field.",
       t("TypeDesignItemBase"), numbering="n5LssAehItem", actions=[RELEASE_ACTION],
       attributes=[
           a("hardwarePartNumber", "Hardware Part Number", required=True),
           a("hardwareVersion", "Hardware Version", required=True),
           a("do254Level", "DO-254 Hardware Level", lov=DAL, required=True),
           a("complexityClassification", "Complexity Classification",
             lov=["Simple", "Complex"], required=True, default="Simple"),
           a("deviceType", "Device Type",
             lov=["FPGA", "CPLD", "ASIC", "PLD", "Microcontroller firmware",
                  "Analogue custom device"]),
           a("deviceFamily", "Device Family"),
           a("phacReference", "PHAC Reference"),
           a("hasReference", "Hardware Accomplishment Summary"),
           a("hdlLanguage", "HDL Language",
             lov=["VHDL", "Verilog", "SystemVerilog", "Schematic capture",
                  "Not applicable"]),
           a("elaborationToolsQualified", "Elaboration Tools Assessed", kind="Bool",
             default=False),
       ]),

    ty("VendorRep", "Vendor Representative",
       "A named contact at a supplier. Not type design data, but the non-disclosure and "
       "export-briefing position is held because an export-controlled drawing may not be sent "
       "to a person whose paperwork has lapsed.",
       t("NonTypeDesignItemBase"),
       attributes=[
           a("companyName", "Company", required=True),
           a("contactRole", "Role",
             lov=["Account manager", "Programme manager", "Design engineer",
                  "Quality representative", "Delegated inspector", "Logistics"]),
           a("emailAddress", "Email"),
           a("telephone", "Telephone"),
           a("supplierCageCode", "Supplier CAGE Code"),
           a("ndaOnFile", "NDA On File", kind="Bool", default=False),
           a("ndaExpiryDate", "NDA Expiry", kind="Date"),
           a("exportBriefingDate", "Export Control Briefing", kind="Date"),
           a("siteAccessAuthorised", "Site Access Authorised", kind="Bool",
             default=False),
       ]),

    ty("Tooling", "Tooling and Ground Support Equipment",
       "Production tooling, inspection fixtures, test rigs and ground support equipment. Not "
       "type design data, but a check fixture whose calibration has lapsed invalidates the "
       "inspection records taken with it, so calibration status is held as data and not in a "
       "spreadsheet.",
       t("NonTypeDesignItemBase"), numbering="n5LssTooling",
       attributes=[
           a("toolType", "Tool Type",
             lov=["Assembly jig", "Drill template", "Bond fixture", "Layup mould",
                  "Check fixture", "Inspection gauge", "Test rig",
                  "Ground support equipment", "Lifting / handling", "Trim tool"],
             required=True),
           a("toolClass", "Tool Class",
             lov=["Hard tool - master", "Hard tool - production", "Soft tool",
                  "Rate tool", "Prototype only"]),
           a("calibrationRequired", "Calibration Required", kind="Bool", default=False),
           a("calibrationInterval", "Calibration Interval", kind="Number",
             unit="months"),
           a("calibrationDueDate", "Calibration Due", kind="Date"),
           a("calibrationCertificateRef", "Calibration Certificate"),
           a("locationCode", "Location"),
           a("custodian", "Custodian"),
           a("qualifiedForParts", "Qualified For Part Numbers"),
           a("toolProvingRecordRef", "Tool Proving Record"),
       ]),

    ty("Consumable", "Consumable Material",
       "Sealants, adhesives, primers, finishes and fluids. Shelf life and cure schedule are "
       "held because an expired sealant batch is a nonconformance waiting to be found, and "
       "because the batch is what a traceability question lands on.",
       t("NonTypeDesignItemBase"), numbering="n5LssConsumable",
       attributes=[
           a("consumableClass", "Consumable Class",
             lov=["Sealant", "Adhesive - film", "Adhesive - paste", "Primer",
                  "Topcoat", "Lubricant", "Hydraulic fluid", "Solvent / cleaner",
                  "Potting compound", "Abradable", "Tape"], required=True),
           a("specification", "Governing Specification", required=True),
           a("manufacturer", "Manufacturer"),
           a("shelfLifeMonths", "Shelf Life", kind="Number", unit="months"),
           a("storageConditions", "Storage Conditions"),
           a("cureSchedule", "Cure Schedule"),
           a("mixRatio", "Mix Ratio"),
           a("potLifeMinutes", "Pot Life", kind="Number", unit="min"),
           a("hazardClassification", "Hazard Classification"),
           a("safetyDataSheetRef", "Safety Data Sheet"),
           a("batchTraceabilityRequired", "Batch Traceability Required", kind="Bool",
             default=True),
       ]),
]


# ─────────────────────────────────────────────────────────────────────────────
# Concrete document types
# ─────────────────────────────────────────────────────────────────────────────

DOC_RELEASE_ACTION = action(
    "SubmitForRelease", "Submit for release",
    "Starts the type design data release route.",
    WF_TYPE_DESIGN,
    ["In Work", "In Design Review", "In Stress Review", "Airworthiness Sign-off"],
)

CONCRETE_DOC_TYPES = [
    ty("Drawing", "Engineering Drawing",
       "A released engineering drawing or model-based definition package. Whether the drawing "
       "has been ballooned is held here because an AS9102 Form 3 has to agree with a specific "
       "ballooned issue of a specific drawing, and 'the latest drawing' is not an answer an "
       "auditor accepts.",
       t("TypeDesignDocumentsBase"), numbering="n5LssDrawing",
       actions=[DOC_RELEASE_ACTION],
       attributes=[
           a("drawingType", "Drawing Type",
             lov=["Detail", "Assembly", "Installation", "Schematic",
                  "Wiring diagram", "Tube routing", "Layout", "Interface",
                  "Model based definition"], required=True),
           a("sheetSize", "Sheet Size",
             lov=["A0", "A1", "A2", "A3", "A4", "ANSI A", "ANSI B", "ANSI C",
                  "ANSI D", "ANSI E"]),
           a("sheetCount", "Sheet Count", kind="Number"),
           a("drawingScale", "Scale"),
           a("projectionAngle", "Projection",
             lov=["First angle", "Third angle"], default="First angle"),
           a("cadSourceSystem", "CAD Source System"),
           a("gdtApplied", "GD&T Applied", kind="Bool", default=True),
           a("balloonedForFai", "Ballooned for FAI", kind="Bool", default=False),
           a("balloonedIssue", "Ballooned Issue"),
           a("characteristicCount", "Characteristic Count", kind="Number"),
       ]),

    ty("Specification", "Specification",
       "A design, material, process, test, procurement or software requirements "
       "specification. The class drives the numbering sequence, so a process specification "
       "and a material specification never share a number.",
       t("TypeDesignDocumentsBase"), numbering="n5LssSpecification",
       actions=[DOC_RELEASE_ACTION],
       attributes=[
           a("specificationClass", "Specification Class",
             lov=["Design specification", "Material specification",
                  "Process specification", "Test specification",
                  "Procurement specification", "Software requirements specification",
                  "Interface requirements specification"], required=True),
           a("specificationAuthority", "Issuing Authority"),
           a("supersededStandards", "Supersedes Standards"),
           a("flowdownRequired", "Supplier Flowdown Required", kind="Bool",
             default=False),
           a("verificationMethod", "Verification Method",
             lov=["Inspection", "Analysis", "Demonstration", "Test",
                  "Similarity"]),
       ]),

    ty("Icd", "Interface Control Document",
       "The agreed interface between two items, held as a document in its own right so both "
       "sides reference one controlled definition rather than two drawings that drift.",
       t("TypeDesignDocumentsBase"), numbering="n5LssInterfaceControl",
       actions=[DOC_RELEASE_ACTION],
       attributes=[
           a("interfaceType", "Interface Type",
             lov=["Mechanical", "Electrical", "Data bus", "Thermal", "Pneumatic",
                  "Hydraulic", "Software", "Structural attachment"], required=True),
           a("partyA", "Party A"),
           a("partyB", "Party B"),
           a("busProtocol", "Bus Protocol",
             lov=["ARINC 429", "ARINC 664 / AFDX", "MIL-STD-1553B", "CAN / CAN FD",
                  "RS-422", "RS-485", "Ethernet", "Discrete", "Analogue",
                  "Not applicable"], default="Not applicable"),
           a("interfaceBaselineRef", "Interface Baseline"),
           a("bilateralAgreementSigned", "Bilaterally Agreed", kind="Bool",
             default=False),
           a("supplierAgreementDate", "Supplier Agreement Date", kind="Date"),
       ]),

    ty("ComplianceReport", "Compliance Report",
       "One demonstration of compliance against one certification requirement: what the "
       "requirement is, how it was shown, what the evidence is and who accepted it. This is "
       "the type the certification compliance board is built from, and the type an auditor "
       "samples when asking how compliance was shown.",
       t("TypeDesignDocumentsBase"), numbering="n5LssCertificationDoc",
       lifecycle=states(COMPLIANCE_STATES),
       actions=[action("SubmitEvidence", "Submit evidence",
                       "Starts the means-of-compliance acceptance route.",
                       WF_COMPLIANCE,
                       ["Planned", "Method Agreed", "Evidence in Work",
                        "Finding Open"])],
       attributes=[
           a("regulationParagraph", "Regulation Paragraph", required=True),
           a("requirementText", "Requirement Text"),
           a("consensusStandardRef", "Consensus Standard (ASTM F44)"),
           a("complianceStatus", "Compliance Status",
             lov=["Not started", "In work", "Compliant",
                  "Compliant with limitation", "Equivalent safety finding",
                  "Special condition", "Not compliant", "Not applicable"],
             default="Not started"),
           a("evidenceDocumentRefs", "Evidence Documents"),
           a("acceptedBy", "Accepted By"),
           a("acceptanceDate", "Acceptance Date", kind="Date"),
           a("openFindingCount", "Open Findings", kind="Number"),
           a("levelOfInvolvement", "Authority Level of Involvement",
             lov=["DOA privilege - no authority involvement",
                  "Authority notified", "Authority witnessed",
                  "Authority reviewed and accepted"],
             default="DOA privilege - no authority involvement"),
       ]),

    ty("QualTestPlan", "Qualification Test Plan",
       "The plan for an equipment qualification campaign, normally DO-160G. Names the "
       "sections and environmental categories the equipment will be shown against before any "
       "specimen goes on a shaker.",
       t("TypeDesignDocumentsBase"), numbering="n5LssCertificationDoc",
       actions=[DOC_RELEASE_ACTION],
       attributes=[
           a("do160Revision", "DO-160 Revision",
             lov=["DO-160G", "DO-160F", "ED-14G", "MIL-STD-810H"],
             default="DO-160G"),
           a("do160Sections", "Sections in Scope", lov=DO160_SECTIONS),
           a("environmentalCategories", "Environmental Categories"),
           a("equipmentUnderTest", "Equipment Under Test"),
           a("specimenCount", "Specimen Count", kind="Number"),
           a("testLaboratory", "Test Laboratory"),
           a("labAccreditation", "Laboratory Accreditation"),
           a("plannedStartDate", "Planned Start", kind="Date"),
           a("witnessRequired", "Witness Required", kind="Bool", default=False),
       ]),

    ty("QualTestReport", "Qualification Test Report",
       "The result of a qualification campaign. The outcome and any deviation taken during "
       "test are first-class fields, because a pass with a deviation is a different "
       "certification position from a clean pass and the difference must not live in a "
       "paragraph somebody has to read.",
       t("TypeDesignDocumentsBase"), numbering="n5LssCertificationDoc",
       actions=[DOC_RELEASE_ACTION],
       attributes=[
           a("do160Revision", "DO-160 Revision",
             lov=["DO-160G", "DO-160F", "ED-14G", "MIL-STD-810H"],
             default="DO-160G"),
           a("do160Sections", "Sections Tested", lov=DO160_SECTIONS),
           a("environmentalCategories", "Categories Achieved"),
           a("testPlanReference", "Test Plan Reference", required=True),
           a("testLaboratory", "Test Laboratory"),
           a("labAccreditation", "Laboratory Accreditation"),
           a("testStartDate", "Test Start", kind="Date"),
           a("testEndDate", "Test End", kind="Date"),
           a("specimenSerialNumbers", "Specimen Serial Numbers"),
           a("testResult", "Result",
             lov=["Pass", "Pass with deviation", "Partial - retest required",
                  "Fail"], required=True),
           a("deviationReferences", "Deviations Taken"),
           a("retestRequired", "Retest Required", kind="Bool", default=False),
       ]),

    ty("SafetyAssessment", "Safety Assessment",
       "A functional hazard assessment, preliminary or final system safety assessment, common "
       "cause analysis or failure mode analysis under ARP4754A and ARP4761A. Holds the "
       "quantitative target and what was achieved against it, which is how a design assurance "
       "level is justified rather than asserted.",
       t("TypeDesignDocumentsBase"), numbering="n5LssCertificationDoc",
       actions=[DOC_RELEASE_ACTION],
       attributes=[
           a("assessmentType", "Assessment Type",
             lov=["FHA - aircraft level", "FHA - system level", "PASA", "PSSA",
                  "SSA", "CCA - zonal", "CCA - particular risk",
                  "CCA - common mode", "FMEA", "FMES", "Fault tree analysis"],
             required=True),
           a("arpReference", "Governing Practice",
             lov=["ARP4754A", "ARP4761A", "ARP4761", "ARP5150", "CS 23.2510"],
             default="ARP4754A"),
           a("functionAnalysed", "Function Analysed"),
           a("worstCaseFailureEffect", "Worst Case Failure Effect",
             lov=FAILURE_EFFECT),
           a("quantitativeTarget", "Quantitative Target (per flight hour)"),
           a("achievedProbability", "Achieved Probability (per flight hour)"),
           a("allocatedDal", "Allocated Design Assurance Level", lov=DAL),
           a("derivedRequirementCount", "Derived Requirements Raised", kind="Number"),
           a("openHazardCount", "Open Hazards", kind="Number"),
       ]),

    ty("SwPlan", "Software and AEH Plan",
       "One of the DO-178C or DO-254 plans and indices: PSAC, SDP, SVP, SCMP, SQAP, PHAC, "
       "accomplishment summary or configuration index. Held as its own type because the "
       "authority asks for a specific plan by name and the set has to be shown complete.",
       t("TypeDesignDocumentsBase"), numbering="n5LssCertificationDoc",
       actions=[DOC_RELEASE_ACTION],
       attributes=[
           a("planType", "Plan Type",
             lov=["PSAC - plan for software aspects of certification",
                  "SDP - software development plan",
                  "SVP - software verification plan",
                  "SCMP - software configuration management plan",
                  "SQAP - software quality assurance plan",
                  "SAS - software accomplishment summary",
                  "SCI - software configuration index",
                  "PHAC - plan for hardware aspects of certification",
                  "HAS - hardware accomplishment summary",
                  "HCI - hardware configuration index"], required=True),
           a("assuranceStandard", "Assurance Standard",
             lov=["DO-178C / ED-12C", "DO-254 / ED-80", "DO-278A", "DO-330",
                  "DO-331 model based", "DO-332 object oriented",
                  "DO-333 formal methods"], required=True),
           a("applicableLevel", "Assurance Level", lov=DAL, required=True),
           a("objectivesApplicable", "Objectives Applicable", kind="Number"),
           a("objectivesWithIndependence", "Objectives Requiring Independence",
             kind="Bool", default=False),
           a("supplementsApplied", "Supplements Applied"),
           a("authorityAgreementRef", "Authority Agreement Reference"),
       ]),

    ty("PrjSpecificCertPlan", "Certification Programme Plan",
       "The project-specific certification plan: the certification basis, the special "
       "conditions and equivalent safety findings sought, the certification review items "
       "open, and which design organisation privileges will be used. The document the whole "
       "compliance checklist hangs off.",
       t("TypeDesignDocumentsBase"), numbering="n5LssCertificationDoc",
       actions=[DOC_RELEASE_ACTION],
       attributes=[
           a("certificationProgramme", "Certification Programme", required=True),
           a("applicableSpecification", "Applicable Specification", lov=CERT_BASIS,
             required=True),
           a("amendmentLevel", "Amendment Level"),
           a("specialConditions", "Special Conditions"),
           a("equivalentSafetyFindings", "Equivalent Safety Findings"),
           a("deviationsRequested", "Deviations Requested"),
           a("certificationReviewItems", "Certification Review Items"),
           a("complianceChecklistRef", "Compliance Checklist Reference"),
           a("doaPrivilegesUsed", "DOA Privileges Used"),
           a("levelOfInvolvementAgreed", "Level of Involvement Agreed", kind="Bool",
             default=False),
           a("plannedCertificationDate", "Planned Certification Date", kind="Date"),
       ]),

    ty("EMICAR", "EMI Compliance Assessment Report",
       "The electromagnetic interference compliance assessment for an installed equipment "
       "item: DO-160G sections 20, 21, 22 and 25 together with the HIRF and lightning "
       "environment the installation sits in.",
       t("TypeDesignDocumentsBase"), numbering="n5LssCertificationDoc",
       actions=[DOC_RELEASE_ACTION],
       attributes=[
           a("equipmentUnderTest", "Equipment Assessed", required=True),
           a("do160Sections", "Sections Assessed", lov=DO160_SECTIONS),
           a("equipmentCategory", "Equipment Category"),
           a("hirfEnvironment", "HIRF Environment",
             lov=["Certification environment", "Severe environment",
                  "Normal environment"], default="Certification environment"),
           a("lightningZone", "Lightning Zone",
             lov=["Zone 1A", "Zone 1B", "Zone 1C", "Zone 2A", "Zone 2B", "Zone 3",
                  "Interior - induced only"]),
           a("testLaboratory", "Test Laboratory"),
           a("assessmentDate", "Assessment Date", kind="Date"),
           a("assessmentResult", "Result",
             lov=["Compliant", "Compliant with installation limitation",
                  "Not compliant", "Assessment incomplete"]),
           a("installationLimitations", "Installation Limitations"),
       ]),

    # ── Quality and production records ──────────────────────────────────────

    ty("FaiReport", "First Article Inspection Report",
       "An AS9102 Rev C first article inspection. Forms 1, 2 and 3 are tracked separately "
       "because a submission is incomplete until all three are, and because a delta FAI "
       "legitimately re-uses forms from the full FAI it builds on.",
       t("NonTypeDesignDocumentsBase"), numbering="n5LssQualityRecord",
       actions=[action("SubmitFai", "Submit for approval",
                       "Starts the first article inspection approval route.",
                       WF_FAI, ["Open", "Under Review"])],
       attributes=[
           a("as9102Revision", "AS9102 Revision", lov=["Rev C", "Rev B", "Rev A"],
             default="Rev C"),
           a("faiPartNumber", "Part Number Inspected", required=True),
           a("faiPartRevision", "Part Revision Inspected", required=True),
           a("balloonedDrawingRef", "Ballooned Drawing", required=True),
           a("faiType", "FAI Type",
             lov=["Full FAI", "Partial FAI", "Delta FAI"], required=True,
             default="Full FAI"),
           a("faiReason", "Reason for FAI",
             lov=["New part", "Engineering change", "Manufacturing process change",
                  "Change of manufacturing source", "Change of tooling",
                  "Lapse in production over two years", "Customer request",
                  "Corrective action"], required=True),
           a("form1Complete", "Form 1 - Part Accountability", kind="Bool",
             default=False),
           a("form2Complete", "Form 2 - Product Accountability", kind="Bool",
             default=False),
           a("form3Complete", "Form 3 - Characteristic Accountability", kind="Bool",
             default=False),
           a("characteristicCount", "Characteristics Verified", kind="Number"),
           a("nonconformanceCount", "Nonconformances Found", kind="Number"),
           a("serialOrLotNumber", "Serial / Lot Number"),
           a("manufacturingProcessRef", "Manufacturing Process Reference"),
           a("measurementSystemAnalysisRef", "MSA Reference"),
           a("faiResult", "Result",
             lov=["Accepted", "Accepted with deviation", "Rejected",
                  "Awaiting disposition"], default="Awaiting disposition"),
           a("customerApprovalRequired", "Customer Approval Required", kind="Bool",
             default=False),
           a("customerApprovalDate", "Customer Approval Date", kind="Date"),
       ]),

    ty("Ncr", "Nonconformance Report",
       "A nonconformance and its material review board disposition under AS9100D 8.7. The "
       "escape flag and the safety-impact flag are separate fields on purpose: an escape is a "
       "customer notification question and a safety impact is a continued-airworthiness "
       "question, and one does not imply the other.",
       t("NonTypeDesignDocumentsBase"), numbering="n5LssQualityRecord",
       actions=[action("RaiseToMrb", "Raise to material review board",
                       "Starts the material review board disposition route.",
                       WF_MRB, ["Open", "Under Review"])],
       attributes=[
           a("affectedPartNumber", "Affected Part Number", required=True),
           a("affectedPartRevision", "Affected Revision"),
           a("affectedSerialNumbers", "Affected Serial / Lot Numbers"),
           a("quantityAffected", "Quantity Affected", kind="Number"),
           a("severity", "Severity", lov=["Critical", "Major", "Minor"],
             required=True, default="Minor"),
           a("detectedAt", "Detected At",
             lov=["Receiving inspection", "In-process", "Final inspection",
                  "Assembly", "Ground test", "Flight test", "In service",
                  "Supplier self-disclosure", "Audit"], required=True),
           a("nonconformanceType", "Nonconformance Type",
             lov=["Dimensional", "Material", "Special process", "Documentation",
                  "Handling damage", "Missing operation", "Foreign object debris",
                  "Software", "Wrong configuration fitted",
                  "Suspect unapproved part"], required=True),
           a("containmentAction", "Containment Action"),
           a("mrbDisposition", "MRB Disposition",
             lov=["Use as is", "Rework to drawing", "Repair to approved scheme",
                  "Scrap", "Return to supplier", "Deviation - this build only",
                  "Waiver - already delivered", "Awaiting disposition"],
             default="Awaiting disposition"),
           a("dispositionAuthority", "Disposition Authority",
             lov=["Material review board", "DOA engineering signatory",
                  "Customer", "Airworthiness authority", "Supplier"],
             default="Material review board"),
           a("repairSchemeRef", "Approved Repair Scheme"),
           a("safetyImpact", "Safety Impact", kind="Bool", default=False),
           a("escapeToCustomer", "Escaped to Customer", kind="Bool", default=False),
           a("customerNotificationDate", "Customer Notified", kind="Date"),
           a("rootCause", "Root Cause"),
           a("correctiveActionRef", "Corrective Action Reference"),
           a("recurrenceCount", "Prior Recurrences", kind="Number"),
           a("costOfNonconformance", "Cost of Nonconformance", kind="Number"),
       ]),

    ty("CofC", "Certificate of Conformity",
       "A supplier's statement that what was shipped conforms to the purchase order and its "
       "flowed-down requirements. Issued once and then immutable, which is why the lifecycle "
       "has no route back out of Issued.",
       t("NonTypeDesignDocumentsBase"), numbering="n5LssQualityRecord",
       lifecycle=states(CERTIFICATE_STATES),
       attributes=[
           a("supplierName", "Supplier", required=True),
           a("supplierCageCode", "Supplier CAGE Code"),
           a("purchaseOrderNumber", "Purchase Order", required=True),
           a("purchaseOrderLine", "PO Line"),
           a("certifiedPartNumber", "Part Number", required=True),
           a("certifiedPartRevision", "Part Revision"),
           a("quantityShipped", "Quantity Shipped", kind="Number"),
           a("lotNumber", "Lot / Batch Number"),
           a("serialNumbers", "Serial Numbers"),
           a("materialCertificateRefs", "Material Certificates"),
           a("specialProcessCertRefs", "Special Process Certificates"),
           a("deviationsDeclared", "Deviations Declared"),
           a("authorisedSignatory", "Authorised Signatory", required=True),
           a("statementOfConformity", "Statement of Conformity"),
       ]),

    ty("AirworthinessRelease", "Authorised Release Certificate",
       "An FAA 8130-3 or EASA Form 1. The release status in block 12/13 and the eligibility "
       "statement decide what an operator may legally do with the part, so they are held as "
       "fields rather than as text in an attachment.",
       t("NonTypeDesignDocumentsBase"), numbering="n5LssQualityRecord",
       lifecycle=states(CERTIFICATE_STATES),
       attributes=[
           a("formType", "Form Type",
             lov=["FAA Form 8130-3", "EASA Form 1", "TCCA Form One",
                  "Dual release 8130-3 / Form 1"], required=True),
           a("certificateNumber", "Authorised Release Certificate Number",
             required=True),
           a("releasedPartNumber", "Part Number", required=True),
           a("releasedPartRevision", "Part Revision"),
           a("quantity", "Quantity", kind="Number"),
           a("serialOrBatchNumber", "Serial / Batch Number"),
           a("releaseStatus", "Status / Work",
             lov=["New", "Prototype", "Overhauled", "Inspected / tested",
                  "Repaired", "Modified", "Reassembled"], required=True,
             default="New"),
           a("approvalDesignData", "Approved Design Data Reference"),
           a("releasingOrganisationApproval", "Releasing Organisation Approval"),
           a("eligibilityStatement", "Eligibility"),
           a("remarks", "Remarks"),
           a("nonApprovedDesignData", "Non-Approved Design Data", kind="Bool",
             default=False),
           a("dateOfIssue", "Date of Issue", kind="Date"),
           a("authorisedSignatory", "Authorised Signatory"),
       ]),

    ty("ServiceBulletin", "Service Bulletin",
       "A continued-airworthiness publication to operators. Effectivity and compliance period "
       "are structured fields because an operator's compliance is judged against them, and "
       "because a mandatory bulletin is frequently the means of complying with an "
       "airworthiness directive.",
       t("NonTypeDesignDocumentsBase"), numbering="n5LssServiceBulletin",
       lifecycle=states(PUBLICATION_STATES),
       actions=[action("SubmitForIssue", "Submit for issue",
                       "Starts the publication issue route.",
                       WF_PUBLICATION, ["Draft", "In Review"])],
       attributes=[
           a("bulletinType", "Bulletin Type",
             lov=["Mandatory", "Recommended", "Optional", "Alert service bulletin"],
             required=True, default="Recommended"),
           a("bulletinCategory", "Category",
             lov=["Modification", "Inspection", "Life limit change",
                  "Software update", "Manual revision", "Tooling",
                  "Parts information"], required=True),
           a("effectivityRange", "Effectivity", required=True),
           a("compliancePeriod", "Compliance Period"),
           a("estimatedManHours", "Estimated Labour", kind="Number", unit="h"),
           a("aircraftDowntimeHours", "Aircraft Downtime", kind="Number", unit="h"),
           a("kitPartNumber", "Modification Kit Part Number"),
           a("relatedDirectiveRef", "Related Airworthiness Directive"),
           a("weightChangeKg", "Weight Change", kind="Number", unit="kg"),
           a("publicationDate", "Publication Date", kind="Date"),
           a("warrantyApplicable", "Warranty Applicable", kind="Bool",
             default=False),
       ]),

    ty("ProcessSpec", "Special Process Specification",
       "A special process specification: a process whose result cannot be verified by "
       "inspecting the finished part, so the process itself is controlled. Carries whether "
       "NADCAP accreditation is required of the performing source and whether the plan is "
       "frozen.",
       t("NonTypeDesignDocumentsBase"), numbering="n5LssProcessSpec",
       lifecycle=states(TYPE_DESIGN_STATES),
       attributes=[
           a("processFamily", "Process Family", lov=NADCAP_FAMILIES, required=True),
           a("governingStandard", "Governing Standard"),
           a("nadcapAccreditationRequired", "NADCAP Accreditation Required",
             kind="Bool", default=True),
           a("approvedSourceList", "Approved Sources"),
           a("parameterControlLimits", "Parameter Control Limits"),
           a("qualifiedOperatorRequired", "Qualified Operator Required", kind="Bool",
             default=True),
           a("frozenPlanRequired", "Frozen Process Plan Required", kind="Bool",
             default=False),
           a("periodicTestRequirement", "Periodic Test Requirement"),
           a("pyrometryClass", "Pyrometry Class (AMS2750)"),
           a("recordRetentionYears", "Record Retention", kind="Number",
             unit="years"),
       ]),

    ty("SupplierQualRecord", "Supplier Qualification Record",
       "The approval position for one supplier: scope, certificates and their expiry, audit "
       "outcome and risk rating. An expiring AS9100 certificate is a data question, which is "
       "the point of holding it here rather than in a purchasing spreadsheet.",
       t("NonTypeDesignDocumentsBase"), numbering="n5LssQualityRecord",
       attributes=[
           a("supplierName", "Supplier", required=True),
           a("supplierCageCode", "Supplier CAGE Code"),
           a("approvalScope", "Approval Scope", required=True),
           a("as9100CertificateNumber", "AS9100 Certificate Number"),
           a("as9100CertificateExpiry", "AS9100 Certificate Expiry", kind="Date"),
           a("nadcapScopes", "NADCAP Accredited Scopes"),
           a("auditDate", "Last Audit", kind="Date"),
           a("auditType", "Audit Type",
             lov=["Desktop assessment", "On-site initial", "On-site surveillance",
                  "For-cause", "Delegated"]),
           a("auditResult", "Audit Result",
             lov=["Satisfactory", "Satisfactory with observations",
                  "Minor findings", "Major findings", "Unsatisfactory"]),
           a("openFindingCount", "Open Findings", kind="Number"),
           a("nextAuditDue", "Next Audit Due", kind="Date"),
           a("riskRating", "Risk Rating", lov=["Low", "Medium", "High", "Critical"],
             default="Medium"),
           a("approvalStatus", "Approval Status",
             lov=["Approved", "Approved - conditional", "Probation", "Suspended",
                  "Removed", "Under assessment"], required=True,
             default="Under assessment"),
           a("flowdownAccepted", "Requirement Flowdown Accepted", kind="Bool",
             default=False),
           a("deliveredQualityPpm", "Delivered Quality", kind="Number", unit="ppm"),
           a("onTimeDeliveryPercent", "On Time Delivery", kind="Number", unit="%"),
       ]),
]

# ─────────────────────────────────────────────────────────────────────────────
# Concrete requirement types
# ─────────────────────────────────────────────────────────────────────────────
# The out-of-the-box requirement levels - MissionRequirement, StakeholderRequirement,
# SystemRequirement, SubsystemRequirement and ComponentRequirement - are all ABSTRACT, so
# no object can be created against them. A site that wants a requirements tree has to
# declare its own concrete type at each level, which is what these six do.
#
# They are siblings on five unrelated branches of the out-of-the-box tree, so there is no
# single ancestor the shared aviation attributes could live on. REQ_AVIATION_ATTRS is
# therefore defined once here and referenced by each type: one definition in the source,
# even though the generated JSON repeats it. RequirementsBase already carries the
# substantial shared set - priority, rationale, source, acceptanceCriteria, body,
# requirementType, verificationMethod, safetyDAL and regulatoryReference - so what is added
# here is only what that set is missing for a certification programme.

REQ_AVIATION_ATTRS = [
    # A requirement's branch of the out-of-the-box tree never passes through
    # n5LightSpeedSystemsItemBase, so the programme has to be declared here. Without it a
    # requirement cannot be filtered by programme, which is the first thing anyone does.
    a("programmeCode", "Programme", required=True, lov=PROGRAMMES, default="NX-200"),
    a("ataChapter", "ATA Chapter", lov=ATA_ALL),
    a("requirementOwner", "Requirement Owner"),
    a("allocationStatus", "Allocation Status",
      lov=["Not allocated", "Allocated", "Partially allocated",
           "Over-allocated", "Allocation not required"],
      default="Not allocated"),
    a("verificationStatus", "Verification Status",
      lov=["Not verified", "Verification planned", "In verification",
           "Verified", "Verification failed", "Verification waived"],
      default="Not verified"),
    a("verificationEvidenceRef", "Verification Evidence"),
    a("certificationCredit", "Claimed for Certification Credit", kind="Bool",
      default=False),
    a("complianceItemRef", "Compliance Item Reference"),
    # ARP4754A calls a requirement that does not trace up to a higher-level requirement a
    # derived requirement, and requires it to be fed back into the safety assessment. A
    # flag rather than an inference, so the set can be listed and reviewed.
    a("derivedRequirement", "Derived Requirement (ARP4754A)", kind="Bool",
      default=False),
    a("safetyAssessmentRef", "Safety Assessment Reference"),
    a("volatilityRisk", "Volatility Risk",
      lov=["Stable", "Likely to change", "Under negotiation",
           "Awaiting authority position"], default="Stable"),
]

REQ_LIFECYCLE = states([
    ("Draft",       "#607080"),
    ("In Review",   "#4A6FA5"),
    ("Approved",    "#2E8B57"),
    ("Implemented", "#6A5ACD"),
    ("Verified",    "#2F6F4F"),
    ("Rejected",    "#8B2828"),
])

CONCRETE_REQ_TYPES = [
    ty("AircraftRequirement", "Aircraft Requirement",
       "A top-level aircraft requirement for the NX-200 - range, cabin altitude, noise, "
       "field length. The root of the trace tree; everything else is allocated down from "
       "here.",
       "MissionRequirement", numbering="n5LssRequirement", lifecycle=REQ_LIFECYCLE,
       attributes=REQ_AVIATION_ATTRS + [
           a("designMissionProfile", "Design Mission Profile"),
           a("performanceTarget", "Performance Target"),
           a("marketDriver", "Market Driver"),
       ]),

    ty("OperatorRequirement", "Operator Requirement",
       "A need expressed by a launch operator, completion centre or the certification "
       "authority. Held separately from aircraft requirements so a negotiated customer "
       "wish is never mistaken for a design commitment.",
       "StakeholderRequirement", numbering="n5LssRequirement", lifecycle=REQ_LIFECYCLE,
       attributes=REQ_AVIATION_ATTRS + [
           a("operatorName", "Operator / Stakeholder"),
           a("fleetSize", "Fleet Size", kind="Number"),
           a("contractualCommitment", "Contractual Commitment", kind="Bool",
             default=False),
           a("negotiationStatus", "Negotiation Status",
             lov=["Proposed", "Under negotiation", "Agreed", "Declined",
                  "Deferred to growth variant"], default="Proposed"),
       ]),

    ty("SystemRequirement", "System Requirement",
       "A requirement on one ATA system - the environmental control system, the "
       "communications system, the furnishings. Allocated down from aircraft level and the "
       "level at which a functional hazard assessment is normally performed.",
       "SystemRequirement", numbering="n5LssRequirement", lifecycle=REQ_LIFECYCLE,
       attributes=REQ_AVIATION_ATTRS + [
           a("systemName", "System Name"),
           a("functionalHazardRef", "Functional Hazard Assessment Reference"),
           a("failureEffectClassification", "Failure Effect (ARP4754A)",
             lov=FAILURE_EFFECT),
           a("redundancyRequirement", "Redundancy Requirement",
             lov=["None", "Dual independent", "Dual dissimilar",
                  "Triple", "Fail-operational", "Fail-safe"], default="None"),
       ]),

    ty("SubsystemRequirement", "Subsystem Requirement",
       "A requirement on a subsystem inside an ATA system, such as the pressurisation "
       "control subsystem within ATA 21 or audio integrating within ATA 23.",
       "SubsystemRequirement", numbering="n5LssRequirement", lifecycle=REQ_LIFECYCLE,
       attributes=REQ_AVIATION_ATTRS + [
           a("subsystemLabel", "Subsystem"),
           a("ataSubject", "ATA Subject"),
           a("interfaceDocumentRef", "Interface Control Document"),
       ]),

    ty("ComponentRequirement", "Component Requirement",
       "A requirement on one item of equipment. This is the level that becomes a "
       "procurement specification for a bought item or a design specification for a part "
       "Light Speed Systems makes.",
       "ComponentRequirement", numbering="n5LssRequirement", lifecycle=REQ_LIFECYCLE,
       attributes=REQ_AVIATION_ATTRS + [
           a("componentLabel", "Component"),
           a("targetPartNumber", "Implementing Part Number"),
           a("do160CategoryRequired", "DO-160 Category Required"),
           a("supplierFlowdown", "Flowed Down to Supplier", kind="Bool",
             default=False),
           a("procurementSpecRef", "Procurement Specification"),
       ]),

    ty("CertRequirement", "Certification Requirement",
       "A requirement that comes straight from the certification basis - a CS-23 paragraph, "
       "a special condition or an equivalent safety finding. Kept as a requirement rather "
       "than only as a compliance item so the design can be traced to the rule it exists to "
       "satisfy, and so a rule change shows up as a suspect trace link.",
       "SystemRequirement", numbering="n5LssRequirement", lifecycle=REQ_LIFECYCLE,
       attributes=REQ_AVIATION_ATTRS + [
           a("regulationParagraph", "Regulation Paragraph", required=True),
           a("certificationBasis", "Certification Basis", lov=CERT_BASIS),
           a("consensusStandardRef", "Consensus Standard (ASTM F44)"),
           a("meansOfCompliance", "Planned Means of Compliance",
             lov=MEANS_OF_COMPLIANCE),
           a("specialCondition", "Special Condition", kind="Bool", default=False),
           a("equivalentSafetyFinding", "Equivalent Safety Finding", kind="Bool",
             default=False),
       ]),
]

ALL_TYPES = (ABSTRACT_TYPES + CONCRETE_ITEM_TYPES + CONCRETE_DOC_TYPES
             + CONCRETE_REQ_TYPES)
