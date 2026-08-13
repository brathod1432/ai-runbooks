#!/usr/bin/env python3
"""Run all repository checks in sequence and summarize the results.

This is the single command contributors and CI can run:

    python scripts/run_all_checks.py

It runs structure validation, runbook validation, link checking, documentation
coverage, and repository scoring. Markdown lint (Node/markdownlint-cli2) is run
separately in CI and locally via npx. Exit 1 if any required check fails.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from common import bold, green, red

SCRIPTS = Path(__file__).resolve().parent

# (label, argv, required)
CHECKS: list[tuple[str, list[str], bool]] = [
    ("Structure validation", ["validate_structure.py"], True),
    ("Runbook validation", ["validate_runbooks.py"], True),
    ("Link check", ["check_links.py"], True),
    ("Documentation coverage", ["doc_coverage.py"], False),
    ("Repository scoring", ["score_repository.py"], False),
]


def run(label: str, argv: list[str]) -> int:
    print(bold(f"\n{'=' * 78}\n{label}\n{'=' * 78}"))
    proc = subprocess.run([sys.executable, str(SCRIPTS / argv[0]), *argv[1:]])
    return proc.returncode


def main() -> int:
    results: list[tuple[str, int, bool]] = []
    for label, argv, required in CHECKS:
        code = run(label, argv)
        results.append((label, code, required))

    print(bold(f"\n{'=' * 78}\nSUMMARY\n{'=' * 78}"))
    hard_fail = False
    for label, code, required in results:
        status = green("PASS") if code == 0 else (red("FAIL") if required else red("WARN"))
        print(f"  {status}  {label}")
        if code != 0 and required:
            hard_fail = True

    if hard_fail:
        print(red(bold("\nOne or more required checks failed.")))
        return 1
    print(green(bold("\nAll required checks passed.")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
