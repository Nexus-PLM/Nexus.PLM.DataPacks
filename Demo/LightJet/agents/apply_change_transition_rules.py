"""Author the transition rules for the change objects on the live site (NI-00000783/796/799).

Marc's decision, 26 Oct 2026: configuration, not code - who may move what, from which state to
which, on ECR, ECO, ECN and ProblemReport. The rules mirror each controller's state machine
(EcrsController/EcosController/EcnsController/ProblemReportsController `Transitions`) and the
subjects the site's policy already grants `canTransition` in each from-state: authors
(Design Engineering, Systems Engineering, plus Quality Assurance for problem reports) move a
record out of Draft and Submitted and may cancel/void it; the Change Control Board takes every
decision from Under Review onward. Administrators appear on every rule.

Deliberately NOT the platform-wide option of making an empty rule set mean deny.

Run with NEXUS_ADMIN_PASSWORD set. Writes a backup of each model to reports/ before changing it
and refuses to run against a type that already has rules.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plm_agent import admin_agent  # noqa: E402

AUTHORS    = "role:Admin, group:LSS Change Control Board, group:LSS Design Engineering, group:LSS Systems Engineering"
PR_AUTHORS = AUTHORS + ", group:LSS Quality Assurance"
BOARD      = "role:Admin, group:LSS Change Control Board"


def rules(pairs):
    return [{"fromState": f, "toState": t, "allowedRoles": who} for f, t, who in pairs]


PLAN = {
    "ECR": rules([
        ("Draft", "Submitted", AUTHORS), ("Draft", "Cancelled", AUTHORS),
        ("Submitted", "Under Review", BOARD), ("Submitted", "Cancelled", AUTHORS),
        ("Under Review", "Approved", BOARD), ("Under Review", "Rejected", BOARD),
    ]),
    "ECO": rules([
        ("Draft", "Submitted", AUTHORS), ("Draft", "Cancelled", AUTHORS),
        ("Submitted", "Under Review", BOARD), ("Submitted", "Cancelled", AUTHORS),
        ("Under Review", "Approved", BOARD), ("Under Review", "Rejected", BOARD),
        ("Approved", "Released", BOARD), ("Released", "Closed", BOARD),
    ]),
    "ECN": rules([
        ("Draft", "Submitted", AUTHORS), ("Draft", "Cancelled", AUTHORS),
        ("Submitted", "Under Review", BOARD), ("Submitted", "Cancelled", AUTHORS),
        ("Under Review", "Approved", BOARD), ("Under Review", "Rejected", BOARD),
        ("Approved", "Issued", BOARD), ("Issued", "Closed", BOARD),
    ]),
    "ProblemReport": rules([
        ("Draft", "Submitted", PR_AUTHORS), ("Draft", "Voided", PR_AUTHORS),
        ("Submitted", "Under Triage", PR_AUTHORS), ("Submitted", "Voided", PR_AUTHORS),
        ("Under Triage", "Open", PR_AUTHORS), ("Under Triage", "Rejected", PR_AUTHORS),
        ("Open", "In Analysis", PR_AUTHORS), ("Open", "On Hold", PR_AUTHORS),
        ("In Analysis", "Pending Action", PR_AUTHORS), ("In Analysis", "On Hold", PR_AUTHORS),
        ("Pending Action", "Under Review", PR_AUTHORS), ("Pending Action", "On Hold", PR_AUTHORS),
        ("Under Review", "Closed", BOARD), ("Under Review", "In Analysis", BOARD),
        ("On Hold", "Open", PR_AUTHORS), ("On Hold", "In Analysis", PR_AUTHORS),
        ("On Hold", "Pending Action", PR_AUTHORS), ("On Hold", "Under Review", PR_AUTHORS),
    ]),
}


def main():
    adm = admin_agent()
    backup = {}
    for type_name, type_rules in PLAN.items():
        sec = adm.get("/api/types/%s/security" % type_name)
        if sec["transitionRules"]:
            raise SystemExit("%s already has %d transition rules - not overwriting." % (type_name, len(sec["transitionRules"])))
        backup[type_name] = json.loads(json.dumps(sec))
        sec["transitionRules"] = type_rules
        adm.put("/api/types/%s/security" % type_name, sec)
        print("%-14s rules now %d" % (type_name, len(adm.get("/api/types/%s/security" % type_name)["transitionRules"])))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "policy-backup-before-transition-rules.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(backup, fh, indent=1)
    print("backup written to", out)


if __name__ == "__main__":
    main()
