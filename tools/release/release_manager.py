#!/usr/bin/env python3
"""Repository release system (Phase 30).

Provides semantic-version aware release tooling driven by Conventional Commits:

  * ``--next``      compute the next semver from commits since the last tag
  * ``--notes``     generate categorized release notes for the pending release
  * ``--changelog`` render a Keep-a-Changelog section for the pending release
  * ``--plan``      print a full release plan (version + notes + checklist)

It never pushes or tags automatically; it prints artifacts for a human to
review and apply. Works with or without any existing tags.

Usage:
    python tools/release/release_manager.py --plan
    python tools/release/release_manager.py --next
    python tools/release/release_manager.py --notes > RELEASE_NOTES.md
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runbook_lib import REPO_ROOT, bold, green, load_runbooks  # type: ignore  # noqa: E402

CC_RE = re.compile(r"^(?P<type>feat|fix|docs|chore|refactor|test|perf|ci|build|security)(?P<bang>!)?(?:\((?P<scope>[^)]+)\))?:\s*(?P<desc>.+)$")

SECTION_TITLES = {
    "feat": "Added",
    "fix": "Fixed",
    "security": "Security",
    "docs": "Documentation",
    "perf": "Performance",
    "refactor": "Changed",
    "ci": "CI",
    "build": "Build",
    "chore": "Maintenance",
    "test": "Tests",
}


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def last_tag() -> str | None:
    tag = _git("describe", "--tags", "--abbrev=0")
    return tag or None


def commits_since(ref: str | None) -> list[str]:
    rng = f"{ref}..HEAD" if ref else "HEAD"
    out = _git("log", rng, "--pretty=format:%s")
    return [ln for ln in out.splitlines() if ln.strip()]


def parse_commits(commits: list[str]) -> tuple[dict[str, list[str]], str]:
    buckets: dict[str, list[str]] = {}
    bump = "patch"
    for c in commits:
        m = CC_RE.match(c)
        if not m:
            buckets.setdefault("chore", []).append(c)
            continue
        ctype = m.group("type")
        desc = m.group("desc")
        scope = m.group("scope")
        entry = f"{'**' + scope + ':** ' if scope else ''}{desc}"
        buckets.setdefault(ctype, []).append(entry)
        if m.group("bang") or "BREAKING CHANGE" in c:
            bump = "major"
        elif ctype == "feat" and bump != "major":
            bump = "minor"
    return buckets, bump


def bump_version(current: str, bump: str) -> str:
    m = re.match(r"v?(\d+)\.(\d+)\.(\d+)", current or "0.0.0")
    major, minor, patch = (int(x) for x in (m.groups() if m else ("0", "0", "0")))
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def current_version() -> str:
    tag = last_tag()
    if tag:
        return tag.lstrip("v")
    # Fall back to CHANGELOG latest version.
    cl = REPO_ROOT / "CHANGELOG.md"
    if cl.exists():
        m = re.search(r"##\s*\[(\d+\.\d+\.\d+)\]", cl.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
    return "1.0.0"


def render_notes(buckets: dict[str, list[str]], version: str) -> str:
    lines = [f"# Release v{version} — {date.today().isoformat()}", ""]
    n_runbooks = len(load_runbooks())
    lines.append(f"> Repository contains **{n_runbooks} runbooks** at release time.")
    lines.append("")
    for ctype in ["feat", "fix", "security", "docs", "perf", "refactor", "ci", "build", "test", "chore"]:
        items = buckets.get(ctype)
        if not items:
            continue
        lines.append(f"## {SECTION_TITLES[ctype]}")
        lines.append("")
        for it in items:
            lines.append(f"- {it}")
        lines.append("")
    if len(lines) <= 4:
        lines += ["## Changes", "", "- Initial release.", ""]
    return "\n".join(lines)


def render_changelog(buckets: dict[str, list[str]], version: str) -> str:
    lines = [f"## [{version}] - {date.today().isoformat()}", ""]
    for ctype in ["feat", "fix", "security", "docs", "refactor", "perf", "ci", "chore"]:
        items = buckets.get(ctype)
        if not items:
            continue
        lines.append(f"### {SECTION_TITLES[ctype]}")
        lines.append("")
        for it in items:
            lines.append(f"- {it}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--next", action="store_true", dest="next_", help="print next version")
    parser.add_argument("--notes", action="store_true", help="print release notes")
    parser.add_argument("--changelog", action="store_true", help="print changelog section")
    parser.add_argument("--plan", action="store_true", help="print full release plan")
    args = parser.parse_args()

    tag = last_tag()
    commits = commits_since(tag)
    buckets, bump = parse_commits(commits)
    cur = current_version()
    nxt = bump_version(cur, bump if commits else "patch")

    if args.next_:
        print(nxt)
        return 0
    if args.notes:
        print(render_notes(buckets, nxt))
        return 0
    if args.changelog:
        print(render_changelog(buckets, nxt))
        return 0

    # Default / --plan
    print(bold("=== Release Plan ===\n"))
    print(f"  Current version : {cur}")
    print(f"  Last tag        : {tag or '(none)'}")
    print(f"  Commits analyzed: {len(commits)}")
    print(f"  Bump            : {bump}")
    print(green(bold(f"  Next version    : v{nxt}\n")))
    print(render_notes(buckets, nxt))
    print(bold("\nRelease checklist:"))
    for step in [
        "Run: python tools/quality/runbook_validator.py",
        "Run: python -m pytest -q",
        "Run: python tools/health/repository_health.py",
        "Update CHANGELOG.md with the section above",
        f"Tag: git tag -a v{nxt} -m 'Release v{nxt}'",
        "Push tag to trigger release.yml",
    ]:
        print(f"  - [ ] {step}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
