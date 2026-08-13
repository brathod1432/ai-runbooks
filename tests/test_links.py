"""Relative-link integrity tests (Phase 22)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)]+)\)")
IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def _broken_links(md_file: Path) -> list[str]:
    text = md_file.read_text(encoding="utf-8")
    broken = []
    for target in LINK_RE.findall(text) + IMG_RE.findall(text):
        t = target.strip()
        if t.startswith("#") or t.startswith(("http://", "https://", "mailto:", "tel:")):
            continue
        path_part = t.split("#", 1)[0]
        if not path_part:
            continue
        if not (md_file.parent / path_part).resolve().exists():
            broken.append(t)
    return broken


def test_runbook_links_resolve(runbook):
    broken = _broken_links(runbook.path)
    assert not broken, f"{runbook.rel}: broken relative links {broken}"


def test_key_docs_links_resolve():
    docs = [
        "README.md",
        "CONTRIBUTING.md",
        "ENTERPRISE_GUIDE.md",
        "docs/AI_AGENT_STANDARDS.md",
        "docs/QUALITY_ASSURANCE.md",
    ]
    problems = {}
    for rel in docs:
        p = REPO_ROOT / rel
        if p.exists():
            broken = _broken_links(p)
            if broken:
                problems[rel] = broken
    assert not problems, f"broken links: {problems}"
