#!/usr/bin/env python3
"""Check relative Markdown links across the repository.

Verifies that every relative link and image target in every Markdown file points
at an existing file (anchors and external http(s)/mailto links are not fetched,
only validated for basic shape). Exit 1 if any relative link is broken.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from common import REPO_ROOT, bold, green, red, yellow

LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)]+)\)")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")

SKIP_SCHEMES = {"http", "https", "mailto", "tel"}


def iter_markdown() -> list[Path]:
    files: list[Path] = []
    for path in REPO_ROOT.rglob("*.md"):
        if any(part in {".git", "node_modules"} for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def resolve_target(md_file: Path, target: str) -> tuple[bool, str]:
    # Strip anchor.
    raw = target.strip()
    if raw.startswith("#"):
        return True, "in-page anchor"
    parsed = urlparse(raw)
    if parsed.scheme in SKIP_SCHEMES:
        return True, "external"
    path_part = raw.split("#", 1)[0]
    if not path_part:
        return True, "anchor-only"
    candidate = (md_file.parent / path_part).resolve()
    if candidate.exists():
        return True, "ok"
    return False, f"missing target: {path_part}"


def main() -> int:
    files = iter_markdown()
    broken = 0
    checked = 0
    print(bold(f"Checking links in {len(files)} Markdown file(s)...\n"))
    for f in files:
        text = f.read_text(encoding="utf-8")
        targets = LINK_RE.findall(text) + IMAGE_RE.findall(text)
        rel = str(f.relative_to(REPO_ROOT)).replace("\\", "/")
        for t in targets:
            checked += 1
            ok, reason = resolve_target(f, t)
            if not ok:
                broken += 1
                print(red(f"BROKEN  {rel}  ->  {t}  ({reason})"))

    print()
    print(f"Checked {checked} link(s) across {len(files)} file(s).")
    if broken:
        print(red(bold(f"{broken} broken relative link(s) found.")))
        return 1
    print(green(bold("No broken relative links.")))
    if checked == 0:
        print(yellow("(No links were found to check.)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
