"""Light Speed Systems Word templates, and the type blocks that attach them.

A customization set can carry template bytes. A type with a `template` block gives every
new document of that kind a starting point, and the Customization Sets apply uploads the
bytes to the Vault content-addressed by their own SHA-256 — the same key the package used,
so the template is the same file on every site that applies the package.

Three templates rather than one, because a certification report and a nonconformance
record do not want the same front matter:

    controlled   Specifications, interface control documents, plans, certification
                 programme documents. Approval block, revision history, scope.
    report       Qualification and test reports, safety assessments, EMI assessments.
                 Adds the test configuration and result sections an authority reads first.
    quality      Nonconformances and process specifications. Adds containment,
                 disposition and corrective action.

Each carries the Light Speed Systems title block, the DOA reference, and the
"uncontrolled when printed" footer a controlled document has to have.
"""

from __future__ import annotations

import hashlib
from io import BytesIO

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor

COMPANY = "Light Speed Systems"
DOA = "EASA.21J.0742"
ACCENT = RGBColor(0x1F, 0x3A, 0x5F)

PLACEHOLDER = (
    "[Replace this text. Nexus fills the document number, title, issue and approval "
    "names from the object's own fields, so do not retype them here.]"
)


def _base(title_hint: str, subtitle: str):
    document = Document()
    normal = document.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10)

    header = document.sections[0].header.paragraphs[0]
    header.text = f"{COMPANY}   |   NX-200   |   Design Organisation Approval {DOA}"
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT

    footer = document.sections[0].footer.paragraphs[0]
    footer.text = ("UNCONTROLLED WHEN PRINTED — the controlled copy is the object in "
                   "Nexus PLM")
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER

    heading = document.add_heading(title_hint, level=0)
    heading.runs[0].font.color.rgb = ACCENT
    lead = document.add_paragraph(subtitle)
    lead.runs[0].italic = True

    table = document.add_table(rows=0, cols=2)
    table.style = "Light Grid Accent 1"
    for label in ("Document number", "Title", "Issue", "Status", "Author", "Checked",
                  "Approved", "Issue date", "Certification basis", "Retention class",
                  "Confidentiality"):
        cells = table.add_row().cells
        cells[0].text = label
        cells[1].text = "[from the PLM object]"
        for paragraph in cells[0].paragraphs:
            for run in paragraph.runs:
                run.bold = True

    document.add_heading("Revision history", level=1)
    history = document.add_table(rows=1, cols=4)
    history.style = "Light List Accent 1"
    for index, column in enumerate(("Issue", "Date", "Description of change",
                                    "Approved")):
        history.rows[0].cells[index].text = column
    row = history.add_row().cells
    row[0].text = "A"
    row[1].text = "[date]"
    row[2].text = "First issue."
    row[3].text = "[name]"
    return document


def _close(document):
    document.add_heading("Statement on this document", level=1)
    note = document.add_paragraph(
        "This document is controlled in Nexus PLM. The object is the master; this file "
        "is its content. Do not edit a released issue — revise the object and edit the "
        "new revision, so the change is on the record.")
    note.runs[0].font.size = Pt(8)
    note.runs[0].font.color.rgb = RGBColor(0x8B, 0x28, 0x28)
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def controlled_document() -> bytes:
    document = _base("[Document title]",
                     "Light Speed Systems controlled document")
    for heading, body in (
        ("1. Purpose and scope",
         "State what this document covers and, just as importantly, what it does not."),
        ("2. Applicable documents",
         "List the documents this one depends on by number and issue. Reference them "
         "from the object as well, so the dependency is navigable and not just text."),
        ("3. Requirements",
         "State requirements as measurable values with tolerances. Where a figure comes "
         "from the certification basis, write it out in full rather than referring to "
         "it — a supplier reading a reference will eventually read the wrong one."),
        ("4. Verification",
         "For each requirement, how compliance is shown: inspection, analysis, "
         "demonstration, test or similarity."),
        ("5. Notes", PLACEHOLDER),
    ):
        document.add_heading(heading, level=1)
        document.add_paragraph(body)
    return _close(document)


def report_document() -> bytes:
    document = _base("[Report title]",
                     "Light Speed Systems certification evidence report")
    for heading, body in (
        ("1. Purpose",
         "Which requirement or compliance item this report provides evidence for. Name "
         "the regulation paragraph and the means of compliance."),
        ("2. Article under test",
         "Part number, revision and serial number of exactly what was tested. Evidence "
         "that does not identify its configuration proves nothing."),
        ("3. Test configuration",
         "Standard and revision, sections, environmental categories, laboratory and its "
         "accreditation, dates, and the test plan this was run against."),
        ("4. Results",
         "The measured values against the required values. State the outcome plainly: "
         "pass, pass with deviation, or fail."),
        ("5. Deviations",
         "Any departure from the test plan, with the rationale for why the result is "
         "still valid. A pass with a deviation is a different certification position "
         "from a clean pass and must not be presented as one."),
        ("6. Conclusion",
         "What is now substantiated, and what is not."),
    ):
        document.add_heading(heading, level=1)
        document.add_paragraph(body)
    return _close(document)


def quality_record() -> bytes:
    document = _base("[Record title]",
                     "Light Speed Systems quality record")
    for heading, body in (
        ("1. Description",
         "What was found, where, by whom and against which requirement."),
        ("2. Affected product",
         "Part number, revision, serial or lot numbers and quantity. Answer 'where else "
         "is this?' before anything else."),
        ("3. Containment",
         "What was done immediately to stop the nonconforming product moving."),
        ("4. Disposition",
         "Use as is, rework, repair to an approved scheme, scrap or return — and the "
         "authority for it. A disposition that leaves a deviation in the aircraft needs "
         "an airworthiness signature."),
        ("5. Root cause",
         "Why it happened. Not who."),
        ("6. Corrective action",
         "What changes so it does not recur. The disposition deals with the parts; this "
         "deals with the cause."),
    ):
        document.add_heading(heading, level=1)
        document.add_paragraph(body)
    return _close(document)


# Which template each document type starts from.
TEMPLATES = {
    "controlled": {
        "builder": controlled_document,
        "fileName": "LSS-Controlled-Document-Template.docx",
        "name": "Light Speed Systems controlled document",
        "description": "Title block, revision history, approval block and the standard "
                       "section set for a specification, interface control document or "
                       "plan.",
        "types": ["Specification", "Icd", "SwPlan", "PrjSpecificCertPlan"],
    },
    "report": {
        "builder": report_document,
        "fileName": "LSS-Evidence-Report-Template.docx",
        "name": "Light Speed Systems certification evidence report",
        "description": "For qualification and test reports, safety assessments and EMI "
                       "assessments. Carries the article-under-test and deviation "
                       "sections an authority reads first.",
        "types": ["QualTestPlan", "QualTestReport", "SafetyAssessment", "EMICAR",
                  "ComplianceReport"],
    },
    "quality": {
        "builder": quality_record,
        "fileName": "LSS-Quality-Record-Template.docx",
        "name": "Light Speed Systems quality record",
        "description": "For nonconformances and process specifications. Containment "
                       "before disposition, and root cause separate from both.",
        "types": ["Ncr", "ProcessSpec", "SupplierQualRecord"],
    },
}

DOCX_MIME = ("application/vnd.openxmlformats-officedocument."
             "wordprocessingml.document")


def build_all() -> dict[str, dict]:
    """Every template's bytes and its SHA-256, which is also its Vault key."""
    built = {}
    for key, spec in TEMPLATES.items():
        data = spec["builder"]()
        built[key] = {
            **spec,
            "bytes": data,
            "sha256": hashlib.sha256(data).hexdigest(),
            "size": len(data),
        }
    return built


def template_block(entry: dict) -> dict:
    """The `template` block a type carries, pointing at the packaged bytes."""
    return {
        "name": entry["name"],
        "description": entry["description"],
        "mimeType": DOCX_MIME,
        "revisions": [{
            "vaultKey": entry["sha256"],
            "fileName": entry["fileName"],
            "fileSize": entry["size"],
            "uploadedBy": "demo-build",
            # Fixed, so the package stays byte-reproducible.
            "uploadedAt": "2026-10-17T00:00:00.0000000+00:00",
        }],
    }
