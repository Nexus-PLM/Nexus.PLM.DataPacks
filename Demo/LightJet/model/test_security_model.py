"""Invariants the NX-200 security model must hold, as tests.

Nine role agents spent a working day finding these by hand, one 403 at a time, and most of
what they found was not a product defect - it was this model granting the wrong thing. The
expensive part was never the fix; it was discovering the gap at all. So each invariant here
is one a live agent had to discover, and the comment says which.

These run without a server and without pytest:

    cd Demo/LightJet && LIGHTJET_PREFIX=cst python model/test_security_model.py

pytest collects them too, if it is installed.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
# The project-membership invariant reads the seed's project table, because that is where
# the fact lives - and project membership is checked BEFORE any policy row, so a model
# that looks right can still refuse everybody.
sys.path.insert(0, str(Path(__file__).parent.parent / "seed"))

import aviation_model as A                                            # noqa: E402
import aviation_types as A_TYPES                                      # noqa: E402
import build_customization as B                                      # noqa: E402

# Every lifecycle the model declares, with a concrete type that uses it, so an invariant is
# checked against each shape rather than against one convenient example.
LIFECYCLES = [
    ("type design", "Drawing",          [s for s, _ in A.TYPE_DESIGN_STATES]),
    ("support",     "Tooling",          [s for s, _ in A.SUPPORT_STATES]),
    ("compliance",  "ComplianceReport", [s for s, _ in A.COMPLIANCE_STATES]),
    ("quality",     "Ncr",              [s for s, _ in A.QUALITY_STATES]),
    ("certificate", "CofC",             [s for s, _ in A.CERTIFICATE_STATES]),
    ("publication", "ServiceBulletin",  [s for s, _ in A.PUBLICATION_STATES]),
]

GROUP_NAMES = {name for name, _description in A.GROUPS}


# The reference kinds that carry a certification credit: the link IS the credit, so it pins
# the revision it was granted against. The operational kinds (affected item, affected unit,
# fitted to, occurrence on, governs application of, embodied by, regulatory basis) describe a
# live relationship and correctly follow the current revision.
CREDIT_BEARING_KINDS = {
    "EvidenceForLink", "DemonstratesComplianceOfLink", "TestedConfigurationLink",
    "FirstArticleOfLink", "SubstantiatedByLink",
}


def models():
    """Every (label, stem, states, built model) the model declares.

    Every CONCRETE type that ships a policy, not a hand-picked sample. It started as six
    representative lifecycles, which is how a defect in the Aircraft type's delete scope
    survived the first run of these tests: the sample is the part you remember to look at,
    and the type added next month is the part you do not. The LIFECYCLES table is kept
    because a named lifecycle gives a readable label when something fails.
    """
    sampled = {stem for _label, stem, _states in LIFECYCLES}
    for label, stem, states in LIFECYCLES:
        yield label, stem, states, B.security_model(stem, states)

    for definition in (B.CONCRETE_ITEM_TYPES + B.CONCRETE_DOC_TYPES
                       + B.CONCRETE_REQ_TYPES + B.CONCRETE_MATERIAL_TYPES
                       + B.CONCRETE_RECORD_TYPES):
        stem = definition["typeName"].replace(B.BASE, "", 1)
        if stem in sampled:
            continue
        states = B.states_of(stem)
        if not states:
            continue
        yield stem, stem, states, B.security_model(stem, states)


def rows_for(model, state):
    return [r for r in model["statePermissions"] if r["stateName"] == state]


def subject(row):
    if row["subjectType"] == "*":
        return "*"
    return f"{row['subjectType']}:{row['subjectName']}"


# ─────────────────────────────────────────────────────────────────────────────
# Who the rows name
# ─────────────────────────────────────────────────────────────────────────────

def test_every_subject_is_a_group_the_package_ships():
    """A policy row naming a group that does not exist matches nobody, silently.

    This is the shape of the defect that cost this exercise the most: `accountType` was
    "User", which is not one of the four the Engine matches, so thirteen accounts fell
    through every row to the wildcard and nine agents reported that they could not do
    their jobs. A misspelt GROUP name fails exactly the same way and just as quietly.
    """
    for label, stem, _states, model in models():
        for row in model["statePermissions"]:
            if row["subjectType"] == "group":
                assert row["subjectName"] in GROUP_NAMES, \
                    f"{label}/{stem}: policy row names group {row['subjectName']!r}, " \
                    f"which the package does not ship"
            elif row["subjectType"] == "role":
                assert row["subjectName"] in {"Admin", "System Administrator",
                                              "Member", "Guest"}, \
                    f"{label}/{stem}: role subject {row['subjectName']!r} is not one of " \
                    "the four account types the Engine matches"


def test_every_transition_rule_names_real_subjects():
    """An allowedRoles list with a bad name is an allowlist that allows nobody."""
    for label, stem, _states, model in models():
        for rule in model["transitionRules"]:
            assert rule["allowedRoles"].strip(), \
                f"{label}/{stem}: {rule['fromState']} -> {rule['toState']} allows nobody"
            for who in rule["allowedRoles"].split(","):
                who = who.strip()
                kind, _, name = who.partition(":")
                if kind == "group":
                    assert name in GROUP_NAMES, \
                        f"{label}/{stem}: rule {rule['fromState']} -> " \
                        f"{rule['toState']} names unknown group {name!r}"
                else:
                    assert kind == "role" and name == "Admin", f"unexpected subject {who!r}"


def test_every_group_can_reach_at_least_one_project():
    """A group in no project is 403 on every object filed in one, whatever its rows say.

    Project membership is a hard filter applied before the policy row - the security
    inspector says so in as many words: "refused whatever the policy row says". Customer
    Support and Systems Engineering each reported a flat 403 on data their role exists to
    read, and in both cases every policy row already granted it (NI-00000763,
    NI-00000764). Nothing in the security model can show that, which is why it belongs
    here.
    """
    import lightjet_projects  # noqa: PLC0415 - seed package, not needed by the model
    covered = {g for p in lightjet_projects.PROJECTS for g in p["memberGroups"]}
    missing = sorted(GROUP_NAMES - covered)
    assert not missing, \
        f"these groups are in no project, so they are 403 on anything filed: {missing}"


# ─────────────────────────────────────────────────────────────────────────────
# What the rows grant
# ─────────────────────────────────────────────────────────────────────────────

def test_create_is_granted_to_somebody_on_every_type():
    """A policy that grants create to nobody now means nobody but an administrator may
    create one, so a type whose rows are all false is a type the demo cannot author.

    This invariant is the inverse of the one it replaces. `canCreate` used to be false on
    every row of every type on purpose, because the Engine read "no row grants create" as
    "create is unconfigured, so anyone may" - so the safe-looking configuration was the one
    that granted creation to the entire site, and a project manager in no engineering group
    could author type design data (NI-00000742, NI-00000699, NI-00000643, NI-00000691).
    With a configured policy now answering the question, all-false denies everyone."""
    for label, stem, _states, model in models():
        granted = {subject(row) for row in model["statePermissions"] if row["canCreate"]}
        assert granted, f"{label}/{stem}: no row grants create, so nobody may author one"


def test_create_is_never_granted_to_the_wildcard():
    """Create by account type alone was the finding: a supply-chain user could create type
    design data because every account type matched the wildcard row (NI-00000691). Create
    belongs to the groups that author the type, so the wildcard must never carry it."""
    for label, stem, _states, model in models():
        for row in model["statePermissions"]:
            if row["subjectType"] == "*":
                assert row["canCreate"] is False, \
                    f"{label}/{stem}: the wildcard grants create in {row['stateName']}"


def test_create_is_granted_only_to_groups_that_may_edit_the_type():
    """Whoever may create one must be able to work on it afterwards, or the create leaves
    an object its author cannot touch - and an author who cannot edit is how
    "a user can create an object and then cannot delete it" happens (NI-00000683).

    An administrator is exempt: the role carries edit Any in every state anyway."""
    for label, stem, _states, model in models():
        editors = {subject(row) for row in model["statePermissions"]
                   if row["editScope"] in ("Own", "Any")}
        for row in model["statePermissions"]:
            if not row["canCreate"] or row["subjectType"] == "role":
                continue
            assert subject(row) in editors, \
                f"{label}/{stem}: {subject(row)} may create one but may never edit it"


def test_create_is_consistent_across_the_states_of_a_type():
    """Create is asked before any object exists, so no state can qualify it. A subject
    granted create in one state and refused it in another is a policy that cannot be read:
    the Engine takes the first grant it finds, so the quiet row is the one that is wrong."""
    for label, stem, _states, model in models():
        answers: dict[str, set[bool]] = {}
        for row in model["statePermissions"]:
            answers.setdefault(subject(row), set()).add(bool(row["canCreate"]))
        for who, values in answers.items():
            assert len(values) == 1, \
                f"{label}/{stem}: {who} both may and may not create, depending on the state"


def test_a_locked_state_grants_edit_to_nobody_but_admin_and_a_finding():
    """A released or accepted revision being editable is the defect that makes a release
    mean nothing - reported from both directions, by the designer who could rewrite
    approved content in place (NI-00000484) and by the DER who found she could alter the
    evidence she was judging (NI-00000492)."""
    for label, stem, _states, model in models():
        for row in model["statePermissions"]:
            if row["stateName"] not in B.RELEASE_LOCKED:
                continue
            if subject(row) == "role:Admin" or row["stateName"] == B.FINDING_STATE:
                continue
            assert row["editScope"] == "None", \
                f"{label}/{stem}: {subject(row)} may edit in locked state " \
                f"{row['stateName']}"


def test_nobody_edits_data_that_is_awaiting_a_decision():
    """A systems engineer found he could edit a certification test report while it sat in
    the airworthiness gate (NI-00000506). The honest answer is not that he is the wrong
    group - it is that nobody edits data awaiting a signature, because the signatory
    decides on the data they were shown. The way to change it is to pull it back out of
    the gate, which the transition rules allow and which leaves a trace."""
    for label, stem, states, model in models():
        for state in states:
            if state not in B.AWAITING_DECISION:
                continue
            for row in rows_for(model, state):
                if subject(row) == "role:Admin":
                    continue
                assert row["editScope"] == "None", \
                    f"{label}/{stem}: {subject(row)} may edit in {state}, which is " \
                    "awaiting somebody else's decision"
            # ...and it must still be possible to take it back out, or the lock is a trap.
            out = [r for r in model["transitionRules"] if r["fromState"] == state]
            assert out, f"{label}/{stem}: {state} locks editing with no way back out"


def test_a_record_kept_for_life_is_deletable_only_by_an_administrator():
    """Customer Support held delete-Any on a mandatory service bulletin with life-of-type
    retention: the role that issues a bulletin could erase it (NI-00000510, NI-00000675).
    Retention is a records requirement, so the withdrawal states are the route, not a
    delete."""
    for stem in sorted(B.RETAINED_FOR_LIFE):
        states = B.states_of(stem)
        if states is None:
            continue
        model = B.security_model(stem, states)
        for row in model["statePermissions"]:
            if subject(row) == "role:Admin":
                continue
            assert row["deleteScope"] == "None", \
                f"{stem}: {subject(row)} may delete in {row['stateName']}, but this type " \
                "is retained for the life of the type"


def test_the_delegated_authority_can_read_its_scope_and_write_only_a_finding():
    """The DER group had no row of any kind, so its only rights came from the site's DER
    also sitting in the airworthiness group - exactly the conflation a separate group
    exists to prevent. She had 403 on edit, 404 on every transition and 409 on the action:
    no writable surface at all on the evidence she is there to judge (NI-00000760)."""
    for stem in sorted(B.AUTHORITY_SCOPE):
        states = B.states_of(stem)
        if states is None:
            continue
        model = B.security_model(stem, states)
        for state in states:
            rows = [r for r in rows_for(model, state)
                    if r["subjectName"] == B.AUTHORITY_GROUP]
            assert len(rows) == 1, f"{stem}/{state}: the authority has {len(rows)} rows"
            row = rows[0]
            assert row["canRead"] and row["canDownload"], \
                f"{stem}/{state}: the authority cannot read the evidence it judges"
            # On the one type the authority RAISES, it is the author and edits in a working
            # state like any owning group. On everything else in its delegation it approves
            # data rather than editing it, and writes only where a finding re-opens the item.
            if stem in B.AUTHORITY_RAISES:
                expected = "None" if state in B.RELEASE_LOCKED else "Any"
            else:
                expected = "Any" if state == B.FINDING_STATE else "None"
            assert row["editScope"] == expected, \
                f"{stem}/{state}: the authority's edit is {row['editScope']}, " \
                f"expected {expected}"


def test_a_contributing_group_may_work_but_may_not_approve():
    """A contributing group exists because the named assignee of a compliance item could
    not write a word on it (NI-00000765). It does the work; it does not decide when the
    work is done, and it never deletes."""
    for stem, groups in B.CONTRIBUTING_GROUPS.items():
        states = B.states_of(stem)
        if states is None:
            continue
        model = B.security_model(stem, states)
        for group in groups:
            if group == B.OWNING_GROUP.get(stem):
                continue
            for state in states:
                rows = [r for r in rows_for(model, state) if r["subjectName"] == group]
                assert rows, f"{stem}/{state}: no row for contributing group {group}"
                row = rows[0]
                assert row["canTransition"] is False, \
                    f"{stem}/{state}: contributing group {group} may transition"
                assert row["deleteScope"] == "None", \
                    f"{stem}/{state}: contributing group {group} may delete"
                # A working state only. A state that is locked - approved, or awaiting
                # somebody else's decision - is locked for a contributing group too.
                if state not in B.RELEASE_LOCKED and state not in B.AWAITING_DECISION:
                    assert row["editScope"] == "Any", \
                        f"{stem}/{state}: contributing group {group} cannot do its work"


def test_canTransition_is_not_advertised_where_the_rules_refuse_it():
    """GET /permissions reported transition rights the transitionRules allowlist then
    refused, which is how a systems engineer came to report that he could transition a
    test report inside the airworthiness gate (NI-00000506). Nothing was actually released
    without a signatory - but a flag that says yes where the rules say no is a worse answer
    than a plain no."""
    for label, stem, states, model in models():
        routes = {}
        for rule in model["transitionRules"]:
            routes.setdefault(rule["fromState"], set()).update(
                w.strip() for w in rule["allowedRoles"].split(","))
        for row in model["statePermissions"]:
            if not row["canTransition"] or subject(row) == "*":
                continue
            allowed = routes.get(row["stateName"], set())
            assert subject(row) in allowed, \
                f"{label}/{stem}: {subject(row)} is told it may transition from " \
                f"{row['stateName']}, but no rule out of {row['stateName']} allows it"


# ─────────────────────────────────────────────────────────────────────────────
# Where a revision may go
# ─────────────────────────────────────────────────────────────────────────────

def test_every_type_declares_at_least_one_transition_rule():
    """`transitionRules` is an allowlist and an empty one is not a safe default: the Engine
    enforces transitions only when a type declares a rule, so a type with none has no
    transition control whatever its canTransition flags say. That is how type design data
    could be set straight to Released (NI-00000509), and it is the same shape as the
    change gates shipping with every approver list empty (NI-00000497)."""
    for label, stem, _states, model in models():
        assert model["transitionRules"], f"{label}/{stem}: no transition rules at all"


def test_an_approval_is_entered_only_from_the_state_before_it_and_only_by_a_signatory():
    """"Approval from any working state" made the review stages decoration: the built graph
    carried "In Work -> Released", so type design data could be signed without passing
    design review, stress review or the airworthiness gate (NI-00000494, NI-00000509), and
    "Planned -> Accepted", so a compliance demonstration could be accepted with no agreed
    method and no evidence."""
    for label, stem, states, model in models():
        for rule in model["transitionRules"]:
            if rule["toState"] not in B.SIGNATORY_STATES:
                continue
            assert f"group:{B.SIGNATORY_GROUP}" in rule["allowedRoles"], \
                f"{label}/{stem}: {rule['toState']} entered without a signatory"
            # The owning group must not be able to approve its own work - UNLESS it IS the
            # signatory group, which is the case for the types airworthiness both authors
            # and signs: the project certification plan, the airworthiness release, a
            # published limitation. That is not self-approval being waved through, it is
            # what a Part 21 Subpart J design organisation is: the signatories are a pool
            # of named individuals holding a privilege, and the group is that pool.
            #
            # What the model still cannot express is that the approving PERSON must differ
            # from the authoring person. Policy resolves per group, not per individual, so
            # one member of airworthiness can sign their own plan. Two reporters found that
            # from different angles (NI-00000488, NI-00000750) and it is an open product
            # question - author-versus-approver - not something this model can close.
            owner = B.OWNING_GROUP.get(stem)
            if owner and owner != B.SIGNATORY_GROUP:
                assert f"group:{owner}" not in rule["allowedRoles"], \
                    f"{label}/{stem}: the owning group may enter {rule['toState']} itself"
            gate = states[states.index(rule["toState"]) - 1]
            assert rule["fromState"] == gate, \
                f"{label}/{stem}: {rule['toState']} may be entered from " \
                f"{rule['fromState']}, skipping {gate}"


def test_a_settled_state_is_never_walked_back_into_the_workflow():
    """RELEASE_LOCKED and the transition sets were two answers to one question, and where
    they disagreed a state that forbade editing still had working-state routes out of it.
    The built graph carried "Cancelled -> Issued", which puts a cancelled service bulletin
    back into service."""
    for label, stem, states, model in models():
        for rule in model["transitionRules"]:
            if rule["fromState"] not in B.SETTLED_STATES:
                continue
            target = rule["toState"]
            ok = (target in B.SETTLED_STATES or target == B.FINDING_STATE)
            assert ok, \
                f"{label}/{stem}: {rule['fromState']} -> {target} walks a settled " \
                "record back into the workflow"


def test_retirement_only_moves_forward():
    """"Obsolete -> Superseded" would bring a part withdrawn from service back as merely
    replaced."""
    for label, stem, states, model in models():
        for rule in model["transitionRules"]:
            if rule["fromState"] in B.POST_APPROVAL_STATES \
                    and rule["toState"] in B.POST_APPROVAL_STATES:
                assert states.index(rule["toState"]) > states.index(rule["fromState"]), \
                    f"{label}/{stem}: {rule['fromState']} -> {rule['toState']} " \
                    "un-retires a revision"


def test_every_state_is_reachable_and_every_live_state_has_a_way_out():
    """A state nothing reaches is a lane of the board that can never be filled; a live
    state nothing leaves is a dead end that needs an administrator. ECR's 'Approved' was
    found to be exactly that (NI-00000519)."""
    for label, stem, states, model in models():
        reached = {r["toState"] for r in model["transitionRules"]} | {states[0]}
        assert set(states) <= reached, \
            f"{label}/{stem}: unreachable states {sorted(set(states) - reached)}"
        leaves = {r["fromState"] for r in model["transitionRules"]}
        stuck = sorted(s for s in states if s not in leaves and s not in B.SETTLED_STATES)
        assert not stuck, f"{label}/{stem}: live states with no way out: {stuck}"


# ─────────────────────────────────────────────────────────────────────────────
# The routes a record travels
# ─────────────────────────────────────────────────────────────────────────────

def test_every_declared_action_names_a_workflow_the_package_ships():
    """An action pointing at a workflow that is not in the package answers 422
    no_workflow_bound, and the object is then frozen: a manufacturing engineer could
    neither submit a process specification for approval nor revise it, and every declared
    action failed the same way (NI-00000567, NI-00000689). The type looked perfectly
    configured - it HAD actions - which is why nobody noticed until somebody tried to use
    one."""
    shipped = {w["id"] for w in A.WORKFLOWS}
    for definition in A_TYPES.ALL_TYPES:
        for act in definition.get("actions") or []:
            assert act["workflowDefinitionId"] in shipped, \
                f"{definition['typeName']}: action {act['name']!r} names workflow " \
                f"{act['workflowDefinitionId']} which the package does not ship"


def test_every_type_that_has_a_settled_state_has_a_way_to_reach_it():
    """A lifecycle whose approved state can only be entered by a signatory, on a type with
    no action to start a route, is a record that can never be approved by anybody except
    through a direct status change - which is the bare status flip NI-00000567 objected to.
    """
    actioned = {d["typeName"] for d in A_TYPES.ALL_TYPES if d.get("actions")}
    for label, stem, states, _model in models():
        if not (B.SIGNATORY_STATES & set(states)):
            continue
        name = B.BASE + stem
        assert name in actioned, \
            f"{label}/{stem}: has an approved state but no action to start a route to it, " \
            "so the only way in is a direct status change"


def test_every_approval_gate_states_what_it_is_asking():
    """A task arrived as a title, a null instruction and two buttons, so an approver was
    asked to approve something without being told what approving it would do - and on a
    release gate what it does is let aeroplanes be built to the data (NI-00000586). The
    Engine puts a node's Parameters["instruction"] on every task it creates and into the
    notification body, so the question only has to be written down."""
    for workflow in A.WORKFLOWS:
        for node in workflow["definition"]["Nodes"]:
            if node["NodeType"] != "Approver":
                continue
            instruction = (node.get("Parameters") or {}).get("instruction")
            assert instruction and len(instruction) > 40, \
                f"{workflow['name']}: gate {node['Title']!r} does not say what it is asking"


def test_no_approval_gate_is_addressed_to_nobody():
    """An approver node naming no user, group or role creates no task at all, so the
    workflow waits for ever on work nobody was given. The out-of-the-box change gates ship
    addressed to a single administrator account for exactly this reason - a payload cannot
    know a site's group names - but a SITE's own workflows have no such excuse
    (NI-00000724, NI-00000720)."""
    for workflow in A.WORKFLOWS:
        for node in workflow["definition"]["Nodes"]:
            if node["NodeType"] != "Approver":
                continue
            named = (node.get("ApproverUserIds") or []) + (node.get("ApproverGroupIds") or []) \
                + (node.get("ApproverRoleIds") or [])
            assert named, \
                f"{workflow['name']}: gate {node['Title']!r} is addressed to nobody"


def test_a_certification_credit_pins_the_revision_it_was_granted_against():
    """`revisionRule` is declared on the out-of-the-box ReferenceLinkBase and defaults to
    'latest-released', so every reference followed whichever revision happened to be released
    at the time of reading - including on Accepted type design data.

    That is backwards for a compliance credit. The credit was granted against the revision
    that was examined, and if that revision is superseded the credit has to go SUSPECT rather
    than silently transfer to work nobody has assessed: a test report evidencing compliance of
    revision A does not evidence revision B (NI-00000604, NI-00000603).

    Overriding an inherited attribute replaces the ancestor's definition outright, so this
    also checks the list of values survived the override - losing it would make the field free
    text again, which is the defect the list exists to prevent."""
    for definition in A_TYPES.CONCRETE_REFERENCE_TYPES:
        stem = definition["typeName"].replace(B.BASE, "", 1)
        if stem not in CREDIT_BEARING_KINDS:
            continue
        rule = [x for x in definition["attributes"] if x["name"] == "revisionRule"]
        assert rule, f"{stem}: carries a certification credit but does not pin a revision"
        assert rule[0].get("defaultValue") == "pinned",             f"{stem}: defaults to {rule[0].get('defaultValue')!r}, not 'pinned'"
        assert "pinned" in (rule[0].get("lov") or []),             f"{stem}: the override dropped the list of values, so the field is free text again"


def test_every_reference_kind_can_record_whether_it_was_reviewed():
    """A link is suspect when one end has moved on since it was reviewed. Nothing computes
    that yet, but it cannot even be RECORDED without somewhere to put it, and a review
    identity is what makes "we looked at this" different from "nobody has looked"
    (NI-00000485, NI-00000525, NI-00000712)."""
    declared = {x["name"] for x in A_TYPES.REFERENCE_KIND_ATTRS}
    for needed in ("reviewStatus", "reviewedBy", "reviewedOn", "reviewedAgainstRevision"):
        assert needed in declared, f"reference kinds cannot record {needed}"


def test_a_submission_can_be_returned_with_a_finding_not_only_accepted():
    """From a state awaiting a decision there were exactly two routes: forward to the
    approved state, and back a step for rework. So the one thing a certification reviewer
    most needs to do at the point of acceptance - object, on the record - had nowhere to
    land. "Accept" was available and "return with a finding" was not, and sending the item
    back to Evidence in Work says "do more work" rather than "the authority has an
    objection of record" (NI-00000557).

    The same act, and the same reasoning, as the finding against an already accepted
    demonstration: objecting BEFORE signing should not be harder than objecting after."""
    for label, stem, states, model in models():
        gates = B.AWAITING_DECISION & set(states)
        if not gates or B.FINDING_STATE not in states:
            continue
        rules = {(r["fromState"], r["toState"]): r["allowedRoles"]
                 for r in B.transition_rules(states, B.OWNING_GROUP.get(stem))}
        for gate in gates:
            who = rules.get((gate, B.FINDING_STATE))
            assert who,                 f"{label}/{stem}: {gate} can be accepted but not returned with a finding"
            assert B.AUTHORITY_GROUP in who,                 f"{label}/{stem}: the authority cannot raise a finding from {gate}"


def _resolved_live_states(stem):
    """
    The states a type really offers once the Engine has walked its ancestors.

    Mirrors PlmTypeRegistry.Resolve: walk the chain root-first, merge by name, and let a
    "disabled" entry remove a state an ancestor declared. Any base this package does not
    define is an out-of-the-box one, which bottoms out at PLMCoreAbstractModel's four.
    """
    by_name = {d["typeName"]: d for d in A_TYPES.ALL_TYPES}
    chain, seen, cur = [], set(), A.t(stem)
    while cur and cur not in seen:
        seen.add(cur)
        chain.append(cur)
        cur = (by_name.get(cur) or {}).get("baseTypeName")

    live = {}
    for name in reversed(chain):
        if name not in by_name:                       # an out-of-the-box ancestor
            for s in A.OOTB_STATES:
                live[s] = True
            continue
        for row in (by_name[name].get("lifecycleStates") or []):
            if not row.get("name"):
                continue
            if row.get("disabled"):
                live.pop(row["name"], None)
            else:
                live[row["name"]] = True
    return set(live)


def test_no_type_offers_a_state_inherited_from_a_base_it_does_not_use():
    """
    A type offers exactly the ladder it declares - nothing its ancestors happen to declare.

    This is the invariant that was missing, and it cost NI-00000802. Lifecycle states are
    inherited down the type chain but security models deliberately are not, and
    security_model() is built from states_of(), i.e. from the ladder the type MEANS to have.
    So every state that leaked down from an intermediate base arrived with no policy rows -
    and a state with no rows denies everything to everybody, administrators included, while
    looking exactly like a state somebody locked down on purpose.

    On NX-200 that was 122 type-state gaps across 20 types: every quality, certificate and
    publication record offered "In Design Review", "In Stress Review" and an "Airworthiness
    Sign-off" nobody could use, and a compliance report offered "In Work" on top of its seven
    board lanes - which is how two revisions of LSS-CERT-COMP-006 came to sit in a lane with
    no transition out of it.

    The other state tests all read states_of(), the INTENDED ladder, so none of them could
    see this. This one resolves the chain the way the Engine does.
    """
    for label, stem, states, _model in models():
        offered = _resolved_live_states(stem)
        extra = offered - set(states)
        assert not extra, (
            f"{label}/{stem} offers {sorted(extra)}, which it inherits from a base and has "
            f"no policy rows for; its own ladder is {states}")


def main() -> int:
    tests = [(name, obj) for name, obj in sorted(globals().items())
             if name.startswith("test_") and callable(obj)]
    failed = []
    for name, test in tests:
        try:
            test()
            print(f"  PASS  {name}")
        except AssertionError as exc:
            failed.append((name, str(exc)))
            print(f"  FAIL  {name}\n          {exc}")
    print(f"\n{len(tests) - len(failed)}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
