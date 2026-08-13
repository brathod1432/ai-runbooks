#!/usr/bin/env python3
"""Report documentation coverage across runbooks.

Coverage = the fraction of runbooks in which every required section contains
non-trivial content (more than a heading and a stub). Also breaks down coverage
by category. Informational by default; --min fails the build below a threshold.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict

from common import (
    REQUIRED_SECTIONS,
    RunbookDoc,
    bold,
    green,
    iter_runbooks,
    red,
    yellow,
)

MIN_SECTION_WORDS = 15


def section_bodies(doc: RunbookDoc) -> dict[str, str]:
    """Return a mapping of required section title -> body text.

    Section headings are located by exact match against the canonical section
    names (anchored at the start of a line). This is robust against '##' shell
    comments inside fenced code blocks, which never match a real section name.
    """
    # Find the document offset of each required section heading.
    found: list[tuple[int, str]] = []
    for name in REQUIRED_SECTIONS:
        m = re.search(rf"^##\s+{re.escape(name)}\s*$", doc.text, re.MULTILINE)
        if m:
            found.append((m.start(), name))
    found.sort()

    bodies: dict[str, str] = {}
    for i, (start, name) in enumerate(found):
        heading_end = doc.text.index("\n", start) if "\n" in doc.text[start:] else len(doc.text)
        end = found[i + 1][0] if i + 1 < len(found) else len(doc.text)
        bodies[name] = doc.text[heading_end:end]
    return bodies


def filled_sections(doc: RunbookDoc) -> tuple[int, list[str]]:
    bodies = section_bodies(doc)
    thin: list[str] = []
    filled = 0
    for section in REQUIRED_SECTIONS:
        body = bodies.get(section, "")
        words = len(re.findall(r"\b\w[\w'-]*\b", body))
        # A section is "filled" if it has enough prose, OR its content is a
        # diagram / code block (e.g. the Mermaid in Investigation Workflow and
        # Decision Tree, which is exactly the expected content there).
        has_fence = "```" in body
        if words >= MIN_SECTION_WORDS or has_fence:
            filled += 1
        else:
            thin.append(section)
    return filled, thin


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min", type=float, default=None, help="Fail below this coverage %%")
    args = parser.parse_args()

    docs = iter_runbooks()
    if not docs:
        print(yellow("No runbooks to measure."))
        return 0

    per_category: dict[str, list[float]] = defaultdict(list)
    fully_covered = 0
    total_ratio = 0.0

    print(bold(f"Documentation coverage across {len(docs)} runbook(s)\n"))
    for doc in docs:
        filled, thin = filled_sections(doc)
        ratio = filled / len(REQUIRED_SECTIONS)
        total_ratio += ratio
        category = doc.front_matter.get("category", "uncategorized")
        per_category[category].append(ratio)
        if not thin:
            fully_covered += 1
        else:
            name = doc.rel.replace("runbooks/", "")
            print(yellow(f"THIN  {name}: {len(thin)} thin section(s) -> {', '.join(thin)}"))

    mean = 100 * total_ratio / len(docs)
    print(bold("\nCoverage by category:"))
    for cat in sorted(per_category):
        vals = per_category[cat]
        print(f"  {cat:<16} {100 * sum(vals) / len(vals):5.1f}%  ({len(vals)} runbook(s))")

    print()
    print(bold(f"Fully covered runbooks: {fully_covered}/{len(docs)}"))
    print(bold(f"Mean section coverage:  {mean:.1f}%"))

    if args.min is not None and mean < args.min:
        print(red(bold(f"Coverage {mean:.1f}% is below required minimum {args.min}%.")))
        return 1
    print(green("Documentation coverage check complete."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
