#!/usr/bin/env python3
"""Enrich runbook front matter with the extended Phase 2 metadata fields.

Idempotent: only inserts keys that are missing, and never rewrites existing
values. Derives sensible defaults from the existing v1 metadata so the whole
library conforms to ``schemas/runbook.schema.json`` and powers the metadata
catalog, search index, and recommendation engine.

Usage:
    python tools/metadata_enrich.py            # apply
    python tools/metadata_enrich.py --check    # report what would change (exit 1 if any)
"""

from __future__ import annotations

import argparse
import sys

from runbook_lib import (  # type: ignore
    RUNBOOKS_DIR,
    bold,
    difficulty_from_risk,
    green,
    load_runbooks,
    maturity_level_number,
    split_front_matter,
    yellow,
)

PLATFORM_BY_CATEGORY = {
    "reliability": "cross-platform",
    "observability": "observability-stack",
    "databases": "database",
    "messaging": "kafka",
    "security": "cross-platform",
    "kubernetes": "kubernetes",
    "cloud-cost": "multi-cloud",
    "migrations": "language-runtime",
    "architecture": "cross-platform",
    "cicd": "ci-cd",
    "ai-ml": "ai-platform",
}

TOOLS_BY_CATEGORY = {
    "reliability": ["prometheus", "grafana", "pagerduty"],
    "observability": ["opentelemetry", "grafana", "jaeger"],
    "databases": ["psql", "mysql", "redis-cli", "mongosh"],
    "messaging": ["kafka-cli", "prometheus"],
    "security": ["trivy", "tfsec", "checkov"],
    "kubernetes": ["kubectl", "helm"],
    "cloud-cost": ["aws-cli", "az-cli", "gcloud"],
    "migrations": ["git", "package-manager"],
    "architecture": ["git"],
    "cicd": ["github-actions", "argocd"],
    "ai-ml": ["python", "curl"],
}

COMPLIANCE_BY_CATEGORY = {
    "security": ["owasp-top-10", "cis", "nist-ai-rmf"],
    "ai-ml": ["nist-ai-rmf"],
}


def _fmt_list(values: list[str]) -> str:
    return "[" + ", ".join(values) + "]"


def build_additions(rb) -> dict[str, str]:
    """Return the missing key -> serialized-value additions for one runbook."""
    cat = rb.category
    additions: dict[str, str] = {}

    def add(key: str, value: str) -> None:
        # Idempotent: only add a key that is entirely absent. An explicitly
        # empty value (e.g. ``compliance_tags: []``) is a real, intentional
        # value and must not be re-added on subsequent runs.
        if key not in rb.meta or rb.meta.get(key) in (None, ""):
            additions[key] = value

    add("difficulty", difficulty_from_risk(rb.meta.get("risk_level")))
    add("domain", cat)
    add("platform", PLATFORM_BY_CATEGORY.get(cat, "cross-platform"))
    add("agent_type", _fmt_list(rb.supported_agents))
    add("author", str(rb.meta.get("owner", "awesome-ai-runbooks-maintainers")))
    add("reviewers", _fmt_list(["awesome-ai-runbooks-maintainers"]))
    add("required_tools", _fmt_list(TOOLS_BY_CATEGORY.get(cat, ["git"])))
    add("compliance_tags", _fmt_list(COMPLIANCE_BY_CATEGORY.get(cat, [])))
    add("status", "approved")
    add("maturity_level", str(maturity_level_number(rb.meta.get("maturity"), rb.meta.get("status"))))
    return additions


def apply_additions(text: str, additions: dict[str, str]) -> str:
    fm, body = split_front_matter(text)
    if not fm or not additions:
        return text
    new_lines = [f"{k}: {v}" for k, v in additions.items()]
    new_fm = fm.rstrip("\n") + "\n" + "\n".join(new_lines)
    # Reconstruct with the original leading BOM/--- handling.
    prefix = "\ufeff" if text.startswith("\ufeff") else ""
    return f"{prefix}---\n{new_fm}\n---\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Report only; exit 1 if changes needed")
    args = parser.parse_args()

    runbooks = load_runbooks()
    changed = 0
    print(bold(f"Metadata enrichment across {len(runbooks)} runbook(s)\n"))
    for rb in runbooks:
        additions = build_additions(rb)
        if not additions:
            continue
        changed += 1
        keys = ", ".join(additions)
        if args.check:
            print(yellow(f"WOULD UPDATE  {rb.rel}: +{keys}"))
        else:
            new_text = apply_additions(rb.text, additions)
            rb.path.write_text(new_text, encoding="utf-8", newline="\n")
            print(green(f"UPDATED  {rb.rel}: +{keys}"))

    print()
    if changed == 0:
        print(green(bold("All runbooks already carry extended metadata.")))
        return 0
    if args.check:
        print(yellow(bold(f"{changed} runbook(s) need metadata enrichment.")))
        return 1
    print(green(bold(f"Enriched {changed} runbook(s).")))
    return 0


if __name__ == "__main__":
    # Ensure sibling imports work when run from anywhere.
    sys.path.insert(0, str(RUNBOOKS_DIR.parent / "tools"))
    sys.exit(main())
