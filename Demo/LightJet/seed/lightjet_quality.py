"""NX-200 quality and production records, and the change chains that connect them.

This is the auditability half of the demo. The story it has to be able to answer, live, in
front of an aviation audience:

    A coupling loosens in service.
      -> a problem report records it                        LSS-PR-00001
      -> a change request proposes a thicker clamp band     LSS-ECR-00001
      -> the change control board dispositions it           ECR -> ECO
      -> the change order implements it as revision B       LSS-ECO-00004
      -> the change notice tells production and operators   LSS-ECN-00004
      -> a delta first article proves the new revision      LSS-FAI-00004
      -> a service bulletin tells the fleet                 LSS-SB-21-001
      -> and the pinned trace link from the requirement
         went suspect the moment revision B appeared        LSS-REQ-CMP-0008

Every one of those is a real object with a real link, so the question "show me the evidence"
is a navigation rather than a story. The nonconformance set deliberately includes an escape
to a customer, a lapsed-calibration case and a suspect unapproved part, because those are
the three an AS9100D auditor reaches for.
"""

from lightjet_data import ATA21, ATA23, ATA25, PROGRAMME, ROOT_FOLDER, T

Q_OPEN, Q_REVIEW, Q_DISP, Q_CLOSED = "Open", "Under Review", "Dispositioned", "Closed"
CERT_DRAFT, CERT_ISSUED = "Draft", "Issued"
PUB_DRAFT, PUB_REVIEW, PUB_ISSUED = "Draft", "In Review", "Issued"
PS_REL = "Released"

F_FAI = f"{ROOT_FOLDER}/Quality Records/First Article Inspection"
F_NCR = f"{ROOT_FOLDER}/Quality Records/Nonconformance and MRB"
F_COC = f"{ROOT_FOLDER}/Quality Records/Certificates of Conformity"
F_ARC = f"{ROOT_FOLDER}/Quality Records/Authorised Release Certificates"
F_SQR = f"{ROOT_FOLDER}/Quality Records/Supplier Approval"
F_PS = f"{ROOT_FOLDER}/Quality Records/Special Processes"
F_SB = f"{ROOT_FOLDER}/Continued Airworthiness/Service Bulletins"
F_PR = f"{ROOT_FOLDER}/Continued Airworthiness/In-Service Reports"


def rec(stem, pn, title, status, attrs, folder, notes=None, doc_file=None,
        revision="A", history=None):
    return {
        "type": f"{T}{stem}", "pn": pn, "description": title, "status": status,
        "revision": revision, "attrs": attrs, "folder": folder, "notes": notes,
        "file": doc_file, "history": history or [("A", status)],
    }


def _qbase(author, issue, clause, function, pages=4, retention="Quality record - 7 years",
           evidence=None, **extra):
    base = {
        "authorName": author, "issueDate": issue, "pageCount": pages,
        "retentionClass": retention, "confidentiality": "Internal",
        "qmsClause": clause, "recordOwnerFunction": function,
        "auditEvidence": True, "objectiveEvidenceRefs": evidence,
        "typeDesignData": False,
    }
    base.update(extra)
    return {k: v for k, v in base.items() if v is not None}


# ─────────────────────────────────────────────────────────────────────────────
# First article inspection - AS9102 Rev C
# ─────────────────────────────────────────────────────────────────────────────

FAI_REPORTS = [
    rec("FaiReport", "LSS-FAI-00001",
        "First article inspection - bleed air supply duct assembly LSS-21-0001",
        Q_CLOSED,
        _qbase("k.tanaka", "2026-03-06", "8.5.1 Control of Production", "Quality",
               pages=14, evidence="CMM report CMM-26-0118, weld penetrant WPI-26-0044",
               as9102Revision="Rev C",
               faiPartNumber="LSS-21-0001", faiPartRevision="A",
               balloonedDrawingRef="LSS-DWG-21-0002 revision A",
               faiType="Full FAI", faiReason="New part",
               form1Complete=True, form2Complete=True, form3Complete=True,
               characteristicCount=48, nonconformanceCount=0,
               serialOrLotNumber="S/N 0001",
               manufacturingProcessRef="MPP-21-0001 revision B",
               measurementSystemAnalysisRef="MSA-26-0017",
               faiResult="Accepted", customerApprovalRequired=False),
        F_FAI, doc_file="LSS-FAI-00001.xlsx",
        notes="Full first article on a new part. All 48 ballooned characteristics "
              "accounted for on Form 3, materials and the welding special process "
              "certified on Form 2."),

    rec("FaiReport", "LSS-FAI-00002",
        "First article inspection - seat track fitting LSS-25-0001",
        Q_CLOSED,
        _qbase("a.novak", "2026-04-17", "8.5.1 Control of Production", "Quality",
               pages=11, evidence="CMM report CMM-26-0164, FPI record FPI-26-0071",
               as9102Revision="Rev C",
               faiPartNumber="LSS-25-0001", faiPartRevision="A",
               balloonedDrawingRef="LSS-DWG-25-0004 revision A",
               faiType="Full FAI", faiReason="New part",
               form1Complete=True, form2Complete=True, form3Complete=True,
               characteristicCount=26, nonconformanceCount=1,
               serialOrLotNumber="Lot 26071",
               manufacturingProcessRef="MPP-25-0001 revision A",
               measurementSystemAnalysisRef="MSA-26-0022",
               faiResult="Accepted with deviation",
               customerApprovalRequired=False),
        F_FAI, doc_file="LSS-FAI-00002.xlsx",
        notes="One characteristic out of tolerance: the fillet radius at the heel came "
              "in at 2.3 mm against a drawing requirement of 2.5 mm minimum. Raised as "
              "LSS-NCR-00001 and dispositioned use-as-is on the strength of the stress "
              "re-check, so the first article closed accepted with deviation."),

    rec("FaiReport", "LSS-FAI-00003",
        "First article inspection - sidewall panel LSS-F-00020",
        Q_CLOSED,
        _qbase("a.novak", "2026-08-05", "8.4 Externally Provided Processes", "Quality",
               pages=16,
               evidence="Volant FAI package VOL-FAI-1140-03, "
                        "heat release report LSS-CERT-QUAL-008",
               as9102Revision="Rev C",
               faiPartNumber="LSS-F-00020", faiPartRevision="A",
               balloonedDrawingRef="LSS-DWG-25-0007 revision A",
               faiType="Full FAI", faiReason="New supplier",
               form1Complete=True, form2Complete=True, form3Complete=True,
               characteristicCount=41, nonconformanceCount=0,
               serialOrLotNumber="Lot 26118",
               manufacturingProcessRef="VOL-MPP-1140 revision C",
               faiResult="Accepted", customerApprovalRequired=False),
        F_FAI, doc_file="LSS-FAI-00003.xlsx",
        notes="Supplier first article, flowed down in the purchase order with the "
              "AS9102 revision specified. Form 2 carries the composite cure and bond "
              "special process certifications from the supplier's NADCAP accreditation."),

    rec("FaiReport", "LSS-FAI-00004",
        "Delta first article inspection - duct coupling LSS-21-0004 revision B",
        Q_REVIEW,
        _qbase("k.tanaka", "2026-10-02", "8.5.6 Control of Changes", "Quality",
               pages=7,
               evidence="CMM report CMM-26-0391, LSS-ECO-00004",
               as9102Revision="Rev C",
               faiPartNumber="LSS-21-0004", faiPartRevision="B",
               balloonedDrawingRef="LSS-DWG-21-0005 revision B",
               faiType="Delta FAI", faiReason="Engineering change",
               form1Complete=True, form2Complete=True, form3Complete=False,
               characteristicCount=6, nonconformanceCount=0,
               serialOrLotNumber="Lot 26196",
               manufacturingProcessRef="MPP-21-0004 revision C",
               faiResult="Awaiting disposition",
               customerApprovalRequired=False),
        F_FAI, doc_file="LSS-FAI-00004.xlsx",
        notes="Delta first article against revision B. Only the six characteristics the "
              "engineering change affected are re-verified; the rest carry forward from "
              "the full first article on revision A, which is exactly what a delta is "
              "for. Form 3 is still open, so the submission is not yet complete."),

    rec("FaiReport", "LSS-FAI-00005",
        "First article inspection - passenger seat assembly LSS-F-00010 revision B",
        Q_OPEN,
        _qbase("a.novak", "2026-10-10", "8.5.6 Control of Changes", "Quality",
               pages=3,
               evidence="Caldera FAI package pending",
               as9102Revision="Rev C",
               faiPartNumber="LSS-F-00010", faiPartRevision="B",
               balloonedDrawingRef="LSS-DWG-25-0005 revision B",
               faiType="Delta FAI", faiReason="Engineering change",
               form1Complete=True, form2Complete=False, form3Complete=False,
               characteristicCount=14, nonconformanceCount=0,
               serialOrLotNumber="S/N 0011",
               faiResult="Awaiting disposition",
               customerApprovalRequired=True),
        F_FAI, doc_file="LSS-FAI-00005.xlsx",
        notes="Delta first article for the swivel interlock added at revision B. "
              "Customer approval is required because the launch operator's contract "
              "makes seat configuration a customer-approved item."),
]


# ─────────────────────────────────────────────────────────────────────────────
# Nonconformance and material review board
# ─────────────────────────────────────────────────────────────────────────────

NCRS = [
    rec("Ncr", "LSS-NCR-00001",
        "Fillet radius below drawing minimum - seat track fitting LSS-25-0001",
        Q_CLOSED,
        _qbase("a.novak", "2026-04-15", "8.7 Control of Nonconforming Outputs",
               "Quality", pages=5,
               evidence="CMM report CMM-26-0164, stress re-check SRC-26-0038",
               affectedPartNumber="LSS-25-0001", affectedPartRevision="A",
               affectedSerialNumbers="Lot 26071, 24 pieces",
               quantityAffected=24, severity="Minor",
               detectedAt="Final inspection", nonconformanceType="Dimensional",
               containmentAction="Lot 26071 quarantined at final inspection. "
                                 "No pieces had been issued to assembly.",
               mrbDisposition="Use as is",
               dispositionAuthority="DOA engineering signatory",
               safetyImpact=False, escapeToCustomer=False,
               rootCause="Tool wear on the forming radius. The tool life monitor was "
                         "set to a count that assumed a harder material than the "
                         "7075-T7351 actually used.",
               correctiveActionRef="CAPA-26-0014",
               recurrenceCount=0, costOfNonconformance=1840),
        F_NCR, doc_file="LSS-NCR-00001.docx",
        notes="Dispositioned use-as-is. The stress re-check showed the reduced radius "
              "still gives a margin of safety of 1.18 against the 16g condition, and "
              "Airworthiness concurred because the fitting is flight safety critical. "
              "The corrective action fixed the tool life count, not the parts."),

    rec("Ncr", "LSS-NCR-00002",
        "Weld porosity exceeding acceptance criteria - bleed duct LSS-21-0002",
        Q_CLOSED,
        _qbase("k.tanaka", "2026-05-28", "8.7 Control of Nonconforming Outputs",
               "Quality", pages=6,
               evidence="Penetrant record FPI-26-0094, radiograph RT-26-0021",
               affectedPartNumber="LSS-21-0002", affectedPartRevision="A",
               affectedSerialNumbers="S/N 0014",
               quantityAffected=1, severity="Major",
               detectedAt="In-process", nonconformanceType="Special process",
               containmentAction="Part held. The welder's remaining output from that "
                                 "shift re-inspected; no other indications found.",
               mrbDisposition="Scrap",
               dispositionAuthority="Material review board",
               safetyImpact=False, escapeToCustomer=False,
               rootCause="Shielding gas flow had drifted low. The flow alarm had been "
                         "silenced at the machine and nobody had recorded it.",
               correctiveActionRef="CAPA-26-0019",
               recurrenceCount=0, costOfNonconformance=4260),
        F_NCR, doc_file="LSS-NCR-00002.docx",
        notes="Scrapped. A pressure-boundary weld with porosity above the acceptance "
              "criteria is not a candidate for use-as-is, and the demo should say so: "
              "the disposition took four minutes, and the corrective action on the "
              "silenced alarm took three weeks."),

    rec("Ncr", "LSS-NCR-00003",
        "Clamp band loosening in service - duct coupling LSS-21-0004 revision A",
        Q_CLOSED,
        _qbase("k.tanaka", "2026-07-09", "10.2 Nonconformity and Corrective Action",
               "Quality", pages=12,
               evidence="LSS-PR-00001, torque audit TQA-26-0063",
               affectedPartNumber="LSS-21-0004", affectedPartRevision="A",
               affectedSerialNumbers="All revision A couplings, 3 aircraft affected",
               quantityAffected=9, severity="Major",
               detectedAt="In service", nonconformanceType="Dimensional",
               containmentAction="Repeat torque check introduced at the 100 hour "
                                 "inspection on all three aircraft by "
                                 "LSS-SB-21-001 interim instruction.",
               mrbDisposition="Rework to drawing",
               dispositionAuthority="Material review board",
               safetyImpact=True, escapeToCustomer=True,
               customerNotificationDate="2026-07-14",
               rootCause="The 1.2 mm clamp band relaxes under thermal cycling at bleed "
                         "temperature. The original design used a room temperature "
                         "relaxation figure.",
               correctiveActionRef="CAPA-26-0027",
               recurrenceCount=3, costOfNonconformance=38200),
        F_NCR, doc_file="LSS-NCR-00003.docx",
        notes="Safety impact and an escape to the customer, which are two separate "
              "questions and both answered yes here. Three recurrences. This is the "
              "nonconformance that started the change chain: LSS-PR-00001 -> "
              "LSS-ECR-00001 -> LSS-ECO-00004 -> revision B -> LSS-SB-21-001."),

    rec("Ncr", "LSS-NCR-00004",
        "Suspect unapproved part - headset jack panel from unauthorised broker",
        Q_DISP,
        _qbase("y.cheng", "2026-09-12", "8.1.4 Prevention of Counterfeit Parts",
               "Supply Chain", pages=9,
               evidence="Receiving inspection RI-26-0288, "
                        "supplier trace request STR-26-0041",
               affectedPartNumber="LSS-V-00015", affectedPartRevision="A",
               affectedSerialNumbers="Lot BRK-4471, 12 pieces",
               quantityAffected=12, severity="Critical",
               detectedAt="Receiving inspection",
               nonconformanceType="Suspect unapproved part",
               containmentAction="Lot quarantined in the bonded store on receipt and "
                                 "physically segregated. Not entered into stock, so "
                                 "nothing could be issued to a build.",
               mrbDisposition="Return to supplier",
               dispositionAuthority="Material review board",
               safetyImpact=False, escapeToCustomer=False,
               rootCause="Purchasing sourced through a broker during the last-time-buy "
                         "window without raising the counterfeit risk assessment the "
                         "procedure requires for a non-franchised source.",
               correctiveActionRef="CAPA-26-0033",
               recurrenceCount=0, costOfNonconformance=6400),
        F_NCR, doc_file="LSS-NCR-00004.docx",
        notes="The counterfeit-parts case. Date codes on the lot did not match the "
              "manufacturer's published sequence and the certificate of conformity "
              "named a distributor that is not on the authorised list. Quarantined, "
              "never stocked, returned. Dispositioned but not yet closed: the corrective "
              "action on the purchasing route is still open."),

    rec("Ncr", "LSS-NCR-00005",
        "Sealant applied beyond shelf life - pack bay installation",
        Q_CLOSED,
        _qbase("k.tanaka", "2026-06-20", "8.5.1 Control of Production",
               "Manufacturing", pages=5,
               evidence="Batch record BR-26-0177, store issue log SIL-26-0211",
               affectedPartNumber="LSS-21-INST-001", affectedPartRevision="A",
               affectedSerialNumbers="Airframe 003",
               quantityAffected=1, severity="Major",
               detectedAt="In-process", nonconformanceType="Material",
               containmentAction="Work stopped on airframe 003. Every joint sealed from "
                                 "the affected batch identified from the batch record.",
               mrbDisposition="Rework to drawing",
               dispositionAuthority="Material review board",
               safetyImpact=False, escapeToCustomer=False,
               rootCause="Batch 26052 of LSS-CM-0001 was issued four days past its "
                         "expiry. The store's expiry check was a manual label read.",
               correctiveActionRef="CAPA-26-0023",
               recurrenceCount=1, costOfNonconformance=9100),
        F_NCR, doc_file="LSS-NCR-00005.docx",
        notes="Batch traceability earned its keep: because the consumable is batch "
              "traceable and the batch was recorded against the installation, the "
              "affected joints were identified in an hour rather than by stripping the "
              "whole pack bay."),

    rec("Ncr", "LSS-NCR-00006",
        "Inspection records taken with a check fixture whose calibration had lapsed",
        Q_REVIEW,
        _qbase("a.novak", "2026-10-08", "8.5.2 Identification and Traceability",
               "Quality", pages=8,
               evidence="Calibration record CAL-2026-0119, "
                        "inspection log IL-26-0355 to IL-26-0398",
               affectedPartNumber="LSS-21-0001", affectedPartRevision="A",
               affectedSerialNumbers="S/N 0021 to S/N 0027",
               quantityAffected=7, severity="Major",
               detectedAt="Audit", nonconformanceType="Documentation",
               containmentAction="Check fixture LSS-TL-0002 quarantined and set to "
                                 "Restricted. The seven affected assemblies are held "
                                 "pending re-inspection on a calibrated fixture.",
               mrbDisposition="Awaiting disposition",
               dispositionAuthority="Material review board",
               safetyImpact=False, escapeToCustomer=False,
               rootCause="Under investigation. The calibration due date was held in the "
                         "tooling record but nothing stopped the fixture being used "
                         "after it passed.",
               recurrenceCount=0),
        F_NCR, doc_file="LSS-NCR-00006.docx",
        notes="Found by internal audit, not by inspection. An uncalibrated fixture does "
              "not make a part wrong, it makes the record worthless, which is why the "
              "nonconformance is against traceability rather than dimension. Still "
              "under review: the disposition depends on the re-inspection result."),
]


# ─────────────────────────────────────────────────────────────────────────────
# Certificates of conformity and authorised release certificates
# ─────────────────────────────────────────────────────────────────────────────

COCS = [
    rec("CofC", "LSS-COC-00001",
        "Certificate of conformity - air cycle machine, Meridian Air Systems",
        CERT_ISSUED,
        _qbase("y.cheng", "2026-02-19", "8.4 Externally Provided Processes",
               "Supply Chain", pages=2,
               retention="Production record - 10 years",
               evidence="Material certificate MC-MAS-7730-0211",
               supplierName="Meridian Air Systems", supplierCageCode="K4821",
               purchaseOrderNumber="PO-2026-00418", purchaseOrderLine="010",
               certifiedPartNumber="LSS-V-00002", certifiedPartRevision="A",
               quantityShipped=2, lotNumber="MAS-L-26037",
               serialNumbers="MAS7730-0007, MAS7730-0008",
               materialCertificateRefs="MC-MAS-7730-0211",
               specialProcessCertRefs="NADCAP heat treat cert HT-MAS-0092",
               deviationsDeclared="None",
               authorisedSignatory="A. Pretorius, Quality Manager",
               statementOfConformity=
               "The items described conform in all respects to the purchase order and "
               "to drawing LSS-V-00002 revision A, including all flowed down "
               "requirements."),
        F_COC, doc_file="LSS-COC-00001.pdf"),

    rec("CofC", "LSS-COC-00002",
        "Certificate of conformity - cabin pressure controller, Meridian Air Systems",
        CERT_ISSUED,
        _qbase("y.cheng", "2026-04-23", "8.4 Externally Provided Processes",
               "Supply Chain", pages=2,
               retention="Production record - 10 years",
               supplierName="Meridian Air Systems", supplierCageCode="K4821",
               purchaseOrderNumber="PO-2026-00502", purchaseOrderLine="010",
               certifiedPartNumber="LSS-V-00004", certifiedPartRevision="A",
               quantityShipped=1, lotNumber="MAS-L-26062",
               serialNumbers="MAS9901-0011",
               materialCertificateRefs="Not applicable - assembled unit",
               specialProcessCertRefs="Conformal coating cert CC-MAS-0144",
               deviationsDeclared="None",
               authorisedSignatory="A. Pretorius, Quality Manager",
               statementOfConformity=
               "Conforms to purchase order PO-2026-00502 and ETSO-C2d authorisation."),
        F_COC, doc_file="LSS-COC-00002.pdf"),

    rec("CofC", "LSS-COC-00003",
        "Certificate of conformity - composite sandwich panel blanks, Volant",
        CERT_ISSUED,
        _qbase("y.cheng", "2026-07-02", "8.4 Externally Provided Processes",
               "Supply Chain", pages=3,
               retention="Production record - 10 years",
               supplierName="Volant Composites", supplierCageCode="H5508",
               purchaseOrderNumber="PO-2026-00611", purchaseOrderLine="020",
               certifiedPartNumber="LSS-V-00022", certifiedPartRevision="A",
               quantityShipped=40, lotNumber="VOL-L-26118",
               serialNumbers="Not serialised - lot traceable",
               materialCertificateRefs="Prepreg cert PC-VOL-4471, core cert CC-VOL-2210",
               specialProcessCertRefs="NADCAP composites cert NC-VOL-0038",
               deviationsDeclared="None",
               authorisedSignatory="I. Vogt, Quality Assurance",
               statementOfConformity=
               "Conforms to LSS-SPEC-MAT-002 and purchase order PO-2026-00611."),
        F_COC, doc_file="LSS-COC-00003.pdf"),

    rec("CofC", "LSS-COC-00004",
        "Certificate of conformity - headset jack panels, broker supplied (REJECTED)",
        "Withdrawn",
        _qbase("y.cheng", "2026-09-10", "8.1.4 Prevention of Counterfeit Parts",
               "Supply Chain", pages=2,
               retention="Quality record - 7 years",
               evidence="LSS-NCR-00004",
               supplierName="Aeroparts Clearing House (broker)",
               supplierCageCode="Not held",
               purchaseOrderNumber="PO-2026-00744", purchaseOrderLine="010",
               certifiedPartNumber="LSS-V-00015", certifiedPartRevision="A",
               quantityShipped=12, lotNumber="BRK-4471",
               serialNumbers="Not supplied",
               materialCertificateRefs="Not supplied",
               deviationsDeclared="None declared",
               authorisedSignatory="Illegible",
               statementOfConformity=
               "Withdrawn. The certificate names a distributor that is not on the "
               "authorised list for this part and the manufacturer has confirmed it did "
               "not supply the named lot. See LSS-NCR-00004."),
        F_COC, doc_file="LSS-COC-00004.pdf",
        notes="A withdrawn certificate, kept rather than deleted. The record that a bad "
              "certificate was received and rejected is itself the audit evidence that "
              "the counterfeit-parts control worked."),

    rec("CofC", "LSS-COC-00005",
        "Certificate of conformity - 16g passenger seats, Caldera Seating",
        CERT_ISSUED,
        _qbase("y.cheng", "2026-09-30", "8.4 Externally Provided Processes",
               "Supply Chain", pages=4,
               retention="Production record - 10 years",
               supplierName="Caldera Seating", supplierCageCode="F2914",
               purchaseOrderNumber="PO-2026-00698", purchaseOrderLine="010",
               certifiedPartNumber="LSS-F-00010", certifiedPartRevision="B",
               quantityShipped=4, lotNumber="CAL-L-26171",
               serialNumbers="CAL-0011, CAL-0012, CAL-0013, CAL-0014",
               materialCertificateRefs="Leather cert LC-PYR-0820-26152",
               specialProcessCertRefs=
               "Flammability test cert FT-CAL-0211, weld cert WC-CAL-0088",
               deviationsDeclared="None",
               authorisedSignatory="M. Bellini, Quality Representative",
               statementOfConformity=
               "Conforms to LSS-SPEC-PRO-004 revision B including the swivel interlock, "
               "and to drawing LSS-DWG-25-0005 revision B."),
        F_COC, doc_file="LSS-COC-00005.pdf"),
]

ARCS = [
    rec("AirworthinessRelease", "LSS-ARC-00001",
        "EASA Form 1 - environmental control system installation, airframe 002",
        CERT_ISSUED,
        _qbase("g.rossi", "2026-06-05", "8.5.2 Identification and Traceability",
               "Airworthiness", pages=1,
               retention="Airworthiness release - life of part",
               evidence="LSS-FAI-00001, LSS-COC-00001",
               formType="EASA Form 1",
               certificateNumber="LSS/F1/2026/00114",
               releasedPartNumber="LSS-21-INST-001", releasedPartRevision="A",
               quantity=1, serialOrBatchNumber="S/N 0002",
               releaseStatus="New",
               approvalDesignData="NX-200 type design, EASA.21J.0742",
               releasingOrganisationApproval="EASA.21G.0318",
               eligibilityStatement="NX-200 series aeroplanes",
               remarks="Released under production organisation approval EASA.21G.0318 "
                       "against the approved type design.",
               nonApprovedDesignData=False,
               dateOfIssue="2026-06-05",
               authorisedSignatory="G. Rossi, Certifying Staff 0042"),
        F_ARC, doc_file="LSS-ARC-00001.pdf"),

    rec("AirworthinessRelease", "LSS-ARC-00002",
        "Dual release 8130-3 / Form 1 - duct coupling revision B, spares batch",
        CERT_ISSUED,
        _qbase("g.rossi", "2026-10-09", "8.5.2 Identification and Traceability",
               "Airworthiness", pages=1,
               retention="Airworthiness release - life of part",
               evidence="LSS-FAI-00004, LSS-ECN-00004",
               formType="Dual release 8130-3 / Form 1",
               certificateNumber="LSS/DR/2026/00188",
               releasedPartNumber="LSS-21-0004", releasedPartRevision="B",
               quantity=30, serialOrBatchNumber="Lot 26196",
               releaseStatus="New",
               approvalDesignData="NX-200 type design, EASA.21J.0742, "
                                  "LSS-DWG-21-0005 revision B",
               releasingOrganisationApproval="EASA.21G.0318 / FAA 14 CFR 21 Subpart G",
               eligibilityStatement="NX-200 series aeroplanes. Supersedes revision A; "
                                    "revision A couplings remain eligible until the "
                                    "compliance date of LSS-SB-21-001.",
               remarks="Spares batch for LSS-SB-21-001 compliance. Dual released for "
                       "operators in both jurisdictions.",
               nonApprovedDesignData=False,
               dateOfIssue="2026-10-09",
               authorisedSignatory="G. Rossi, Certifying Staff 0042"),
        F_ARC, doc_file="LSS-ARC-00002.pdf",
        notes="The eligibility statement does the real work here: it says what an "
              "operator may fit and until when, which is the question a release "
              "certificate exists to answer."),

    rec("AirworthinessRelease", "LSS-ARC-00003",
        "EASA Form 1 - cabin interior installation, airframe 002, prototype",
        CERT_ISSUED,
        _qbase("g.rossi", "2026-07-21", "8.5.2 Identification and Traceability",
               "Airworthiness", pages=1,
               retention="Airworthiness release - life of part",
               formType="EASA Form 1",
               certificateNumber="LSS/F1/2026/00141",
               releasedPartNumber="LSS-25-INST-001", releasedPartRevision="A",
               quantity=1, serialOrBatchNumber="S/N 0002",
               releaseStatus="Prototype",
               approvalDesignData="NX-200 type design data, not yet type certificated",
               releasingOrganisationApproval="EASA.21J.0742 design organisation",
               eligibilityStatement="NX-200 prototype airframe 002 only. Not eligible "
                                    "for installation on a type certificated aeroplane.",
               remarks="Prototype release for the certification programme. The design "
                       "data is approved under the design organisation approval but the "
                       "type certificate has not been issued.",
               nonApprovedDesignData=True,
               dateOfIssue="2026-07-21",
               authorisedSignatory="G. Rossi, Certifying Staff 0042"),
        F_ARC, doc_file="LSS-ARC-00003.pdf",
        notes="Status Prototype with non-approved design data flagged. This is the "
              "distinction that matters before type certification and the one most "
              "often got wrong on a release certificate."),
]


# ─────────────────────────────────────────────────────────────────────────────
# Supplier qualification
# ─────────────────────────────────────────────────────────────────────────────

def _sqr(pn, supplier, cage, scope, cert, expiry, nadcap, audit, atype, result,
         findings, next_due, risk, approval, flowdown, ppm, otd, status=Q_CLOSED,
         notes=None):
    return rec("SupplierQualRecord", pn,
               f"Supplier qualification - {supplier}", status,
               _qbase("y.cheng", audit, "8.4 Externally Provided Processes",
                      "Supply Chain", pages=18,
                      supplierName=supplier, supplierCageCode=cage,
                      approvalScope=scope,
                      as9100CertificateNumber=cert,
                      as9100CertificateExpiry=expiry,
                      nadcapScopes=nadcap,
                      auditDate=audit, auditType=atype, auditResult=result,
                      openFindingCount=findings, nextAuditDue=next_due,
                      riskRating=risk, approvalStatus=approval,
                      flowdownAccepted=flowdown,
                      deliveredQualityPpm=ppm, onTimeDeliveryPercent=otd),
               F_SQR, doc_file=f"{pn}.xlsx", notes=notes)


SUPPLIER_RECORDS = [
    _sqr("LSS-SQR-00001", "Meridian Air Systems", "K4821",
         "Air cycle machines, heat exchangers, pressurisation control equipment",
         "AS9100D-K4821-0211", "2028-04-30",
         "Heat Treating, Chemical Processing", "2026-01-28",
         "On-site surveillance", "Satisfactory with observations", 0, "2027-01-31",
         "Low", "Approved", True, 420, 96.4),

    _sqr("LSS-SQR-00002", "Thorne Avionics", "L7730",
         "VHF and satellite communications, audio integrating, voice recorders",
         "AS9100D-L7730-0088", "2027-02-28",
         "Not applicable - electronics", "2026-02-11",
         "On-site surveillance", "Minor findings", 2, "2026-12-31",
         "Medium", "Approved", True, 880, 91.2,
         notes="AS9100 certificate expires on 28 February 2027 and two minor findings "
               "are still open. Both are visible as data, which is the point: an "
               "expiring certificate is a report, not a diary reminder."),

    _sqr("LSS-SQR-00003", "Caldera Seating", "F2914",
         "16g dynamically tested seating, restraint systems, cushions",
         "AS9100D-F2914-0144", "2028-09-30",
         "Welding, Materials Testing Laboratories", "2026-03-18",
         "On-site initial", "Satisfactory", 0, "2027-03-31",
         "Low", "Approved", True, 310, 94.8),

    _sqr("LSS-SQR-00004", "Volant Composites", "H5508",
         "Composite sandwich panels, cabin monuments, interior trim",
         "AS9100D-H5508-0302", "2027-11-30",
         "Composites, Non-Destructive Testing", "2026-05-06",
         "On-site surveillance", "Minor findings", 1, "2027-05-31",
         "Medium", "Approved - conditional", False, 1240, 87.6,
         notes="Conditional approval and the requirement flowdown is not yet formally "
               "accepted, which is why the sidewall first article needed the AS9102 "
               "revision spelled out in the purchase order."),

    _sqr("LSS-SQR-00005", "Arclight Interconnect", "M1172",
         "Wiring harnesses, connectors, EWIS assembly",
         "AS9100D-M1172-0077", "2028-01-31",
         "Not applicable - assembly", "2026-04-22",
         "Desktop assessment", "Satisfactory", 0, "2027-04-30",
         "Low", "Approved", True, 540, 93.1),

    _sqr("LSS-SQR-00006", "Pyrosafe Materials", "N6643",
         "Flame retardant textiles, sealants, adhesives and finishes",
         "AS9100D-N6643-0199", "2027-06-30",
         "Chemical Processing, Materials Testing Laboratories", "2026-06-17",
         "For-cause", "Major findings", 3, "2026-11-30",
         "High", "Probation", True, 2680, 79.4, status=Q_REVIEW,
         notes="On probation after a for-cause audit triggered by the shelf-life escape "
               "in LSS-NCR-00005. Three major findings open, delivered quality at "
               "2 680 ppm and on-time delivery below 80 percent. High risk, and the "
               "obvious candidate when the demo is asked which supplier to worry about."),
]


# ─────────────────────────────────────────────────────────────────────────────
# Special process specifications
# ─────────────────────────────────────────────────────────────────────────────

def _process(pn, title, family, standard, nadcap, sources, limits, frozen, pyro=None,
            periodic=None, retention_years=10, notes=None):
    return rec("ProcessSpec", pn, title, PS_REL,
               _qbase("t.brennan", "2026-02-05", "8.5.1 Control of Production",
                      "Manufacturing", pages=22,
                      retention="Production record - 10 years",
                      processFamily=family, governingStandard=standard,
                      nadcapAccreditationRequired=nadcap,
                      approvedSourceList=sources,
                      parameterControlLimits=limits,
                      qualifiedOperatorRequired=True,
                      frozenPlanRequired=frozen,
                      periodicTestRequirement=periodic,
                      pyrometryClass=pyro,
                      recordRetentionYears=retention_years),
               F_PS, doc_file=f"{pn}.docx", notes=notes)


PROCESS_SPECS = [
    _process("LSS-PS-0001",
             "Fusion welding of titanium tube and fittings",
             "Welding", "AWS D17.1 Class A", True,
             "Light Speed Systems Bay 2; Meridian Air Systems",
             "Shielding gas purity 99.995 percent minimum; interpass temperature "
             "177 degrees C maximum; trailing shield required on all welds",
             True, periodic="Operator requalification every 6 months; "
                            "weld coupon every 40 welds",
             notes="Frozen process plan: the parameters, the operator and the equipment "
                   "are fixed and a change needs requalification. The porosity "
                   "nonconformance LSS-NCR-00002 was a departure from this "
                   "specification, not a tolerance on it."),

    _process("LSS-PS-0002",
             "Machining and deburring of corrosion resistant steel",
             "Non-Conventional Machining", "LSS-SPEC-PRC-004", False,
             "Light Speed Systems Bay 1",
             "Surface roughness 1.6 micrometres Ra maximum; no sharp edges; "
             "edge break 0.2 to 0.4 mm",
             False),

    _process("LSS-PS-0003",
             "Fluorescent penetrant inspection, Type 1 Method C Level 3",
             "Non-Destructive Testing", "ASTM E1417 / NAS 410", True,
             "Light Speed Systems inspection room 1; Northgate NDT Services",
             "Penetrant dwell 10 minutes minimum; developer dwell 10 to 30 minutes; "
             "UV-A irradiance 1000 microwatts per square centimetre minimum at the "
             "surface; ambient white light 20 lux maximum",
             True, periodic="System performance check daily; "
                            "inspector vision test annually; NAS 410 Level 2 minimum",
             notes="NAS 410 qualified inspectors only. The irradiance and white light "
                   "limits are the two parameters an audit always samples, so they are "
                   "stated as numbers rather than as a reference."),

    _process("LSS-PS-0004",
             "Chromic acid anodising and chemical conversion coating",
             "Chemical Processing", "MIL-A-8625 Type I / MIL-DTL-5541 Class 1A", True,
             "Northgate Surface Treatments; Meridian Air Systems",
             "Bath temperature 32 to 38 degrees C; chromic acid 45 to 55 g/l; "
             "voltage ramp 0 to 40 V over 10 minutes; seal water pH 5.5 to 7.0",
             False, pyro="Not applicable",
             periodic="Bath analysis twice weekly; "
                      "paint adhesion and salt spray coupon monthly"),

    _process("LSS-PS-0005",
             "Autoclave cure of carbon and glass prepreg laminates and sandwich panels",
             "Composites", "LSS-SPEC-MAT-001 / AMS 2750 pyrometry", True,
             "Light Speed Systems composite shop; Volant Composites",
             "Cure 177 degrees C plus or minus 6 degrees C for 120 minutes; "
             "ramp 1 to 3 degrees C per minute; autoclave pressure 0.59 to 0.69 MPa; "
             "vacuum 0.085 MPa minimum; prepreg out-time 30 days maximum",
             True, pyro="AMS 2750 Class 2 instrumentation Type B",
             periodic="Thermal survey every 6 months; "
                      "mechanical property coupon per cure cycle",
             notes="Out-time is the parameter that most often puts a composite part out "
                   "of specification, and it is only auditable if the prepreg batch is "
                   "traceable to the part, which is why LSS-SPEC-MAT-001 requires it."),

    _process("LSS-PS-0006",
             "Application of polysulphide sealant to pressure and fuel boundaries",
             "Sealants", "AMS 3277 / SAE AS5127", False,
             "Light Speed Systems Bay 3",
             "Surface temperature 18 to 32 degrees C; relative humidity 30 to 70 "
             "percent; application within the sealant pot life; cure 72 hours minimum "
             "before pressure test",
             False, periodic="Batch acceptance test on receipt; "
                             "peel adhesion coupon per batch",
             notes="The shelf-life escape LSS-NCR-00005 was a failure to apply this "
                   "specification's receipt and expiry controls, which is why the "
                   "corrective action changed the store issue process rather than the "
                   "specification."),
]


# ─────────────────────────────────────────────────────────────────────────────
# Service bulletins
# ─────────────────────────────────────────────────────────────────────────────

SERVICE_BULLETINS = [
    rec("ServiceBulletin", "LSS-SB-21-001",
        "Bleed air duct coupling - replace V-band coupling with revision B",
        PUB_ISSUED,
        _qbase("f.mbeki", "2026-10-12", "8.5.6 Control of Changes",
               "Customer Support", pages=14,
               retention="Type design - life of type",
               evidence="LSS-ECN-00004, LSS-NCR-00003, LSS-ARC-00002",
               bulletinType="Mandatory", bulletinCategory="Modification",
               effectivityRange="NX-200 airframes 001 through 003, and any aeroplane "
                                "with LSS-21-0004 revision A installed",
               compliancePeriod="Within 300 flight hours or 12 months, whichever occurs "
                                "first. Repeat torque check at each 100 hour inspection "
                                "until accomplished.",
               estimatedManHours=6.5, aircraftDowntimeHours=10,
               kitPartNumber="LSS-KIT-21-001",
               relatedDirectiveRef="Proposed AD - EASA PAD 26-0188",
               weightChangeKg=0.12,
               publicationDate="2026-10-12",
               warrantyApplicable=True),
        F_SB, doc_file="LSS-SB-21-001.pdf",
        notes="Mandatory. This is the end of the chain that started with the in-service "
              "loosening report: the fleet instruction that makes the design change "
              "real on aeroplanes already delivered. EASA has a proposed airworthiness "
              "directive out against it, so compliance will become a legal obligation "
              "rather than a recommendation."),

    rec("ServiceBulletin", "LSS-SB-21-002",
        "Environmental control system controller - load software version 2.1.0",
        PUB_ISSUED,
        _qbase("f.mbeki", "2026-09-18", "8.5.6 Control of Changes",
               "Customer Support", pages=9,
               retention="Type design - life of type",
               evidence="LSS-ECN-00002, LSS-CERT-SWP-004, LSS-CERT-SWP-005",
               bulletinType="Recommended", bulletinCategory="Software update",
               effectivityRange="NX-200 airframes 001 through 003 with software "
                                "version 2.0.x installed",
               compliancePeriod="At the next scheduled maintenance opportunity",
               estimatedManHours=1.5, aircraftDowntimeHours=2,
               kitPartNumber="LSS-SW-0001-02 loadable media",
               weightChangeKg=0,
               publicationDate="2026-09-18",
               warrantyApplicable=True),
        F_SB, doc_file="LSS-SB-21-002.pdf",
        notes="Field loadable software needs a service bulletin as well as a change "
              "notice, because loading it changes the aeroplane's approved "
              "configuration and the operator has to record which load is fitted."),

    rec("ServiceBulletin", "LSS-SB-23-001",
        "Underwater locating beacon - battery replacement at six year life limit",
        PUB_ISSUED,
        _qbase("f.mbeki", "2026-08-07", "8.5.2 Identification and Traceability",
               "Customer Support", pages=6,
               retention="Type design - life of type",
               bulletinType="Mandatory", bulletinCategory="Life limit change",
               effectivityRange="All NX-200 aeroplanes fitted with LSS-V-00013",
               compliancePeriod="Before the beacon battery reaches six years from its "
                                "date of manufacture, as marked on the unit",
               estimatedManHours=1.0, aircraftDowntimeHours=1.5,
               kitPartNumber="TAV-ULB-0410-BAT",
               weightChangeKg=0,
               publicationDate="2026-08-07",
               warrantyApplicable=False),
        F_SB, doc_file="LSS-SB-23-001.pdf",
        notes="A calendar life limit rather than a flight hour limit. It is listed in "
              "the airworthiness limitations section, which is why the bulletin is "
              "mandatory even though nothing has gone wrong."),

    rec("ServiceBulletin", "LSS-SB-25-001",
        "Passenger seat - install swivel interlock, revision B configuration",
        PUB_REVIEW,
        _qbase("f.mbeki", "2026-10-14", "8.5.6 Control of Changes",
               "Customer Support", pages=18,
               retention="Type design - life of type",
               evidence="LSS-ECO-00001, LSS-CERT-QUAL-002, LSS-CERT-COMP-015",
               bulletinType="Mandatory", bulletinCategory="Modification",
               effectivityRange="NX-200 airframes fitted with LSS-F-00010 revision A "
                                "club seats",
               compliancePeriod="Before further flight with passengers in the club "
                                "seat positions, once the equivalent safety finding is "
                                "accepted",
               estimatedManHours=4.0, aircraftDowntimeHours=6,
               kitPartNumber="LSS-KIT-25-001",
               weightChangeKg=0.34,
               publicationDate=None,
               warrantyApplicable=True),
        F_SB, doc_file="LSS-SB-25-001.pdf",
        notes="In review and deliberately not issued. The compliance item for the "
              "equivalent safety finding is still Submitted, and a bulletin cannot be "
              "issued ahead of the certification position it depends on. This is the "
              "demo's example of a publication correctly held back."),
]


# ─────────────────────────────────────────────────────────────────────────────
# Problem reports and the change chains
# ─────────────────────────────────────────────────────────────────────────────
# ProblemReport, ECR, ECO and ECN are out-of-the-box types, so the demo uses the platform's
# own change objects rather than company copies. Their links are real link objects created
# through the change controllers: problem -> ECR, ECR -> ECO, ECO -> ECN, plus affected
# items on each.

PROBLEM_REPORTS = [
    {
        "pn": "LSS-PR-00001",
        "title": "Bleed duct coupling found loose at 100 hour inspection, three aircraft",
        "status": "Under Review",
        "attrs": {
            "problemStatement":
                "Operators of airframes 001, 002 and 003 have each reported a V-band "
                "coupling on the bleed air supply duct found loose at the 100 hour "
                "inspection. Torque measured between 3.1 and 4.2 Nm against an "
                "installation requirement of 5.6 Nm. No bleed leak had developed and no "
                "flight was affected, but the trend is consistent across three "
                "independent aircraft.",
            "severity": "Major",
            "detectionPhase": "In Service",
            "originator": "f.mbeki",
            "dateRaised": "2026-07-06",
            "affectedItem": "LSS-21-0004",
            "rootCauseCategory": "Design",
        },
        "folder": F_PR,
        "notes": "Three independent reports of the same symptom is a design question, "
                 "not three maintenance errors. Raised to ECR LSS-ECR-00001.",
    },
    {
        "pn": "LSS-PR-00002",
        "title": "Cabin temperature oscillation in the descent, airframe 002",
        "status": "Closed",
        "attrs": {
            "problemStatement":
                "Cabin temperature oscillates plus or minus 4 degrees C with a period of "
                "about 90 seconds during descent below 6 000 m. Traced to an integrator "
                "wind-up in the temperature control law when the pack outlet is at its "
                "lower limit.",
            "severity": "Minor",
            "detectionPhase": "Flight Test",
            "originator": "r.achebe",
            "dateRaised": "2026-06-11",
            "affectedItem": "LSS-SW-0001",
            "rootCauseCategory": "Software",
            "disposition": "Corrected by design change",
            "correctiveAction": "Integrator limiting added in software version 2.1.0.",
        },
        "folder": F_PR,
        "notes": "Closed by ECS controller software version 2.1.0, released through "
                 "LSS-ECO-00002 and notified by LSS-ECN-00002. The fleet instruction "
                 "is LSS-SB-21-002.",
    },
    {
        "pn": "LSS-PR-00003",
        "title": "Satellite terminal transmission desensitises VHF 2 receive",
        "status": "Under Review",
        "attrs": {
            "problemStatement":
                "During ground test on airframe 002, satellite terminal transmission "
                "reduced VHF 2 receive sensitivity by 9 dB when VHF 2 was tuned within "
                "1.2 MHz of a satellite terminal harmonic. Both systems meet their own "
                "DO-160G section 21 emission limits individually.",
            "severity": "Major",
            "detectionPhase": "Ground Test",
            "originator": "d.okonjo",
            "dateRaised": "2026-07-02",
            "affectedItem": "LSS-23-INST-001",
            "rootCauseCategory": "Integration",
        },
        "folder": F_PR,
        "notes": "Resolved by an installation limitation enforced in the audio control "
                 "panel software rather than by a hardware change, which is recorded on "
                 "LSS-CERT-EMI-002 and is why that compliance item reads 'compliant with "
                 "limitation'. Still open pending the software change that enforces it.",
    },
]

# Each chain: the ECR, the ECO it was promoted to, the ECN that notified it, the items each
# affects, and the transitions to walk them through. `changeAction` on an affected item is
# what the change does to that item, which is the field a change impact review reads first.

CHANGE_CHAINS = [
    {
        "ecr": {
            "pn": "LSS-ECR-00001",
            "title": "Increase V-band clamp band thickness, bleed duct coupling",
            "status": "Approved",
            "attrs": {
                "reason":
                    "Three independent in-service reports of a loose coupling on the "
                    "bleed air supply duct (LSS-PR-00001), and a nonconformance "
                    "(LSS-NCR-00003) attributing it to thermal relaxation of the 1.2 mm "
                    "clamp band. The original design used a room temperature relaxation "
                    "figure for a joint that runs at bleed temperature.",
                "proposedSolution":
                    "Increase the clamp band thickness from 1.2 mm to 1.6 mm, retaining "
                    "the existing V-band geometry and installation torque so the joint "
                    "remains interchangeable. Re-run the proof pressure test and raise a "
                    "delta first article against the changed characteristics.",
                "justification":
                    "Safety related and already escaped to three customers. The interim "
                    "repeat torque check is an operational burden that cannot be carried "
                    "indefinitely. A mandatory service bulletin will be needed, and "
                    "EASA has indicated a proposed airworthiness directive.",
                "costEstimate": 84000,
                "sourceProblemId": "LSS-PR-00001",
            },
            "affects": [
                ("LSS-21-0004", "Revise", "B"),
                ("LSS-DWG-21-0005", "Revise", "B"),
                ("LSS-21-0001", "Affected - no change", None),
                ("LSS-21-INST-001", "Affected - no change", None),
            ],
            "problems": ["LSS-PR-00001"],
            "transitions": [
                ("Submitted", "Raised following the third in-service report. "
                              "Nonconformance LSS-NCR-00003 attached as evidence."),
                ("Under Review", "To the change control board of 2026-07-23 with the "
                                 "thermal relaxation analysis and the cost case."),
                ("Approved", "Approved by the change control board. Safety related, so "
                             "approved for immediate implementation with a mandatory "
                             "service bulletin. Weight impact 0.12 kg per coupling "
                             "accepted."),
            ],
        },
        "eco": {
            "pn": "LSS-ECO-00004",
            "title": "Implement V-band coupling revision B and release spares",
            "status": "Closed",
            "attrs": {
                "implementationPlan":
                    "Release LSS-21-0004 revision B and LSS-DWG-21-0005 revision B "
                    "through the type design release route. Re-run the proof pressure "
                    "test. Raise a delta first article (LSS-FAI-00004) covering the six "
                    "changed characteristics only. Produce a spares batch of 30 and "
                    "release it on a dual 8130-3 / Form 1 for service bulletin "
                    "compliance.",
                "effectivityValue":
                    "Revision B is effective on airframe 004 and subsequent in "
                    "production, and on airframes 001 to 003 on accomplishment of "
                    "LSS-SB-21-001.",
                "effectivityType": "Serial number",
                "disposition": "Approved for production and retrofit",
            },
            "affects": [
                ("LSS-21-0004", "Revise", "B"),
                ("LSS-DWG-21-0005", "Revise", "B"),
            ],
            "transitions": [
                ("Submitted", "Raised from approved ECR LSS-ECR-00001."),
                ("Approved", "Revision B released under the design organisation "
                                "privilege on 2026-09-28. Proof pressure test repeated "
                                "and passed."),
                ("Released", "Delta first article raised and the spares batch released "
                             "on LSS-ARC-00002. Implementation complete."),
            ],
        },
        "ecn": {
            "pn": "LSS-ECN-00004",
            "title": "Notice of change - V-band coupling LSS-21-0004 revision B",
            "status": "Issued",
            "attrs": {
                "changeSummary":
                    "LSS-21-0004 is now at revision B. The clamp band thickness has "
                    "increased from 1.2 mm to 1.6 mm. The V-band geometry and the 5.6 Nm "
                    "installation torque are unchanged, and revision B is fully "
                    "interchangeable with revision A.",
                "effectivityValue":
                    "Airframe 004 and subsequent in production. Airframes 001 to 003 on "
                    "accomplishment of LSS-SB-21-001.",
                "effectivityType": "Serial number",
                "reason":
                    "Manufacturing: build to revision B from lot 26196. Supply chain: "
                    "update the purchase order to revision B and scrap remaining "
                    "revision A stock. Customer support: issue LSS-SB-21-001. Quality: "
                    "close LSS-FAI-00004.",
            },
            "distribution": ["LSS Manufacturing Engineering", "LSS Supply Chain",
                             "LSS Quality Assurance", "LSS Customer Support",
                             "LSS Airworthiness and Certification"],
            "transitions": [
                ("Submitted", "Raised on completion of LSS-ECO-00004."),
                ("Issued", "Issued to manufacturing, supply chain, quality, customer "
                           "support and airworthiness with a 14 day acknowledgement "
                           "deadline."),
            ],
        },
    },
    {
        "ecr": {
            "pn": "LSS-ECR-00002",
            "title": "Redesign ram air inlet scoop for improved pressure recovery",
            "status": "Under Review",
            "attrs": {
                "reason":
                    "Ground test of the environmental control system measured pack inlet "
                    "pressure 3.1 kPa below the value the performance model assumed, "
                    "which reduces cooling capacity margin on a hot day at maximum "
                    "take-off weight to below the design target.",
                "proposedSolution":
                    "Redesign the ram air inlet scoop with a longer diffuser and a "
                    "revised lip radius, in carbon/epoxy rather than the current glass "
                    "laminate. Predicted recovery improvement 4.2 kPa.",
                "justification":
                    "Cooling capacity margin on a hot day is a performance guarantee in "
                    "the sales specification. Recovering it in the scoop is cheaper than "
                    "uprating the air cycle machine, which would require requalification.",
                "costEstimate": 142000,
            },
            "affects": [
                ("LSS-21-0012", "Revise", "A"),
                ("LSS-DWG-21-0012", "Revise", "A"),
                ("LSS-21-INST-001", "Affected - no change", None),
                ("LSS-V-00002", "Affected - no change", None),
            ],
            "problems": [],
            "transitions": [
                ("Submitted", "Raised from the ground test performance shortfall."),
                ("Under Review", "At the change control board. The board has asked for "
                                 "the stress case on the revised attachment before it "
                                 "will disposition, which is why the part is held in "
                                 "stress review."),
            ],
        },
        "eco": None,
        "ecn": None,
    },
    {
        "ecr": {
            "pn": "LSS-ECR-00003",
            "title": "Qualify an alternate source for the headset jack panel",
            "status": "Submitted",
            "attrs": {
                "reason":
                    "Thorne Avionics has announced a last time buy on LSS-V-00015 for "
                    "31 March 2027. The part is fitted three times per aeroplane and has "
                    "no approved alternate source. A broker purchase has already produced "
                    "a suspect unapproved part nonconformance (LSS-NCR-00004).",
                "proposedSolution":
                    "Qualify a form, fit and function alternate from an approved source, "
                    "or redesign the jack panel as an LSS part. Carry out a last time buy "
                    "sufficient for 24 months of production in the meantime.",
                "justification":
                    "Obsolescence with no alternate source is a production stop risk, and "
                    "the counterfeit exposure is already demonstrated. Acting before the "
                    "last time buy date is materially cheaper than acting after it.",
                "costEstimate": 68000,
            },
            "affects": [
                ("LSS-V-00015", "Alternate source", None),
                ("LSS-23-INST-001", "Affected - no change", None),
            ],
            "problems": [],
            "transitions": [
                ("Submitted", "Raised by supply chain on the last time buy notice, with "
                              "LSS-NCR-00004 attached."),
            ],
        },
        "eco": None,
        "ecn": None,
    },
    {
        "ecr": {
            "pn": "LSS-ECR-00004",
            "title": "Add swivel interlock to passenger club seat",
            "status": "Approved",
            "attrs": {
                "reason":
                    "The equivalent safety finding sought for swivelling club seats "
                    "(certification review item CRI-25-002) depends on a mechanical means "
                    "of holding the forward-facing position during taxi, take-off and "
                    "landing. The revision A seat has no such means.",
                "proposedSolution":
                    "Add a mechanical swivel interlock, driven from the seat belt sign "
                    "circuit, that locks the seat forward-facing whenever the sign is "
                    "illuminated. Re-run the 16g dynamic test on the modified seat.",
                "justification":
                    "Without the interlock the club four arrangement cannot be "
                    "certificated, and the club four is a condition of the launch order.",
                "costEstimate": 215000,
            },
            "affects": [
                ("LSS-F-00010", "Revise", "B"),
                ("LSS-DWG-25-0005", "Revise", "B"),
                ("LSS-SPEC-PRO-004", "Revise", "B"),
                ("LSS-25-INST-001", "Affected - no change", None),
            ],
            "problems": [],
            "transitions": [
                ("Submitted", "Raised on the authority position at the CRI-25-002 "
                              "meeting."),
                ("Under Review", "At the change control board with the certification "
                                 "case and the retest cost."),
                ("Approved", "Approved. Certification blocking, so approved despite the "
                             "cost and the retest."),
            ],
        },
        "eco": {
            "pn": "LSS-ECO-00001",
            "title": "Implement passenger seat revision B with swivel interlock",
            "status": "Approved",
            "attrs": {
                "implementationPlan":
                    "Release LSS-F-00010 revision B, drawing LSS-DWG-25-0005 revision B "
                    "and procurement specification LSS-SPEC-PRO-004 revision B. Flow the "
                    "interlock requirement down to Caldera Seating. Re-run the 16g "
                    "dynamic test (LSS-CERT-QUAL-002). Raise a delta first article "
                    "(LSS-FAI-00005) with customer approval. Prepare service bulletin "
                    "LSS-SB-25-001 for seats already delivered.",
                "effectivityValue":
                    "Revision B is effective on all aeroplanes. Seats already delivered "
                    "are modified on accomplishment of LSS-SB-25-001.",
                "effectivityType": "All aeroplanes",
                "disposition": "Approved - certification blocking",
            },
            "affects": [
                ("LSS-F-00010", "Revise", "B"),
                ("LSS-DWG-25-0005", "Revise", "B"),
                ("LSS-SPEC-PRO-004", "Revise", "B"),
            ],
            "transitions": [
                ("Submitted", "Raised from approved ECR LSS-ECR-00004."),
                ("Approved", "Revision B released. The dynamic test has been run and "
                                "passed but the report is still in airworthiness "
                                "sign-off, so the change cannot complete and the service "
                                "bulletin cannot issue."),
            ],
        },
        "ecn": None,
    },
    {
        "ecr": None,
        "eco": {
            "pn": "LSS-ECO-00002",
            "title": "Release ECS controller software version 2.1.0",
            "status": "Closed",
            "attrs": {
                "implementationPlan":
                    "Release LSS-SW-0001 revision C carrying software version 2.1.0, "
                    "which corrects the integrator wind-up in the temperature control law "
                    "reported in LSS-PR-00002. Update the software accomplishment summary "
                    "and the configuration index. Issue a recommended service bulletin "
                    "for aeroplanes already delivered.",
                "effectivityValue":
                    "Version 2.1.0 is effective on airframe 004 and subsequent. "
                    "Airframes 001 to 003 on accomplishment of LSS-SB-21-002.",
                "effectivityType": "Serial number",
                "disposition": "Approved for production and retrofit",
            },
            "affects": [
                ("LSS-SW-0001", "Revise", "C"),
                ("LSS-CERT-SWP-004", "Revise", "A"),
                ("LSS-CERT-SWP-005", "Revise", "A"),
                ("LSS-E-00001", "Affected - no change", None),
            ],
            "problems": ["LSS-PR-00002"],
            "transitions": [
                ("Submitted", "Raised to close problem report LSS-PR-00002."),
                ("Approved", "Version 2.1.0 verified to DO-178C level C with "
                                "independence. Accomplishment summary and configuration "
                                "index updated."),
                ("Released", "Released 2026-09-15. Service bulletin LSS-SB-21-002 "
                             "issued."),
            ],
        },
        "ecn": {
            "pn": "LSS-ECN-00002",
            "title": "Notice of change - ECS controller software version 2.1.0",
            "status": "Issued",
            "attrs": {
                "changeSummary":
                    "LSS-SW-0001 is now at revision C, carrying software version 2.1.0. "
                    "The temperature control law integrator is now limited when the pack "
                    "outlet is at its lower limit, which removes the cabin temperature "
                    "oscillation in the descent.",
                "effectivityValue":
                    "Airframe 004 and subsequent. Airframes 001 to 003 on accomplishment "
                    "of LSS-SB-21-002.",
                "effectivityType": "Serial number",
                "reason":
                    "Manufacturing: load version 2.1.0 from airframe 004. Customer "
                    "support: issue LSS-SB-21-002 and record the loaded version per "
                    "aeroplane. Airworthiness: the configuration index LSS-CERT-SWP-005 "
                    "is the reference for any configuration question.",
            },
            "distribution": ["LSS Manufacturing Engineering", "LSS Customer Support",
                             "LSS Airworthiness and Certification",
                             "LSS Systems Engineering"],
            "transitions": [
                ("Submitted", "Raised on completion of LSS-ECO-00002."),
                ("Issued", "Issued with a 14 day acknowledgement deadline."),
            ],
        },
    },
]
