#!/usr/bin/env python3
"""Security maturity score (Phase 23).

Aggregates the secret scan, dependency scan, security governance docs, and
runbook-level security hygiene into a single Security Maturity Score (0-100)
with a 1-5 maturity level. Writes ``security/security-score.json``.

Security Maturity Levels:
  L1 Ad-hoc      : no scanning, no policy
  L2 Defined     : SECURITY.md + guidelines exist
  L3 Managed     : automated secret + dependency scanning, no high findings
  L4 Measured    : + threat model, second-review process, compliance metadata
  L5 Optimizing  : + CI-enforced, defensive-only verified, zero findings

Usage:
    python tools/security/security_score.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runbook_lib import REPO_ROOT, bold, green, load_runbooks, red, write_json, yellow  # type: ignore  # noqa: E402

HERE = Path(__file__).resolve().parent


def _run(script: str) -> dict:
    """Run a sibling scanner and return its JSON report (best effort)."""
    subprocess.run([sys.executable, str(HERE / script)], capture_output=True, text=True)
    out = {
        "secret_scanner.py": REPO_ROOT / "security" / "secret-scan.json",
        "dependency_scanner.py": REPO_ROOT / "security" / "dependency-scan.json",
    }[script]
    if out.exists():
        return json.loads(out.read_text(encoding="utf-8"))
    return {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default="security/security-score.json")
    args = parser.parse_args()

    secret = _run("secret_scanner.py")
    deps = _run("dependency_scanner.py")

    docs = {
        "SECURITY.md": (REPO_ROOT / "SECURITY.md").exists(),
        "threat_model": (REPO_ROOT / "security" / "threat-model.md").exists(),
        "review_process": (REPO_ROOT / "security" / "security-review-process.md").exists(),
        "guidelines": (REPO_ROOT / "security" / "runbook-security-guidelines.md").exists(),
    }
    ci_security = (REPO_ROOT / ".github" / "workflows" / "security.yml").exists()

    runbooks = load_runbooks()
    sec_runbooks = [rb for rb in runbooks if rb.category == "security"]
    with_compliance = sum(1 for rb in runbooks if rb.meta.get("compliance_tags"))
    high_risk_reviewed = sum(
        1 for rb in runbooks
        if rb.meta.get("risk_level") in ("high", "critical") and rb.meta.get("reviewers")
    )
    high_risk_total = sum(1 for rb in runbooks if rb.meta.get("risk_level") in ("high", "critical"))

    # --- scoring ---------------------------------------------------------
    components = {}
    components["no_high_secrets"] = 20 if secret.get("high_confidence", 0) == 0 else 0
    components["no_high_deps"] = 15 if deps.get("high_severity", 0) == 0 else 0
    components["docs"] = round(20 * sum(docs.values()) / len(docs))
    components["ci_enforced"] = 15 if ci_security else 0
    components["security_runbooks"] = min(10, len(sec_runbooks))
    components["high_risk_review"] = round(10 * (high_risk_reviewed / high_risk_total)) if high_risk_total else 10
    components["compliance_metadata"] = round(10 * with_compliance / len(runbooks)) if runbooks else 0
    score = sum(components.values())

    # --- maturity level --------------------------------------------------
    level = 1
    if docs["SECURITY.md"] and docs["guidelines"]:
        level = 2
    if level == 2 and secret.get("high_confidence", 0) == 0 and deps.get("high_severity", 0) == 0:
        level = 3
    if level == 3 and docs["threat_model"] and docs["review_process"] and with_compliance > 0:
        level = 4
    if level == 4 and ci_security and score >= 95:
        level = 5
    level_names = {1: "Ad-hoc", 2: "Defined", 3: "Managed", 4: "Measured", 5: "Optimizing"}

    report = {
        "generated_by": "tools/security/security_score.py",
        "security_maturity_score": score,
        "security_maturity_level": level,
        "security_maturity_name": level_names[level],
        "components": components,
        "signals": {
            "high_confidence_secrets": secret.get("high_confidence", 0),
            "high_severity_dependencies": deps.get("high_severity", 0),
            "docs_present": docs,
            "ci_security_workflow": ci_security,
            "security_runbooks": len(sec_runbooks),
            "high_risk_runbooks": high_risk_total,
            "high_risk_reviewed": high_risk_reviewed,
            "runbooks_with_compliance_tags": with_compliance,
        },
    }
    write_json(REPO_ROOT / args.json, report)

    print(bold("\n=== Security Maturity ===\n"))
    for k, v in components.items():
        print(f"  {k:<22} {v}")
    color = green if score >= 90 else yellow if score >= 70 else red
    print(bold(color(f"\n  SCORE: {score}/100 — Level {level} ({level_names[level]})")))
    print(green(f"\nWrote {args.json}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
