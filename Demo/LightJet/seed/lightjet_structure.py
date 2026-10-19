"""The NX-200 bill of materials for ATA 21, 23 and 25.

Each row is (parent, child, quantity, instance name, find number, revision rule). The
revision rule matters and is not decoration:

* `latest` is the default and right for an item still in work.
* `latest-released` is right for most production structure - the parent follows the child's
  released configuration and ignores an in-work revision.
* `pinned` is for the cases where an assembly is tied to one specific revision of a child,
  which in aviation is usually because a qualification test or a dynamic test was run with
  that exact configuration and the credit does not carry forward.

Bill-of-materials links are deliberately NOT carried in a `.nexuspack` - the format has no
representation for them - so this structure only exists through the Engine's BOM API. That
is the reason the seed loader exists at all rather than everything shipping as a data pack.

Scrap percentage is set where the real process has a known loss: composite layup and the
machined fittings cut from plate.
"""

LATEST = "latest"
RELEASED = "latest-released"
PINNED = "pinned"


def bom(parent, child, qty=1, instance=None, find=None, rule=RELEASED, scrap=0.0,
        pin_revision=None, note=None):
    return {
        "parent": parent, "child": child, "qty": qty,
        "instance": instance, "find": find, "rule": rule,
        "scrap": scrap, "pinRevision": pin_revision, "note": note,
    }


# ─────────────────────────────────────────────────────────────────────────────
# ATA 21 - Environmental control system
# ─────────────────────────────────────────────────────────────────────────────

BOM_21 = [
    # Level 1 - the installation
    bom("LSS-21-INST-001", "LSS-21-0001", 1, "Bleed supply duct", 10),
    bom("LSS-21-INST-001", "LSS-V-00001", 1, "Bleed shutoff / PRV", 20),
    bom("LSS-21-INST-001", "LSS-V-00007", 1, "Primary heat exchanger", 30),
    bom("LSS-21-INST-001", "LSS-21-0005", 1, "HX mount assembly", 40),
    bom("LSS-21-INST-001", "LSS-V-00002", 1, "Air cycle machine", 50,
        rule=PINNED, pin_revision="A",
        note="Pinned to revision A: the DO-160G qualification campaign "
             "LSS-CERT-QUAL-003 was run on this configuration and the credit does not "
             "carry forward to a later revision without a delta assessment."),
    bom("LSS-21-INST-001", "LSS-V-00003", 1, "Water separator", 60),
    bom("LSS-21-INST-001", "LSS-21-0013", 1, "Condenser drain line", 70),
    bom("LSS-21-INST-001", "LSS-21-0008", 1, "Cabin distribution manifold", 80),
    bom("LSS-21-INST-001", "LSS-E-00001", 1, "ECS controller", 90),
    bom("LSS-21-INST-001", "LSS-W21-001", 1, "ECS control harness", 100),
    bom("LSS-21-INST-001", "LSS-V-00004", 1, "Cabin pressure controller", 110),
    bom("LSS-21-INST-001", "LSS-21-0011", 2, "Outflow valve bracket", 120),
    bom("LSS-21-INST-001", "LSS-V-00005", 1, "Outflow valve", 130),
    bom("LSS-21-INST-001", "LSS-V-00006", 1, "Cabin pressure safety valve", 140),
    bom("LSS-21-INST-001", "LSS-21-0012", 1, "Ram air inlet scoop", 150, rule=LATEST,
        note="Follows latest, not latest-released: the redesigned scoop is still in "
             "design review and the installation is tracking it."),
    bom("LSS-21-INST-001", "LSS-21-0014", 1, "Firewall penetration seal plate", 160),
    bom("LSS-21-INST-001", "LSS-CM-0001", 1, "Sealant, as required", 900,
        rule=LATEST, note="Quantity as required; batch traceability recorded at build."),

    # Level 2 - bleed duct assembly
    bom("LSS-21-0001", "LSS-21-0002", 1, "Forward duct", 10),
    bom("LSS-21-0001", "LSS-21-0003", 1, "Aft duct", 20),
    bom("LSS-21-0001", "LSS-21-0004", 3, "V-band coupling", 30),
    bom("LSS-21-0001", "LSS-STD-00001", 3, "V-band clamp", 40),

    # Level 2 - heat exchanger mount assembly
    bom("LSS-21-0005", "LSS-21-0006", 1, "Mount bracket LH", 10, scrap=8.0),
    bom("LSS-21-0005", "LSS-21-0007", 1, "Mount bracket RH", 20, scrap=8.0),
    bom("LSS-21-0005", "LSS-STD-00002", 8, "Attachment bolt", 30),
    bom("LSS-21-0005", "LSS-STD-00003", 8, "Self-locking nut", 40),

    # Level 2 - distribution manifold
    bom("LSS-21-0008", "LSS-21-0009", 1, "Manifold shell", 10, scrap=12.0),
    bom("LSS-21-0008", "LSS-21-0010", 6, "Outlet nozzle", 20),

    # Level 2 - the controller carries its software as a configuration item
    bom("LSS-E-00001", "LSS-SW-0001", 1, "Controller software", 10, rule=PINNED,
        pin_revision="C",
        note="Pinned to revision C. Loadable software is part of the approved "
             "configuration: an operator has to know which version is installed, so the "
             "link does not float."),
]


# ─────────────────────────────────────────────────────────────────────────────
# ATA 23 - Communications
# ─────────────────────────────────────────────────────────────────────────────

BOM_23 = [
    bom("LSS-23-INST-001", "LSS-E-00010", 1, "Audio control panel", 10),
    bom("LSS-23-INST-001", "LSS-V-00010", 2, "VHF transceiver", 20),
    bom("LSS-23-INST-001", "LSS-V-00011", 1, "SATCOM terminal", 30),
    bom("LSS-23-INST-001", "LSS-V-00014", 1, "SATCOM antenna", 40),
    bom("LSS-23-INST-001", "LSS-E-00011", 2, "VHF blade antenna", 50),
    bom("LSS-23-INST-001", "LSS-23-0001", 2, "Antenna doubler", 60, scrap=6.0),
    bom("LSS-23-INST-001", "LSS-V-00012", 1, "Cockpit voice recorder", 70),
    bom("LSS-23-INST-001", "LSS-V-00015", 3, "Headset jack panel", 80),
    bom("LSS-23-INST-001", "LSS-23-0002", 1, "Avionics tray", 90),
    bom("LSS-23-INST-001", "LSS-E-00012", 1, "Static discharger set", 100),
    bom("LSS-23-INST-001", "LSS-W23-001", 1, "Coaxial harness", 110),
    bom("LSS-23-INST-001", "LSS-W23-002", 1, "Audio harness", 120),
    bom("LSS-23-INST-001", "LSS-W23-003", 1, "SATCOM harness", 130, rule=LATEST,
        note="Follows latest: awaiting airworthiness sign-off."),

    bom("LSS-E-00010", "LSS-SW-0002", 1, "Audio panel software", 10, rule=PINNED,
        pin_revision="A"),
    bom("LSS-E-00010", "LSS-HW-0001", 1, "Audio matrix CPLD", 20, rule=PINNED,
        pin_revision="A",
        note="Pinned: the DO-254 substantiation is against hardware version B of this "
             "item at revision A of the part."),

    bom("LSS-V-00012", "LSS-V-00013", 1, "Underwater locating beacon", 10),
]


# ─────────────────────────────────────────────────────────────────────────────
# ATA 25 - Equipment and furnishings
# ─────────────────────────────────────────────────────────────────────────────

BOM_25 = [
    bom("LSS-25-INST-001", "LSS-F-00001", 2, "Pilot seat", 10),
    bom("LSS-25-INST-001", "LSS-F-00010", 4, "Passenger club seat", 20),
    bom("LSS-25-INST-001", "LSS-F-00020", 1, "Sidewall LH forward", 30),
    bom("LSS-25-INST-001", "LSS-F-00021", 1, "Sidewall RH forward", 40),
    bom("LSS-25-INST-001", "LSS-F-00030", 1, "Ceiling panel assembly", 50),
    bom("LSS-25-INST-001", "LSS-F-00040", 1, "Carpet set", 60),
    bom("LSS-25-INST-001", "LSS-F-00050", 1, "Galley monument", 70),
    bom("LSS-25-INST-001", "LSS-F-00060", 1, "Lavatory module", 80),
    bom("LSS-25-INST-001", "LSS-F-00070", 1, "Baggage restraint net", 90),
    bom("LSS-25-INST-001", "LSS-F-00080", 6, "Window shade", 100),
    bom("LSS-25-INST-001", "LSS-F-00090", 1, "Emergency equipment stowage", 110),
    bom("LSS-25-INST-001", "LSS-F-00100", 1, "Insulation blanket set", 120),
    bom("LSS-25-INST-001", "LSS-25-0002", 4, "Cabin floor panel", 130, scrap=10.0),
    bom("LSS-25-INST-001", "LSS-25-0003", 16, "Cabin seat track fitting", 140,
        scrap=7.0),
    bom("LSS-25-INST-001", "LSS-25-0001", 8, "Flight compartment track fitting", 150,
        scrap=7.0),
    bom("LSS-25-INST-001", "LSS-F-00110", 1, "Divider and credenza", 160, rule=LATEST,
        note="Customer variant still in design review; the installation tracks latest "
             "until the heat release and smoke density results are in."),
    bom("LSS-25-INST-001", "LSS-CM-0010", 1, "Film adhesive, as required", 900,
        rule=LATEST),

    # Pilot seat assembly
    bom("LSS-F-00001", "LSS-F-00002", 1, "Bottom cushion", 10, rule=PINNED,
        pin_revision="A",
        note="Pinned to the cushion revision the Appendix F Part II oil burner test was "
             "run on. A cushion change invalidates the fire blocking credit."),
    bom("LSS-F-00001", "LSS-F-00003", 1, "Back cushion", 20, rule=PINNED,
        pin_revision="A"),
    bom("LSS-F-00001", "LSS-V-00020", 1, "Restraint, four point", 30),

    # Passenger seat assembly
    bom("LSS-F-00010", "LSS-F-00011", 1, "Cushion set", 10, rule=PINNED,
        pin_revision="A"),
    bom("LSS-F-00010", "LSS-V-00020", 1, "Restraint, four point", 20),
    bom("LSS-F-00010", "LSS-V-00021", 1, "Recline and swivel mechanism", 30),

    # Panels are built from bought blanks
    bom("LSS-F-00020", "LSS-V-00022", 2, "Sandwich panel blank", 10, scrap=15.0),
    bom("LSS-F-00020", "LSS-V-00023", 1, "Upholstery leather", 20, scrap=18.0),
    bom("LSS-F-00021", "LSS-V-00022", 2, "Sandwich panel blank", 10, scrap=15.0),
    bom("LSS-F-00021", "LSS-V-00023", 1, "Upholstery leather", 20, scrap=18.0),
    bom("LSS-F-00030", "LSS-V-00022", 3, "Sandwich panel blank", 10, scrap=15.0),
    bom("LSS-F-00050", "LSS-V-00022", 4, "Sandwich panel blank", 10, scrap=15.0),
    bom("LSS-F-00060", "LSS-V-00022", 5, "Sandwich panel blank", 10, scrap=15.0),
    bom("LSS-F-00011", "LSS-V-00023", 1, "Upholstery leather", 10, scrap=20.0),
]

ALL_BOM = BOM_21 + BOM_23 + BOM_25
