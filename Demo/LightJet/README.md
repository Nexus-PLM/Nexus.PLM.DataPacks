# NX-200 Light Jet — aviation demonstration dataset

A complete, self-consistent aviation dataset for demonstrating Nexus PLM to an aerospace
audience: the data model, the part numbering schemas, the ATA classification tree, the
kanban boards, the approval workflows, a multi-level product structure for ATA chapters 21,
23 and 25, a six-level requirement tree with traceability, the certification evidence set,
the quality records, and the change chains that join them together.

The company (**Light Speed Systems**), the aeroplane (**NX-200**), the suppliers, the
operator and the people are all fictional. The standards, clause numbers, process
parameters and document structures are real, because an aerospace audience will check them.

---

## What is here

```
Demo/LightJet/
  model/                      The data model, as data
    aviation_model.py           Lifecycle sets, numbering schemas, groups, workflows
    aviation_types.py           7 abstract bases + 35 concrete types
    build_customization.py      Seals it into a .nexuscustomization package
  seed/                       The content, and the loader
    lightjet_data.py            People, suppliers, ATA 21 items
    lightjet_items.py           ATA 23 and ATA 25 items
    lightjet_structure.py       The bill of materials
    lightjet_requirements.py    Requirements, trace links, baseline
    lightjet_documents.py       Drawings, specs, ICDs, certification evidence
    lightjet_quality.py         FAI, NCR, CoC, release certificates, SBs, changes
    lightjet_projects.py        Projects and the work breakdown
    seed_lightjet.py            Validator + loader
  docgen/
    generate_documents.py       Writes the 105 real PDF / Word / Excel files
  verify/
    VerifyPackage.csproj        Opens the sealed package with the Engine's own reader
    Program.cs
  build/                      Generated output (not committed)
  DEMO-RUNBOOK.md             The demo narrative, screen by screen
  README.md                   This file
```

---

## Build it

```bash
cd Demo/LightJet

# 1. Seal the data model into a customization-set package.
python model/build_customization.py
#    -> build/lightjet-nx200-baseline-1.0.0.nexuscustomization

# 2. Prove the package opens, using the Engine's own reader rather than trusting ours.
dotnet run --project verify/VerifyPackage.csproj -- \
  build/lightjet-nx200-baseline-1.0.0.nexuscustomization

# 3. Generate the document files.
python docgen/generate_documents.py
#    -> build/documents/  (31 PDF, 62 Word, 12 Excel)

# 4. Validate the dataset without touching a server.
python seed/seed_lightjet.py --dry-run
```

Step 4 is the one worth running before every demo. It resolves every type through its
inheritance chain — the out-of-the-box bases included — and checks that every attribute,
status, part number, bill-of-materials link, trace link and classification path actually
resolves. **A misspelled attribute name is accepted silently by the Engine**: it lands in
the revision's extension data and simply never appears on a form. Without this check a demo
dataset can load with a clean exit code and a third of its content invisible.

---

## Load it

Order matters. The customization set has to be applied **before** the objects, because the
objects are of types it creates. The loader refuses to start otherwise and says so.

1. **Apply the customization set.** Open the **Customization Sets** app as an administrator,
   go to **Import**, choose `build/lightjet-nx200-baseline-1.0.0.nexuscustomization`, read
   the diff, and apply. The site takes a snapshot first, so **History → Roll back** puts it
   back exactly as it was.

2. **Load the objects.**

   ```bash
   python seed/seed_lightjet.py \
     --engine http://192.168.1.47:5000 \
     --vault  http://192.168.1.47:5200 \
     --user admin --password admin
   ```

   Omit `--vault` to load everything except the document files.

Object ids are derived from part numbers (UUID v5), so a second run updates rather than
duplicates.

---

## What the dataset contains

| | Count |
|---|---|
| Company object types (7 abstract bases, 35 concrete) | 42 |
| Out-of-the-box types used (ECR, ECO, ECN, ProblemReport, Program, Phase, Milestone, WorkPackage, Task) | 9 |
| Numbering schemas | 19 |
| Approval workflows | 6 |
| Groups | 10 |
| Kanban boards | 6 |
| Classification folders | 88 |
| Objects | 278 |
| Bill-of-materials links | 75 |
| Requirements | 29 across 6 levels |
| Requirement trace links | 53 |
| Work breakdown items | 30 |
| Projects | 3 |
| Document files | 105 |

### The product structure

Three ATA chapters, built to real depth:

- **ATA 21 Air Conditioning** — a bleed-air bootstrap environmental control system: engine
  bleed through a shutoff and pressure-regulating valve, primary heat exchanger, air cycle
  machine, water separator, cabin distribution, a dual-channel digital controller with its
  own DO-178C level C software, plus the pressurisation control and protection subsystems.
- **ATA 23 Communications** — dual VHF, a satellite terminal, an audio integrating panel
  with DO-178C software and a DO-254 programmable logic device, a cockpit voice recorder
  with its life-limited locating beacon, antennas with their structural doublers, static
  dischargers and the harnesses.
- **ATA 25 Equipment and Furnishings** — crew and passenger seating substantiated to the
  16g dynamic condition, lining panels against the Appendix F heat-release and smoke
  criteria, cushions against the Part II oil-burner test, carpets and soft goods, galley and
  lavatory monuments, emergency equipment stowage, and the seat track fittings that carry it
  all into the floor structure.

The rest of the aircraft is present at ATA chapter level in the classification tree, so the
breakdown reads like a real aeroplane rather than three orphan systems.

### Standards the model is built against

ATA iSpec 2200 chapter and subchapter numbering · CS-23 Amendment 5 and 14 CFR Part 23
Amendment 64 with ASTM F44 consensus standards (F3061, F3064, F3083, F3114) as accepted
means of compliance · EASA Part 21 Subpart J design organisation privileges, including
21A.263 · the EASA MC0–MC9 means-of-compliance codes · ARP4754A and ARP4761A safety
assessment · DO-178C software and DO-254 electronic hardware assurance levels · DO-160G
environmental qualification sections · AS9100D clauses 8.1.2, 8.1.3, 8.1.4, 8.4, 8.5.1,
8.5.2, 8.5.6, 8.7, 9.2 and 10.2 · AS9102 Rev C first article inspection Forms 1–3 · AS9145
APQP phase structure · NADCAP special process families · FAA 8130-3 and EASA Form 1.

---

## Design decisions worth knowing

**It fills the existing stubs rather than adding a second hierarchy.** The installer payload
already ships empty `n5LightSpeedSystems*` aviation types — `AircraftPart`, `AeroStdPart`,
`ElectricalPart`, `InteriorPart`, `VendorPart`, the type-design and non-type-design bases,
`PrjSpecificCertPlan`, `EMICAR`. This model fills them. A site that already has them sees a
*Modified* diff on the bases and *New* on everything else, instead of two half-built
aviation models standing side by side.

**Requirement types had to be created.** The out-of-the-box `MissionRequirement`,
`StakeholderRequirement`, `SystemRequirement`, `SubsystemRequirement` and
`ComponentRequirement` are all **abstract**, so no object can be created against them. Six
concrete company types sit under them. They are siblings on five unrelated branches, so
there is no single ancestor the shared aviation attributes could live on — they are defined
once in Python and referenced by each type, which keeps one definition in the source even
though the generated JSON repeats it.

**Bill-of-materials links cannot ship in a data pack.** The `.nexuspack` v2 format has no
representation for a BOM link, which is why this dataset needs a loader driving the Engine
API rather than shipping as a pack. The customization set carries the *shape*; the loader
creates the *content*.

**`canCreate` names the groups that author each type.** It used to be false on every row of
every model, which — before Services PR #798 — was the most dangerous line in this package:
`CanCreateAsync` treated create as opt-in, so a model that denied it to every subject granted
it to the whole site. Create is now deny-by-default for any type that carries a security model
at all, which means the grants have to be real: every one of the 47 models names at least one
group that may author its type, and the wildcard row never does. A type with no granting row
can be created by nobody but an administrator, and `verify/VerifyPackage.csproj` fails the
package if one appears.

Because of that pairing, **this package and an Engine built from #798 or later must go out
together.** The old Engine with this package is harmless; a new Engine without it leaves every
non-administrator unable to create anything in NX-200.

**`defaultValue` is always a JSON string.** The Engine reads a type file through
`TypeAttributeEntry`, whose `defaultValue` is `string?`. A raw `true` or `42` throws on
deserialisation and takes the whole type file down with it.

**The out-of-the-box change objects carry hand-written numbers.** `LSS-ECR-00001` reads far
better in a demo than `NX00000042`, and the Engine accepts any explicit part number — a
numbering schema only decides what the site *mints*. Giving the change types a company
schema would mean packaging a type named `ECR`, which would shadow the out-of-the-box one
and be refused. The validator reports these as notes rather than failures and says why.

**The package is byte-reproducible.** Nothing in it depends on the clock or a random id, so
two builds of the same model produce the same archive, and a diff between builds is a diff
of the model rather than of noise.

---

## Honest limits

- **The live load has not been executed.** Every endpoint and request body in
  `seed_lightjet.py` was written against the controller that serves it, and the dataset
  passes full local validation, but the loader has never run against a live Engine. Expect
  to debug a few request shapes on the first run — particularly the work-item child and
  dependency endpoints, which were inferred from their controller routes rather than from a
  worked example.
- **Drawings carry no geometry.** The drawing PDFs are title block, revision history and
  ballooned characteristic schedule. If the demo needs a 3D model in the viewer, that is a
  separate job — a STEP file per part, which this dataset does not generate.
- **Flight test reports, AMM chapters and the maintenance programme are referenced but not
  generated.** Where a document names `FTR-26-0114` or an AMM chapter, that reference has no
  object behind it. Everything with an `LSS-` number does.
- **No workflow instances are running.** Objects sit in the lifecycle states the dataset
  gives them. Starting a workflow during the demo is live behaviour, not seeded state — which
  is better for a demo, but it means the "my tasks" list starts empty.

See `DEMO-RUNBOOK.md` for the narrative.
