#!/usr/bin/env python3
"""Validate the repository's top-level structure and required files.

Ensures the canonical directories and governance files exist so the repo stays
navigable and conformant. Exit 0 on success, 1 on any missing required path.
"""

from __future__ import annotations

import sys

from common import REPO_ROOT, bold, green, red, yellow

REQUIRED_DIRS = [
    "docs",
    "docs/planning",
    "templates",
    "runbooks",
    "prompts",
    "scripts",
    "examples",
    "assets",
    ".github",
    ".github/workflows",
]

REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CHANGELOG.md",
    "ENTERPRISE_GUIDE.md",
    "templates/runbook-template.md",
    "templates/report-template.md",
    "docs/AI_AGENT_STANDARDS.md",
    "docs/QUALITY_ASSURANCE.md",
    "docs/planning/VISION.md",
    "docs/planning/PROJECT_SCOPE.md",
    "docs/planning/TARGET_AUDIENCE.md",
    "docs/planning/ROADMAP.md",
    "docs/planning/COMPETITIVE_ANALYSIS.md",
    "prompts/README.md",
]


def main() -> int:
    missing: list[str] = []

    print(bold("Checking required directories...\n"))
    for d in REQUIRED_DIRS:
        p = REPO_ROOT / d
        if p.is_dir():
            print(green(f"PASS  {d}/"))
        else:
            print(red(f"FAIL  {d}/ (missing)"))
            missing.append(d + "/")

    print(bold("\nChecking required files...\n"))
    for f in REQUIRED_FILES:
        p = REPO_ROOT / f
        if p.is_file():
            print(green(f"PASS  {f}"))
        else:
            print(red(f"FAIL  {f} (missing)"))
            missing.append(f)

    # Warn if runbooks directory is empty.
    runbooks = list((REPO_ROOT / "runbooks").rglob("*.md"))
    print(bold(f"\nRunbooks discovered: {len(runbooks)}"))
    if not runbooks:
        print(yellow("WARN  no runbook markdown files found"))

    print()
    if missing:
        print(red(bold(f"Structure validation failed: {len(missing)} missing path(s).")))
        return 1
    print(green(bold("Repository structure is valid.")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
