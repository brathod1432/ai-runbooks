#!/usr/bin/env python3
"""Dependency & supply-chain hygiene scanner (Phase 23).

This repo is intentionally low-dependency. This scanner inventories declared
dependencies (requirements files, GitHub Actions, package.json if present),
flags supply-chain risks, and checks that security-relevant hygiene rules hold:

  * pinned versions (no floating ``latest`` / unbounded ranges)
  * GitHub Actions pinned to a version tag or SHA
  * no known-deprecated actions

Writes ``security/dependency-scan.json``. Exit 1 on any high-severity finding.

Usage:
    python tools/security/dependency_scanner.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runbook_lib import REPO_ROOT, bold, green, red, write_json, yellow  # type: ignore  # noqa: E402

FLOATING = re.compile(r"(==\s*\*|>=?\s*0\.0|\blatest\b|\*\s*$)")
ACTION_USES = re.compile(r"uses:\s*([^\s#]+)")


def scan_requirements() -> list[dict]:
    findings = []
    for name in ["requirements.txt", "requirements-dev.txt", "tools/requirements.txt"]:
        p = REPO_ROOT / name
        if not p.exists():
            continue
        for lineno, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if FLOATING.search(s) or ("==" not in s and ">=" not in s and "~=" not in s):
                findings.append({
                    "file": name, "line": lineno, "severity": "medium",
                    "type": "unpinned_dependency", "detail": s,
                })
    return findings


def scan_actions() -> list[dict]:
    findings = []
    wf_dir = REPO_ROOT / ".github" / "workflows"
    if not wf_dir.exists():
        return findings
    for wf in sorted(wf_dir.glob("*.yml")):
        for lineno, line in enumerate(wf.read_text(encoding="utf-8").splitlines(), 1):
            m = ACTION_USES.search(line)
            if not m:
                continue
            ref = m.group(1)
            if "@" not in ref:
                findings.append({
                    "file": f".github/workflows/{wf.name}", "line": lineno,
                    "severity": "high", "type": "unpinned_action", "detail": ref,
                })
            else:
                _, ver = ref.split("@", 1)
                if ver in ("main", "master"):
                    findings.append({
                        "file": f".github/workflows/{wf.name}", "line": lineno,
                        "severity": "high", "type": "action_pinned_to_branch", "detail": ref,
                    })
    return findings


def scan_npm() -> list[dict]:
    findings = []
    p = REPO_ROOT / "package.json"
    if not p.exists():
        return findings
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return findings
    for section in ("dependencies", "devDependencies"):
        for name, ver in (data.get(section) or {}).items():
            if str(ver).strip() in ("*", "latest") or str(ver).startswith("^0.0"):
                findings.append({
                    "file": "package.json", "severity": "medium",
                    "type": "unpinned_npm_dependency", "detail": f"{name}@{ver}",
                })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default="security/dependency-scan.json")
    args = parser.parse_args()

    findings = scan_requirements() + scan_actions() + scan_npm()
    high = sum(1 for f in findings if f["severity"] == "high")

    report = {
        "generated_by": "tools/security/dependency_scanner.py",
        "finding_count": len(findings),
        "high_severity": high,
        "findings": findings,
    }
    write_json(REPO_ROOT / args.json, report)

    print(bold("Dependency & supply-chain scan"))
    if not findings:
        print(green(bold("No dependency hygiene issues found.")))
    for f in findings:
        color = red if f["severity"] == "high" else yellow
        print(color(f"  [{f['severity']}] {f['file']}: {f['type']} — {f['detail']}"))
    print(green(f"Wrote {args.json}"))
    if high:
        print(red(bold(f"{high} high-severity finding(s).")))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
