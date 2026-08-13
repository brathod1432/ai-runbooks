#!/usr/bin/env python3
"""Repository health report (Phase 13).

Aggregates repository-wide signals into a single health report:

  * Coverage              — required governance/docs artifacts present
  * Documentation quality — mean completeness of runbooks + doc density
  * Automation coverage   — tools, workflows, tests, schema present
  * Structure quality     — expected directory layout intact
  * Maintainability score — freshness, ownership, review metadata

Writes ``quality/repository-health.json`` and prints a scorecard. Exit code 1
if the overall health grade is below the ``--min`` threshold (default 70).

Usage:
    python tools/health/repository_health.py [--min 70]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runbook_lib import (  # type: ignore  # noqa: E402
    REPO_ROOT,
    REQUIRED_SECTIONS,
    bold,
    green,
    load_runbooks,
    red,
    write_json,
    yellow,
)

REQUIRED_ARTIFACTS = [
    "README.md",
    "LICENSE",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CHANGELOG.md",
    "ENTERPRISE_GUIDE.md",
    "MAINTAINERS.md",
    "REVIEW_GUIDE.md",
    "mkdocs.yml",
    "docs/AI_AGENT_STANDARDS.md",
    "docs/QUALITY_ASSURANCE.md",
    "schemas/runbook.schema.json",
    "templates/runbook-template.md",
    "templates/report-template.md",
]

EXPECTED_DIRS = [
    "runbooks",
    "docs",
    "docs/planning",
    "docs/integrations",
    "templates",
    "prompts",
    "tools",
    "tools/quality",
    "scripts",
    "schemas",
    "governance",
    "security",
    "tests",
    "agent-framework",
    ".github/workflows",
]

AUTOMATION_SIGNALS = [
    "tools/runbook_lib.py",
    "tools/quality/runbook_validator.py",
    "tools/quality/runbook_quality_engine.py",
    "tools/search/build_index.py",
    "metrics/repository_metrics.py",
    "tools/security/security_score.py",
    "tools/badges.py",
    "tools/run_platform.py",
    "schemas/runbook.schema.json",
    ".github/workflows/validation.yml",
    ".github/workflows/lint.yml",
    "tests",
]


def pct(n: int, d: int) -> float:
    return round(100 * n / d, 1) if d else 0.0


def exists(rel: str) -> bool:
    return (REPO_ROOT / rel).exists()


def coverage_score() -> tuple[float, list[str]]:
    missing = [a for a in REQUIRED_ARTIFACTS if not exists(a)]
    return pct(len(REQUIRED_ARTIFACTS) - len(missing), len(REQUIRED_ARTIFACTS)), missing


def structure_score() -> tuple[float, list[str]]:
    missing = [d for d in EXPECTED_DIRS if not (REPO_ROOT / d).is_dir()]
    return pct(len(EXPECTED_DIRS) - len(missing), len(EXPECTED_DIRS)), missing


def automation_score() -> tuple[float, list[str]]:
    missing = [a for a in AUTOMATION_SIGNALS if not exists(a)]
    wf_dir = REPO_ROOT / ".github" / "workflows"
    workflows = len(list(wf_dir.glob("*.yml"))) if wf_dir.exists() else 0
    base = pct(len(AUTOMATION_SIGNALS) - len(missing), len(AUTOMATION_SIGNALS))
    # Reward workflow breadth (target >= 8).
    wf_bonus = min(10.0, workflows)
    return round(min(100.0, 0.85 * base + wf_bonus), 1), missing


def documentation_quality(runbooks) -> tuple[float, dict]:
    if not runbooks:
        return 0.0, {}
    sec_cov = []
    for rb in runbooks:
        present = sum(1 for s in REQUIRED_SECTIONS if s in set(rb.sections))
        sec_cov.append(present / len(REQUIRED_SECTIONS))
    mean_sections = sum(sec_cov) / len(sec_cov)
    mean_words = sum(rb.word_count() for rb in runbooks) / len(runbooks)
    depth_factor = min(1.0, mean_words / 1600)
    doc_md = len(list((REPO_ROOT / "docs").rglob("*.md"))) if (REPO_ROOT / "docs").exists() else 0
    score = round(100 * (0.6 * mean_sections + 0.4 * depth_factor), 1)
    return score, {"mean_section_coverage": round(mean_sections * 100, 1), "mean_words": round(mean_words), "doc_pages": doc_md}


def maintainability_score(runbooks) -> tuple[float, dict]:
    if not runbooks:
        return 0.0, {}
    owned = sum(1 for rb in runbooks if rb.meta.get("owner"))
    reviewed = sum(1 for rb in runbooks if rb.meta.get("reviewers"))
    versioned = sum(1 for rb in runbooks if rb.meta.get("version"))
    dated = sum(1 for rb in runbooks if rb.meta.get("last_reviewed"))
    status = sum(1 for rb in runbooks if rb.meta.get("status"))
    n = len(runbooks)
    score = round(100 * (owned + reviewed + versioned + dated + status) / (5 * n), 1)
    return score, {
        "ownership_pct": pct(owned, n),
        "reviewers_pct": pct(reviewed, n),
        "versioned_pct": pct(versioned, n),
        "review_date_pct": pct(dated, n),
        "status_pct": pct(status, n),
    }


def grade(score: float) -> str:
    return "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "F"


def bar(score: float, width: int = 24) -> str:
    filled = int(round(width * score / 100))
    return "[" + "#" * filled + "." * (width - filled) + "]"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min", type=float, default=70.0)
    parser.add_argument("--json", default="quality/repository-health.json")
    args = parser.parse_args()

    runbooks = load_runbooks()

    cov, cov_missing = coverage_score()
    struct, struct_missing = structure_score()
    auto, auto_missing = automation_score()
    docq, docq_detail = documentation_quality(runbooks)
    maint, maint_detail = maintainability_score(runbooks)

    weights = {"coverage": 0.2, "documentation": 0.25, "automation": 0.2, "structure": 0.15, "maintainability": 0.2}
    dims = {"coverage": cov, "documentation": docq, "automation": auto, "structure": struct, "maintainability": maint}
    overall = round(sum(dims[k] * weights[k] for k in weights), 1)

    print(bold("\n=== Repository Health Report ===\n"))
    print(f"Runbooks analyzed: {len(runbooks)}\n")
    labels = {
        "coverage": "Coverage",
        "documentation": "Documentation quality",
        "automation": "Automation coverage",
        "structure": "Structure quality",
        "maintainability": "Maintainability",
    }
    for k in ["coverage", "documentation", "automation", "structure", "maintainability"]:
        print(f"  {labels[k]:<22} {bar(dims[k])} {dims[k]:>5}  ({grade(dims[k])})")
    print()
    print(bold(f"  OVERALL HEALTH        {bar(overall)} {overall:>5}  (grade {grade(overall)})"))

    if cov_missing:
        print(yellow(f"\n  Missing artifacts: {', '.join(cov_missing)}"))
    if struct_missing:
        print(yellow(f"  Missing directories: {', '.join(struct_missing)}"))
    if auto_missing:
        print(yellow(f"  Missing automation: {', '.join(auto_missing)}"))

    write_json(REPO_ROOT / args.json, {
        "generated_by": "tools/health/repository_health.py",
        "overall": overall,
        "grade": grade(overall),
        "weights": weights,
        "dimensions": dims,
        "details": {
            "coverage_missing": cov_missing,
            "structure_missing": struct_missing,
            "automation_missing": auto_missing,
            "documentation": docq_detail,
            "maintainability": maint_detail,
        },
    })
    print(green(f"\nWrote {args.json}"))

    if overall < args.min:
        print(red(bold(f"Health {overall} below minimum {args.min}.")))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
