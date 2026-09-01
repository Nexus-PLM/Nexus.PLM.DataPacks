# Nexus Materials Data Packs

Ten importable material libraries, one per family, built from
`PLM_Materials_Library_Starter.xlsx` (10 sheets × 50 records).

Each folder holds a `.nexuspack` — a zip Nexus imports through **Data Packs → Import** —
and the cleaned `.csv` beside it so the data is reviewable without unzipping.

```
Materials/<Family>/
  <family>-materials-1.0.nexuspack    manifest.json + types/*.json + data/<Type>.csv
  n5<Family>.csv                      the same rows, for reading in Excel or a diff
```

| Folder | PLM type | Rows | Category | Model |
|---|---|---|---|---|
| Steel | `n5Steel` | 50 | Metal | Isotropic |
| Stainless Steel | `n5StainlessSteel` | 50 | Metal | Isotropic |
| Aluminium | `n5Aluminium` | 50 | Metal | Isotropic |
| Titanium | `n5Titanium` | 50 | Metal | Isotropic |
| Copper Alloy | `n5CopperAlloy` | 50 | Metal | Isotropic |
| Plastic | `n5Plastic` | 50 | Polymer | Isotropic |
| Wood | `n5Wood` | 50 | Composite | Orthotropic |
| Composites | `n5Composite` | 50 | Composite | Orthotropic |
| Ceramics | `n5Ceramic` | 50 | Ceramic | Isotropic |
| Glass | `n5Glass` | 50 | Ceramic | Isotropic |

Every family type derives from the standard `MaterialBase` and declares no attributes of
its own — all ~38 properties are inherited, so a pack never forks the standard model.

---

## ⚠️ Read before using this data

These are **starter / typical reference values, not certified design allowables**. The
source workbook says so, and spot-checking against published values confirms it matters:

| Material | Field | Pack | Published | Error |
|---|---|---|---|---|
| 4140 annealed | yield | 286 | 655 MPa | **−56 %** |
| 1018 | yield | 257 | 370 MPa | **−31 %** |
| Ti-6Al-4V Grade 23 | yield | 333 | 880 MPa | **−62 %** |
| 6061-T6 | yield | 178 | 276 MPa | **−36 %** |
| 316 cold worked | yield | 362 | 205 MPa | **+77 %** |

**Density and elastic modulus are broadly sound** (typically within a few percent).
**Strength values are not** — they appear to be generated around a family average rather
than sourced per grade, so they are wrong for specific named grades.

Re-source yield, tensile, compressive, shear and endurance values per grade before this
library is sold, published, or used for anything load-bearing.

---

## What was cleaned, and why

The workbook was normalised into the `MaterialBase` schema before packing:

- **Dropped columns that carry no information** — the source system's `Object Id`, the nine
  orthotropic columns (`E1/E2/E3`, `G12/G13/G23`, `ν12/ν13/ν23`, empty in *every* family,
  including Wood and Composites where they would matter), and `Revision`/`Status`/`Modified`
  (the importing site generates its own).
- **Dropped a property that was one value shared by all 50 materials** where it genuinely
  varies material to material. `Hardness` was `"HB 130-180"` for every steel and
  `"Mohs ~5-7"` for every glass — a single figure for fifty different materials is
  misinformation, not data. Family-level constants that *are* legitimately family-wide
  (Poisson's ratio, reference temperature, unit system) were kept.
- **Blanked physically meaningless values.** Glass and ceramics are brittle: they have no
  yield point, and the source stored `0`, which reads as *zero strength*. They now carry no
  value at all.
- **Mapped categorical values onto the schema's lists.** `Material Category` held the family
  name (`"Steel"`, `"Wood"`); it now holds a real LOV value. `Material Model` held
  `"Orthotropic / Approx."`, which is not a valid value; it is now `Orthotropic`.
- **Rounded to 4 significant figures**, removing the 15-decimal jitter of the generated
  source (`71553.83468761358` → `71550`).
- **Kept provenance.** `Data Source` travels with every row, and each pack's manifest
  repeats the "not certified" caveat so a receiving site sees it before importing.

Descriptions are rewritten as `<grade> — typical reference properties at approximately
20 °C. Not a certified material specification.`

---

## Importing

1. **Create a numbering schema first.** Part numbers are permanent; importing before a
   schema exists stamps the whole batch with the wrong convention. The existing pattern is
   `MTRL` + counter + family suffix (`s5Steel`, `s5Innox`, `s5Aluminum`), producing
   `MTRL-00000001-STEEL`.
2. Data Packs → **Import** → choose the `.nexuspack`.
3. Review how its types compare with the site. All three types in these packs
   (`PLMCoreAbstractModel`, `MaterialBase`, `n5<Family>`) will report *"already on this
   site"* except the family type on a site that has not seen it, which offers **Create**.
4. Choose a **classification folder** and the **numbering schema**, then select rows.

Data Packs is an administrator tool.

---

## Regenerating

`build_material_packs.py` rebuilds every pack from the workbook. Two format details matter:

- Type JSON must carry `"relationship": "Derive"` — the **string**. Files on disk store the
  integer enum (`0`), and `POST /api/types` rejects it with *"The JSON value could not be
  converted to System.String"*.
- CSV headers use raw attribute **names** (`attr:youngsModulus`), never display labels.
  Labels are not unique across a registry — `ProblemTask.instructions` is labelled
  "Description" — and matching on them silently routes data into the wrong attribute.

## Sources

See the `Sources` sheet in the workbook (NIST materials repositories, NIST Alloy Data, a
CC0 Kaggle steel dataset). Licensing belongs to each underlying dataset — check before
redistributing.
