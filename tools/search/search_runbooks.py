#!/usr/bin/env python3
"""Search the runbook catalog (Phase 16).

Supports keyword search plus tag / difficulty / domain / category / platform /
agent-compatibility filters against ``catalog/runbook-index.json`` (built by
``build_index.py``; rebuilt automatically if missing or stale).

Examples:
    python tools/search/search_runbooks.py kafka lag
    python tools/search/search_runbooks.py --category security --agent devin
    python tools/search/search_runbooks.py --tag rca --difficulty advanced
    python tools/search/search_runbooks.py --platform kubernetes --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runbook_lib import REPO_ROOT, bold, green, yellow  # type: ignore  # noqa: E402

INDEX_PATH = REPO_ROOT / "catalog" / "runbook-index.json"


def load_index() -> dict:
    if not INDEX_PATH.exists():
        # Build it on demand.
        import build_index  # type: ignore

        build_index.main()
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def score_entry(entry: dict, terms: list[str]) -> float:
    if not terms:
        return 1.0
    hay_title = entry["title"].lower()
    hay_tags = " ".join(entry.get("tags", [])).lower()
    hay_kw = " ".join(entry.get("keywords", [])).lower()
    score = 0.0
    for t in terms:
        t = t.lower()
        if t in entry["id"].lower():
            score += 3
        if t in hay_title:
            score += 3
        if re.search(rf"\b{re.escape(t)}\b", hay_tags):
            score += 2
        if re.search(rf"\b{re.escape(t)}\b", hay_kw):
            score += 1
    return score


def matches_filters(entry: dict, args) -> bool:
    if args.category and entry.get("category") != args.category:
        return False
    if args.domain and entry.get("domain") != args.domain:
        return False
    if args.platform and entry.get("platform") != args.platform:
        return False
    if args.difficulty and entry.get("difficulty") != args.difficulty:
        return False
    if args.tag and args.tag not in [t.lower() for t in entry.get("tags", [])]:
        return False
    if args.agent and args.agent not in entry.get("supported_agents", []):
        return False
    if args.risk and entry.get("risk_level") != args.risk:
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Search AI agent runbooks")
    parser.add_argument("terms", nargs="*", help="keywords")
    parser.add_argument("--category")
    parser.add_argument("--domain")
    parser.add_argument("--platform")
    parser.add_argument("--difficulty", choices=["beginner", "intermediate", "advanced", "expert"])
    parser.add_argument("--tag")
    parser.add_argument("--agent")
    parser.add_argument("--risk", choices=["low", "medium", "high", "critical"])
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.tag:
        args.tag = args.tag.lower()

    index = load_index()
    results = []
    for entry in index["runbooks"]:
        if not matches_filters(entry, args):
            continue
        sc = score_entry(entry, args.terms)
        if args.terms and sc <= 0:
            continue
        results.append((sc, entry))

    results.sort(key=lambda x: (-x[0], x[1]["title"]))
    results = results[: args.limit]

    if args.json:
        print(json.dumps([e for _, e in results], indent=2))
        return 0

    if not results:
        print(yellow("No runbooks matched."))
        return 0

    print(bold(f"{len(results)} result(s):\n"))
    for sc, e in results:
        print(green(e["title"]) + f"  ({e['category']}, {e['difficulty']}, risk={e.get('risk_level')})")
        print(f"    {e['path']}")
        if e.get("tags"):
            print(f"    tags: {', '.join(e['tags'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
