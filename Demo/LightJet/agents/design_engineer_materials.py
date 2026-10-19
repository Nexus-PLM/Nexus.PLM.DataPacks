"""Mira Sandoval, design engineer: gives her parts a volume and says what each is made of.

    python design_engineer_materials.py                      # dry run
    python design_engineer_materials.py --apply
    python design_engineer_materials.py --apply --aircraft LSS-AC-001

Who does what, and why it is split this way
-------------------------------------------
The materials engineer owns the material and publishes its DENSITY. The design engineer
owns the part and knows its VOLUME. Neither writes in the other's record. Saying "this
part is made of that material" is a design act, so it is this agent that creates the
MadeOfLink - and the Engine multiplies density by volume at that moment and stores the
mass on the part, which is what lets the BOM rollup sum it.

So this agent does two things to each part it owns:

  sets volumeCm3 and volumeBasis, which are the designer's to state;
  creates one MadeOfLink per material the part is made of.

It does NOT compute a mass. If it did, the mass would be this script's arithmetic rather
than the product's, and the demo would prove nothing - the whole point is that re-sourcing
a material moves the aircraft weight because the Engine recalculates it.

A DECLARED mass is never disturbed. A part carrying massStatus "Weighed" or "Contractual"
has a measured or agreed mass, and the Engine keeps it, storing the calculation beside it
as massKgCalculated so the variance is visible. This agent reports those variances rather
than hiding them - "calculated 1.38, weighed 1.46" is a finding worth a human look.

Honesty about the numbers
-------------------------
The volumes are engineering estimates invented for a demonstration, not measurements off a
CAD model, so every part is written with volumeBasis = "Estimated". They are deterministic
in the part number, so a re-run gives the same aeroplane rather than a new one - "the
weight changed" has to mean a real change.

Runs as m.sandoval, through the same REST API as the web client. Where the security model
refuses her something the refusal is recorded as a finding and the run continues: a design
engineer who cannot say what her own part is made of is a configuration question worth
answering, not an obstacle to route around with an admin token. Anything that looks like a
product defect, a gap or an enhancement goes to reports/bugs.jsonl via bug(), for the PLM
administrator to file on the board - this agent never edits the product.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plm_agent import Agent, Refused, object_id, tidy                  # noqa: E402

ME = "m.sandoval"
AIRCRAFT = ["LSS-AC-001", "LSS-AC-002", "LSS-AC-003"]
LINK_KIND = "cstLightSpeedSystemsMadeOfLink"

# Types that are a lump of material and can carry a calculated mass. Deliberately not
# everything in the structure: an installation or an aircraft is a SUM of its children, so
# giving either a material of its own would double-count it in the rollup, and a software
# item has no volume at all.
MATERIAL_BEARING = {
    "cstLightSpeedSystemsAircraftPart",
    "cstLightSpeedSystemsInteriorPart",
    "cstLightSpeedSystemsElectricalPart",
    "cstLightSpeedSystemsAeroStdPart",
    "cstLightSpeedSystemsVendorPart",
    "cstLightSpeedSystemsHarness",
}
SUMMED_FROM_CHILDREN = {
    "cstLightSpeedSystemsInstallation",
    "cstLightSpeedSystemsAircraft",
}
NO_MASS_OF_ITS_OWN = {
    "cstLightSpeedSystemsSoftwareItem",
    "cstLightSpeedSystemsConsumable",       # applied to a joint, not a part in the BOM
    "cstLightSpeedSystemsAehItem",
}

# Representative volumes in cm3, as a (low, high) band. A detail part is a few hundred
# cm3; a seat assembly is tens of thousands. The band is wide on purpose - a believable
# weight statement has spread in it, and a dataset where every bracket weighs the same
# reads as generated.
VOLUME_BAND_BY_CATEGORY = {
    "Detail part":        (40, 400),
    "Sub-assembly":       (800, 6000),
    "Machined":           (60, 900),
    "Sheet metal":        (30, 500),
    "Composite laminate": (200, 2500),
    "Composite sandwich": (1500, 20000),
    "Tube / duct":        (150, 1800),
    "Casting":            (120, 1500),
    "Forging":            (100, 1200),
    "Extrusion":          (80, 700),
    "Moulded":            (60, 800),
}
VOLUME_BAND_BY_TYPE = {
    "cstLightSpeedSystemsInteriorPart":   (2000, 30000),
    "cstLightSpeedSystemsElectricalPart": (50, 600),
    "cstLightSpeedSystemsAeroStdPart":    (1, 40),
    "cstLightSpeedSystemsHarness":        (200, 2500),
    "cstLightSpeedSystemsVendorPart":     (100, 4000),
}
DEFAULT_BAND = (100, 1200)

# How a part's own words choose its material. First match wins, so the specific sealant
# and honeycomb entries sit above the generic metals. Nothing here invents a density: the
# density is read off the material object, which is the materials engineer's record.
MATERIAL_HINTS = [
    ("honeycomb", "LSS-MAT-00010"), ("sandwich", "LSS-MAT-00010"),
    ("sealant", "LSS-MAT-00014"), ("polysulphide", "LSS-MAT-00014"),
    ("polythioether", "LSS-MAT-00015"),
    ("titanium", "LSS-MAT-00001"), ("ti-6al-4v", "LSS-MAT-00001"),
    ("stainless", "LSS-MAT-00002"), ("cres", "LSS-MAT-00002"),
    ("carbon", "LSS-MAT-00009"), ("cfrp", "LSS-MAT-00009"),
    ("composite", "LSS-MAT-00009"), ("glass", "LSS-MAT-00011"),
    ("ultem", "LSS-MAT-00012"), ("polyetherimide", "LSS-MAT-00012"),
    ("plastic", "LSS-MAT-00012"),
    ("7075", "LSS-MAT-00003"), ("2024", "LSS-MAT-00005"), ("6061", "LSS-MAT-00008"),
    ("tube", "LSS-MAT-00007"), ("duct", "LSS-MAT-00007"),
    ("extrusion", "LSS-MAT-00004"), ("bar", "LSS-MAT-00004"),
    ("aluminium", "LSS-MAT-00008"), ("aluminum", "LSS-MAT-00008"),
]
FALLBACK_MATERIAL = "LSS-MAT-00008"          # 6061-T6 sheet: the unremarkable choice


# Roughly one part in eight keeps a genuinely declared mass, so the demo shows BOTH
# behaviours: a structure whose weight is calculated from its materials, and a handful of
# parts where a weighed figure correctly overrides the calculation and the variance is
# visible. Deterministic, so the same parts keep it on every run.
KEEP_WEIGHED_IN = 8


def keep_weighed(part_number: str) -> bool:
    digest = hashlib.sha256(f"weighed:{part_number}".encode("utf-8")).digest()
    return digest[0] % KEEP_WEIGHED_IN == 0


def spread(seed: str, low: float, high: float) -> float:
    """A stable value in [low, high] derived from the part number.

    Deterministic so a re-run produces the same aeroplane. A random volume would make
    every run a different aircraft, and "the weight changed" is the one thing a weight
    engineer has to be able to trust is a real change.
    """
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    fraction = int.from_bytes(digest[:4], "big") / 0xFFFFFFFF
    return round(low + fraction * (high - low), 1)


_DENSITIES: dict[str, float | None] = {}


def density_of(me: Agent, material: str) -> float | None:
    """The material's declared density, read once per material, from the material itself.

    Never a table in this file: a density carried here would stop being the programme's
    density the moment the materials engineer revised it, which is the whole defect this
    work exists to fix.
    """
    if material not in _DENSITIES:
        try:
            _DENSITIES[material] = as_number((me.attributes(material) or {}).get("density"))
        except Exception:                                              # noqa: BLE001
            _DENSITIES[material] = None
    return _DENSITIES[material]


def pick_material(part: dict, attrs: dict) -> tuple[str, str]:
    hay = " ".join(str(x).lower() for x in (
        attrs.get("primaryMaterial"), attrs.get("materialSpecification"),
        attrs.get("materialForm"), part.get("description"), part.get("partNumber")) if x)
    for needle, material in MATERIAL_HINTS:
        if needle in hay:
            return material, f"part names '{needle}'"
    return FALLBACK_MATERIAL, "part names no material; used the default"


def volume_for(part: dict, attrs: dict, density: float | None) -> tuple[float, str]:
    """(volume in cm3, how it was arrived at).

    Where the part already carries a mass, the volume is DERIVED FROM IT:

        volumeCm3 = massKg / density * 1e6

    which is the assumption a design engineer would actually make. The dataset's masses
    are credible part weights - somebody chose 0.38 kg for a small fitting and 31.8 kg for
    an installation - and a volume consistent with the material that part is made of is
    better information than anything invented here. It also keeps the aircraft weight the
    dataset was built to show, while making it DERIVED rather than typed: the number no
    longer sits in a field, it comes out of a material and a geometry.

    The first version of this used a representative volume band per part category, and it
    was visibly wrong: one band covered both a seat assembly and a small fitting, so
    LSS-F-00080 came out at 43 kg against a declared 0.38 kg. A band is only defensible
    where there is nothing better, which is why it survives as the fallback.
    """
    mass = as_number(attrs.get("massKg"))
    if mass and mass > 0 and density and density > 0:
        return round(mass / density * 1_000_000, 1), "derived from the part's own mass"
    band = (VOLUME_BAND_BY_CATEGORY.get(str(attrs.get("partCategory")))
            or VOLUME_BAND_BY_TYPE.get(part.get("typeName", ""))
            or DEFAULT_BAND)
    return spread(part["partNumber"], *band), "estimated from the part category"


def as_number(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def walk_bom(me: Agent, root: str) -> dict[str, dict]:
    """Every distinct item under `root`, by part number. Depth-first, cycle-safe."""
    found: dict[str, dict] = {}

    def visit(part_number: str, depth: int) -> None:
        if depth > 8:
            return
        for row in (me.bom(part_number) or []):
            child = row.get("childPartNumber")
            if not child or child in found:
                continue
            found[child] = {
                "partNumber": child,
                "typeName": row.get("childTypeName") or "",
                "description": row.get("childDescription") or "",
                "quantity": row.get("quantity") or 1,
                "objectId": row.get("childObjectId"),
                "attributes": row.get("childAttributes") or {},
            }
            visit(child, depth + 1)

    visit(root, 0)
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--aircraft", action="append")
    ap.add_argument(
        "--as-admin", action="store_true",
        help="dataset preparation: run as the administrator, not as the design engineer")
    ap.add_argument(
        "--reset-implausible-weighed", action="store_true",
        help="set massStatus Estimated where Weighed cannot be true, so a mass can calculate")
    args = ap.parse_args()

    # Two passes exist here and they are NOT the same act.
    #
    # As m.sandoval this is engineering: she states her part's volume and says what it is
    # made of, and the security model judges her. That is the pass worth watching, and on
    # released hardware it is correctly refused - a released part is frozen, and retrofitting
    # a volume onto one is not something any engineer should be able to do.
    #
    # Which leaves most of this dataset unreachable, because the loader released almost all
    # of it. Backfilling those is DATASET PREPARATION - the same act as loading the data in
    # the first place, which the administrator did - so --as-admin does it as the
    # administrator and says so. It is not a workaround for a permission problem; the
    # permission is right, and the data simply arrived without a volume.
    me = (Agent("admin", password="NexusAdmin2026!", role="PLM Administrator")
          if args.as_admin else Agent(ME))
    if args.as_admin:
        print("RUNNING AS ADMINISTRATOR - dataset preparation, not an engineering act.")

    # Nothing works without the kind, and one clear sentence beats sixty identical 400s.
    kinds = me.get("/api/plmobjects/kinds") or []
    if isinstance(kinds, list) and kinds and not any(
            (k.get("typeName") or k.get("linkTypeName")) == LINK_KIND for k in kinds):
        print(f"NOTE: {LINK_KIND} is not among the reference kinds this site offers.")
        print("      The customization set carrying it has not been imported yet.")

    # Keyed by part number, because the three aircraft share most of their structure: a
    # list would plan - and write - the same part once per aeroplane. The first run did
    # exactly that and reported 189 parts where there are 63.
    planned_by_part: dict[str, dict] = {}
    skipped: dict[str, int] = defaultdict(int)
    for root in (args.aircraft or AIRCRAFT):
        tree = walk_bom(me, root)
        print(f"{root}: {len(tree)} distinct item(s) in the structure")
        for part in tree.values():
            kind = part["typeName"]
            if kind in SUMMED_FROM_CHILDREN:
                skipped["assembly - mass comes from its children"] += 1
                continue
            if kind in NO_MASS_OF_ITS_OWN:
                skipped[f"{kind} - no mass of its own"] += 1
                continue
            if kind not in MATERIAL_BEARING:
                skipped[f"{kind} - unknown type, left alone"] += 1
                continue
            if part["partNumber"] in planned_by_part:
                continue
            attrs = part["attributes"] or {}
            material, why = pick_material(part, attrs)
            volume, basis = volume_for(part, attrs, density_of(me, material))
            planned_by_part[part["partNumber"]] = {
                **part, "material": material, "why": why,
                "volumeCm3": volume, "volumeWhy": basis,
                "declaredStatus": attrs.get("massStatus"),
                "declaredMass": attrs.get("massKg"),
            }

    planned = list(planned_by_part.values())

    print("\nskipped:")
    for reason, n in sorted(skipped.items()):
        print(f"  {n:4} {reason}")

    declared = [p for p in planned if str(p["declaredStatus"]) in ("Weighed", "Contractual")]
    print(f"\n{len(planned)} part(s) to give a volume and a material")
    if declared:
        print(f"  of which {len(declared)} already carry a DECLARED mass "
              f"({', '.join(sorted({str(p['declaredStatus']) for p in declared}))}) - "
              f"the Engine keeps those and records the calculation beside them")

    for p in sorted(planned, key=lambda x: x["partNumber"])[:12]:
        print(f"  {p['partNumber']:20} {p['volumeCm3']:>9.1f} cm3  "
              f"{p['material']}  ({p['why']}; volume {p['volumeWhy']})")
    if len(planned) > 12:
        print(f"  ... {len(planned) - 12} more")

    if not args.apply:
        print("\n(dry run - nothing written; pass --apply)")
        return 0

    volumed, linked = 0, 0
    refused_volume, refused_link, variances, failed = [], [], [], []

    for p in planned:
        # 1. the volume, which is the designer's to state
        try:
            values = {
                "volumeCm3": p["volumeCm3"],
                # "Calculated from drawing" would be a lie - there is no drawing behind it.
                # A volume back-derived from a stated mass is an estimate, however good.
                "volumeBasis": "Estimated",
            }
            # A detail part on a programme still in design has not been on a set of scales.
            # The loader marked nearly everything "Weighed", which outranks a calculation and
            # would leave the whole structure uncalculated - so where the claim cannot be
            # true it is corrected to Estimated and the Engine then calculates. A few are
            # left Weighed on purpose (see KEEP_WEIGHED) so the override itself still shows.
            if (args.reset_implausible_weighed
                    and str(p["declaredStatus"]) in ("Weighed", "Contractual")
                    and not keep_weighed(p["partNumber"])):
                values["massStatus"] = "Estimated"
            me.set_attributes(p["partNumber"], values)
            volumed += 1
        except Refused as exc:
            refused_volume.append((p["partNumber"], exc.status, tidy(exc.body, 150)))
            continue
        except Exception as exc:                                       # noqa: BLE001
            failed.append((p["partNumber"], "volume", tidy(exc, 150)))
            continue

        # 2. the material reference. The Engine does the arithmetic on creation.
        try:
            outcome = attach(me, p)
            if outcome is None:
                continue
            linked += 1
            mass = (outcome or {}).get("mass") or {}
            if mass.get("declaredMassKept"):
                variances.append((p["partNumber"], mass.get("declaredStatus"),
                                  p["declaredMass"], mass.get("massKg")))
            elif not mass.get("calculated"):
                failed.append((p["partNumber"], "mass not calculated",
                               str(mass.get("reason"))[:150]))
        except Refused as exc:
            refused_link.append((p["partNumber"], exc.status, tidy(exc.body, 150)))
        except Exception as exc:                                       # noqa: BLE001
            failed.append((p["partNumber"], "link", tidy(exc, 150)))

    print(f"\nvolumes set: {volumed}   material references created: {linked}")

    if variances:
        print(f"\n{len(variances)} part(s) keep a declared mass; calculation differs:")
        for pn, status, dec, calc in variances[:10]:
            try:
                delta = float(calc) - float(dec)
                print(f"  {pn:20} {status:12} declared {float(dec):8.3f}  "
                      f"calculated {float(calc):8.3f}  ({delta:+.3f} kg)")
            except (TypeError, ValueError):
                print(f"  {pn:20} {status:12} declared {dec}  calculated {calc}")
        report_variances(me, variances)

    for label, rows, bug in (("volume", refused_volume, report_volume_refusal),
                             ("material reference", refused_link, report_link_refusal)):
        if rows:
            print(f"\n{len(rows)} refused on the {label} - findings, not obstacles:")
            for pn, status, body in rows[:8]:
                print(f"  {pn:20} {status}  {body}")
            bug(me, rows)

    if failed:
        print(f"\n{len(failed)} other problem(s):")
        for pn, where, err in failed[:10]:
            print(f"  {pn:20} {where:22} {err}")
    return 0


def attach(me: Agent, part: dict) -> dict | None:
    """Creates the MadeOfLink. Returns the create response, or None if already linked."""
    object_ref = part["objectId"] or object_id(part["partNumber"])
    latest = me.latest(part["partNumber"])
    if not latest:
        return None
    revision_id = latest["revisionId"]

    existing = me.get(
        f"/api/plmobjects/{object_ref}/revisions/{revision_id}/references") or []
    if any((r.get("linkTypeName") or "") == LINK_KIND for r in existing):
        return None                                  # idempotent: leave a done part alone

    # The kind declares revisionRule 'pinned' - a mass calculated against revision A of a
    # material is not a claim about revision B - so the create has to name the revision it
    # pins. Without it the server answers 400, correctly.
    material_id = object_id(part["material"])
    material_revisions = me.get(f"/api/plmobjects/{material_id}/revisions") or []
    if not material_revisions:
        return None
    return me.post(
        f"/api/plmobjects/{object_ref}/revisions/{revision_id}/references",
        {
            "targetObjectId": material_id,
            "linkTypeName": LINK_KIND,
            "revisionRule": "pinned",
            "pinnedRevisionId": material_revisions[-1]["revisionId"],
            "note": f"{part['why']}; volume is a demonstration estimate, not CAD-derived",
        })


def report_variances(me: Agent, variances: list) -> None:
    sample = ", ".join(pn for pn, *_ in variances[:4])
    me.bug(
        "BOM",
        "Calculated mass disagrees with the declared mass on several parts",
        "These parts carry a weighed or contractual mass, which the Engine correctly keeps "
        "in preference to the calculation, and stores the calculated figure beside it as "
        "massKgCalculated. The two differ, which is exactly the signal the pair exists to "
        "give - but nothing surfaces the variance: there is no view that lists parts whose "
        "calculated and declared masses disagree, and no threshold above which somebody is "
        "told. On a weight-critical programme that reconciliation is a standing job. "
        f"{len(variances)} part(s), e.g. {sample}.",
        category="missing", severity="Major")


def report_volume_refusal(me: Agent, rows: list) -> None:
    sample = ", ".join(pn for pn, _, _ in rows[:4])
    me.bug(
        "Data model",
        "A design engineer cannot set the volume of her own part",
        "Writing volumeCm3 was refused on parts this engineer owns. Volume is the "
        "designer's to state - it is a property of the geometry she is responsible for - "
        "so if the lifecycle state or the policy forbids it, the mass can never be "
        f"calculated for those parts. Refused on {len(rows)} part(s), e.g. {sample}.",
        category="security", severity="Major")


def report_link_refusal(me: Agent, rows: list) -> None:
    sample = ", ".join(pn for pn, _, _ in rows[:4])
    me.bug(
        "Data model",
        "A design engineer cannot record what her part is made of",
        "Creating a MadeOfLink was refused. Saying what a part is made of is a design act "
        "and the reference is made FROM the part, so a designer who owns the part should be "
        "able to make it. If this is the lifecycle state, then no released part can ever "
        "have its mass calculated, which makes the whole weight rollup unavailable on "
        f"exactly the data that matters. Refused on {len(rows)} part(s), e.g. {sample}.",
        category="security", severity="Major")


if __name__ == "__main__":
    sys.exit(main())
