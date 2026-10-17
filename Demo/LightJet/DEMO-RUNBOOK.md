# NX-200 demo runbook

A ninety-minute demonstration of Nexus PLM to an aviation audience, built on the NX-200
light jet dataset. Eight acts. Each one names the screens, the objects to open, and the
question it answers — because an aerospace audience does not want a feature tour, they want
to know whether the system can answer the questions an auditor and a chief engineer ask.

Cut acts 6 and 7 for a forty-five minute slot. Never cut act 8.

**Before you start:** run `python seed/seed_lightjet.py --dry-run`. It takes two seconds
and tells you the dataset is intact. Then log in as `l.harkness` — an administrator who is
also an airworthiness signatory, so every screen in the demo is reachable without switching
accounts mid-flow.

---

## Act 1 — The data model is theirs, not ours (8 min)

**Screen:** Data Model Designer → `n5LightSpeedSystemsAircraftPart`

The opening claim: this is not a generic parts database with aviation fields bolted on. Walk
up the inheritance chain on screen:

```
ItemsBase                                  (platform)
  n5LightSpeedSystemsItemBase               programme, ATA chapter, export control
    n5LightSpeedSystemsTypeDesignItemBase   airworthiness class, DAL, mass, life limits
      n5LightSpeedSystemsEngBase            CAD ref, drawing, GD&T, interchangeability
        n5LightSpeedSystemsAircraftPart     material, NDT, fatigue, damage tolerance
```

Say why each attribute sits where it does: **an attribute lives on the lowest type that
needs it.** `exportClassification` is on the company base because every item has one.
`designAssuranceLevel` is on the type-design base because only approved-design items have
one. `ndtRequirement` is on the aircraft part because an interior cushion does not get
penetrant inspected.

Then the line that lands with a certification audience: **open
`n5LightSpeedSystemsNonTypeDesignItemBase`** and point out that `typeDesignData` is `false`
by default there and `true` on the type-design side. The system knows the difference between
a thing that changes the type certificate and a thing that does not.

**Show:** Numbering → `n5LssAircraftPart`. The ATA chapter is an `lov` segment ahead of the
counter, and the counter is keyed by everything before it — so chapter 21 and chapter 25
sequence independently. `LSS-21-0014` and `LSS-25-0003` are not the fourteenth and third
parts on the aeroplane, they are the fourteenth air conditioning part and the third
furnishings part. That is what an ATA-significant part number means.

> **If asked "can we change it?"** — yes, in this screen, and the change ships to another
> site as a customization set. That is act 7.

---

## Act 2 — The product structure (10 min)

**Screen:** BOM Builder → `LSS-21-INST-001` (Environmental control system installation)

Expand the tree. Four levels, 86.4 kg, weighed not estimated. Point out:

- **`LSS-21-0001` Bleed air supply duct assembly** — expand it. Titanium to AMS 4911, every
  weld penetrant inspected, part of the pressure boundary.
- **`LSS-V-00002` Air cycle machine** — click the link, not the part. Its revision rule is
  **pinned to revision A**, and the note says why: the DO-160G qualification campaign
  `LSS-CERT-QUAL-003` was run on that configuration and the credit does not carry forward.
  This is the moment to say that a revision rule is an engineering decision, not a
  preference. Most of this structure is `latest-released`; `LSS-21-0012` is `latest` because
  the redesigned scoop is still in design review; three links are pinned because a test
  credit is tied to a configuration.
- **`LSS-E-00001` ECS controller → `LSS-SW-0001`** — the software is in the bill of
  materials, pinned to revision C. An operator has to be able to say which software load is
  installed; a floating link cannot answer that.
- **Scrap percentage** on `LSS-21-0006` is 8 %, and 12 % on the composite manifold shell.
  Real process loss, and the cost rollup grosses up for it.

**Then switch to `LSS-25-INST-001`** (Cabin interior) and make the flammability point:
every interior item carries its `flammabilityTest` basis as a field — Part I vertical burn,
Part II oil burner for cushions, Part IV heat release for the large lining panels. Filter the
grid by it. **A late material substitution without a re-test is the most common cause of a
cabin certification delay, and here it is a query rather than a memory.**

---

## Act 3 — Requirements and traceability (12 min)

**Screen:** Requirements → NX-200 tree

Six levels. Walk one thread top to bottom:

```
LSS-REQ-ACFT-0001   Cabin altitude ≤ 2 400 m at maximum operating altitude
  LSS-REQ-SYS-0001    ECS shall maintain it, with rate-of-change limits
```

and a second thread that shows the certification basis driving the design:

```
LSS-REQ-CERT-0001   CS 23.2525 — pressurised cabin, single failure
  LSS-REQ-SYS-0002    No single failure shall cause a hazardous cabin pressure
    LSS-REQ-SUB-0001    Dual channel controller with independent sensing
      LSS-REQ-CMP-0001    Cabin pressure controller — ETSO, DAL B, DO-160G
```

`LSS-REQ-CMP-0001` is the procurement specification for the controller. Say that out loud:
the component-level requirement *is* what gets flowed down to the supplier, which is why
`supplierFlowdown` is a field on it.

**Now the part a systems engineer will lean forward for.** Open **`LSS-REQ-SUB-0002`** — an
independent mechanical cabin pressure safety valve. It has **no parent**, and
`derivedRequirement` is **true**. Explain: under ARP4754A a derived requirement is one that
did not come down from a higher level — it came out of the safety assessment. The standard
requires it to be fed back into that assessment, and its `derived-from` trace link points at
`LSS-CERT-SAFE-001`, the preliminary system safety assessment that raised it. **Filter the
grid on `derivedRequirement = true` and you have the review list the standard asks for**,
rather than a set of requirements nobody can find again.

**Then trace links.** Open `LSS-REQ-CMP-0005` (passenger seat) → Trace tab. Five links:
`implements` to the seat, `verified-by` to the dynamic test report, `satisfied-by` to the
compliance item. The `implements` link is **pinned to the seat revision the dynamic test was
run on** — and the seat is now at revision B, so the link is **suspect**. Say the sentence:
*"Nobody had to remember that. The system noticed."*

**Finish with the baseline.** Requirements → Baselines → *NX-200 requirements baseline at
certification plan issue 3* → **Compare**. This is the answer to "what has moved since we
agreed the requirements with the authority?", and it is a click.

---

## Act 4 — Certification compliance (12 min)

**Screen:** Kanban → *NX-200 Certification Compliance*

Twenty-three compliance items, seven lanes from Planned to Closed. Do not claim they are all
green — point at the ones that are not, because that is what makes it credible:

| Card | Lane | Why |
|---|---|---|
| `LSS-CERT-COMP-022` | **Planned** | Egress path with the customer divider. CRI-25-004. No method agreed yet because the divider is still in design. |
| `LSS-CERT-COMP-023` | **Method Agreed** | Cabin network security, against special condition SC-23-002. Method agreed with the authority, evidence not started. |
| `LSS-CERT-COMP-014` | **Submitted** | 16g occupant protection. Blocked: the passenger seat test report is still in airworthiness sign-off. |
| `LSS-CERT-COMP-010` | **Finding Open** | Damage tolerance of the antenna doubler. The authority wants the analysis re-run against the actual fatigue spectrum. |
| `LSS-CERT-COMP-002` | **Accepted** | Pressurisation, accepted under the DOA privilege on 30 April. |

Open **`LSS-CERT-COMP-002`**. Every field a compliance checklist row needs: the paragraph
(`CS 23.2525`), the consensus standard (`ASTM F3061/F3061M-22b`), the means of compliance
(`MC3 — Safety assessment`), the evidence, who accepted it, when, and the authority's level
of involvement. Then say: **this object is the checklist row.** The spreadsheet attached to
`LSS-CERT-PLAN-002` is a rendering of these objects, not the master. Open it to prove the
point, then close it again.

Open **`LSS-CERT-QUAL-004`** — the controller lightning test, result **Pass with
deviation**. Section 22 waveform 4 was applied at 90 % of the category level because the
laboratory generator could not reach it. The deviation is a field, the acceptance rationale
is recorded on the compliance item, and the installation sits in an interior lightning zone
which is why it is acceptable. **A pass with a deviation is a different certification
position from a clean pass, and it must not live in a paragraph somebody has to read.**

Finally open **`LSS-CERT-PLAN-001`** and point at `doaPrivilegesUsed` and
`levelOfInvolvementAgreed`. On a Part 21 Subpart J programme, agreeing the level of
involvement is the single most schedule-relevant agreement there is, because it is what lets
most items close under the design organisation privilege instead of item by item with the
authority.

---

## Act 5 — The change chain, end to end (15 min)

This is the act that sells the system. One story, seven objects, no slides.

**Start at the symptom.** Open **`LSS-PR-00001`** — three operators have each found a bleed
duct coupling loose at the 100 hour inspection. Torque 3.1 to 4.2 Nm against 5.6 Nm
required. *Three independent reports of the same symptom is a design question, not three
maintenance errors.*

**The nonconformance.** → **`LSS-NCR-00003`**. Severity Major, detected **In service**,
`safetyImpact` **true**, `escapeToCustomer` **true**, customer notified 14 July, three prior
recurrences, cost 38 200. Make the point that safety impact and escape are **two separate
fields** because they are two separate questions: an escape is a customer notification
matter, a safety impact is a continued airworthiness matter, and one does not imply the
other. Root cause: the 1.2 mm clamp band relaxes under thermal cycling; the original design
used a room-temperature relaxation figure.

**The change request.** → **`LSS-ECR-00001`**. Reason, proposed solution, justification,
cost 84 000. Affected items tab: four items, each with a `changeAction` — `LSS-21-0004`
*Revise* to B, `LSS-DWG-21-0005` *Revise* to B, and two *Affected — no change*. Transitions
tab shows Submitted → Under Review → Approved with the change control board's comment on
each.

> **Show the board:** Kanban → *Engineering Change Control Board*. It is bound to the
> platform's own `ECR` type, not a copy of it. `LSS-ECR-00002` sits in Under Review because
> the board asked for the stress case first; `LSS-ECR-00003` is the obsolescence case on the
> headset jack panel.

**The change order.** → **`LSS-ECO-00004`**, promoted from the ECR, linked both ways.
Implementation plan, effectivity: revision B effective on airframe 004 and subsequent, and
on 001–003 on accomplishment of the service bulletin.

**The revision.** → **`LSS-21-0004`**. Revision A is **Superseded** and still there —
*parts built to it are in service, so it cannot be deleted*. Revision B is Released. Open
the Where Used tab: the duct assembly and the installation above it.

**The proof.** → **`LSS-FAI-00004`**, a **Delta FAI** against revision B. Six characteristics
re-verified, not twenty-two — the rest carry forward from the full first article on revision
A, which is exactly what a delta is for. Forms 1 and 2 complete, **Form 3 still open**, so
the submission is not yet complete and the card sits in Under Review. Open the attached
workbook and show Forms 1, 2 and 3 on three sheets, with the balloon numbers on Form 3
agreeing with the ballooned issue of the drawing named on Form 1.

**The notice.** → **`LSS-ECN-00004`**. Distribution to five groups with a 14-day
acknowledgement deadline, and an acknowledgement list showing who has read it.

**The fleet.** → **`LSS-SB-21-001`**. Mandatory. Effectivity, compliance within 300 flight
hours or 12 months, 6.5 hours labour, kit part number, **and a proposed EASA airworthiness
directive against it** — so compliance stops being a recommendation and becomes a legal
obligation on the operator. Then **`LSS-ARC-00002`**, the dual 8130-3 / Form 1 for the spares
batch, whose eligibility statement says what an operator may fit and until when.

**Close the loop.** Go back to `LSS-REQ-CMP-0008` and show the pinned trace link onto
`LSS-21-0004` sitting **suspect**, because the target moved to revision B. Seven objects, one
thread, and the last link in the chain reported itself.

---

## Act 6 — Quality, suppliers and auditability (10 min)

**Screen:** Kanban → *Nonconformance and Material Review Board*

Six nonconformances, and each one is a different AS9100D question:

- **`LSS-NCR-00001`** — dimensional, dispositioned **Use as is** on the strength of a stress
  re-check, with airworthiness concurrence because the fitting is flight safety critical.
- **`LSS-NCR-00002`** — weld porosity on a pressure boundary, **Scrap**. Say the line: *the
  disposition took four minutes and the corrective action on the silenced gas-flow alarm
  took three weeks.*
- **`LSS-NCR-00004`** — **suspect unapproved part**, AS9100D **8.1.4**. Date codes did not
  match the manufacturer's sequence and the certificate named a distributor not on the
  authorised list. Quarantined on receipt, never stocked, returned to supplier. Then open
  **`LSS-COC-00004`** — the rejected certificate of conformity, status **Withdrawn**, *kept
  rather than deleted*, because the record that a bad certificate was received and caught
  **is** the audit evidence that the control worked.
- **`LSS-NCR-00005`** — sealant applied four days past shelf life. Because the consumable is
  batch traceable and the batch was recorded against the installation, the affected joints
  were found in an hour rather than by stripping the pack bay.
- **`LSS-NCR-00006`** — found by **internal audit**, not inspection: seven assemblies
  inspected on a check fixture whose calibration had lapsed. The nonconformance is against
  **traceability**, not dimension — an uncalibrated fixture does not make a part wrong, it
  makes the record worthless. Open **`LSS-TL-0002`**: status **Restricted**, calibration due
  30 September, quarantined.

**Then the audit sample.** Every quality record carries a `qmsClause` field. Filter on
`8.1.4 Prevention of Counterfeit Parts` and you have the audit sample for that clause,
assembled from the data rather than from a folder. Do this live — it is a five-second
demonstration of something auditors spend days on.

**Suppliers.** Open **`LSS-SQR-00006`** (Pyrosafe Materials): **Probation**, three major
findings, 2 680 ppm delivered quality, 79.4 % on-time delivery, for-cause audit triggered by
the shelf-life escape. Then **`LSS-SQR-00002`** (Thorne Avionics): AS9100 certificate expires
28 February 2027. *An expiring certificate is a report, not a diary reminder.*

---

## Act 7 — Programme, and shipping the model (8 min)

**Screen:** Schedule → NX-200 development and type certification

AS9145 APQP phases — Planning, Product design, Process design, Product and process
validation, Production — with gate reviews on the boundaries. Programme health **At-Risk**.

Open **`NX00200305`** "Release passenger seat dynamic test report": **Late**, on the critical
path, 80 % complete. Then show what is waiting on it — two compliance items
(`LSS-CERT-COMP-014`, `LSS-CERT-COMP-015`), one milestone (`NX00200105` Cabin interior
certification, forecast seven weeks late) and one service bulletin (`LSS-SB-25-001`, held in
review). **One signature. That is the answer to "what is actually holding the programme
up?", and it took three clicks.**

**Then Customization Sets → Export.** The whole data model — 42 types, 19 numbering schemas,
6 workflows, 35 security models, 88 classification folders, 10 groups and 6 boards — exports
as one signed file. Every entry carries its SHA-256 and the manifest carries its own, so a
package that opens cleanly is exactly what its author sealed. Import on another site shows a
diff per entry (New / Identical / Modified / Conflict), takes a snapshot before applying, and
**History → Roll back** reverses it.

That is the answer to "how do we move this to our own tenant?" and to "what happens when we
get it wrong?"

---

## Act 8 — Auditability, in one question (5 min)

Never cut this. Ask the room to pick the question, then answer it live. All three work:

**"Show me that the cabin pressure safety valve is qualified, and why it exists at all."**
`LSS-V-00006` → failure effect **Catastrophic** → trace links → `LSS-REQ-SUB-0002`, a
**derived** requirement → `derived-from` → `LSS-CERT-SAFE-001`, the safety assessment that
raised it → `verified-by` → `LSS-CERT-QUAL-005`, cracking pressure 0.618 and 0.624 bar
against 0.62 ± 0.02, with no power and the outflow valve failed closed → `satisfied-by` →
`LSS-CERT-COMP-003`, **Accepted** by `g.rossi` on 29 May under the DOA privilege. *Five hops
from a part to a signature.*

**"A supplier tells you a material batch was out of specification. What is affected?"**
`LSS-CM-0001` → Where Used → `LSS-21-INST-001` → the batch is recorded against airframe 003
on `LSS-NCR-00005`, with the sealed joints identified from the batch record.

**"Who changed this, and when?"** Any object → History. Every revision, every status
transition with the approver's comment, every attribute change with its old and new value,
every board move with the comment the mover typed. Not a log file — rows on the object.

**Close on this:** everything in this demo was one dataset. No slides, no mock-ups, no
screen that was prepared for a question. The reason a question could be answered in three
clicks is that the data model holds the distinctions that aviation actually makes — type
design data against production record, safety impact against customer escape, a derived
requirement against an allocated one, a pass against a pass with a deviation. **Get those
distinctions into the model and the audit answers itself. Leave them out and no amount of
reporting puts them back.**

---

## Appendix — objects worth having open in tabs

| Object | Why |
|---|---|
| `LSS-21-INST-001` | The ATA 21 structure, four levels, pinned and floating links |
| `LSS-25-INST-001` | The cabin, flammability basis per item |
| `LSS-21-0004` | Revision A superseded, revision B released — the change story's spine |
| `LSS-REQ-SUB-0002` | The ARP4754A derived requirement |
| `LSS-REQ-CMP-0005` | Suspect trace link onto the revised seat |
| `LSS-CERT-COMP-002` | A compliance item accepted under the DOA privilege |
| `LSS-CERT-COMP-010` | A compliance item with an open authority finding |
| `LSS-CERT-QUAL-004` | Pass with deviation |
| `LSS-NCR-00003` | Safety impact and escape, both true |
| `LSS-NCR-00004` | Counterfeit parts, AS9100D 8.1.4 |
| `LSS-COC-00004` | A withdrawn certificate, kept as evidence |
| `LSS-FAI-00004` | Delta FAI, Form 3 still open |
| `LSS-SB-21-001` | Mandatory bulletin with a proposed AD against it |
| `LSS-ARC-00003` | Prototype release, non-approved design data flagged |
| `LSS-SQR-00006` | A supplier on probation |
| `NX00200305` | The one late task everything is waiting on |

## Appendix — questions that will be asked, and the honest answer

**"Does it hold the 3D model?"** Yes — the platform has a Three.js viewer and the add-ins
check CAD in and out. This dataset does not ship geometry, so the viewer will be empty.
Say so rather than navigating away from it.

**"Can it talk to our CAD?"** There are add-ins for FreeCAD, CATIA V5, Office, LibreOffice,
ONLYOFFICE and others, all over the same add-in SDK. Not part of this dataset.

**"Is this a real aeroplane?"** No, and say it clearly and early — Light Speed Systems and
the NX-200 are fictional, every document carries a demonstration notice on its face, and the
suppliers and people are invented. The standards, clause numbers and process parameters are
real, which is the part that matters.

**"How long did this dataset take to build?"** It is generated from about three thousand
lines of declarative Python, and the validator checks it holds together in two seconds. Worth
saying, because the real question underneath it is how long *their* data would take.
