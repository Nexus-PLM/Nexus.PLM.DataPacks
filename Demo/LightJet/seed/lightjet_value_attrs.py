"""Requirement value attributes, and the requirement text that uses them.

A requirement that says "cabin altitude shall not exceed 2 400 m" has the number typed
into its prose. Change the number and you are hunting through sentences in a dozen
documents, and the one you miss is the one a supplier builds to.

A value attribute is the number held once, on the requirement that owns it, and
referenced from the text by a chip:

    <span class="req-attr-ref" data-name="MAX_CABIN_ALT"
          data-value="2400" data-magnitude="m">MAX_CABIN_ALT: 2400 m</span>

The value baked into the HTML is a cache, not the answer - the client re-resolves every
chip against the current attribute values before display. So changing the attribute
changes every sentence that references it, everywhere, at once.

**Inheritance is the half that matters for a certification programme.** A child
requirement sees its ancestors' value attributes and may reference them in its own text.
The client renders an inherited chip differently from an own chip, so a reviewer can see
at a glance which numbers this requirement OWNS and which it merely RESTATES. That
distinction is the whole argument against copying numbers down a tree: the aircraft-level
requirement owns the cabin altitude, the system requirement restates it, and nobody can
quietly change it at the bottom.

The tree below is built so that every level demonstrates it:

    LSS-REQ-ACFT-0001  owns MAX_CABIN_ALT, MAX_OP_ALT, the cabin rate limits
      LSS-REQ-SYS-0001   restates all four, owns none
    LSS-REQ-CERT-0001  owns the single-failure condition
      LSS-REQ-SYS-0002   owns the probability target and the emergency ceiling
        LSS-REQ-SUB-0001   restates the target, owns the channel count
          LSS-REQ-CMP-0001   restates both, owns the DO-160 category
"""

# ─────────────────────────────────────────────────────────────────────────────
# The values, by the requirement that OWNS them
# ─────────────────────────────────────────────────────────────────────────────


def v(name, value, magnitude=""):
    return {"name": name, "value": str(value), "magnitude": magnitude}


VALUE_ATTRS = {
    # ── Aircraft level: the numbers the whole programme hangs off ───────────
    "LSS-REQ-ACFT-0001": [
        v("MAX_CABIN_ALT", 2400, "m"),
        v("MAX_OP_ALT", 13700, "m"),
        v("CABIN_RATE_CLIMB", 150, "m/min"),
        v("CABIN_RATE_DESCENT", 90, "m/min"),
    ],
    "LSS-REQ-ACFT-0002": [
        v("INDEPENDENT_COMMS", 2, "means"),
        v("VHF_CHANNEL_SPACING", 8.33, "kHz"),
    ],
    "LSS-REQ-ACFT-0003": [
        v("OCCUPANT_PLACES", 7, "places"),
        v("CREW_PLACES", 2, "places"),
    ],

    # ── Certification level: what the rule demands ──────────────────────────
    "LSS-REQ-CERT-0001": [
        v("MAX_DIFF_PRESSURE", 0.62, "bar"),
    ],
    "LSS-REQ-CERT-0003": [
        v("DYNAMIC_LONGITUDINAL", 16, "g"),
        v("HIC_LIMIT", 1000, ""),
        v("FEMUR_LOAD_LIMIT", 10.0, "kN"),
    ],
    "LSS-REQ-CERT-0004": [
        v("VERTICAL_BURN_DURATION", 12, "s"),
    ],

    # ── System level: allocated, with the system's own derived numbers ──────
    "LSS-REQ-SYS-0004": [
        v("OCCUPANT_PLACES", 7, "places"),
    ],
    "LSS-REQ-SYS-0002": [
        v("HAZ_PROB_TARGET", "1E-7", "per FH"),
        v("CAT_PROB_TARGET", "1E-9", "per FH"),
        v("MAX_EMERGENCY_CABIN_ALT", 4600, "m"),
    ],
    "LSS-REQ-SYS-0003": [
        v("VHF_COUNT", 2, "units"),
    ],

    # ── Subsystem level ─────────────────────────────────────────────────────
    # The derived requirement has no parent by definition - that is what derived means -
    # so it has to own the structural limit it protects, or its own component
    # requirement below it would have nothing to inherit.
    "LSS-REQ-SUB-0002": [
        v("MAX_DIFF_PRESSURE", 0.62, "bar"),
    ],
    "LSS-REQ-SUB-0001": [
        v("CONTROL_CHANNELS", 2, "channels"),
    ],
    "LSS-REQ-SUB-0005": [
        v("PEAK_HEAT_RELEASE", 65, "kW/m2"),
        v("TOTAL_HEAT_RELEASE", 65, "kW-min/m2"),
        v("SMOKE_DENSITY_DS", 200, ""),
    ],

    # ── Component level: the numbers that reach a supplier ──────────────────
    "LSS-REQ-CMP-0001": [
        v("DO160_CATEGORY", "A2/B/S(B)", ""),
        v("SOFTWARE_LEVEL", "B", ""),
    ],
    "LSS-REQ-CMP-0002": [
        v("CRACK_PRESSURE", 0.62, "bar"),
        v("CRACK_TOLERANCE", 0.02, "bar"),
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# The requirement text that references them
# ─────────────────────────────────────────────────────────────────────────────

def chip(name, value, magnitude=""):
    """One value-attribute reference, in the markup the client resolves."""
    label = f"{name}: {value}" + (f" {magnitude}" if magnitude else "")
    return (f'<span class="req-attr-ref" data-name="{name}" '
            f'data-value="{value}" data-magnitude="{magnitude}">{label}</span>')


def _c(owner_pn, name):
    """A chip for an attribute, looked up from whichever requirement owns it."""
    for attr in VALUE_ATTRS[owner_pn]:
        if attr["name"] == name:
            return chip(attr["name"], attr["value"], attr["magnitude"])
    raise KeyError(f"{owner_pn} does not own {name}")


A1, A2, A3 = "LSS-REQ-ACFT-0001", "LSS-REQ-ACFT-0002", "LSS-REQ-ACFT-0003"
C1, C3, C4 = "LSS-REQ-CERT-0001", "LSS-REQ-CERT-0003", "LSS-REQ-CERT-0004"
S2, S3 = "LSS-REQ-SYS-0002", "LSS-REQ-SYS-0003"
B1, B5 = "LSS-REQ-SUB-0001", "LSS-REQ-SUB-0005"
M1, M2 = "LSS-REQ-CMP-0001", "LSS-REQ-CMP-0002"

# Every body below is HTML, and every number in it that is governed elsewhere is a chip
# rather than a typed figure. The ones marked "inherited" come from an ancestor, and the
# client styles them apart so a reviewer can see what this requirement does not own.
BODIES = {
    A1: (
        "<p>With the aeroplane at its maximum operating altitude of "
        f"{_c(A1, 'MAX_OP_ALT')} and the environmental control system operating "
        f"normally, cabin pressure altitude shall not exceed {_c(A1, 'MAX_CABIN_ALT')}."
        "</p>"
    ),
    "LSS-REQ-SYS-0001": (
        f"<p>The environmental control system shall maintain cabin pressure altitude at "
        f"or below {_c(A1, 'MAX_CABIN_ALT')} with the aeroplane at "
        f"{_c(A1, 'MAX_OP_ALT')}.</p>"
        f"<p>Cabin rate of change shall not exceed {_c(A1, 'CABIN_RATE_CLIMB')} in climb "
        f"or {_c(A1, 'CABIN_RATE_DESCENT')} in descent.</p>"
        "<p><em>Every figure above is inherited from the aircraft requirement "
        "LSS-REQ-ACFT-0001. This requirement allocates them to a system; it does not "
        "own them, and changing one here would be changing it in the wrong place.</em>"
        "</p>"
    ),
    A2: (
        f"<p>The aeroplane shall provide {_c(A2, 'INDEPENDENT_COMMS')} of independent "
        "air-to-ground voice communication and one satellite voice capability, usable "
        "from either crew station throughout the certified operating envelope. Channel "
        f"spacing shall be {_c(A2, 'VHF_CHANNEL_SPACING')}.</p>"
    ),
    S3: (
        f"<p>The communications system shall provide {_c(S3, 'VHF_COUNT')} VHF "
        "transceivers on independent power sources and independent antennas, with "
        f"{_c(A2, 'VHF_CHANNEL_SPACING')} channel spacing, plus one satellite voice "
        "terminal.</p>"
        "<p><em>The channel spacing is inherited from LSS-REQ-ACFT-0002; the transceiver "
        "count is this requirement's own.</em></p>"
    ),
    C1: (
        "<p>The pressurisation system shall be designed and substantiated so that no "
        "single failure, and no probable combination of failures, results in a cabin "
        "pressure altitude or a cabin differential pressure exceeding the limits of the "
        f"certification basis. Maximum differential pressure is "
        f"{_c(C1, 'MAX_DIFF_PRESSURE')}.</p>"
    ),
    S2: (
        "<p>No single failure, and no probable combination of failures, of the "
        "pressurisation control system shall result in cabin pressure altitude exceeding "
        f"{_c(S2, 'MAX_EMERGENCY_CABIN_ALT')} or in cabin differential pressure "
        f"exceeding {_c(C1, 'MAX_DIFF_PRESSURE')}.</p>"
        f"<p>The hazardous failure condition shall be shown extremely remote, at or below "
        f"{_c(S2, 'HAZ_PROB_TARGET')}; the catastrophic condition at or below "
        f"{_c(S2, 'CAT_PROB_TARGET')}.</p>"
        "<p><em>The differential pressure is inherited from the certification requirement "
        "LSS-REQ-CERT-0001. The probability targets and the emergency ceiling are "
        "derived here, which is why this requirement owns them.</em></p>"
    ),
    B1: (
        f"<p>The cabin pressure controller shall provide {_c(B1, 'CONTROL_CHANNELS')} "
        "control channels with independent pressure sensing, automatic changeover on "
        "channel failure, and a manual mode available to the crew.</p>"
        f"<p>The resulting hazardous failure condition shall meet "
        f"{_c(S2, 'HAZ_PROB_TARGET')}.</p>"
        "<p><em>The probability target is inherited from LSS-REQ-SYS-0002.</em></p>"
    ),
    M1: (
        f"<p>The cabin pressure controller shall be a {_c(B1, 'CONTROL_CHANNELS')} "
        "channel digital unit holding an ETSO authorisation, developed to design "
        f"assurance level {_c(M1, 'SOFTWARE_LEVEL')}, and qualified to DO-160G for "
        f"category {_c(M1, 'DO160_CATEGORY')} as installed.</p>"
        f"<p>It shall meet {_c(S2, 'HAZ_PROB_TARGET')} for the hazardous condition.</p>"
        "<p><em>This is the procurement specification the supplier builds to. The channel "
        "count and the probability target are inherited; the assurance level and the "
        "DO-160 category are set here because they are installation specific.</em></p>"
    ),
    M2: (
        "<p>The cabin pressure safety valve shall be wholly mechanical, shall crack at "
        f"{_c(M2, 'CRACK_PRESSURE')} differential plus or minus "
        f"{_c(M2, 'CRACK_TOLERANCE')}, and shall provide the flow capacity to limit "
        f"differential pressure to {_c('LSS-REQ-SUB-0002', 'MAX_DIFF_PRESSURE')} with "
        "the outflow valve "
        "failed closed and no electrical power available.</p>"
        "<p><em>Wholly mechanical is the point: anything electrical shares a failure mode "
        "with the control path this valve exists to protect against.</em></p>"
    ),
    C3: (
        "<p>Each occupant shall be protected under the emergency landing conditions. The "
        f"longitudinal dynamic condition is {_c(C3, 'DYNAMIC_LONGITUDINAL')}, with head "
        f"injury criterion not exceeding {_c(C3, 'HIC_LIMIT')} and femur load not "
        f"exceeding {_c(C3, 'FEMUR_LOAD_LIMIT')}.</p>"
    ),
    "LSS-REQ-SYS-0004": (
        "<p>Every occupant place, its restraint and its attachment to primary structure "
        f"shall withstand the {_c(C3, 'DYNAMIC_LONGITUDINAL')} longitudinal dynamic "
        "condition without failure of the restraint, injurious loads on the occupant, or "
        "separation of the seat from the floor.</p>"
        f"<p>This applies to all {_c('LSS-REQ-SYS-0004', 'OCCUPANT_PLACES')} occupant "
        "places.</p>"
        "<p><em>The dynamic condition is inherited from the certification basis; the "
        "occupant count is this requirement's own, because the system is what has to "
        "protect them. The load path argument is this requirement's too.</em></p>"
    ),
    "LSS-REQ-CMP-0005": (
        f"<p>The passenger club seat shall be substantiated to the "
        f"{_c(C3, 'DYNAMIC_LONGITUDINAL')} longitudinal dynamic condition in the "
        "forward-facing position, shall incorporate a swivel interlock that holds the "
        "forward-facing position whenever the seat belt sign is illuminated, and shall "
        "use fire blocked cushions meeting the Appendix F Part II oil burner criteria.</p>"
        f"<p>Head injury criterion shall not exceed {_c(C3, 'HIC_LIMIT')} and femur load "
        f"shall not exceed {_c(C3, 'FEMUR_LOAD_LIMIT')}.</p>"
        "<p><em>Every acceptance figure here is inherited from LSS-REQ-CERT-0003. The "
        "seat supplier is told the number once, and if the certification basis moves the "
        "specification moves with it.</em></p>"
    ),
    B5: (
        "<p>Cabin lining panels whose exposed surface area exceeds the threshold of the "
        f"certification basis shall meet a peak heat release of not more than "
        f"{_c(B5, 'PEAK_HEAT_RELEASE')}, a total heat release of not more than "
        f"{_c(B5, 'TOTAL_HEAT_RELEASE')}, and a specific optical smoke density of not "
        f"more than {_c(B5, 'SMOKE_DENSITY_DS')}.</p>"
    ),
    "LSS-REQ-CMP-0006": (
        "<p>The forward sidewall panels shall meet a peak and total heat release of not "
        f"more than {_c(B5, 'PEAK_HEAT_RELEASE')} and {_c(B5, 'TOTAL_HEAT_RELEASE')} "
        f"respectively, and a specific optical smoke density of not more than "
        f"{_c(B5, 'SMOKE_DENSITY_DS')}, as built with the production decorative "
        "finish.</p>"
        "<p><em>All three criteria are inherited from the subsystem requirement. 'As "
        "built with the production finish' is this requirement's own addition, and it is "
        "the part that actually fails in test.</em></p>"
    ),
    C4: (
        "<p>Materials used in the cabin interior shall meet the flammability criteria "
        "appropriate to their surface area and location. The vertical burn condition is "
        f"applied for {_c(C4, 'VERTICAL_BURN_DURATION')}.</p>"
    ),
}
