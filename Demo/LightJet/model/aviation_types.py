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
    PREFIX,
    AIRWORTHINESS_CLASS, AS9100D_CLAUSES, ATA_CHAPTERS_IN_SCOPE, CERTIFICATE_STATES,
    CERT_BASIS, COMPLIANCE_STATES, CONFIDENTIALITY, DAL, DO160_SECTIONS, EXPORT_CLASS,
    EXPORT_JURISDICTION, FAILURE_EFFECT, MEANS_OF_COMPLIANCE, NADCAP_FAMILIES,
    PUBLICATION_STATES, QUALITY_STATES, RETENTION, SUPPORT_STATES, TYPE_DESIGN_STATES,
    WF_CERTIFICATE_ISSUE, WF_COMPLIANCE, WF_CONCESSION, WF_CORRECTIVE_ACTION,
    WF_FAI, WF_FINDING, WF_MRB,
    WF_PROCESS_SPEC, WF_PUBLICATION, WF_SUBSTANTIATION, WF_SUPPLIER, WF_TYPE_DESIGN,
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
    a("priority", "Priority",
      lov=["Critical", "High", "Medium", "Low"], default="Medium"),
    # Who has the ball now, as opposed to who owns the design. A drawing in stress review
    # is still owned by its designer but is held by a stress engineer, and a board that
    # cannot show that is a board nobody trusts.
    a("assignee", "Currently With"),
    # A kanban card takes its headline from a `title` attribute; without one every
    # card on every board reads as its part number. ChangeBase and RequirementsBase
    # already declare one out of the box, so only the item and document trees need
    # it - and a title is worth having in the grids and in search regardless.
    a("title", "Title"),
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
    # A life limit in flight hours alone cannot administer a mandatory ALS limit, and the
    # ones that bite in service are usually calendar: a hose, a seal, a pyrotechnic or a
    # battery goes out on elapsed time whatever the aeroplane has flown. With only hours,
    # lifeLimitHours=0 was the whole life statement on a life-limited part, and "when is
    # this due" had no answer (NI-00000522). The datum matters as much as the number -
    # a limit measured from manufacture expires in the stores; one measured from
    # installation does not.
    a("lifeLimitMonths", "Calendar Life Limit", kind="Number", unit="months"),
    a("lifeLimitDatum", "Life Limit Measured From",
      lov=["Date of manufacture", "Date of installation", "Date of overhaul",
           "Date of first use", "Not applicable"],
      default="Not applicable"),
    a("lifeLimitSource", "Life Limit Source",
      lov=["Airworthiness limitations section (mandatory)",
           "Certification maintenance requirement", "Manufacturer recommendation",
           "Supplier component maintenance manual", "Not established"],
      default="Not established"),
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
    a("programmeCode", "Programme", lov=PROGRAMMES, default="NX-200"),
    # Which chapter the document belongs to. An item carries this through the item base;
    # a document had no equivalent, which meant the compliance board could not be filtered
    # by system - the first thing a chief engineer asks it to do.
    a("ataChapter", "ATA Chapter", lov=ATA_ALL),
    a("priority", "Priority",
      lov=["Critical", "High", "Medium", "Low"], default="Medium"),
    # Who has the ball now, as opposed to who owns the design. A drawing in stress review
    # is still owned by its designer but is held by a stress engineer, and a board that
    # cannot show that is a board nobody trusts.
    a("assignee", "Currently With"),
    # A kanban card takes its headline from a `title` attribute; without one every
    # card on every board reads as its part number. ChangeBase and RequirementsBase
    # already declare one out of the box, so only the item and document trees need
    # it - and a title is worth having in the grids and in search regardless.
    a("title", "Title"),
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
    # How the record closed, in one phrase. Derived from the field that already holds the
    # outcome - the MRB disposition, the first article result, the approval status - so
    # the board can show it without anyone keeping two fields in step by hand.
    a("resolution", "Outcome"),
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
       t("EngBase"), numbering=f"{PREFIX}LssAircraftPart", actions=[RELEASE_ACTION],
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
       t("EngBase"), numbering=f"{PREFIX}LssElectricalPart", actions=[RELEASE_ACTION],
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
       t("EngBase"), numbering=f"{PREFIX}LssInteriorPart", actions=[RELEASE_ACTION],
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
       t("EngBase"), numbering=f"{PREFIX}LssInstallation", actions=[RELEASE_ACTION],
       attributes=[
           a("installationZone", "Aircraft Zone"),
           a("systemInstalled", "System Installed"),
           a("torqueSpecificationRef", "Torque Specification"),
           a("sealantSpecification", "Sealant Specification"),
           a("riggingProcedureRef", "Rigging / Adjustment Procedure"),
           a("accessPanelRefs", "Access Panels"),
           a("clearanceRequirementMm", "Minimum Clearance", kind="Number", unit="mm"),
           a("installationManHours", "Installation Time", kind="Number", unit="h"),
           # A material carries maxServiceTemperature; nothing carried the temperature of
           # the PLACE it is used, so the limit could never be checked against anything -
           # a sealant qualified to 120 C in a bay that runs at 180 C would look perfectly
           # correct in the data (NI-00000535). The bay, not the part, is what has an
           # environment, which is why this sits on the installation.
           a("operatingTemperatureMinC", "Operating Temperature - Minimum",
             kind="Number", unit="C"),
           a("operatingTemperatureMaxC", "Operating Temperature - Maximum",
             kind="Number", unit="C"),
           a("thermalEnvironmentBasis", "Thermal Environment Basis",
             lov=["Measured in ground test", "Measured in flight test", "Analysis",
                  "Specification requirement", "Not established"],
             default="Not established"),
           a("fluidExposure", "Fluid Exposure"),
           a("vibrationZone", "Vibration Zone (DO-160G)"),
       ]),

    ty("Harness", "Wiring Harness",
       "A wiring harness or loom. Separation category and route zone are held because EWIS "
       "substantiation depends on them, not on the wire list alone.",
       t("EngBase"), numbering=f"{PREFIX}LssHarness", actions=[RELEASE_ACTION],
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
       t("TypeDesignItemBase"), numbering=f"{PREFIX}LssStandardPart",
       actions=[action("RequestApprovalForUse", "Request approval for use",
                       "Starts the source approval route, which is the right shape "
                       "for a catalogue part: supply chain confirms the source and "
                       "obsolescence position, quality the AS9100D 8.4 controls and "
                       "counterfeit safeguards, and engineering accepts it "
                       "technically for use on the programme. Released previously "
                       "had no route at all.",
                       WF_SUPPLIER, ["In Work", "In Design Review"])],
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
       t("TypeDesignItemBase"), numbering=f"{PREFIX}LssVendorPart",
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
       t("TypeDesignItemBase"), numbering=f"{PREFIX}LssSoftwareItem", actions=[RELEASE_ACTION],
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
       t("TypeDesignItemBase"), numbering=f"{PREFIX}LssAehItem", actions=[RELEASE_ACTION],
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

    ty("Aircraft", "Aircraft",
       "One individual aeroplane, by manufacturer serial number. The type design says "
       "what an NX-200 is; this says what THIS one is - which revision of each "
       "installation it left the factory with, who operates it, how many hours it has "
       "flown and which bulletins are outstanding against it. "
       "It is not type design data: revising an aircraft record does not touch the type "
       "certificate. Its as-built structure is ordinary bill-of-materials links PINNED "
       "to the revision actually fitted, because an as-built that follows the latest "
       "drawing answers the one question it must never answer.",
       t("NonTypeDesignItemBase"), numbering=f"{PREFIX}LssAircraft",
       attributes=[
           a("manufacturerSerialNumber", "Manufacturer Serial Number", required=True),
           a("registration", "Registration"),
           a("operator", "Operator"),
           a("deliveryDate", "Delivery Date", kind="Date"),
           a("aircraftStatus", "Status",
             lov=["In build", "Flight test - experimental", "In service",
                  "In maintenance", "Stored", "Withdrawn from use", "Written off"],
             required=True, default="In build"),
           a("certificationStatus", "Certification Status",
             lov=["Not type certificated; permit to fly",
                  "Permit to fly pending type certificate",
                  "Certificate of airworthiness", "Restricted certificate"],
             default="Not type certificated; permit to fly"),
           a("buildStandard", "Build Standard"),
           a("baseLocation", "Base"),
           a("totalFlightHours", "Total Flight Hours", kind="Number", unit="FH"),
           a("totalCycles", "Total Cycles", kind="Number", unit="FC"),
           a("lastInspectionDate", "Last Inspection", kind="Date"),
           # Free text for now, and deliberately so: there is no bulletin-compliance
           # record in the product, which the customer support role reported as a
           # Critical gap. This field is the workaround, not the answer.
           a("openBulletins", "Outstanding Service Bulletins"),
       ]),

    ty("Tooling", "Tooling and Ground Support Equipment",
       "Production tooling, inspection fixtures, test rigs and ground support equipment. Not "
       "type design data, but a check fixture whose calibration has lapsed invalidates the "
       "inspection records taken with it, so calibration status is held as data and not in a "
       "spreadsheet.",
       t("NonTypeDesignItemBase"), numbering=f"{PREFIX}LssTooling",
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
       t("NonTypeDesignItemBase"), numbering=f"{PREFIX}LssConsumable",
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
           # The service limits lived only on the linked Material, and the record a
           # mechanic or a process engineer actually reaches for at the point of
           # application is this one - so the limit was one hop away from every question
           # that needed it, and the reporter raised it twice (NI-00000535, NI-00000749).
           # Holding it here is duplication on purpose: the consumable is a specific
           # product with its own qualified range, which is not always the whole range of
           # the material family it belongs to.
           a("serviceTemperatureMinC", "Service Temperature - Minimum",
             kind="Number", unit="C"),
           a("serviceTemperatureMaxC", "Service Temperature - Maximum",
             kind="Number", unit="C"),
           a("intermittentTemperatureMaxC", "Intermittent Temperature - Maximum",
             kind="Number", unit="C"),
           a("serviceLimitSource", "Service Limit Source",
             lov=["Manufacturer data sheet", "Governing specification",
                  "Programme qualification test", "Not established"],
             default="Not established"),
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
       t("TypeDesignDocumentsBase"), numbering=f"{PREFIX}LssDrawing",
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
       t("TypeDesignDocumentsBase"), numbering=f"{PREFIX}LssSpecification",
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
       t("TypeDesignDocumentsBase"), numbering=f"{PREFIX}LssInterfaceControl",
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
       t("TypeDesignDocumentsBase"), numbering=f"{PREFIX}LssCertificationDoc",
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
       t("TypeDesignDocumentsBase"), numbering=f"{PREFIX}LssCertificationDoc",
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
       t("TypeDesignDocumentsBase"), numbering=f"{PREFIX}LssCertificationDoc",
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
       t("TypeDesignDocumentsBase"), numbering=f"{PREFIX}LssCertificationDoc",
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
       t("TypeDesignDocumentsBase"), numbering=f"{PREFIX}LssCertificationDoc",
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
       t("TypeDesignDocumentsBase"), numbering=f"{PREFIX}LssCertificationDoc",
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
       t("TypeDesignDocumentsBase"), numbering=f"{PREFIX}LssCertificationDoc",
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
       t("NonTypeDesignDocumentsBase"), numbering=f"{PREFIX}LssQualityRecord",
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
           # A DELTA first article re-verifies only what the change touched, so "6
           # characteristics" says nothing about whether the right six were done. AS9102
           # numbers every characteristic on the ballooned drawing, and the delta's scope
           # is a list of those numbers - without it the report cannot be audited against
           # the change that triggered it (NI-00000521).
           a("deltaScope", "Delta Scope - Characteristics Covered"),
           a("deltaScopeBasis", "Delta Scope Basis",
             lov=["Change order affected characteristics", "Supplier change notice",
                  "Process change", "Tooling change", "Full FAI - not a delta"],
             default="Full FAI - not a delta"),
           a("balloonedDrawingRevision", "Ballooned Drawing Revision"),
           # Who signed it off, which is the field a first article is worthless without -
           # dispositionAuthority existed on the nonconformance and nothing equivalent
           # here (NI-00000581).
           a("faiApprovedBy", "First Article Approved By"),
           a("faiApprovalDate", "First Article Approval Date", kind="Date"),
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
       t("NonTypeDesignDocumentsBase"), numbering=f"{PREFIX}LssQualityRecord",
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
           # Every value was a production or handling defect, so a condition that
           # DEVELOPED in service on hardware that conformed when it was built had no
           # value that fits: the reporter recorded "Material" and explained the truth in
           # prose (NI-00000729). That matters more than tidiness - `detectedAt` already
           # offers "In service", so the two fields could not agree, and a fleet-wide
           # query for corrosion findings returned nothing. In-service deterioration is
           # also the category that feeds continued airworthiness rather than the
           # production MRB, so collapsing it into "Material" hides the one class of
           # nonconformance that can generate an airworthiness directive.
           a("nonconformanceType", "Nonconformance Type",
             lov=["Dimensional", "Material", "Special process", "Documentation",
                  "Handling damage", "Missing operation", "Foreign object debris",
                  "Software", "Wrong configuration fitted",
                  "Suspect unapproved part",
                  "Corrosion", "Fatigue cracking", "Wear beyond limits",
                  "Environmental degradation", "Accidental damage in service",
                  "Measurement system"], required=True),
           a("containmentAction", "Containment Action"),
           # Eight values, all of them about hardware. A documentation or
           # measurement-system nonconformance has nothing wrong with the PART, so none of
           # them could be chosen truthfully and the decision went into free text
           # (NI-00000538). Note which ones these are: re-inspecting to a corrected record
           # and voiding measurements taken on an out-of-calibration gauge are the two
           # dispositions an AS9100 audit asks to see, because they are what you do when
           # the product is fine and the evidence is not.
           #
           # The interim/terminal split is from the same family (NI-00000713): "contained,
           # not yet dispositioned" is a real and reportable position, and recording it as
           # "Awaiting disposition" loses the fact that containment has happened.
           a("mrbDisposition", "MRB Disposition",
             lov=["Use as is", "Rework to drawing", "Repair to approved scheme",
                  "Scrap", "Return to supplier", "Deviation - this build only",
                  "Waiver - already delivered",
                  "Re-inspect to corrected documentation",
                  "Re-verify with calibrated equipment",
                  "Void affected measurement records",
                  "Correct the record - no product impact",
                  "Contained - interim, pending disposition",
                  "Awaiting disposition"],
             default="Awaiting disposition"),
           a("interimDisposition", "Interim Disposition",
             lov=["None", "Quarantined", "Released under concession",
                  "Held pending engineering", "Held pending customer"],
             default="None"),
           a("dispositionAuthority", "Disposition Authority",
             lov=["Material review board", "DOA engineering signatory",
                  "Customer", "Airworthiness authority", "Supplier"],
             default="Material review board"),
           # Who was in the room, who concurred, and on what basis. dispositionAuthority
           # named an institution; an audit asks for people and a rationale, and both were
           # free text or absent (NI-00000581). Airworthiness concurrence is called out
           # separately because this site's own rule requires it for any disposition other
           # than scrap or return to supplier.
           a("mrbMembers", "Material Review Board Members"),
           a("mrbChair", "Board Chair"),
           a("dispositionBasis", "Basis for the Disposition"),
           a("airworthinessConcurrenceBy", "Airworthiness Concurrence By"),
           a("airworthinessConcurrenceDate", "Airworthiness Concurrence Date",
             kind="Date"),
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
       t("NonTypeDesignDocumentsBase"), numbering=f"{PREFIX}LssQualityRecord",
       lifecycle=states(CERTIFICATE_STATES),
       actions=[action("SubmitForIssue", "Submit for issue",
                       "Starts the certificate issue route: quality verifies the "
                       "certificate against the purchase order and its flowed-down "
                       "requirements, then an authorised signatory signs it. Both "
                       "this type and the airworthiness release had an Issued state "
                       "only a signatory could enter and no action to reach it, so "
                       "the only way to issue the one document whose purpose is to "
                       "carry a signature was a bare status change.",
                       WF_CERTIFICATE_ISSUE, ["Draft"])],
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
       t("NonTypeDesignDocumentsBase"), numbering=f"{PREFIX}LssQualityRecord",
       lifecycle=states(CERTIFICATE_STATES),
       actions=[action("SubmitForIssue", "Submit for issue",
                       "Starts the certificate issue route: quality verifies the "
                       "certificate against the purchase order and its flowed-down "
                       "requirements, then an authorised signatory signs it. Both "
                       "this type and the airworthiness release had an Issued state "
                       "only a signatory could enter and no action to reach it, so "
                       "the only way to issue the one document whose purpose is to "
                       "carry a signature was a bare status change.",
                       WF_CERTIFICATE_ISSUE, ["Draft"])],
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
       t("NonTypeDesignDocumentsBase"), numbering=f"{PREFIX}LssServiceBulletin",
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
       t("NonTypeDesignDocumentsBase"), numbering=f"{PREFIX}LssProcessSpec",
       lifecycle=states(TYPE_DESIGN_STATES),
       # This type had NO workflow bound, so every declared action answered 422
       # no_workflow_bound and the object was frozen: a manufacturing engineer could
       # neither submit it for approval nor revise it, and release was a bare status flip
       # with no approver and no trail (NI-00000567, NI-00000689).
       actions=[action("SubmitForApproval", "Submit for approval",
                       "Starts the special process approval route: the process owner and "
                       "quality in parallel, then an airworthiness signatory. A special "
                       "process cannot be verified by inspecting the part afterwards, so "
                       "the approved parameters are the evidence of conformity and who "
                       "approved them is the record.",
                       WF_PROCESS_SPEC,
                       ["In Work", "In Design Review", "In Stress Review",
                        "Airworthiness Sign-off"])],
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
       t("NonTypeDesignDocumentsBase"), numbering=f"{PREFIX}LssQualityRecord",
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
       "MissionRequirement", numbering=f"{PREFIX}LssRequirement", lifecycle=REQ_LIFECYCLE,
       attributes=REQ_AVIATION_ATTRS + [
           a("designMissionProfile", "Design Mission Profile"),
           a("performanceTarget", "Performance Target"),
           a("marketDriver", "Market Driver"),
       ]),

    ty("OperatorRequirement", "Operator Requirement",
       "A need expressed by a launch operator, completion centre or the certification "
       "authority. Held separately from aircraft requirements so a negotiated customer "
       "wish is never mistaken for a design commitment.",
       "StakeholderRequirement", numbering=f"{PREFIX}LssRequirement", lifecycle=REQ_LIFECYCLE,
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
       "SystemRequirement", numbering=f"{PREFIX}LssRequirement", lifecycle=REQ_LIFECYCLE,
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
       "SubsystemRequirement", numbering=f"{PREFIX}LssRequirement", lifecycle=REQ_LIFECYCLE,
       attributes=REQ_AVIATION_ATTRS + [
           a("subsystemLabel", "Subsystem"),
           a("ataSubject", "ATA Subject"),
           a("interfaceDocumentRef", "Interface Control Document"),
       ]),

    ty("ComponentRequirement", "Component Requirement",
       "A requirement on one item of equipment. This is the level that becomes a "
       "procurement specification for a bought item or a design specification for a part "
       "Light Speed Systems makes.",
       "ComponentRequirement", numbering=f"{PREFIX}LssRequirement", lifecycle=REQ_LIFECYCLE,
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
       "SystemRequirement", numbering=f"{PREFIX}LssRequirement", lifecycle=REQ_LIFECYCLE,
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

# ─────────────────────────────────────────────────────────────────────────────
# Material
# ─────────────────────────────────────────────────────────────────────────────
# MaterialBase ships out of the box and is abstract, and it already carries the whole
# mechanical and thermal property set. What it does not carry is the half that decides
# whether a material may be used on a certified aeroplane at all: the statistical basis
# of its allowables, whether it is qualified for THIS programme, and the storage and
# out-time controls that make a composite part conform or not.

MATERIAL_BASE_ATTRS = [
    a("programmeCode", "Programme", lov=PROGRAMMES, default="NX-200"),
    # The list had no value a two-part paste sealant fits, so both sealant records were
    # coded "Film adhesive" - a structural bondline material, which is not what a fillet
    # sealant is, and a materials engineer reading the record would draw the wrong
    # conclusion about where it may be used (NI-00000690). A closed list that forces a
    # wrong value is worse than a free-text field, because the wrong value looks
    # authoritative and is queryable.
    a("materialForm", "Form",
      lov=["Plate", "Sheet", "Bar", "Tube", "Extrusion", "Forging", "Casting",
           "Prepreg", "Core", "Film adhesive", "Paste adhesive", "Sealant",
           "Potting compound", "Primer", "Coating", "Wire"]),
    # The single most consequential field here. A-basis is the value 99 percent of the
    # population exceeds with 95 percent confidence and is required for a single load
    # path; B-basis is 90/95 and is permitted where failure would transfer load to
    # another member; S-basis is the specification minimum with no statistical basis at
    # all. "Typical" is not a design allowable, and a part substantiated against typical
    # values is not substantiated.
    a("allowablesBasis", "Allowables Basis",
      lov=["A-basis", "B-basis", "S-basis", "Typical values only", "Not established"],
      required=True, default="Not established"),
    a("allowablesSource", "Allowables Source"),
    a("qualificationStatus", "Qualification Status",
      lov=["Qualified", "Under qualification", "Not qualified",
           "Qualification lapsed", "Obsolete"], required=True,
      default="Not qualified"),
    a("governingSpecification", "Governing Specification"),
    a("procurementSpecification", "Procurement Specification"),
    a("approvedSources", "Approved Sources"),
    # The supply-chain position of a material, which was free text in `approvedSources`
    # and in the object notes - so "is this material at risk" could only be answered by
    # reading prose, one record at a time (NI-00000688). On a certified aeroplane these
    # are not commercial niceties: a material going obsolete is a certification problem,
    # because the substitute has to be re-qualified and the substantiation re-run.
    a("sourceApprovalStatus", "Source Approval Status",
      lov=["Sole source", "Single source approved", "Dual source approved",
           "Multiple sources approved", "Source approval pending", "No approved source"],
      default="Source approval pending"),
    a("obsolescenceStatus", "Obsolescence Status",
      lov=["Active", "Last-time-buy announced", "Discontinued - stock held",
           "Discontinued - no stock", "Substitute qualified"],
      default="Active"),
    a("leadTimeWeeks", "Procurement Lead Time", kind="Number", unit="weeks"),
    # DFARS/AS5553 counterfeit-avoidance posture. A high-risk material bought outside the
    # franchised chain needs incoming test, which is a quality requirement rather than a
    # purchasing preference.
    a("counterfeitRiskLevel", "Counterfeit Risk",
      lov=["Low - franchised source", "Medium - authorised distributor",
           "High - open market", "Not assessed"],
      default="Not assessed"),
    a("nadcapProcessRequired", "NADCAP Accredited Processing Required", kind="Bool",
      default=False),
    a("weldable", "Weldable", kind="Bool", default=False),
    a("corrosionResistance", "Corrosion Behaviour"),
    a("flammabilityRating", "Flammability Rating"),
    a("restrictedSubstances", "Restricted Substances (REACH / RoHS)"),
    a("shelfLifeMonths", "Shelf Life", kind="Number", unit="months"),
    a("storageRequirement", "Storage and Out-Time Requirement"),
    a("batchTraceabilityRequired", "Batch Traceability Required", kind="Bool",
      default=True),
]

ABSTRACT_MATERIAL_BASE = ty(
    "MaterialBase", "Light Speed Systems Material Base",
    "Abstract base for every material qualified, or being qualified, for the NX-200. "
    "The out-of-the-box MaterialBase already carries the mechanical and thermal property "
    "set; what it does not carry is the half that decides whether a material may be used "
    "on a certified aeroplane at all - the statistical basis of its allowables, whether "
    "it is qualified for THIS programme, and the storage and out-time controls that make "
    "a composite part conform or not. Those live here so that a later split into metals, "
    "composites and consumables shares them rather than repeating them.",
    "MaterialBase", abstract=True, attributes=MATERIAL_BASE_ATTRS,
    lifecycle=states(TYPE_DESIGN_STATES))

CONCRETE_MATERIAL_TYPES = [
    ty("Material", "Material",
       "A material qualified, or being qualified, for the NX-200. Holding materials as "
       "objects rather than as text on a part is what lets the questions be asked: which "
       "parts use a material whose qualification lapsed, what the stress case's allowables "
       "basis actually was, and what a restricted-substance change would touch.",
       t("MaterialBase"), numbering=f"{PREFIX}LssMaterial",
       actions=[RELEASE_ACTION],
       attributes=[]),
]

# ─────────────────────────────────────────────────────────────────────────────
# The records the exercise found nowhere to put
# ─────────────────────────────────────────────────────────────────────────────
# Eleven roles, between them, reported the same shape of problem twenty times: a real
# record of a real decision had nowhere to live, so it survived as prose in a notes field.
# Prose is not the complaint - unverifiable prose is. A disposition in free text cannot be
# queried, cannot be counted, cannot be shown to an auditor as a population, and cannot be
# made to expire.
#
# Each type below is one of those records. None of them is speculative: every one was asked
# for by name, with the question it would answer.

CONCRETE_RECORD_TYPES = [
    # ── Structural substantiation ────────────────────────────────────────────
    ty("StructuralSubstantiation", "Structural Substantiation",
       "The analysis that shows a part or installation meets its strength, fatigue and "
       "damage-tolerance requirements. The stress role had nowhere to record one at all - "
       "no stress fields on the item type, no analysis-report type, nothing to reference - "
       "so the substantiation behind a released part existed only as free text that nobody "
       "could check (NI-00000577, NI-00000727). Under CS-23 this IS the compliance "
       "evidence for the structural paragraphs, which makes it the single most "
       "consequential document a stress engineer produces.",
       t("TypeDesignDocumentsBase"), numbering=f"{PREFIX}LssSubstantiation",
       lifecycle=states(TYPE_DESIGN_STATES),
       actions=[action("SubmitForRelease", "Submit substantiation for release",
                       'Starts the substantiation release route: an independent stress check and design acceptance in parallel, then an airworthiness signatory. The check is separate from the review because an unchecked stress analysis is not evidence.',
                       WF_SUBSTANTIATION, ["In Work", "In Design Review", "In Stress Review", "Airworthiness Sign-off"])],
       attributes=[
           a("analysisType", "Analysis Type",
             lov=["Static strength", "Fatigue", "Damage tolerance", "Flutter and aeroelastic",
                  "Loads", "Thermal", "Mechanism / kinematic", "Crashworthiness",
                  "Bird strike", "Bonded joint"], required=True),
           a("analysisMethod", "Method",
             lov=["Classical hand analysis", "Finite element - linear",
                  "Finite element - non-linear", "Test substantiation",
                  "Test correlated analysis", "Comparative / similarity"],
             required=True),
           # The three numbers an auditor goes to first. A margin of safety below zero is
           # a failed substantiation, so holding it as data makes "is anything negative"
           # a query rather than a reading exercise.
           a("minimumMarginOfSafety", "Minimum Margin of Safety", kind="Number"),
           a("criticalLoadCase", "Critical Load Case"),
           a("criticalLocation", "Critical Location"),
           a("reserveFactor", "Reserve Factor", kind="Number"),
           a("allowablesBasisUsed", "Allowables Basis Used",
             lov=["A-basis", "B-basis", "S-basis", "Test derived", "Typical values only"],
             required=True, default="A-basis"),
           a("materialAllowablesSource", "Material Allowables Source"),
           a("loadsReportRevision", "Loads Report Revision"),
           a("modelRevision", "Analysis Model Revision"),
           a("softwareUsed", "Analysis Software and Version"),
           a("softwareQualified", "Software Qualified for this Use", kind="Bool",
             default=False),
           a("inspectionThreshold", "Inspection Threshold", kind="Number", unit="FH"),
           a("inspectionInterval", "Repeat Inspection Interval", kind="Number", unit="FH"),
           a("substantiationResult", "Result",
             lov=["Positive margins throughout", "Positive with inspection requirement",
                  "Positive with life limit", "Negative margin - redesign required",
                  "Inconclusive - further work required"],
             required=True, default="Inconclusive - further work required"),
           a("checkedBy", "Checked By"),
           a("independentCheckRequired", "Independent Check Required", kind="Bool",
             default=True),
       ]),

    # ── Quality records that were fields on something else ───────────────────
    ty("Concession", "Concession (Deviation / Waiver)",
       "Permission to depart from the approved definition, for a stated quantity or serial "
       "range and with an expiry. It was two values in the nonconformance's disposition "
       "list - 'Deviation - this build only' and 'Waiver - already delivered' - which "
       "cannot carry an effectivity, an expiry or a named approver, and conflates two "
       "different instruments (NI-00000595). A deviation is granted BEFORE manufacture and "
       "a waiver AFTER, and an open-ended concession is a finding in any audit.",
       t("NonTypeDesignDocumentsBase"), numbering=f"{PREFIX}LssQualityRecord",
       lifecycle=states(QUALITY_STATES),
       actions=[action("SubmitConcession", "Submit concession for approval",
                       'Starts the concession approval route: engineering justification and quality control of the bounds in parallel, then airworthiness concurrence. A departure from the approved design is authorised here or not at all.',
                       WF_CONCESSION, ["Open", "Under Review"])],
       attributes=[
           a("concessionType", "Concession Type",
             lov=["Deviation - before manufacture", "Waiver - after manufacture",
                  "Production permit", "Customer concession"], required=True),
           a("departureDescription", "Departure from the Approved Definition",
             required=True),
           a("justification", "Technical Justification", required=True),
           a("quantityAuthorised", "Quantity Authorised", kind="Number"),
           a("serialRangeFrom", "Serial Range From"),
           a("serialRangeTo", "Serial Range To"),
           a("expiryDate", "Expires", kind="Date"),
           a("expiryCondition", "Expiry Condition",
             lov=["Date", "Quantity exhausted", "Design change embodied",
                  "Next revision of the drawing", "No expiry - permanent"],
             required=True, default="Date"),
           a("airworthinessImpact", "Airworthiness Impact", kind="Bool", default=False),
           a("customerApprovalRequired", "Customer Approval Required", kind="Bool",
             default=False),
           a("approvedBy", "Approved By"),
           a("approvalDate", "Approval Date", kind="Date"),
           a("permanentFixRef", "Permanent Corrective Action"),
       ]),

    ty("CorrectiveAction", "Corrective Action",
       "The AS9100D corrective action behind a nonconformance: root cause, the action, who "
       "owns it, when it is due and how its effectiveness was verified. It was a single "
       "free-text reference on the nonconformance - `correctiveActionRef` - so a "
       "nonconformance could be dispositioned and closed with its corrective action "
       "pointing at nothing, and nothing anywhere said whether the action had worked "
       "(NI-00000570). Effectiveness verification is the step that distinguishes a "
       "corrective action from an intention.",
       t("NonTypeDesignDocumentsBase"), numbering=f"{PREFIX}LssQualityRecord",
       lifecycle=states(QUALITY_STATES),
       actions=[action("SubmitForClosure", "Submit for closure",
                       'Starts the corrective action closure route. Effectiveness verification is its own gate, because that is the step that gets skipped.',
                       WF_CORRECTIVE_ACTION, ["Open", "Under Review", "Dispositioned"])],
       attributes=[
           a("problemStatement", "Problem Statement", required=True),
           a("rootCauseMethod", "Root Cause Method",
             lov=["5 Why", "Ishikawa / fishbone", "Fault tree", "8D",
                  "Design of experiments", "Not yet determined"],
             required=True, default="Not yet determined"),
           a("rootCause", "Root Cause"),
           a("containmentAction", "Immediate Containment"),
           a("correctiveAction", "Corrective Action"),
           a("preventiveAction", "Preventive Action - Systemic"),
           a("actionOwner", "Action Owner", required=True),
           a("dueDate", "Due", kind="Date"),
           a("closureDate", "Closed", kind="Date"),
           a("effectivenessVerificationMethod", "Effectiveness Verified By",
             lov=["Audit", "Statistical process control", "Re-inspection of n units",
                  "Process capability study", "Elapsed time with no recurrence",
                  "Not yet verified"], required=True, default="Not yet verified"),
           a("effectivenessVerified", "Effectiveness Confirmed", kind="Bool",
             default=False),
           a("effectivenessVerifiedBy", "Verified By"),
           a("recurrenceAfterClosure", "Recurred After Closure", kind="Bool",
             default=False),
           a("systemicScope", "Systemic Scope",
             lov=["This part only", "This part family", "This process",
                  "This supplier", "Site-wide"], required=True, default="This part only"),
       ]),

    ty("InspectionRecord", "Inspection Record",
       "What was measured, on which unit, against which characteristic, with what gauge. A "
       "nonconformance could only scope itself with free-text log-number ranges, so "
       "'which units did we actually check' had no answer - and a measurement with no "
       "named gauge cannot be voided when that gauge is found out of calibration, which is "
       "precisely when you need to find every measurement it took (NI-00000531, "
       "NI-00000583).",
       t("NonTypeDesignDocumentsBase"), numbering=f"{PREFIX}LssQualityRecord",
       lifecycle=states(QUALITY_STATES),
       attributes=[
           a("inspectionType", "Inspection Type",
             lov=["Receiving", "First article", "In-process", "Final",
                  "Source inspection at supplier", "Scheduled maintenance",
                  "Unscheduled - in service", "Special - after event"], required=True),
           a("characteristicNumber", "Characteristic / Balloon Number"),
           a("characteristicDescription", "Characteristic"),
           a("nominalValue", "Nominal", kind="Number"),
           a("toleranceUpper", "Upper Tolerance", kind="Number"),
           a("toleranceLower", "Lower Tolerance", kind="Number"),
           a("measuredValue", "Measured", kind="Number"),
           a("unitOfMeasure", "Unit"),
           a("withinTolerance", "Within Tolerance", kind="Bool", default=True),
           a("gaugeIdentifier", "Gauge / Equipment Identifier"),
           a("gaugeCalibrationDueDate", "Gauge Calibration Due", kind="Date"),
           a("measurementUncertainty", "Measurement Uncertainty", kind="Number"),
           a("inspectedBy", "Inspected By"),
           a("inspectionDate", "Inspected On", kind="Date"),
           # For a trend. A measured corrosion depth means little on its own and a great
           # deal plotted against the hours the airframe had flown when it was taken.
           a("airframeHoursAtInspection", "Airframe Hours at Inspection",
             kind="Number", unit="FH"),
           a("airframeCyclesAtInspection", "Airframe Cycles at Inspection",
             kind="Number", unit="FC"),
       ]),

    # ── The physical article, as distinct from its definition ────────────────
    ty("SerialisedUnit", "Serialised Unit (As-Built)",
       "One physical article, by serial number, and the definition it was actually built "
       "to. Everything downstream of delivery needs this and nothing had it: "
       "`affectedSerialNumbers` was free text, so a nonconformance could not be scoped to "
       "real units, a deviation for product in the factory could not be raised because "
       "nothing said what was in the factory, and a life limit could not be accumulated "
       "against the unit that flew the hours (NI-00000710, NI-00000522, NI-00000713). The "
       "part tells you what it should be; this tells you what it is.",
       t("NonTypeDesignItemBase"), numbering=f"{PREFIX}LssSerialisedUnit",
       lifecycle=states(SUPPORT_STATES),
       attributes=[
           a("serialNumber", "Serial Number", required=True),
           a("builtToRevision", "Built to Revision", required=True),
           a("manufactureDate", "Manufactured", kind="Date"),
           a("manufacturingLot", "Lot / Batch"),
           a("manufacturedBy", "Manufactured By"),
           a("unitStatus", "Unit Status",
             lov=["In manufacture", "In stores", "Installed", "Removed - serviceable",
                  "Removed - unserviceable", "In repair", "Quarantined", "Scrapped"],
             required=True, default="In manufacture"),
           a("hoursSinceNew", "Hours Since New", kind="Number", unit="FH"),
           a("cyclesSinceNew", "Cycles Since New", kind="Number", unit="FC"),
           a("hoursSinceOverhaul", "Hours Since Overhaul", kind="Number", unit="FH"),
           a("installationDate", "Installed On", kind="Date"),
           a("removalDate", "Removed On", kind="Date"),
           # The computed answer the fleet role asked for. Holding it as data rather than
           # deriving it on read is deliberate: the due date has to survive the part
           # definition being revised, because the unit was built to the old one.
           a("nextDueDate", "Next Due", kind="Date"),
           a("nextDueHours", "Next Due at Hours", kind="Number", unit="FH"),
           a("lifeRemainingHours", "Life Remaining", kind="Number", unit="FH"),
           a("concessionsApplied", "Concessions Applied"),
       ]),

    # ── Continued airworthiness ──────────────────────────────────────────────
    ty("InServiceOccurrence", "In-Service Occurrence",
       "Something that happened to a delivered aeroplane. The fleet role could record an "
       "occurrence only in a notes field, against an `affectedItem` that was one "
       "free-text string, with no link to the airframe it happened on - so nothing could "
       "be counted per tail number or trended at all (NI-00000578, NI-00000583). This is "
       "also the reporting obligation: an occurrence meeting the reportable criteria has a "
       "statutory clock on it, and a record with no date and no airframe cannot evidence "
       "that the clock was met.",
       t("NonTypeDesignDocumentsBase"), numbering=f"{PREFIX}LssInServiceRecord",
       lifecycle=states(QUALITY_STATES),
       actions=[action("RaiseForReview", "Raise for review",
                       'Starts the review route for an in-service occurrence: the discipline whose system misbehaved assesses it, then airworthiness decides whether it is fleet-wide.',
                       WF_FINDING, ["Open", "Under Review"])],
       attributes=[
           a("occurrenceType", "Occurrence Type",
             lov=["Pilot report", "Maintenance finding", "Component failure",
                  "System malfunction", "Structural finding", "Incident",
                  "Accident", "Ground damage", "Operational interruption"],
             required=True),
           a("occurrenceDate", "Occurred On", kind="Date", required=True),
           a("flightPhase", "Flight Phase",
             lov=["Ground", "Taxi", "Take-off", "Climb", "Cruise", "Descent",
                  "Approach", "Landing", "Not applicable"], default="Not applicable"),
           a("occurrenceDescription", "What Happened", required=True),
           a("operatorReference", "Operator's Reference"),
           a("airframeHoursAtOccurrence", "Airframe Hours", kind="Number", unit="FH"),
           a("airframeCyclesAtOccurrence", "Airframe Cycles", kind="Number", unit="FC"),
           a("operationalEffect", "Operational Effect",
             lov=["None", "Deferred defect", "Delay", "Cancellation",
                  "Air turnback", "Diversion", "Aircraft on ground"],
             default="None"),
           a("safetyEffect", "Safety Effect (ARP4761A)", lov=FAILURE_EFFECT),
           a("reportableToAuthority", "Reportable to the Authority", kind="Bool",
             default=False),
           a("reportedToAuthorityDate", "Reported On", kind="Date"),
           a("authorityReference", "Authority Reference"),
           a("fleetWideRisk", "Fleet-Wide Risk Assessed", kind="Bool", default=False),
           a("immediateAction", "Immediate Action Taken"),
       ]),

    ty("OperatorComplianceRecord", "Operator Compliance Record",
       "An operator's return confirming a service bulletin has been embodied on a given "
       "airframe. On a Mandatory bulletin facing a proposed airworthiness directive there "
       "was no way to record compliance at all, so the one question the regulator asks - "
       "how much of the fleet has complied - could not be answered (NI-00000558). "
       "`openBulletins` on the aircraft was the only trace and it is a free-text count.",
       t("NonTypeDesignDocumentsBase"), numbering=f"{PREFIX}LssInServiceRecord",
       lifecycle=states(QUALITY_STATES),
       attributes=[
           a("bulletinReference", "Service Bulletin", required=True),
           a("complianceStatus", "Compliance Status",
             lov=["Not yet due", "Due", "Overdue", "Embodied", "Not applicable",
                  "Alternative means approved", "Extension granted"],
             required=True, default="Not yet due"),
           a("complianceDueDate", "Compliance Due", kind="Date"),
           a("complianceDueHours", "Compliance Due at Hours", kind="Number", unit="FH"),
           a("embodimentDate", "Embodied On", kind="Date"),
           a("embodiedBy", "Embodied By (Organisation)"),
           a("embodimentHours", "Airframe Hours at Embodiment", kind="Number", unit="FH"),
           a("partsFittedRevision", "Part Revision Fitted"),
           a("operatorName", "Operator", required=True),
           a("alternativeMeansReference", "Alternative Means of Compliance Reference"),
           a("evidenceReference", "Evidence of Embodiment"),
       ]),

    # ── Publications: the end of the line for a limitation ───────────────────
    ty("AirworthinessLimitation", "Airworthiness Limitation",
       "A limitation that has to reach the people operating and maintaining the aeroplane: "
       "an ALS item, a certification maintenance requirement, a flight manual limitation. "
       "A substantiation that is positive only WITH an inspection, and a compliance "
       "demonstration accepted only with a limitation, both end here - and there was no "
       "publication object of any kind, so a limitation could be agreed with the authority "
       "and never reach a crew (NI-00000532, NI-00000576).",
       t("NonTypeDesignDocumentsBase"), numbering=f"{PREFIX}LssPublication",
       lifecycle=states(PUBLICATION_STATES),
       actions=[action("SubmitForIssue", "Submit for issue",
                       'Starts the publication issue route. A limitation reaches a crew or a maintenance organisation, so it carries an airworthiness signature.',
                       WF_PUBLICATION, ["Draft", "In Review"])],
       attributes=[
           a("limitationKind", "Limitation Kind",
             lov=["Airworthiness limitation (ALS - mandatory)",
                  "Certification maintenance requirement",
                  "Flight manual limitation", "Operating limitation",
                  "Mandatory replacement time", "Mandatory inspection",
                  "Critical design configuration control limitation"],
             required=True),
           a("limitationText", "Limitation as Published", required=True),
           a("mandatory", "Mandatory", kind="Bool", default=True),
           a("thresholdHours", "Threshold", kind="Number", unit="FH"),
           a("repeatIntervalHours", "Repeat Interval", kind="Number", unit="FH"),
           a("thresholdMonths", "Calendar Threshold", kind="Number", unit="months"),
           a("appliesToAtaChapter", "ATA Chapter", lov=ATA_CHAPTERS_IN_SCOPE),
           a("derivedFrom", "Derived From",
             lov=["Damage tolerance analysis", "Fatigue analysis", "Safety assessment",
                  "Test result", "Authority finding", "Service experience"],
             required=True),
           a("publishedIn", "Published In",
             lov=["Airworthiness limitations section", "Aircraft flight manual",
                  "AFM supplement", "Maintenance programme",
                  "Instructions for continued airworthiness", "Not yet published"],
             required=True, default="Not yet published"),
           a("authorityAgreementReference", "Authority Agreement Reference"),
           a("effectiveFrom", "Effective From", kind="Date"),
       ]),

    ty("MaintenanceTask", "Maintenance Task",
       "One scheduled task in the maintenance programme: what to do, at what interval, to "
       "what zone, and where the instruction lives. 'What does the 400 hour inspection "
       "say' could not be answered because nothing in the system held the maintenance "
       "programme at all (NI-00000533).",
       t("NonTypeDesignDocumentsBase"), numbering=f"{PREFIX}LssPublication",
       lifecycle=states(PUBLICATION_STATES),
       actions=[action("SubmitForIssue", "Submit for issue",
                       'Starts the publication issue route, so a scheduled task reaches the maintenance programme through the same signature as any other instruction to an operator.',
                       WF_PUBLICATION, ["Draft", "In Review"])],
       attributes=[
           a("taskCode", "Task Code", required=True),
           a("taskDescription", "Task", required=True),
           a("taskType", "Task Type",
             lov=["General visual inspection", "Detailed inspection",
                  "Special detailed inspection", "Functional check",
                  "Operational check", "Restoration", "Discard",
                  "Lubrication / servicing"], required=True),
           a("intervalHours", "Interval", kind="Number", unit="FH"),
           a("intervalCycles", "Interval", kind="Number", unit="FC"),
           a("intervalMonths", "Interval", kind="Number", unit="months"),
           a("thresholdHours", "First Due At", kind="Number", unit="FH"),
           a("ataChapter", "ATA Chapter", lov=ATA_CHAPTERS_IN_SCOPE),
           a("zone", "Zone"),
           a("accessRequired", "Access Required"),
           a("estimatedManHours", "Estimated Labour", kind="Number", unit="h"),
           a("taskSource", "Task Source",
             lov=["Airworthiness limitations section", "Certification maintenance requirement",
                  "Maintenance review board", "Manufacturer recommendation",
                  "Supplier component maintenance manual", "Operator request"],
             required=True),
           a("mandatoryTask", "Mandatory", kind="Bool", default=False),
           a("instructionReference", "Instruction Reference"),
       ]),

    # ── The authority's own output ───────────────────────────────────────────
    ty("CertificationFinding", "Certification Finding",
       "A finding, observation or condition raised by the authority or by a delegated "
       "representative against submitted data. There was no way to record one, which left "
       "the DER with no writable surface for the single act her delegation exists to "
       "perform, and left a 'compliant with limitation' position resting on a requirement "
       "that did not exist (NI-00000576, NI-00000760, NI-00000555). A finding has to "
       "outlive the item it was raised against, which is why it is a record and not a "
       "field.",
       t("NonTypeDesignDocumentsBase"), numbering=f"{PREFIX}LssCertificationFinding",
       lifecycle=states(QUALITY_STATES),
       actions=[action("SubmitResponse", "Submit response for closure",
                       'Starts the finding closure route: the discipline the finding concerns reviews the response, then airworthiness decides whether it is fit to put to the authority.',
                       WF_FINDING, ["Open", "Under Review"])],
       attributes=[
           a("findingClass", "Finding Class",
             lov=["Level 1 finding - airworthiness significant",
                  "Level 2 finding", "Observation", "Comment",
                  "Condition on acceptance", "Published limitation",
                  "Certification review item"], required=True),
           a("raisedBy", "Raised By", required=True),
           a("raisingAuthority", "Raising Authority",
             lov=["EASA", "FAA", "Designated engineering representative",
                  "Design organisation internal audit", "Other authority"],
             required=True),
           a("findingText", "Finding", required=True),
           a("regulatoryReference", "Regulatory Reference"),
           a("raisedOn", "Raised On", kind="Date", required=True),
           a("responseDueDate", "Response Due", kind="Date"),
           a("applicantResponse", "Applicant's Response"),
           a("closureBasis", "Basis for Closure"),
           a("closedBy", "Closed By"),
           a("closedOn", "Closed On", kind="Date"),
           a("blocksCertification", "Blocks Certification", kind="Bool", default=False),
           # The outcome that NI-00000574 asked for: a credit that has been withdrawn has
           # to be visible AS withdrawn, not merely absent.
           a("creditAffected", "Effect on Certification Credit",
             lov=["None", "Credit conditional on a limitation",
                  "Credit withdrawn - re-substantiation required",
                  "Credit withdrawn - re-test required", "Not yet assessed"],
             required=True, default="Not yet assessed"),
       ]),
]


# ─────────────────────────────────────────────────────────────────────────────
# Reference kinds
# ─────────────────────────────────────────────────────────────────────────────
# A reference kind in this platform is a TYPE, not an enum: ObjectReferenceLinkService
# discovers every non-abstract descendant of `ReferenceLinkBase` from the registry, so a
# kind declared here appears in GET .../references/kinds with no code change. That is a
# good design and this customization had not used it, which is why six roles independently
# reported that every relationship they needed had to be recorded as "Related" with the
# truth in a free-text note.
#
# The six out-of-the-box kinds - Audit Of, Drawing, Markup Of, Related, Specification,
# Supersedes - are a document-management vocabulary. None of them can say "this
# nonconformance is raised against that part", "this report is the evidence for that
# compliance demonstration" or "this specification governs the application of that
# sealant", and those are the sentences a certification trail is made of. Recording them
# all as "Related" is not merely untidy: a traceability walk cannot tell a hop that carries
# obligation from a hop that is a passing mention, so the walk is unusable as evidence -
# which is the whole point of NI-00000486, NI-00000569 and NI-00000712.
#
# Each kind below is one such sentence, in the direction a person would say it.

REFERENCE_KIND_ATTRS = [
    # Why the link exists, on the link. A reviewer asking "why does this evidence count"
    # should not have to open both ends and guess.
    a("linkRationale", "Rationale", scope="Revision"),
    # The suspect mechanism several roles asked for (NI-00000525, NI-00000712). A link is
    # suspect when one end has moved on since it was reviewed; nothing computes that today,
    # but it cannot even be RECORDED without somewhere to put it, and a review identity is
    # what makes "we looked at this" different from "nobody has looked".
    a("reviewStatus", "Review Status",
      lov=["Not reviewed", "Reviewed - current", "Suspect - target revised",
           "Suspect - source revised", "Suspect - manually flagged",
           "Re-reviewed - still valid", "Superseded"],
      default="Not reviewed"),
    a("reviewedBy", "Reviewed By"),
    a("reviewedOn", "Reviewed On", kind="Date"),
    a("reviewedAgainstRevision", "Reviewed Against Revision"),
]

ABSTRACT_REFERENCE_BASE = ty(
    "ReferenceBase", "Light Speed Systems Reference Base",
    "Abstract base for the NX-200 programme's own reference kinds. Sits between the "
    "out-of-the-box ReferenceLinkBase - which holds the endpoints and the revision rule - "
    "and the concrete kinds, so the review and suspect fields every aviation reference "
    "needs are declared once rather than on each kind. No concrete type derives straight "
    "off an out-of-the-box base anywhere in this model, and a reference kind is no "
    "exception.",
    "ReferenceLinkBase", abstract=True, attributes=REFERENCE_KIND_ATTRS)

CONCRETE_REFERENCE_TYPES = [
    ty("AffectedItemOfLink", "Affected Item",
       "The source record is raised AGAINST the target item: a nonconformance against the "
       "part found nonconforming, an inspection finding against the item inspected. The "
       "distinction from 'Related' is obligation - an affected item has to be dispositioned "
       "before the record can close, and until this kind existed that fact lived in a note "
       "(NI-00000708).",
       t("ReferenceBase")),

    ty("AffectedUnitOfLink", "Affected Unit",
       "The source record applies to one serialised unit or airframe rather than to the "
       "part in general. A disposition can differ per airframe - use-as-is on one, rework "
       "on another - and one mrbDisposition value for a whole record cannot say that "
       "(NI-00000713, NI-00000710).",
       t("ReferenceBase")),

    ty("EvidenceForLink", "Evidence For",
       "The source is evidence offered in support of the target compliance demonstration: "
       "a test report, an analysis, an inspection record. Evidence was cited as free text, "
       "so 14 of 23 compliance items named documents that do not exist and 8 of those were "
       "already Accepted - an evidence reference that cannot be resolved is not evidence "
       "(NI-00000569).",
       t("ReferenceBase")),

    ty("DemonstratesComplianceOfLink", "Demonstrates Compliance Of",
       "The source compliance demonstration covers the target configuration - the item, "
       "installation or system whose compliance it shows. Without it a compliance item "
       "floated free of the aeroplane: nothing could answer 'which demonstrations does "
       "revising this part invalidate', which is the question a change board asks first "
       "(NI-00000564, NI-00000730).",
       t("ReferenceBase")),

    ty("TestedConfigurationLink", "Tested Configuration",
       "The target is the exact item revision the source test was run on. A test report "
       "that cannot name its configuration as data cannot have its credit checked when the "
       "configuration changes, which is how a withdrawn credit goes unnoticed "
       "(NI-00000524).",
       t("ReferenceBase")),

    ty("GovernsApplicationOfLink", "Governs Application Of",
       "The source process specification controls how the target material or consumable is "
       "applied - cure, surface preparation, out-time, cleanliness. Revising the "
       "consumable should flag the specifications that govern it, and nothing connected the "
       "two (NI-00000523).",
       t("ReferenceBase")),

    ty("FirstArticleOfLink", "First Article Of",
       "The source first article inspection report is the first article for the target part "
       "revision. The FAI referenced its part by free text, so 'has this part had its "
       "first article' could not be answered from the data (NI-00000534).",
       t("ReferenceBase")),

    ty("EmbodiedByLink", "Embodied By",
       "The target part revision is what the source service bulletin instructs an operator "
       "to fit. A bulletin linked to nothing: no change notice, no modified part, no "
       "originating problem report, so its whole traceability was unvalidated strings "
       "(NI-00000566).",
       t("ReferenceBase")),

    ty("SubstantiatedByLink", "Substantiated By",
       "The target structural substantiation shows that the source item meets its strength, "
       "fatigue and damage-tolerance requirements. A substantiation that cannot be pointed "
       "at from the part it substantiates is unverifiable free text (NI-00000577).",
       t("ReferenceBase")),

    ty("FittedToLink", "Fitted To",
       "The source serialised unit is installed on the target airframe. This is what makes "
       "a life limit administrable: without it a fitted unit's hours cannot be accumulated "
       "against the airframe that flew them (NI-00000522).",
       t("ReferenceBase")),

    ty("OccurrenceOnLink", "Occurrence On",
       "The source in-service occurrence or finding was observed on the target airframe. "
       "Effectivity was a free-text field and occurrences were not recorded per airframe at "
       "all, so nothing could be trended against a tail number (NI-00000578, NI-00000583).",
       t("ReferenceBase")),

    ty("RegulatoryBasisLink", "Regulatory Basis",
       "The target certification requirement is the regulatory basis the source item is "
       "designed to. A part's paragraph was free text with no link to the requirement, so a "
       "paragraph that had fallen outside the certification basis went undetected "
       "(NI-00000730).",
       t("ReferenceBase")),
]

ALL_TYPES = (ABSTRACT_TYPES + [ABSTRACT_MATERIAL_BASE, ABSTRACT_REFERENCE_BASE]
             + CONCRETE_ITEM_TYPES + CONCRETE_DOC_TYPES
             + CONCRETE_REQ_TYPES + CONCRETE_MATERIAL_TYPES
             + CONCRETE_RECORD_TYPES + CONCRETE_REFERENCE_TYPES)
