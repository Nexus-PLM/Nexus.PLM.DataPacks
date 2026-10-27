"""Make the type-design review states reachable only through the release route (NI-00000728).

Marc's decision, 26 Oct 2026: gate the LightSpeed type-design types so that a person sets only
"In Work" and submits, and In Design Review, In Stress Review, Airworthiness Sign-off and
Released are reached only by the workflow's own status nodes. A failed, rejected or terminated
route returns the record to the state it started from (the Engine does that since Services
#955 and the earlier ReleaseRecordAsync work).

Two definitions change, both already on the site:

1. cstLssTypeDesignRelease - the route the SubmitForRelease action starts. It used to carry a
   single Status node (Set Released) at the end, so the review states had to be set by hand;
   and its two branches out of Start were never both followed, because the engine takes the
   first connection, so "Stress substantiation" was never reached. It is now sequential, with a
   Status node ahead of each review: Submit -> In Design Review -> Design check -> In Stress
   Review -> Stress substantiation -> Airworthiness Sign-off -> Airworthiness sign-off ->
   Released -> End. There is deliberately no reject edge: a rejection ends the route as Failed,
   and the engine returns the record to In Work with a history entry saying who rejected it
   and why. Resubmitting starts the route again.

2. cstLssTypeDesignGates - the gates that guard those states for the 19 declared types. Each
   gate's approver list is emptied, and a gate for Released is added. An empty approver list
   means CLOSED to everyone but an administrator (NI-00000497 / 720), which is exactly the
   semantics wanted: the only thing that can write those states is the route, whose status
   nodes do not pass through the gate.

Consequence, accepted by Marc: records that were hand-set into a review state before this
change can no longer be moved by hand (an administrator still can, and the route always can).

Run with NEXUS_ADMIN_PASSWORD set. Backs both definitions up to reports/ first.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plm_agent import admin_agent  # noqa: E402

RELEASE_ID = "21a10000-0000-4000-a000-000000000001"   # cstLssTypeDesignRelease
GATES_ID   = "21a20000-0000-4000-a000-000000000001"   # cstLssTypeDesignGates

DESIGN_ENGINEERING = "e04c86b0-577c-4012-8310-92fc94bff908"
STRESS             = "dadefa57-824c-46c2-bcd2-9d21e38321ed"
AIRWORTHINESS      = "90385854-27fc-442b-9a71-fbbbdbf396c2"


def node(id_, node_type, title, col, row=1, action=None, target=None, groups=None, instruction=None):
    n = {
        "Id": id_, "NodeType": node_type, "Title": title,
        "GridRow": row, "GridColumn": col, "RowSpan": 1, "ColSpan": 1,
        "ActionKey": action, "TargetStatus": target,
        "Parameters": {"instruction": instruction} if instruction else None,
        "ApproverUserIds": [], "ApproverGroupIds": list(groups or []), "ApproverRoleIds": [],
        "PrivilegedUserIds": [], "PrivilegedGroupIds": [], "PrivilegedRoleIds": [],
        "ApprovalMode": "All" if node_type == "Approver" else None,
        "RequiredApprovalCount": 1 if node_type == "Approver" else 0,
    }
    if node_type in ("Approver", "Status"):
        n = {"$nodeType": node_type, **n}
    if node_type == "Approver":
        n["AssignToInitiator"] = False
    return n


def connection(i, source, target):
    return {"Id": "c%d" % i, "SourceNodeId": source, "SourceSide": "Right",
            "TargetNodeId": target, "TargetSide": "Left", "IsRejectPath": False}


RELEASE_ROUTE = {
    "TriggerEvent": "Manual",
    "AssignedUserIds": [], "AssignedGroupIds": [], "AssignedRoleIds": [], "AssignedProjectIds": [],
    "Nodes": [
        node("start", "Start", "Submit for release", 0),
        node("s-design", "Status", "Set In Design Review", 1, action="change_status", target="In Design Review"),
        node("design", "Approver", "Design check", 2, action="approve_workflow", groups=[DESIGN_ENGINEERING],
             instruction="Is the definition complete and correct, and does it match the drawing? "
                         "Approving sends it to stress; it does not release it. Rejecting returns it to In Work."),
        node("s-stress", "Status", "Set In Stress Review", 3, action="change_status", target="In Stress Review"),
        node("stress", "Approver", "Stress substantiation", 4, action="approve_workflow", groups=[STRESS],
             instruction="Is the structural substantiation complete, with positive margins against the critical "
                         "load case? Approving sends it to airworthiness; it does not release it. Rejecting returns it to In Work."),
        node("s-airworthiness", "Status", "Set Airworthiness Sign-off", 5, action="change_status", target="Airworthiness Sign-off"),
        node("airworthiness", "Approver", "Airworthiness sign-off (DOA privilege)", 6, action="approve_workflow", groups=[AIRWORTHINESS],
             instruction="Exercise the Part 21A.263 design organisation privilege: does this data comply with the "
                         "certification basis? APPROVING RELEASES IT - aeroplanes may be built to it, and the only ways "
                         "out afterwards are a new revision or supersession. Rejecting returns it to In Work."),
        node("release", "Status", "Set Released", 7, action="change_status", target="Released"),
        node("end", "End", "End", 8),
    ],
    "Connections": [
        connection(1, "start", "s-design"),
        connection(2, "s-design", "design"),
        connection(3, "design", "s-stress"),
        connection(4, "s-stress", "stress"),
        connection(5, "stress", "s-airworthiness"),
        connection(6, "s-airworthiness", "airworthiness"),
        connection(7, "airworthiness", "release"),
        connection(8, "release", "end"),
    ],
}


def gated(definition):
    """The gates definition with every approver list emptied and a Released gate added."""
    nodes = []
    for n in definition["Nodes"]:
        if n.get("NodeType") == "Approver":
            n = dict(n, ApproverUserIds=[], ApproverGroupIds=[], ApproverRoleIds=[],
                     PrivilegedUserIds=[], PrivilegedGroupIds=[], PrivilegedRoleIds=[])
            n["Parameters"] = {"instruction": "Reached only through the type design release route. "
                                              "Closed to everyone but an administrator."}
        nodes.append(n)
    if not any(n.get("Title") == "Released" for n in nodes):
        nodes.append(node("gate3", "Approver", "Released", 0, row=4, action="approve_workflow",
                          instruction="Reached only through the type design release route. "
                                      "Closed to everyone but an administrator."))
    return dict(definition, Nodes=nodes)


def main():
    adm = admin_agent()
    here = os.path.dirname(os.path.abspath(__file__))
    backup = {}
    for wid in (RELEASE_ID, GATES_ID):
        backup[wid] = adm.get("/api/workflow-definitions/%s" % wid)
    with open(os.path.join(here, "reports", "workflows-backup-before-type-design-gating.json"), "w", encoding="utf-8") as fh:
        json.dump(backup, fh, indent=1)
    print("backup written")

    rel = backup[RELEASE_ID]
    adm.put("/api/workflow-definitions/%s" % RELEASE_ID,
            {"name": rel["name"], "displayName": rel["displayName"], "isOnline": True, "definitionJson": RELEASE_ROUTE})
    gates = backup[GATES_ID]
    adm.put("/api/workflow-definitions/%s" % GATES_ID,
            {"name": gates["name"], "displayName": gates["displayName"], "isOnline": True,
             "definitionJson": gated(json.loads(gates["definitionJson"]))})

    for wid in (RELEASE_ID, GATES_ID):
        d = adm.get("/api/workflow-definitions/%s" % wid)
        dj = json.loads(d["definitionJson"])
        print("%-26s nodes: %s" % (d["name"], ["%s%s" % (n["Title"], "" if n.get("ApproverGroupIds") else " (closed)" if n["NodeType"] == "Approver" else "") for n in dj["Nodes"]]))


if __name__ == "__main__":
    main()
