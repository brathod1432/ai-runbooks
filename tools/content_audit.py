#!/usr/bin/env python3
"""Automatic content auditing (Phase 29).

Detects content-quality problems across the runbook library:
  * missing / thin examples
  * missing / thin validation
  * low-quality (thin) required sections
  * likely-duplicate runbooks (high title/tag/keyword similarity)
  * obsolete references (localhost/example.com/TODO-style placeholders, dead
    relative links)

Writes ``quality/content-audit.json`` and prints a report. Exit 1 if any
``blocking`` issue is found (missing example/validation, broken relative link).

Usage:
    python tools/content_audit.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runbook_lib import (  # type: ignore  # noqa: E402
    REPO_ROOT,
    REQUIRED_SECTIONS,
    Runbook,
    bold,
    green,
    load_runbooks,
    red,
    write_json,
    yellow,
)

THIN_WORDS = 12
DUP_THRESHOLD = 0.6
OBSOLETE_PATTERNS = [
    (r"\bTODO\b", "TODO marker"),
    (r"\bFIXME\b", "FIXME marker"),
    (r"lorem ipsum", "lorem ipsum filler"),
    (r"https?://example\.com", "example.com placeholder URL"),
    (r"\byour-token-here\b", "placeholder token"),
]
LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)]+)\)")


def _words(text: str) -> int:
    return len(re.findall(r"\b\w[\w'-]*\b", re.sub(r"```.*?```", " ", text, flags=re.DOTALL)))


def thin_sections(rb: Runbook) -> list[str]:
    thin = []
    for sec in REQUIRED_SECTIONS:
        body = rb.section_body(sec)
        has_fence = "```" in body
        if _words(body) < THIN_WORDS and not has_fence:
            thin.append(sec)
    return thin


def obsolete_refs(rb: Runbook) -> list[str]:
    found = []
    for pat, label in OBSOLETE_PATTERNS:
        if re.search(pat, rb.text, re.IGNORECASE):
            found.append(label)
    return found


def broken_links(rb: Runbook) -> list[str]:
    broken = []
    for target in LINK_RE.findall(rb.text):
        t = target.strip()
        if t.startswith("#") or t.startswith(("http://", "https://", "mailto:")):
            continue
        path_part = t.split("#", 1)[0]
        if not path_part:
            continue
        if not (rb.path.parent / path_part).resolve().exists():
            broken.append(path_part)
    return broken


def token_set(rb: Runbook) -> set[str]:
    text = f"{rb.title} {' '.join(rb.tags)} {rb.section_body('Objective')}"
    return set(re.findall(r"[a-z][a-z0-9+-]{3,}", text.lower()))


def find_duplicates(runbooks: list[Runbook]) -> list[dict]:
    dups = []
    for i in range(len(runbooks)):
        for j in range(i + 1, len(runbooks)):
            a, b = runbooks[i], runbooks[j]
            ta, tb = token_set(a), token_set(b)
            if not (ta and tb):
                continue
            jac = len(ta & tb) / len(ta | tb)
            if jac >= DUP_THRESHOLD:
                dups.append({"a": a.slug, "b": b.slug, "similarity": round(jac, 3)})
    return dups


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default="quality/content-audit.json")
    args = parser.parse_args()

    runbooks = load_runbooks()
    findings = []
    blocking = 0

    for rb in runbooks:
        issues = {"path": rb.rel, "id": rb.slug, "problems": []}
        if not rb.has_example():
            issues["problems"].append({"severity": "blocking", "type": "missing_example"})
            blocking += 1
        if _words(rb.section_body("Validation Steps")) < THIN_WORDS:
            issues["problems"].append({"severity": "blocking", "type": "missing_validation"})
            blocking += 1
        for sec in thin_sections(rb):
            issues["problems"].append({"severity": "warning", "type": "thin_section", "section": sec})
        for label in obsolete_refs(rb):
            issues["problems"].append({"severity": "warning", "type": "obsolete_reference", "detail": label})
        for link in broken_links(rb):
            issues["problems"].append({"severity": "blocking", "type": "broken_link", "detail": link})
            blocking += 1
        if issues["problems"]:
            findings.append(issues)

    duplicates = find_duplicates(runbooks)

    report = {
        "generated_by": "tools/content_audit.py",
        "runbooks_scanned": len(runbooks),
        "runbooks_with_findings": len(findings),
        "blocking_issues": blocking,
        "duplicate_candidates": duplicates,
        "findings": findings,
    }
    write_json(REPO_ROOT / args.json, report)

    print(bold(f"Content audit: scanned {len(runbooks)} runbook(s)\n"))
    if not findings and not duplicates:
        print(green(bold("No content issues detected.")))
    for f in findings:
        for p in f["problems"]:
            color = red if p["severity"] == "blocking" else yellow
            detail = p.get("section") or p.get("detail") or ""
            print(color(f"  [{p['severity']}] {f['path']}: {p['type']} {detail}"))
    if duplicates:
        print(yellow(f"\n  {len(duplicates)} possible duplicate pair(s):"))
        for d in duplicates:
            print(yellow(f"    {d['a']} ~ {d['b']} ({d['similarity']})"))

    print(green(f"\nWrote {args.json}"))
    if blocking:
        print(red(bold(f"{blocking} blocking content issue(s).")))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
