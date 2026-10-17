"""What each part in the product structure points at: its drawing, its specifications,
its material and its evidence.

Until this existed, a part said `drawingNumber = "LSS-DWG-21-0005"` in a text field. That
is a label, not a link: you cannot open the drawing from the part, you cannot ask which
parts a specification governs, and revising the drawing tells the part nothing. Here they
are real object references, so the relationship is navigable in both directions and the
revision rule is an explicit decision.

The kinds come from the Engine's own reference vocabulary:

    DrawingLink        the target is the drawing that depicts the source part
    SpecificationLink  the target states requirements the source must meet
    RelatedLink        the catch-all, used for material and for evidence

Revision rules matter as much here as in the bill of materials:

    latest-released    the default. The part follows the released drawing.
    latest             right while something is still in work.
    pinned             right when the link is about ONE revision - a test report proves a
                       specific configuration, and a ballooned drawing issue is the one a
                       first article was written against.
"""

RELEASED = "latest-released"
LATEST = "latest"
PINNED = "pinned"

DRAWING = "DrawingLink"
SPECIFICATION = "SpecificationLink"
RELATED = "RelatedLink"


def ref(source, target, kind=RELATED, rule=RELEASED, pin=None, note=None):
    return {"source": source, "target": target, "kind": kind, "rule": rule,
            "pin": pin, "note": note}


# ─────────────────────────────────────────────────────────────────────────────
# Part → its drawing
# ─────────────────────────────────────────────────────────────────────────────

DRAWINGS = [
    ref("LSS-21-INST-001", "LSS-DWG-21-0001", DRAWING,
        note="The installation drawing. Everything in the pack bay is positioned by it."),
    ref("LSS-21-0001", "LSS-DWG-21-0002", DRAWING),
    ref("LSS-21-0004", "LSS-DWG-21-0005", DRAWING, rule=PINNED, pin="B",
        note="Pinned to issue B, the ballooned issue the delta first article "
             "LSS-FAI-00004 is written against. A Form 3 that does not name the issue "
             "its balloon numbers came from is not evidence of anything."),
    ref("LSS-21-0005", "LSS-DWG-21-0006", DRAWING),
    ref("LSS-21-0012", "LSS-DWG-21-0012", DRAWING, rule=LATEST,
        note="Follows latest: the scoop redesign and its drawing are both in work and "
             "move together."),
    ref("LSS-E-00001", "LSS-DWG-21-0015", DRAWING),
    ref("LSS-W21-001", "LSS-DWG-21-0016", DRAWING),
    ref("LSS-23-INST-001", "LSS-DWG-23-0001", DRAWING),
    ref("LSS-23-0001", "LSS-DWG-23-0004", DRAWING),
    ref("LSS-W23-001", "LSS-DWG-23-0007", DRAWING),
    ref("LSS-W23-003", "LSS-DWG-23-0009", DRAWING, rule=LATEST),
    ref("LSS-25-INST-001", "LSS-DWG-25-0001", DRAWING),
    ref("LSS-F-00001", "LSS-DWG-25-0002", DRAWING),
    ref("LSS-F-00010", "LSS-DWG-25-0005", DRAWING, rule=PINNED, pin="B",
        note="Pinned to issue B, which carries the swivel interlock. Issue A describes a "
             "seat that may no longer be built."),
    ref("LSS-25-0001", "LSS-DWG-25-0004", DRAWING),
    ref("LSS-F-00020", "LSS-DWG-25-0007", DRAWING),
    ref("LSS-F-00021", "LSS-DWG-25-0007", DRAWING,
        note="Left and right hand share one drawing, distinguished by dash number - the "
             "normal aerospace practice."),
    ref("LSS-25-0002", "LSS-DWG-25-0011", DRAWING),
    ref("LSS-F-00050", "LSS-DWG-25-0013", DRAWING),
    ref("LSS-F-00110", "LSS-DWG-25-0018", DRAWING, rule=LATEST),
]


# ─────────────────────────────────────────────────────────────────────────────
# Part → the specifications it is built and inspected to
# ─────────────────────────────────────────────────────────────────────────────

SPECIFICATIONS = [
    # Process specifications: how it is made.
    ref("LSS-21-0001", "LSS-PS-0001", SPECIFICATION,
        note="Titanium welding, frozen process plan. The porosity nonconformance "
             "LSS-NCR-00002 was a departure from this, not a tolerance on it."),
    ref("LSS-21-0001", "LSS-PS-0003", SPECIFICATION,
        note="Penetrant inspection of every weld."),
    ref("LSS-21-0002", "LSS-PS-0003", SPECIFICATION),
    ref("LSS-21-0003", "LSS-PS-0003", SPECIFICATION),
    ref("LSS-21-0004", "LSS-PS-0002", SPECIFICATION),
    ref("LSS-21-0006", "LSS-PS-0004", SPECIFICATION),
    ref("LSS-21-0007", "LSS-PS-0004", SPECIFICATION),
    ref("LSS-21-0009", "LSS-PS-0005", SPECIFICATION),
    ref("LSS-21-0012", "LSS-PS-0005", SPECIFICATION),
    ref("LSS-23-0001", "LSS-PS-0004", SPECIFICATION),
    ref("LSS-25-0001", "LSS-PS-0004", SPECIFICATION),
    ref("LSS-25-0002", "LSS-PS-0005", SPECIFICATION),
    ref("LSS-25-0003", "LSS-PS-0004", SPECIFICATION),
    ref("LSS-21-INST-001", "LSS-PS-0006", SPECIFICATION,
        note="Sealant application to the pressure boundary."),

    # Material specifications: what it is made of.
    ref("LSS-21-0009", "LSS-SPEC-MAT-003", SPECIFICATION),
    ref("LSS-21-0010", "LSS-SPEC-MAT-007", SPECIFICATION),
    ref("LSS-21-0012", "LSS-SPEC-MAT-001", SPECIFICATION),
    ref("LSS-25-0002", "LSS-SPEC-MAT-002", SPECIFICATION),

    # Design and procurement specifications: what it has to do.
    ref("LSS-21-INST-001", "LSS-SPEC-DES-001", SPECIFICATION),
    ref("LSS-23-INST-001", "LSS-SPEC-DES-002", SPECIFICATION),
    ref("LSS-25-INST-001", "LSS-SPEC-DES-003", SPECIFICATION),
    ref("LSS-V-00004", "LSS-SPEC-PRO-001", SPECIFICATION,
        note="The procurement specification flowed down to Meridian for the controller."),
    ref("LSS-V-00006", "LSS-SPEC-PRO-002", SPECIFICATION),
    ref("LSS-V-00010", "LSS-SPEC-PRO-003", SPECIFICATION),
    ref("LSS-F-00010", "LSS-SPEC-PRO-004", SPECIFICATION, rule=PINNED, pin="B",
        note="Pinned to revision B, which is where the swivel interlock requirement "
             "entered. Caldera build to this issue."),
    ref("LSS-F-00020", "LSS-SPEC-PRO-005", SPECIFICATION),

    # Installation and test specifications.
    ref("LSS-21-INST-001", "LSS-SPEC-PRC-004", SPECIFICATION),
    ref("LSS-21-INST-001", "LSS-SPEC-PRC-011", SPECIFICATION),
    ref("LSS-23-INST-001", "LSS-SPEC-PRC-012", SPECIFICATION),
    ref("LSS-W21-001", "LSS-SPEC-TST-009", SPECIFICATION,
        note="EWIS zonal inspection and separation verification."),
    ref("LSS-W23-001", "LSS-SPEC-TST-009", SPECIFICATION),
    ref("LSS-W23-002", "LSS-SPEC-TST-009", SPECIFICATION),
    ref("LSS-SW-0001", "LSS-SPEC-SRS-001", SPECIFICATION,
        note="The software requirements specification the level C verification is "
             "written against."),
]


# ─────────────────────────────────────────────────────────────────────────────
# Part → the evidence that it is airworthy
# ─────────────────────────────────────────────────────────────────────────────
# A part and the report that substantiates it. Pinned wherever the evidence is about one
# configuration, which for test evidence is almost always.

EVIDENCE = [
    ref("LSS-V-00002", "LSS-CERT-QUAL-003", RELATED, rule=PINNED, pin="A",
        note="The DO-160G qualification campaign. Pinned, and the bill of materials pins "
             "the part too: the credit is against this configuration and does not carry "
             "forward without a delta assessment."),
    ref("LSS-V-00004", "LSS-CERT-QUAL-004", RELATED, rule=PINNED, pin="A",
        note="Pass with deviation - section 22 waveform 4 at 90 percent of category. The "
             "acceptance rationale is on compliance item LSS-CERT-COMP-002."),
    ref("LSS-V-00006", "LSS-CERT-QUAL-005", RELATED, rule=PINNED, pin="A",
        note="Cracking pressure test with no power and the outflow valve failed closed. "
             "This is the evidence behind the derived requirement LSS-REQ-SUB-0002."),
    ref("LSS-F-00001", "LSS-CERT-QUAL-001", RELATED, rule=PINNED, pin="A",
        note="16g dynamic test of the critical seat position."),
    ref("LSS-F-00010", "LSS-CERT-QUAL-002", RELATED, rule=LATEST,
        note="Follows latest: the report is still in airworthiness sign-off, and two "
             "compliance items and a service bulletin are waiting on it."),
    ref("LSS-F-00002", "LSS-CERT-QUAL-007", RELATED, rule=PINNED, pin="A",
        note="Appendix F Part II oil burner. The credit is construction specific, which "
             "is why the cushion is pinned in the bill of materials as well."),
    ref("LSS-F-00011", "LSS-CERT-QUAL-007", RELATED, rule=PINNED, pin="A"),
    ref("LSS-F-00020", "LSS-CERT-QUAL-008", RELATED, rule=PINNED, pin="A",
        note="Heat release 41 kW/m2 and smoke density 94, tested with the production "
             "decorative finish."),
    ref("LSS-F-00030", "LSS-CERT-QUAL-008", RELATED, rule=PINNED, pin="A"),
    ref("LSS-F-00040", "LSS-CERT-QUAL-009", RELATED, rule=PINNED, pin="A"),
    ref("LSS-F-00100", "LSS-CERT-QUAL-011", RELATED, rule=PINNED, pin="A"),
    ref("LSS-E-00001", "LSS-CERT-EMI-001", RELATED,
        note="EMI compliance assessment as installed."),
    ref("LSS-23-INST-001", "LSS-CERT-EMI-002", RELATED,
        note="Compliant with an installation limitation, which the audio panel software "
             "enforces."),
    ref("LSS-21-INST-001", "LSS-CERT-SAFE-002", RELATED,
        note="System safety assessment: catastrophic overpressure at 4.2E-10 per flight "
             "hour against a 1E-9 target."),
    ref("LSS-SW-0001", "LSS-CERT-SWP-005", RELATED, rule=PINNED, pin="A",
        note="The software configuration index identifies exactly what is in the released "
             "load. Pinned at the index's own revision A, which is the issue covering "
             "software version 2.1.0 - revision C belongs to the software item, not to "
             "this document."),
    ref("LSS-23-0001", "LSS-DWG-23-0004", RELATED,
        note="Damage tolerance analysis reference; the open authority finding on "
             "LSS-CERT-COMP-010 is against this item's inspection threshold."),
    ref("LSS-21-0001", "LSS-FAI-00001", RELATED,
        note="Full first article, 48 characteristics, no nonconformances."),
    ref("LSS-25-0001", "LSS-FAI-00002", RELATED,
        note="Accepted with deviation: a fillet radius 0.2 mm under drawing minimum, "
             "dispositioned use-as-is on the stress re-check."),
    ref("LSS-F-00020", "LSS-FAI-00003", RELATED),
    ref("LSS-21-0004", "LSS-FAI-00004", RELATED, rule=LATEST,
        note="Delta first article against revision B. Form 3 still open."),
    ref("LSS-F-00010", "LSS-FAI-00005", RELATED, rule=LATEST),
]


# ─────────────────────────────────────────────────────────────────────────────
# Supplier part → its certificate
# ─────────────────────────────────────────────────────────────────────────────

CERTIFICATES = [
    ref("LSS-V-00002", "LSS-COC-00001", RELATED,
        note="Certificate of conformity for the delivered air cycle machines."),
    ref("LSS-V-00004", "LSS-COC-00002", RELATED),
    ref("LSS-V-00022", "LSS-COC-00003", RELATED),
    ref("LSS-V-00015", "LSS-COC-00004", RELATED,
        note="The WITHDRAWN certificate. Kept and linked on purpose: the record that a "
             "bad certificate was received and caught is the audit evidence that the "
             "counterfeit-parts control worked."),
    ref("LSS-F-00010", "LSS-COC-00005", RELATED),
    ref("LSS-21-INST-001", "LSS-ARC-00001", RELATED,
        note="EASA Form 1 for airframe 002."),
    ref("LSS-21-0004", "LSS-ARC-00002", RELATED,
        note="Dual release for the revision B spares batch."),
    ref("LSS-25-INST-001", "LSS-ARC-00003", RELATED,
        note="Prototype release against non-approved design data - not eligible for a "
             "type certificated aeroplane."),
]


ALL_REFERENCES = DRAWINGS + SPECIFICATIONS + EVIDENCE + CERTIFICATES
