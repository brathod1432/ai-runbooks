#!/usr/bin/env python3
"""Score each runbook and the repository against the QA rubric.

Implements the mechanical portion of docs/QUALITY_ASSURANCE.md section 1
(completeness scoring out of 100). Qualitative dimensions that require human
judgement are awarded their full weight when their structural proxy is present,
and flagged for reviewer attention.

Outputs a per-runbook table and a repository summary. Exit 0 always (scoring is
informational) unless --min is provided and the mean score is below it.
"""

from __future__ import annotations

import argparse
import re
import sys

from common import (
    MIN_MERMAID_DIAGRAMS,
    MIN_WORDS,
    REQUIRED_FRONT_MATTER_KEYS,
    REQUIRED_SECTIONS,
    RunbookDoc,
    bold,
    green,
    iter_runbooks,
    red,
    yellow,
)


def score(doc: RunbookDoc) -> tuple[int, dict[str, int]]:
    breakdown: dict[str, int] = {}

    # Structural conformance (25): sections + front matter + id match.
    present = set(doc.sections)
    section_ratio = sum(1 for s in REQUIRED_SECTIONS if s in present) / len(REQUIRED_SECTIONS)
    fm_ratio = (
        sum(1 for k in REQUIRED_FRONT_MATTER_KEYS if doc.front_matter.get(k))
        / len(REQUIRED_FRONT_MATTER_KEYS)
    )
    breakdown["structure"] = round(25 * (0.6 * section_ratio + 0.4 * fm_ratio))

    # Depth (20): scaled by word count up to 2x the minimum.
    wc = doc.word_count()
    breakdown["depth"] = min(20, round(20 * wc / (MIN_WORDS * 2)))

    # Diagrams (10).
    md = doc.mermaid_count()
    breakdown["diagrams"] = min(10, round(10 * md / MIN_MERMAID_DIAGRAMS))

    # Actionability (10): code fences + checklists + tables.
    code_fences = doc.text.count("```")
    checklists = len(re.findall(r"^\s*-\s+\[[ xX]\]", doc.text, re.MULTILINE))
    tables = len(re.findall(r"^\s*\|.*\|\s*$", doc.text, re.MULTILINE))
    act = 0
    act += 4 if code_fences >= 4 else code_fences
    act += 3 if checklists >= 3 else checklists
    act += 3 if tables >= 3 else min(tables, 3)
    breakdown["actionability"] = min(10, act)

    # Evidence & validation (10): presence of validation + expected outputs content.
    ev = 0
    if "Validation Steps" in present:
        ev += 5
    if "Expected Outputs" in present:
        ev += 5
    breakdown["evidence"] = ev

    # Safety (10): rollback + escalation + risk_level set.
    safety = 0
    if "Rollback Strategy" in present:
        safety += 4
    if "Escalation Process" in present:
        safety += 3
    if doc.front_matter.get("risk_level"):
        safety += 3
    breakdown["safety"] = safety

    # Example execution (5).
    breakdown["example"] = 5 if "Example Execution" in present else 0

    # References (5).
    breakdown["references"] = 5 if "References" in present else 0

    # Clarity & style (5): heuristic — single H1, no placeholder tokens.
    from common import H1_RE

    clarity = 5
    if len(H1_RE.findall(doc.text)) != 1:
        clarity -= 2
    if re.search(r"\bTODO\b|\bFIXME\b", doc.text):
        clarity -= 3
    breakdown["clarity"] = max(0, clarity)

    total = sum(breakdown.values())
    return total, breakdown


def band(total: int) -> str:
    if total >= 90:
        return "Exemplary"
    if total >= 75:
        return "Solid"
    if total >= 60:
        return "Draft"
    return "Rejected"


def color_for(total: int) -> str:
    if total >= 75:
        return green(str(total))
    if total >= 60:
        return yellow(str(total))
    return red(str(total))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min", type=float, default=None, help="Fail if mean score below this")
    args = parser.parse_args()

    docs = iter_runbooks()
    if not docs:
        print(yellow("No runbooks to score."))
        return 0

    print(bold(f"Scoring {len(docs)} runbook(s) (completeness /100)\n"))
    print(f"{'RUNBOOK':<52} {'SCORE':>6}  BAND")
    print("-" * 78)
    total_sum = 0
    for doc in docs:
        total, _ = score(doc)
        total_sum += total
        name = doc.rel.replace("runbooks/", "")
        print(f"{name:<52} {color_for(total):>15}  {band(total)}")

    mean = total_sum / len(docs)
    print("-" * 78)
    print(bold(f"Mean completeness score: {mean:.1f} / 100  ({band(round(mean))})"))

    if args.min is not None and mean < args.min:
        print(red(bold(f"Mean score {mean:.1f} is below required minimum {args.min}.")))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
