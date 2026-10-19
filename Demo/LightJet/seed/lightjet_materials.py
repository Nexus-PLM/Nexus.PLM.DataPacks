"""NX-200 materials, and the links that tie the product structure to them.

A part that says `primaryMaterial = "Titanium Ti-6Al-4V"` in a text field tells you almost
nothing. You cannot ask which parts use a material whose qualification lapsed, you cannot
find everything made from a batch, and you cannot see the allowables the stress case was
written against. So the materials are objects, and every part references the one it is
made from.

The field that matters most to an aerospace audience is **allowables basis**. A-basis,
B-basis and S-basis are not quality grades - they are statistical bases for the design
allowable, and which one a stress case may use depends on whether the structure has a
single or multiple load path. A material with only typical values has no design allowable
at all, and a part substantiated against typical values is not substantiated.

Property values are representative reference figures at room temperature, not certified
design allowables. Every material record says so in `dataSource`.
"""

from lightjet_data import PROGRAMME, ROOT_FOLDER, T

M_ACTIVE, M_REVIEW, M_OBSOLETE = "Released", "In Work", "Obsolete"
F_MAT = f"{ROOT_FOLDER}/Production/Consumable Materials"

DISCLAIMER = ("Representative reference values at approximately 20 degrees C. Not a "
              "certified material specification and not a design allowable.")


def material(pn, name, code, category, spec, condition, form, basis, source,
             qualification, props, status=M_ACTIVE, notes=None, extra=None):
    attrs = {
        "materialName": name,
        "materialCode": code,
        "materialCategory": category,
        "specificationStandard": spec,
        "conditionTemper": condition,
        "materialModel": "Isotropic" if category != "Composite" else "Orthotropic",
        "referenceTemperature": 20,
        "unitSystem": "SI",
        "dataSource": DISCLAIMER,
        "materialForm": form,
        "allowablesBasis": basis,
        "allowablesSource": source,
        "qualificationStatus": qualification,
        "governingSpecification": spec,
        "programmeCode": PROGRAMME,
    }
    attrs.update(props)
    attrs.update(extra or {})
    return {
        "type": f"{T}Material", "pn": pn, "description": f"{name}, {condition}",
        "status": status, "revision": "A", "history": [("A", status)],
        "attrs": attrs, "folder": F_MAT, "notes": notes,
    }


# Mechanical property sets, SI: MPa for strengths and moduli, kg/m3 for density.
def metal(density, E, nu, fty, ftu, elong, alpha, k, cp, tmax):
    return {
        "density": density, "youngsModulus": E, "poissonsRatio": nu,
        "yieldStrength": fty, "ultimateTensileStrength": ftu,
        "elongationAtBreak": elong, "thermalExpansionCoeff": alpha,
        "thermalConductivity": k, "specificHeatCapacity": cp,
        "maxServiceTemperature": tmax,
    }


MATERIALS = [
    material(
        "LSS-MAT-00001", "Titanium Ti-6Al-4V", "TI64-AMS4911", "Metal",
        "AMS 4911", "Annealed sheet, strip and plate", "Sheet",
        "A-basis", "MMPDS-2023 Table 5.4.1.0(b)", "Qualified",
        metal(4430, 113800, 0.342, 827, 896, 10, 0.0000088, 6.7, 526, 400),
        extra={"corrosionResistance": "Excellent; no protective finish required",
               "nadcapProcessRequired": True,
               "weldable": True,
               "restrictedSubstances": "No SVHC above threshold",
               "flammabilityRating": "Not applicable - structural metal"},
        notes="The bleed duct material. A-basis allowables because the duct is a single "
              "load path pressure boundary: a B-basis allowable may only be used where "
              "failure of the element would transfer load to another member."),

    material(
        "LSS-MAT-00002", "Stainless steel 321", "SS321-AMS5510", "Metal",
        "AMS 5510", "Annealed sheet and plate", "Bar",
        "A-basis", "MMPDS-2023 Table 2.7.1.0(b)", "Qualified",
        metal(8030, 193000, 0.29, 207, 517, 40, 0.0000166, 16.1, 500, 870),
        extra={"corrosionResistance": "Good; titanium-stabilised against sensitisation",
               "nadcapProcessRequired": False, "weldable": True,
               "restrictedSubstances": "No SVHC above threshold",
               "flammabilityRating": "Not applicable - structural metal"},
        notes="Titanium-stabilised, which is why it is used at the V-band coupling: it "
              "resists carbide precipitation at the bleed temperature where plain 304 "
              "would sensitise."),

    material(
        "LSS-MAT-00003", "Aluminium 7075-T7351", "AL7075T7351-AMS4078", "Metal",
        "AMS 4078", "T7351 overaged plate", "Plate",
        "A-basis", "MMPDS-2023 Table 3.7.6.0(b1)", "Qualified",
        metal(2810, 71700, 0.33, 414, 490, 7, 0.0000236, 155, 960, 150),
        extra={"corrosionResistance":
               "Overaged temper; good stress corrosion cracking resistance in the "
               "short transverse direction, which T651 does not have",
               "nadcapProcessRequired": True, "weldable": False,
               "restrictedSubstances": "Chromate conversion coating - hexavalent "
                                       "chromium, REACH authorisation held",
               "flammabilityRating": "Not applicable - structural metal"},
        notes="T7351 rather than T651 specifically for stress corrosion resistance in "
              "the short transverse grain direction. A substitution to T651 would be a "
              "material change, not an equivalent."),

    material(
        "LSS-MAT-00004", "Aluminium 7075-T7351 bar", "AL7075T7351-AMS4124", "Metal",
        "AMS 4124", "T7351 overaged bar and rod", "Bar",
        "A-basis", "MMPDS-2023 Table 3.7.6.0(d)", "Qualified",
        metal(2810, 71700, 0.33, 400, 476, 7, 0.0000236, 155, 960, 150),
        extra={"corrosionResistance": "Overaged temper; good SCC resistance",
               "nadcapProcessRequired": True, "weldable": False,
               "restrictedSubstances": "Chromate conversion coating - REACH "
                                       "authorisation held",
               "flammabilityRating": "Not applicable - structural metal"},
        notes="Bar stock for the seat track fittings, which are machined from solid."),

    material(
        "LSS-MAT-00005", "Aluminium 2024-T351", "AL2024T351-AMS4037", "Metal",
        "AMS 4037", "T351 solution treated and stretched plate", "Plate",
        "B-basis", "MMPDS-2023 Table 3.2.3.0(b1)", "Qualified",
        metal(2780, 73100, 0.33, 324, 469, 12, 0.0000232, 121, 875, 150),
        extra={"corrosionResistance":
               "Poor bare; requires clad or chemical conversion coating",
               "nadcapProcessRequired": True, "weldable": False,
               "restrictedSubstances": "Chromate conversion coating - REACH "
                                       "authorisation held",
               "flammabilityRating": "Not applicable - structural metal"},
        notes="B-basis is acceptable here because the outflow valve bracket is a "
              "multiple load path fitting. Damage tolerant, with good crack growth "
              "behaviour, which is why 2024 rather than 7075 at this location."),

    material(
        "LSS-MAT-00006", "Aluminium 2024-T3 sheet", "AL2024T3-AMS4037", "Metal",
        "AMS 4037", "T3 solution treated and cold worked sheet", "Sheet",
        "B-basis", "MMPDS-2023 Table 3.2.3.0(b4)", "Qualified",
        metal(2780, 72400, 0.33, 290, 441, 15, 0.0000232, 121, 875, 150),
        extra={"corrosionResistance": "Alclad required on exterior surfaces",
               "nadcapProcessRequired": True, "weldable": False,
               "restrictedSubstances": "Chromate conversion coating - REACH "
                                       "authorisation held",
               "flammabilityRating": "Not applicable - structural metal"},
        notes="The antenna doubler material. Chosen for damage tolerance at a cut-out "
              "in the pressurised shell, where crack growth rate matters more than "
              "static strength."),

    material(
        "LSS-MAT-00007", "Aluminium 6061-T6 tube", "AL6061T6-AMS4083", "Metal",
        "AMS 4083", "T6 drawn seamless tube", "Tube",
        "A-basis", "MMPDS-2023 Table 3.6.2.0(f)", "Qualified",
        metal(2700, 68900, 0.33, 276, 310, 12, 0.0000236, 167, 896, 170),
        extra={"corrosionResistance": "Good; readily anodised",
               "nadcapProcessRequired": False, "weldable": True,
               "restrictedSubstances": "No SVHC above threshold",
               "flammabilityRating": "Not applicable - structural metal"}),

    material(
        "LSS-MAT-00008", "Aluminium 6061-T6 sheet", "AL6061T6-AMS4027", "Metal",
        "AMS 4027", "T6 sheet and plate", "Sheet",
        "A-basis", "MMPDS-2023 Table 3.6.2.0(b)", "Qualified",
        metal(2700, 68900, 0.33, 276, 310, 12, 0.0000236, 167, 896, 170),
        extra={"corrosionResistance": "Good; readily anodised",
               "nadcapProcessRequired": False, "weldable": True,
               "restrictedSubstances": "No SVHC above threshold",
               "flammabilityRating": "Not applicable - structural metal"}),

    material(
        "LSS-MAT-00009", "Carbon/epoxy prepreg, 177 C cure", "CFRP-177-LSS001",
        "Composite", "LSS-SPEC-MAT-001", "Unidirectional tape, 60 percent fibre volume",
        "Prepreg", "B-basis", "CMH-17 Rev G and in-house qualification LSS-QUAL-CFRP-01",
        "Qualified",
        {"density": 1580, "youngsModulusE1": 142000, "youngsModulusE2": 9700,
         "youngsModulusE3": 9700, "shearModulusG12": 5100, "shearModulusG13": 5100,
         "shearModulusG23": 3400, "poissonsRatioNu12": 0.30, "poissonsRatioNu13": 0.30,
         "poissonsRatioNu23": 0.45, "ultimateTensileStrength": 2100,
         "compressiveStrength": 1200, "shearStrength": 92,
         "maxServiceTemperature": 120, "thermalExpansionCoeff": 0.0000002,
         "thermalConductivity": 5.5, "specificHeatCapacity": 1050},
        extra={"shelfLifeMonths": 12,
               "storageRequirement": "Minus 18 degrees C sealed; 30 days out-time "
                                     "maximum, cumulative, recorded per roll",
               "nadcapProcessRequired": True, "weldable": False,
               "corrosionResistance":
                   "Galvanically incompatible with aluminium; isolation ply required "
                   "at every aluminium interface",
               "restrictedSubstances": "No SVHC above threshold",
               "flammabilityRating": "Meets Appendix F Part I vertical burn as cured"},
        notes="The redesigned ram air scoop material. Out-time is cumulative and "
              "recorded per roll: a laminate cured after the out-time is exceeded is "
              "not to specification even if it looks perfect, which is why the batch "
              "has to be traceable to the part."),

    material(
        "LSS-MAT-00010", "Carbon/Nomex honeycomb sandwich", "CFRP-NOMEX-LSS002",
        "Composite", "LSS-SPEC-MAT-002", "Carbon face sheets on 48 kg/m3 Nomex core",
        "Core", "B-basis", "CMH-17 Rev G and in-house qualification LSS-QUAL-SAND-01",
        "Qualified",
        {"density": 420, "youngsModulusE1": 48000, "youngsModulusE2": 48000,
         "shearModulusG12": 3800, "poissonsRatioNu12": 0.05,
         "ultimateTensileStrength": 620, "compressiveStrength": 480,
         "shearStrength": 1.8, "maxServiceTemperature": 120,
         "thermalConductivity": 0.08, "specificHeatCapacity": 1200},
        extra={"shelfLifeMonths": 12,
               "storageRequirement": "Minus 18 degrees C sealed; core stored dry",
               "nadcapProcessRequired": True, "weldable": False,
               "restrictedSubstances": "No SVHC above threshold",
               "flammabilityRating":
                   "Meets Appendix F Part IV heat release 65/65 and Part V smoke "
                   "density Ds 200 with the production decorative finish"},
        notes="The cabin floor panel. Core shear is the governing allowable in a "
              "sandwich panel, not face sheet strength, which is why the shear figure "
              "looks small next to the tensile one."),

    material(
        "LSS-MAT-00011", "Glass/epoxy prepreg", "GFRP-LSS003", "Composite",
        "LSS-SPEC-MAT-003", "Woven 7781 style glass, 120 C cure", "Prepreg",
        "S-basis", "In-house qualification LSS-QUAL-GFRP-01", "Qualified",
        {"density": 1900, "youngsModulusE1": 24000, "youngsModulusE2": 24000,
         "shearModulusG12": 4200, "poissonsRatioNu12": 0.13,
         "ultimateTensileStrength": 420, "compressiveStrength": 380,
         "shearStrength": 55, "maxServiceTemperature": 100,
         "thermalConductivity": 0.35, "specificHeatCapacity": 1000},
        extra={"shelfLifeMonths": 12,
               "storageRequirement": "Minus 18 degrees C sealed",
               "nadcapProcessRequired": True, "weldable": False,
               "corrosionResistance": "Galvanically inert; usable against aluminium",
               "restrictedSubstances": "No SVHC above threshold",
               "flammabilityRating": "Meets Appendix F Part I vertical burn"},
        notes="S-basis only: the allowable is the specification minimum rather than a "
              "statistical basis, which is acceptable for the non-structural "
              "distribution ducting but would not be for a load path."),

    material(
        "LSS-MAT-00012", "Polyetherimide, Ultem 1000", "PEI-ULTEM1000", "Plastic",
        "LSS-SPEC-MAT-007", "Unfilled injection moulding grade", "Plate",
        "S-basis", "Supplier datasheet, in-house flammability test", "Qualified",
        {"density": 1270, "youngsModulus": 3200, "poissonsRatio": 0.36,
         "yieldStrength": 105, "ultimateTensileStrength": 110,
         "elongationAtBreak": 60, "maxServiceTemperature": 170,
         "thermalExpansionCoeff": 0.000056, "thermalConductivity": 0.22,
         "specificHeatCapacity": 2000},
        extra={"nadcapProcessRequired": False, "weldable": False,
               "corrosionResistance": "Inert",
               "restrictedSubstances": "No SVHC above threshold",
               "flammabilityRating":
                   "Inherently flame retardant; meets Appendix F Part I vertical burn "
                   "and the Part IV heat release criteria without additives"},
        notes="Chosen for the cabin air outlets because it passes the interior "
              "flammability criteria without a flame retardant additive, so there is "
              "no additive to migrate or to fall foul of a restricted substances "
              "change later."),

    material(
        "LSS-MAT-00013", "Aluminium 7075-T651", "AL7075T651-AMS4045", "Metal",
        "AMS 4045", "T651 peak aged plate", "Plate",
        "A-basis", "MMPDS-2023 Table 3.7.6.0(b)", "Not qualified",
        metal(2810, 71700, 0.33, 462, 538, 5, 0.0000236, 130, 960, 150),
        status=M_REVIEW,
        extra={"corrosionResistance":
               "Peak aged; POOR short transverse stress corrosion cracking resistance",
               "nadcapProcessRequired": True, "weldable": False,
               "restrictedSubstances": "Chromate conversion coating",
               "flammabilityRating": "Not applicable - structural metal"},
        notes="Proposed as a higher-strength substitute for LSS-MAT-00003 and NOT "
              "qualified for the NX-200. Peak aged 7075 is stronger but has poor "
              "short transverse stress corrosion resistance, which is the property "
              "T7351 was chosen for. Kept visible so the substitution case is on the "
              "record rather than rediscovered."),

    material(
        "LSS-MAT-00014", "Sealant, polysulphide Class B-2", "AMS3277-B2", "Plastic",
        "AMS 3277", "Class B-2, two part, 120 minute pot life", "Film adhesive",
        "S-basis", "Supplier qualification", "Qualified",
        {"density": 1450, "youngsModulus": 3, "poissonsRatio": 0.49,
         "ultimateTensileStrength": 2.4, "elongationAtBreak": 250,
         "maxServiceTemperature": 120, "thermalConductivity": 0.25},
        extra={"shelfLifeMonths": 9,
               "storageRequirement": "4 to 27 degrees C, original sealed container",
               "nadcapProcessRequired": False, "weldable": False,
               "corrosionResistance": "Fuel and hydraulic fluid resistant",
               "restrictedSubstances": "No SVHC above threshold",
               "flammabilityRating": "Self-extinguishing when cured"},
        notes="The pack bay sealant. Nine month shelf life is the number that caused "
              "nonconformance LSS-NCR-00005 when a batch was issued four days past "
              "expiry."),
]


# ─────────────────────────────────────────────────────────────────────────────
# Which part is made from which material
# ─────────────────────────────────────────────────────────────────────────────

PART_MATERIAL = {
    "LSS-21-0001": "LSS-MAT-00001", "LSS-21-0002": "LSS-MAT-00001",
    "LSS-21-0003": "LSS-MAT-00001", "LSS-21-0014": "LSS-MAT-00001",
    "LSS-21-0004": "LSS-MAT-00002",
    "LSS-21-0005": "LSS-MAT-00003", "LSS-21-0006": "LSS-MAT-00003",
    "LSS-21-0007": "LSS-MAT-00003",
    "LSS-21-0011": "LSS-MAT-00005",
    "LSS-21-0013": "LSS-MAT-00007",
    "LSS-21-0008": "LSS-MAT-00011", "LSS-21-0009": "LSS-MAT-00011",
    "LSS-21-0010": "LSS-MAT-00012",
    "LSS-21-0012": "LSS-MAT-00009",
    "LSS-23-0001": "LSS-MAT-00006",
    "LSS-23-0002": "LSS-MAT-00008",
    "LSS-25-0001": "LSS-MAT-00004", "LSS-25-0003": "LSS-MAT-00004",
    "LSS-25-0002": "LSS-MAT-00010",
    "LSS-CM-0001": "LSS-MAT-00014",
}

# The substitution case that is open but not approved.
MATERIAL_ALTERNATES = [
    ("LSS-21-0005", "LSS-MAT-00013",
     "Proposed higher-strength substitute. NOT qualified: peak aged 7075 has poor short "
     "transverse stress corrosion resistance, which is the property the T7351 temper was "
     "selected for. Raise a change request before using it."),
]
