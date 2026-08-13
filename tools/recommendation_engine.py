#!/usr/bin/env python3
"""Runbook recommendation & dependency engine (Phase 28).

Given a runbook, computes:
  * related      — most similar runbooks (tag/category/domain/keyword overlap)
  * follow_up    — logical next runbooks (curated category flow + heuristics)
  * dependencies — runbooks whose completion is a sensible precondition
  * same_category

Also emits a full dependency/relationship graph to
``catalog/runbook-graph.json`` for the knowledge-graph documentation.

Usage:
    python tools/recommendation_engine.py <runbook-id>     # recommend for one
    python tools/recommendation_engine.py --graph          # build graph json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runbook_lib import (  # type: ignore  # noqa: E402
    REPO_ROOT,
    Runbook,
    bold,
    green,
    load_runbooks,
    red,
    write_json,
)

# Curated "after X, consider Y" follow-up flows by category.
FOLLOW_UP_FLOWS = {
    "reliability": ["observability", "cicd"],
    "observability": ["reliability"],
    "databases": ["reliability", "observability"],
    "messaging": ["observability", "reliability"],
    "security": ["kubernetes", "cicd"],
    "kubernetes": ["security", "cloud-cost", "observability"],
    "cloud-cost": ["kubernetes", "architecture"],
    "migrations": ["cicd", "architecture", "reliability"],
    "architecture": ["migrations", "observability"],
    "cicd": ["reliability", "security"],
    "ai-ml": ["security", "observability"],
}

# Curated dependency hints (id -> ids that should ideally precede it).
DEPENDENCY_HINTS = {
    "incident-postmortem": ["root-cause-analysis"],
    "monolith-to-microservices": ["microservice-decomposition"],
    "event-driven-migration": ["investigate-kafka-lag"],
    "release-readiness-review": ["production-readiness-review"],
    "eks-audit": ["kubernetes-cluster-audit"],
    "aks-audit": ["kubernetes-cluster-audit"],
    "gke-audit": ["kubernetes-cluster-audit"],
    "rag-system-audit": ["vector-database-review"],
    "agent-evaluation-framework": ["prompt-quality-review"],
    "ai-system-security-review": ["api-security-audit"],
}


def similarity(a: Runbook, b: Runbook) -> float:
    ta, tb = set(a.tags), set(b.tags)
    tag_jaccard = len(ta & tb) / len(ta | tb) if (ta | tb) else 0
    ka = set(a.to_index_entry()["keywords"]) if False else set(_kw(a))
    kb = set(_kw(b))
    kw_jaccard = len(ka & kb) / len(ka | kb) if (ka | kb) else 0
    same_cat = 1.0 if a.category == b.category else 0.0
    same_domain = 1.0 if a.meta.get("domain") == b.meta.get("domain") else 0.0
    agent_overlap = len(set(a.supported_agents) & set(b.supported_agents)) / max(1, len(set(a.supported_agents) | set(b.supported_agents)))
    return round(0.4 * tag_jaccard + 0.25 * kw_jaccard + 0.2 * same_cat + 0.1 * same_domain + 0.05 * agent_overlap, 4)


def _kw(rb: Runbook) -> list[str]:
    import re

    text = f"{rb.title} {' '.join(rb.tags)} {rb.section_body('Objective')}"
    return re.findall(r"[a-z][a-z0-9+-]{3,}", text.lower())


def recommend(target: Runbook, all_rb: list[Runbook], k: int = 5) -> dict:
    others = [rb for rb in all_rb if rb.slug != target.slug]
    sims = sorted(((similarity(target, o), o) for o in others), key=lambda x: -x[0])
    related = [{"id": o.slug, "title": o.title, "score": s} for s, o in sims[:k] if s > 0]

    follow_cats = FOLLOW_UP_FLOWS.get(target.category, [])
    follow_up = [
        {"id": o.slug, "title": o.title, "category": o.category}
        for o in others
        if o.category in follow_cats
    ][:k]

    dep_ids = DEPENDENCY_HINTS.get(target.slug, [])
    by_id = {rb.slug: rb for rb in all_rb}
    dependencies = [{"id": d, "title": by_id[d].title} for d in dep_ids if d in by_id]

    same_category = [
        {"id": o.slug, "title": o.title} for o in others if o.category == target.category
    ]

    return {
        "id": target.slug,
        "title": target.title,
        "related": related,
        "follow_up": follow_up,
        "dependencies": dependencies,
        "same_category": same_category,
    }


def build_graph(all_rb: list[Runbook]) -> dict:
    nodes = [{
        "id": rb.slug,
        "title": rb.title,
        "category": rb.category,
        "difficulty": rb.meta.get("difficulty"),
        "maturity_level": rb.maturity_level,
    } for rb in all_rb]

    edges = []
    by_id = {rb.slug: rb for rb in all_rb}
    # Dependency edges.
    for rid, deps in DEPENDENCY_HINTS.items():
        if rid in by_id:
            for d in deps:
                if d in by_id:
                    edges.append({"source": d, "target": rid, "type": "prerequisite"})
    # Similarity edges (top-2 per node, above threshold) as "related".
    for rb in all_rb:
        sims = sorted(((similarity(rb, o), o) for o in all_rb if o.slug != rb.slug), key=lambda x: -x[0])
        for s, o in sims[:2]:
            if s >= 0.25:
                edges.append({"source": rb.slug, "target": o.slug, "type": "related", "weight": s})

    return {
        "generated_by": "tools/recommendation_engine.py",
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("runbook_id", nargs="?", help="runbook id/slug")
    parser.add_argument("--graph", action="store_true", help="build catalog/runbook-graph.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    all_rb = load_runbooks()

    if args.graph:
        graph = build_graph(all_rb)
        write_json(REPO_ROOT / "catalog" / "runbook-graph.json", graph)
        print(green(f"Wrote catalog/runbook-graph.json ({graph['node_count']} nodes, {graph['edge_count']} edges)"))
        return 0

    if not args.runbook_id:
        print(red("Provide a runbook id, or use --graph."))
        return 2

    by_id = {rb.slug: rb for rb in all_rb}
    target = by_id.get(args.runbook_id)
    if not target:
        print(red(f"Unknown runbook id: {args.runbook_id}"))
        return 2

    rec = recommend(target, all_rb)
    if args.json:
        import json

        print(json.dumps(rec, indent=2))
        return 0

    print(bold(f"Recommendations for: {rec['title']}\n"))
    print(bold("Related:"))
    for r in rec["related"]:
        print(f"  - {r['title']} (score {r['score']})")
    print(bold("\nFollow-up:"))
    for r in rec["follow_up"]:
        print(f"  - {r['title']} ({r['category']})")
    print(bold("\nDependencies (do first):"))
    for r in rec["dependencies"] or [{"title": "(none)"}]:
        print(f"  - {r['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
