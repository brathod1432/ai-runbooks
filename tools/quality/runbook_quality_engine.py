#!/usr/bin/env python3
"""Runbook quality engine (Phase 13).

Computes five orthogonal quality dimensions for each runbook and the repository:

  * Completeness Score   — structure, sections, depth, diagrams, examples
  * Agent Readiness Score — unambiguous execution contract for autonomous agents
  * Validation Score      — validation steps, expected outputs, rollback, metrics
  * Enterprise Score      — governance metadata: reviewers, compliance, HITL, risk
  * Automation Score      — machine-consumability: schema-valid metadata, tags,
                            required_tools, decision tree, structured signals

Writes ``quality/quality-dimensions.json`` and prints a per-runbook table.

Usage:
    python tools/quality/runbook_quality_engine.py [--json quality/quality-dimensions.json]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runbook_lib import (  # type: ignore  # noqa: E402
    REPO_ROOT,
    REQUIRED_METADATA_KEYS,
    REQUIRED_SECTIONS,
    Runbook,
    bold,
    green,
    load_runbooks,
    write_json,
    yellow,
)

MIN_WORDS = 1000


def _clamp(x: float, lo: float = 0, hi: float = 100) -> float:
    return max(lo, min(hi, x))


def completeness(rb: Runbook) -> float:
    present = set(rb.sections)
    section_ratio = sum(1 for s in REQUIRED_SECTIONS if s in present) / len(REQUIRED_SECTIONS)
    depth = min(1.0, rb.word_count() / (MIN_WORDS * 1.8))
    diagrams = min(1.0, rb.mermaid_count() / 2)
    example = 1.0 if rb.has_example() else 0.0
    return round(100 * (0.45 * section_ratio + 0.30 * depth + 0.15 * diagrams + 0.10 * example), 1)


def agent_readiness(rb: Runbook) -> float:
    present = set(rb.sections)
    signals = {
        "Objective": 0.12,
        "Success Criteria": 0.12,
        "Execution Instructions": 0.14,
        "Decision Tree": 0.14,
        "Investigation Workflow": 0.10,
        "Planning Instructions": 0.10,
        "Inputs Required": 0.08,
        "Required Access": 0.08,
        "Agent Persona": 0.06,
    }
    score = sum(w for s, w in signals.items() if s in present)
    # Bonus for explicit HITL + supported agents breadth.
    if rb.meta.get("human_in_the_loop"):
        score += 0.03
    if len(rb.supported_agents) >= 5:
        score += 0.03
    return round(100 * _clamp(score, 0, 1), 1)


def validation(rb: Runbook) -> float:
    present = set(rb.sections)
    weights = {
        "Validation Steps": 0.30,
        "Expected Outputs": 0.20,
        "Rollback Strategy": 0.20,
        "Metrics": 0.15,
        "Post-Execution Review": 0.15,
    }
    score = sum(w for s, w in weights.items() if s in present)
    # Reward concrete checklists in validation.
    if rb.checklist_count() >= 3:
        score = min(1.0, score + 0.05)
    return round(100 * _clamp(score, 0, 1), 1)


def enterprise(rb: Runbook) -> float:
    m = rb.meta
    checks = [
        bool(m.get("owner")),
        bool(m.get("author")),
        bool(m.get("reviewers")),
        bool(m.get("risk_level")),
        bool(m.get("human_in_the_loop")),
        bool(m.get("compliance_tags") is not None),
        bool(m.get("status")),
        bool(m.get("version")),
        bool(m.get("last_reviewed")),
        "Escalation Process" in set(rb.sections),
    ]
    return round(100 * sum(1 for c in checks if c) / len(checks), 1)


def automation(rb: Runbook) -> float:
    m = rb.meta
    checks = [
        all(m.get(k) not in (None, "", [], {}) for k in REQUIRED_METADATA_KEYS),
        bool(m.get("tags")),
        bool(m.get("required_tools")),
        bool(m.get("domain")),
        bool(m.get("platform")),
        bool(m.get("difficulty")),
        rb.mermaid_count() >= 2,
        "Decision Tree" in set(rb.sections),
        rb.table_count() >= 1,
        rb.code_fence_count() >= 2,
    ]
    return round(100 * sum(1 for c in checks if c) / len(checks), 1)


DIMENSIONS = {
    "completeness": completeness,
    "agent_readiness": agent_readiness,
    "validation": validation,
    "enterprise": enterprise,
    "automation": automation,
}

WEIGHTS = {
    "completeness": 0.30,
    "agent_readiness": 0.25,
    "validation": 0.20,
    "enterprise": 0.15,
    "automation": 0.10,
}


def composite(scores: dict[str, float]) -> float:
    return round(sum(scores[k] * WEIGHTS[k] for k in WEIGHTS), 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default="quality/quality-dimensions.json")
    args = parser.parse_args()

    runbooks = load_runbooks()
    if not runbooks:
        print(yellow("No runbooks found."))
        return 0

    rows = []
    for rb in runbooks:
        scores = {name: fn(rb) for name, fn in DIMENSIONS.items()}
        scores_composite = composite(scores)
        rows.append({
            "id": rb.meta.get("id", rb.slug),
            "path": rb.rel,
            "category": rb.category,
            **scores,
            "composite": scores_composite,
        })

    def col_mean(key: str) -> float:
        return round(sum(r[key] for r in rows) / len(rows), 1)

    means = {k: col_mean(k) for k in list(DIMENSIONS) + ["composite"]}

    header = f"{'RUNBOOK':<46}{'CMP':>6}{'AGT':>6}{'VAL':>6}{'ENT':>6}{'AUT':>6}{'COMP':>7}"
    print(bold(header))
    print("-" * len(header))
    for r in rows:
        name = r["path"].replace("runbooks/", "")
        print(f"{name:<46}{r['completeness']:>6}{r['agent_readiness']:>6}{r['validation']:>6}{r['enterprise']:>6}{r['automation']:>6}{r['composite']:>7}")
    print("-" * len(header))
    print(bold(f"{'MEAN':<46}{means['completeness']:>6}{means['agent_readiness']:>6}{means['validation']:>6}{means['enterprise']:>6}{means['automation']:>6}{means['composite']:>7}"))

    write_json(REPO_ROOT / args.json, {
        "generated_by": "tools/quality/runbook_quality_engine.py",
        "weights": WEIGHTS,
        "means": means,
        "runbooks": rows,
    })
    print(green(f"\nWrote {args.json}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
