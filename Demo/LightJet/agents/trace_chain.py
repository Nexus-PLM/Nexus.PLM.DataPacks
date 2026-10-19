"""Walks the audit chain outward from one object and prints what it can reach.

    python trace_chain.py LSS-PR-00001

This is the question an aviation customer actually asks, and the one the demo has to
answer in clicks rather than prose:

    starting from what was found on an aeroplane, show me every object that changed
    because of it, who approved each change and on what basis, and what the fleet
    was told.

It is written as a tool rather than a script because it is also a measurement: every
relationship it CANNOT follow is a gap in the data model, and the gaps are worth more
than the hops. Anything it reports as "not navigable" is a link that exists only as text
in a field, which means it exists only for a human who already knows to look.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plm_agent import Agent, object_id, tidy                        # noqa: E402

ROUTES = {"ECR": "ecrs", "ECO": "ecos", "ECN": "ecns"}


def walk(me: Agent, start: str, depth: int = 4):
    seen: dict[str, int] = {}
    gaps: list[str] = []
    missing_routes: set[str] = set()
    order: list[tuple[int, str, str, str]] = []

    def visit(pn: str, level: int, why: str, via: str):
        if level > depth or pn in seen:
            return
        seen[pn] = level
        obj = me.object(pn)
        if obj is None:
            gaps.append(f"{pn} referenced by {via} but not readable or not an object")
            return
        order.append((level, pn, why, via))

        latest = me.latest(pn) or {}
        attrs = me.attributes(pn)
        type_name = obj["typeName"].replace("cstLightSpeedSystems", "")

        # 1. Change objects: their affected items, and the chain between them.
        route = ROUTES.get(obj["typeName"])
        if route:
            for row in me.get(f"/api/{route}/{object_id(pn)}/affected-items") or []:
                target = row.get("affectedPartNumber") or row.get("partNumber")
                if target:
                    visit(target, level + 1,
                          f"affected by {pn} ({row.get('changeAction') or 'affected'})",
                          pn)
            if route == "ecrs":
                for row in me.get(f"/api/ecrs/{object_id(pn)}/problem-reports") or []:
                    if row.get("problemPartNumber"):
                        visit(row["problemPartNumber"], level + 1,
                              f"problem behind {pn}", pn)
                for row in me.get(f"/api/ecos") or []:
                    pass
            if route == "ecos":
                for row in me.get(f"/api/ecos/{object_id(pn)}/ecrs") or []:
                    if row.get("ecrPartNumber"):
                        visit(row["ecrPartNumber"], level + 1, f"request behind {pn}", pn)
            if route == "ecns":
                for row in me.get(f"/api/ecns/{object_id(pn)}/ecos") or []:
                    if row.get("ecoPartNumber"):
                        visit(row["ecoPartNumber"], level + 1, f"order behind {pn}", pn)

        # 2. Object references: drawing, specification, material, evidence, certificate.
        revision_id = latest.get("revisionId")
        if revision_id:
            for row in me.get(f"/api/plmobjects/{object_id(pn)}/revisions/"
                              f"{revision_id}/references") or []:
                target = (row.get("target") or {}).get("partNumber")
                if target:
                    visit(target, level + 1,
                          f"{row.get('linkTypeName', 'references')} of {pn}", pn)

        # 3. Where the part is used, and what it is made of.
        #
        # Both directions, because the question this tool exists to answer starts at an
        # AEROPLANE. An aircraft is the top of its own structure, so walking only upwards
        # reaches nothing and the tool would report the product as having no chain when in
        # fact it had not been asked properly.
        for row in me.get(f"/api/plmobjects/{object_id(pn)}/bom-parents") or []:
            target = row.get("parentPartNumber")
            if target:
                visit(target, level + 1, f"assembly containing {pn}", pn)
        for row in me.get(f"/api/plmobjects/{object_id(pn)}/bom-children") or []:
            target = row.get("childPartNumber")
            if target:
                visit(target, level + 1, f"installed on {pn}", pn)

        # 3b. The reverse direction, via the route that actually serves it.
        #
        # This probed /affected-by and /referenced-by, got 404 from both, and concluded the
        # product had no reverse navigation. It was the wrong conclusion from the wrong URL:
        # GET /api/plmobjects/{id}/related answers every direction at once - "changes",
        # "problems", "referenced-by", "bom-parents", "bom-children" and more - and
        # RelatedGraphService was built precisely because "which changes affect this part?"
        # had no reverse lookup. Asking it from aeroplane 002 reaches LSS-PR-00004 and
        # LSS-ECR-00005 in one hop.
        #
        # The lesson is the same one the accountType typo taught: when an instrument reports
        # that the product cannot do something, check the instrument first.
        related = me.get(f"/api/plmobjects/{object_id(pn)}/related")
        if related is None:
            missing_routes.add("the related graph (/related) returned nothing")
        else:
            groups = related.get("groups") if isinstance(related, dict) else related
            if isinstance(groups, dict):
                groups = [{"key": k, "items": v} for k, v in groups.items()]
            for group in groups or []:
                key = group.get("key") or group.get("name") or "related"
                if key in ("projects", "classification", "folders", "contacts", "markups"):
                    continue          # filing, not causation
                for item in group.get("items") or []:
                    target = item.get("partNumber")
                    if target and not item.get("restricted"):
                        visit(target, level + 1, f"{key} of {pn}", pn)

        # 4. Requirement traces.
        traces = me.traces(pn)
        for row in (traces.get("outgoing") or []) + (traces.get("incoming") or []):
            for end in ("target", "source"):
                node = row.get(end) or {}
                if node.get("partNumber") and node["partNumber"] != pn:
                    visit(node["partNumber"], level + 1,
                          f"{row.get('linkType', 'traces')} {pn}", pn)

        # 5. The text-only references - the gaps.
        for field, label in (("sourceProblemId", "source problem"),
                             ("correctiveActionRef", "corrective action"),
                             ("relatedDirectiveRef", "airworthiness directive"),
                             ("evidenceDocumentRefs", "evidence"),
                             ("complianceItemRefs", "compliance item"),
                             ("kitPartNumber", "modification kit")):
            value = attrs.get(field)
            if value and value not in ("None", "none", ""):
                gaps.append(f"{pn}.{field} -> '{tidy(value, 60)}' is TEXT, not a link")

    visit(start, 0, "the starting point", "-")
    gaps.extend(sorted(missing_routes))
    return order, gaps, seen


def main() -> int:
    start = sys.argv[1] if len(sys.argv) > 1 else "LSS-PR-00001"
    me = Agent("admin", password="NexusAdmin2026!", role="PLM Administrator")
    order, gaps, seen = walk(me, start)

    print(f"\nChain from {start} - {len(order)} objects reached by navigation\n")
    for level, pn, why, via in order:
        obj = me.object(pn)
        latest = me.latest(pn) or {}
        kind = obj["typeName"].replace("cstLightSpeedSystems", "")
        print(f"{'  ' * level}{pn:<20} {kind:<22} {str(latest.get('status')):<16} {why}")

    print(f"\n{len(gaps)} relationship(s) that exist only as text:")
    for gap in sorted(set(gaps)):
        print(f"  ! {gap}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
