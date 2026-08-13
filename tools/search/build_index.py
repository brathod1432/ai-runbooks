#!/usr/bin/env python3
"""Build the runbook search index and metadata catalog (Phase 16 + 15).

Produces:
  * ``catalog/runbook-index.json`` — one entry per runbook with full metadata
    plus a lightweight inverted keyword index for fast client-side search.
  * ``catalog/taxonomy.json``      — categories, tags, domains, platforms,
    agents, difficulties with counts (Taxonomy engine).

Usage:
    python tools/search/build_index.py
"""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runbook_lib import (  # type: ignore  # noqa: E402
    REPO_ROOT,
    bold,
    green,
    load_runbooks,
    write_json,
)

STOPWORDS = set(
    "the a an and or of to in for on with is are be by as at from this that it its into "
    "when where which who whom what how why not no yes if then else can may should must will "
    "your you we our their they them he she his her run runbook agent agents".split()
)


def keywords(rb) -> list[str]:
    text = f"{rb.title} {' '.join(rb.tags)} {rb.category} {rb.meta.get('domain', '')}"
    text += " " + rb.section_body("Objective")
    words = re.findall(r"[a-z][a-z0-9+-]{2,}", text.lower())
    return [w for w in words if w not in STOPWORDS]


def main() -> int:
    runbooks = load_runbooks()
    entries = []
    inverted: dict[str, list[str]] = defaultdict(list)

    tax = {
        "categories": Counter(),
        "tags": Counter(),
        "domains": Counter(),
        "platforms": Counter(),
        "agents": Counter(),
        "difficulties": Counter(),
        "risk_levels": Counter(),
        "maturity": Counter(),
    }

    for rb in runbooks:
        entry = rb.to_index_entry()
        rid = entry["id"]
        # Precompute a keyword bag for search relevance.
        kw = keywords(rb)
        entry["keywords"] = sorted(set(kw))
        entries.append(entry)
        for k in set(kw):
            inverted[k].append(rid)

        tax["categories"][entry["category"]] += 1
        for t in entry["tags"]:
            tax["tags"][t] += 1
        tax["domains"][entry["domain"]] += 1
        tax["platforms"][entry["platform"]] += 1
        for a in entry["supported_agents"]:
            tax["agents"][a] += 1
        tax["difficulties"][entry["difficulty"]] += 1
        if entry.get("risk_level"):
            tax["risk_levels"][entry["risk_level"]] += 1
        if entry.get("maturity"):
            tax["maturity"][entry["maturity"]] += 1

    index = {
        "generated_by": "tools/search/build_index.py",
        "count": len(entries),
        "runbooks": entries,
        "inverted_index": {k: sorted(set(v)) for k, v in sorted(inverted.items())},
    }
    write_json(REPO_ROOT / "catalog" / "runbook-index.json", index)

    taxonomy = {
        "generated_by": "tools/search/build_index.py",
        "count": len(entries),
        **{k: dict(sorted(v.items(), key=lambda kv: (-kv[1], kv[0]))) for k, v in tax.items()},
    }
    write_json(REPO_ROOT / "catalog" / "taxonomy.json", taxonomy)

    print(bold(f"Indexed {len(entries)} runbook(s)."))
    print(f"  categories : {len(tax['categories'])}")
    print(f"  tags       : {len(tax['tags'])}")
    print(f"  keywords   : {len(inverted)}")
    print(green("Wrote catalog/runbook-index.json and catalog/taxonomy.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
