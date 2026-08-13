#!/usr/bin/env python3
"""One-shot runner for the whole awesome-ai-runbooks platform toolchain.

Runs validation, scoring, health, search/graph, metrics, security, content
audit, and badge generation in dependency order, then prints a summary. This is
what CI and maintainers run locally to (re)generate every artifact.

Usage:
    python tools/run_platform.py            # run all, generate artifacts
    python tools/run_platform.py --check    # fail on any hard error (CI mode)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO_ROOT = TOOLS.parent

# (label, argv, required)
STEPS = [
    ("Metadata drift check", [sys.executable, "tools/metadata_enrich.py", "--check"], True),
    ("Runbook validation + score", [sys.executable, "tools/quality/runbook_validator.py"], True),
    ("Quality dimensions", [sys.executable, "tools/quality/runbook_quality_engine.py"], False),
    ("Maturity model", [sys.executable, "tools/maturity_engine.py"], False),
    ("Repository health", [sys.executable, "tools/health/repository_health.py", "--min", "80"], True),
    ("Search index + taxonomy", [sys.executable, "tools/search/build_index.py"], False),
    ("Knowledge graph", [sys.executable, "tools/recommendation_engine.py", "--graph"], False),
    ("Repository metrics", [sys.executable, "metrics/repository_metrics.py"], False),
    ("Secret scan", [sys.executable, "tools/security/secret_scanner.py"], True),
    ("Dependency scan", [sys.executable, "tools/security/dependency_scanner.py"], True),
    ("Security score", [sys.executable, "tools/security/security_score.py"], False),
    ("Content audit", [sys.executable, "tools/content_audit.py"], True),
    ("Category READMEs", [sys.executable, "tools/runbook_generator/runbook_scaffolder.py", "--all-readmes"], False),
    ("Badges", [sys.executable, "tools/badges.py"], False),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="CI mode: nonzero exit on any required failure")
    args = parser.parse_args()

    results = []
    for label, argv, required in STEPS:
        print(f"\n{'=' * 78}\n{label}\n{'=' * 78}")
        rc = subprocess.run(argv, cwd=REPO_ROOT).returncode
        results.append((label, rc, required))

    print(f"\n{'=' * 78}\nPLATFORM SUMMARY\n{'=' * 78}")
    hard_fail = False
    for label, rc, required in results:
        status = "PASS" if rc == 0 else ("FAIL" if required else "WARN")
        print(f"  {status:<5} {label}")
        if rc != 0 and required:
            hard_fail = True

    if hard_fail:
        print("\nOne or more required steps failed.")
        return 1 if args.check else 0
    print("\nAll platform steps completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
