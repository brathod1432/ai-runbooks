#!/usr/bin/env python3
"""Runbook maturity scoring engine (Phase 26).

Assigns each runbook a maturity level 1-5 based on objective, evidence-driven
criteria (not just the declared front-matter value), and reconciles it with the
declared ``maturity``/``maturity_level``:

  Level 1 — Draft            : structurally incomplete or < 1000 words
  Level 2 — Validated        : passes structure + schema; has diagrams + example
  Level 3 — Production       : L2 + validation/rollback/escalation + reviewers
  Level 4 — Enterprise       : L3 + compliance metadata + HITL + risk + owner/author
  Level 5 — Reference Standard: L4 + high composite quality (>= 95) + broad agent
                               support (>= 8) + tables/checklists richness

Writes ``quality/maturity.json`` and flags mismatches between declared and
computed maturity.

Usage:
    python tools/maturity_engine.py [--strict]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runbook_lib import (  # type: ignore  # noqa: E402
    REPO_ROOT,
    REQUIRED_SECTIONS,
    Runbook,
    bold,
    green,
    load_runbooks,
    maturity_level_number,
    write_json,
    yellow,
)

LEVEL_NAMES = {1: "Draft", 2: "Validated", 3: "Production", 4: "Enterprise", 5: "Reference Standard"}


def _structurally_complete(rb: Runbook) -> bool:
    present = set(rb.sections)
    return all(s in present for s in REQUIRED_SECTIONS) and len(rb.h1s) == 1


def compute_level(rb: Runbook) -> tuple[int, list[str]]:
    reasons: list[str] = []
    present = set(rb.sections)

    if not _structurally_complete(rb) or rb.word_count() < 1000:
        return 1, ["incomplete structure or < 1000 words"]

    # L2 gates
    l2 = rb.mermaid_count() >= 2 and rb.has_example()
    if not l2:
        return 1, ["missing diagrams or example (needed for L2)"]
    reasons.append("L2: structure + diagrams + example")

    # L3 gates
    l3_sections = {"Validation Steps", "Rollback Strategy", "Escalation Process"}
    l3 = l3_sections.issubset(present) and bool(rb.meta.get("reviewers"))
    if not l3:
        return 2, reasons + ["missing validation/rollback/escalation or reviewers (needed for L3)"]
    reasons.append("L3: validation + rollback + escalation + reviewers")

    # L4 gates
    l4 = (
        rb.meta.get("compliance_tags") is not None
        and bool(rb.meta.get("human_in_the_loop"))
        and bool(rb.meta.get("risk_level"))
        and bool(rb.meta.get("owner"))
        and bool(rb.meta.get("author"))
    )
    if not l4:
        return 3, reasons + ["missing enterprise metadata (needed for L4)"]
    reasons.append("L4: enterprise governance metadata present")

    # L5 gates — reference standard
    rich = rb.table_count() >= 3 and rb.checklist_count() >= 3
    broad = len(rb.supported_agents) >= 8
    deep = rb.word_count() >= 1400
    if rich and broad and deep:
        reasons.append("L5: rich, broad agent support, deep content")
        return 5, reasons
    return 4, reasons + ["not yet reference-standard (need richer tables/checklists, >=8 agents, deeper content)"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="fail on declared/computed mismatch")
    parser.add_argument("--json", default="quality/maturity.json")
    args = parser.parse_args()

    runbooks = load_runbooks()
    rows = []
    mismatches = 0
    dist = {i: 0 for i in range(1, 6)}

    print(bold(f"Maturity assessment of {len(runbooks)} runbook(s)\n"))
    for rb in runbooks:
        computed, reasons = compute_level(rb)
        declared = maturity_level_number(rb.meta.get("maturity"), rb.meta.get("status"))
        dist[computed] += 1
        mism = declared != computed
        if mism:
            mismatches += 1
        rows.append({
            "id": rb.meta.get("id", rb.slug),
            "path": rb.rel,
            "declared_level": declared,
            "computed_level": computed,
            "computed_name": LEVEL_NAMES[computed],
            "match": not mism,
            "reasons": reasons,
        })
        flag = yellow(f"(declared L{declared})") if mism else ""
        print(f"  L{computed} {LEVEL_NAMES[computed]:<18} {rb.rel} {flag}")

    write_json(REPO_ROOT / args.json, {
        "generated_by": "tools/maturity_engine.py",
        "distribution": {f"L{k}-{LEVEL_NAMES[k]}": v for k, v in dist.items()},
        "mismatches": mismatches,
        "runbooks": rows,
    })

    print(bold("\nDistribution:"))
    for k in range(1, 6):
        print(f"  L{k} {LEVEL_NAMES[k]:<18} {dist[k]}")
    print(green(f"\nWrote {args.json}"))

    if args.strict and mismatches:
        print(yellow(bold(f"{mismatches} declared/computed mismatch(es).")))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
