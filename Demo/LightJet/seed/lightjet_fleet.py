"""The three NX-200 airframes, and what is actually installed on each.

The customer support agent could not answer the first question the fleet ever asks -
"what is the configuration of airframe 002?" - because no aeroplane existed anywhere in
the data. Three aircraft were flying, and they existed only as English inside free-text
attributes: "airframe 003" in a nonconformance, "S/N 0002" on a release certificate.

An individual aeroplane is a manufactured article, not type design data. The type design
says what an NX-200 is; an airframe says what THIS one is, which revision of each
installation it left the factory with, who operates it and how many hours it has flown.
That distinction is why Aircraft sits under the non-type-design base: revising an aircraft
record does not touch the type certificate.

The as-built structure is ordinary bill-of-materials links from the aircraft to the
installations, **pinned to the revision actually fitted**. Pinned is the whole point: a
released installation that floats on `latest` tells you what the drawing says today, not
what is bolted to the aeroplane. An as-built that floats is not an as-built.

That one change makes the fleet questions answerable by navigation:

    where_used(part)            -> the aeroplanes it is installed on
    bom(aircraft)               -> that aeroplane's configuration
    a service bulletin's effectivity -> a set of real objects, not a sentence
"""

from lightjet_data import PROGRAMME, ROOT_FOLDER, T

ACTIVE, RESTRICTED, DRAFT = "Active", "Restricted", "Draft"
F_FLEET = f"{ROOT_FOLDER}/Continued Airworthiness/In-Service Reports"


def aircraft(pn, msn, registration, operator, delivered, hours, cycles, status,
             notes, extra=None):
    attrs = {
        "programmeCode": PROGRAMME,
        "manufacturerSerialNumber": msn,
        "registration": registration,
        "operator": operator,
        "deliveryDate": delivered,
        "totalFlightHours": hours,
        "totalCycles": cycles,
        "recordOwnerFunction": "Customer Support",
        "controlledItem": True,
        "typeDesignData": False,
        "engineeringOwner": "f.mbeki",
        "assignee": "f.mbeki",
        "itemMaturity": "In production",
    }
    attrs.update(extra or {})
    return {
        "type": f"{T}Aircraft", "pn": pn,
        "description": f"NX-200 MSN {msn} - {registration}",
        "status": status, "revision": "A", "history": [("A", status)],
        "attrs": attrs, "folder": F_FLEET, "notes": notes,
    }


AIRCRAFT = [
    aircraft(
        "LSS-AC-001", "001", "G-NXPA", "Light Speed Systems (flight test)",
        "2026-07-14", 318, 214, RESTRICTED,
        extra={"aircraftStatus": "Flight test - experimental",
               "certificationStatus": "Not type certificated; permit to fly",
               "baseLocation": "Cranfield",
               "lastInspectionDate": "2026-10-02",
               "openBulletins": "LSS-SB-21-001, LSS-SB-21-002",
               "buildStandard": "Prototype build standard 01"},
        notes="First flight 14 July 2026, two weeks late against plan. Restricted: "
              "flying on a permit, not a certificate of airworthiness, so it is not "
              "eligible for revenue service and nothing released against it is approved "
              "design data."),

    aircraft(
        "LSS-AC-002", "002", "G-MECA", "Meridian Executive Charter",
        "2026-08-29", 412, 268, ACTIVE,
        extra={"aircraftStatus": "In service",
               "certificationStatus": "Permit to fly pending type certificate",
               "baseLocation": "Farnborough",
               "lastInspectionDate": "2026-10-11",
               "openBulletins": "LSS-SB-21-001, LSS-SB-21-002, LSS-SB-23-001",
               "buildStandard": "Build standard 02"},
        notes="The aeroplane most of the in-service findings come from. Its ECS "
              "installation was released on EASA Form 1 LSS-ARC-00001, and the weighed "
              "mass of 86.4 kg recorded against LSS-21-INST-001 was weighed on this "
              "airframe with the glass scoop fitted."),

    aircraft(
        "LSS-AC-003", "003", "G-MECB", "Meridian Executive Charter",
        "2026-09-26", 196, 131, ACTIVE,
        extra={"aircraftStatus": "In service",
               "certificationStatus": "Permit to fly pending type certificate",
               "baseLocation": "Farnborough",
               "lastInspectionDate": "2026-10-09",
               "openBulletins": "LSS-SB-21-001, LSS-SB-23-001",
               "buildStandard": "Build standard 02"},
        notes="The airframe on which sealant batch 26052 was applied four days past its "
              "shelf life - nonconformance LSS-NCR-00005, dispositioned rework. The "
              "affected joints were found from the batch record in about an hour, which "
              "is the whole argument for batch traceability."),
]


# ─────────────────────────────────────────────────────────────────────────────
# As-built configuration
# ─────────────────────────────────────────────────────────────────────────────
# Every link is PINNED to the revision actually fitted. An as-built that follows "latest"
# answers what the drawing says today, which is the one thing an as-built must never do.

def fitted(aircraft_pn, installation_pn, revision, position, note=None):
    return {"parent": aircraft_pn, "child": installation_pn, "qty": 1,
            "instance": position, "find": None, "rule": "pinned",
            "pinRevision": revision, "scrap": 0.0, "note": note}


AS_BUILT = [
    # MSN 001 - the prototype. Interior released against non-approved design data.
    fitted("LSS-AC-001", "LSS-21-INST-001", "A", "ECS installation"),
    fitted("LSS-AC-001", "LSS-23-INST-001", "A", "Communications installation"),
    fitted("LSS-AC-001", "LSS-25-INST-001", "A", "Cabin interior",
           "Released on LSS-ARC-00003 as Prototype against non-approved design data - "
           "not eligible for a type certificated aeroplane."),

    # MSN 002 - the one the findings come from.
    fitted("LSS-AC-002", "LSS-21-INST-001", "A", "ECS installation",
           "Released on EASA Form 1 LSS-ARC-00001, 5 June 2026."),
    fitted("LSS-AC-002", "LSS-23-INST-001", "A", "Communications installation"),
    fitted("LSS-AC-002", "LSS-25-INST-001", "A", "Cabin interior"),

    # MSN 003 - sealant nonconformance airframe.
    fitted("LSS-AC-003", "LSS-21-INST-001", "A", "ECS installation",
           "Sealant batch 26052 applied past shelf life at this installation; reworked "
           "under LSS-NCR-00005."),
    fitted("LSS-AC-003", "LSS-23-INST-001", "A", "Communications installation"),
    fitted("LSS-AC-003", "LSS-25-INST-001", "A", "Cabin interior"),
]


# Serialised equipment fitted to a specific aeroplane, where the serial matters for
# continued airworthiness - a life limit, a calendar life, or an authorised release.
SERIALISED_FIT = [
    ("LSS-AC-002", "LSS-V-00002", "A", "Air cycle machine S/N MAS7730-0007",
     "Life limited to 20 000 FH. 412 hours accrued on this airframe."),
    ("LSS-AC-003", "LSS-V-00002", "A", "Air cycle machine S/N MAS7730-0008",
     "Life limited to 20 000 FH."),
    ("LSS-AC-002", "LSS-V-00013", "A", "Underwater locating beacon",
     "Battery life limited to six CALENDAR years, not flight hours. "
     "LSS-SB-23-001 is mandatory against it and there is no calendar-life field on the "
     "part to record it against."),
    ("LSS-AC-003", "LSS-V-00013", "A", "Underwater locating beacon",
     "Battery life limited to six calendar years."),
    ("LSS-AC-002", "LSS-V-00006", "A", "Cabin pressure safety valve",
     "Catastrophic failure effect; the last line of defence against cabin "
     "overpressure."),
    ("LSS-AC-003", "LSS-V-00006", "A", "Cabin pressure safety valve", None),
]
