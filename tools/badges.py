#!/usr/bin/env python3
"""Badge generation (Phase 19).

Emits shields.io-compatible endpoint JSON files under ``.github/badges/`` for:

  * Runbook Count
  * Agent Compatibility
  * Validation Status
  * Repository Health
  * Documentation Coverage
  * Contributors
  * Security Review
  * Automation Coverage
  * Mean Quality Score
  * Maturity (share at L4+)

Each file is a shields.io "endpoint" schema, so a README badge can be rendered
with:

    ![Runbooks](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/OWNER/REPO/main/.github/badges/runbooks.json)

Also writes ``.github/badges/BADGES.md`` with ready-to-paste Markdown snippets.

Usage:
    python tools/badges.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runbook_lib import (  # type: ignore  # noqa: E402
    REPO_ROOT,
    SUPPORTED_AGENTS,
    bold,
    green,
    load_runbooks,
    maturity_level_number,
    write_json,
)

BADGE_DIR = REPO_ROOT / ".github" / "badges"
RAW_BASE = "https://raw.githubusercontent.com/awesome-ai-runbooks/awesome-ai-runbooks/main/.github/badges"


def color_for(pct: float) -> str:
    return "brightgreen" if pct >= 90 else "green" if pct >= 80 else "yellow" if pct >= 70 else "orange" if pct >= 50 else "red"


def endpoint(label: str, message: str, color: str) -> dict:
    return {"schemaVersion": 1, "label": label, "message": message, "color": color}


def _read_json(rel: str) -> dict:
    p = REPO_ROOT / rel
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def contributors() -> int:
    try:
        out = subprocess.run(["git", "shortlog", "-sne", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, timeout=20)
        if out.returncode == 0:
            return len([ln for ln in out.stdout.splitlines() if ln.strip()])
    except Exception:
        pass
    return 0


def main() -> int:
    runbooks = load_runbooks()
    n = len(runbooks)

    quality = _read_json("quality/quality-score.json")
    health = _read_json("quality/repository-health.json")
    security = _read_json("security/security-score.json")

    mean_score = quality.get("mean_score")
    passed = quality.get("passed", n)
    failed = quality.get("failed", 0)
    health_score = health.get("overall")
    docs_cov = (health.get("dimensions") or {}).get("documentation")
    sec_level = security.get("security_maturity_level")
    sec_name = security.get("security_maturity_name", "n/a")

    # Automation coverage: fraction of expected automation signals present.
    automation = (health.get("dimensions") or {}).get("automation", 0)

    # Agent compatibility: agents supported by ALL runbooks.
    universal = set(SUPPORTED_AGENTS)
    for rb in runbooks:
        universal &= set(rb.supported_agents)
    maturity_l5 = sum(1 for rb in runbooks if maturity_level_number(rb.meta.get("maturity"), rb.meta.get("status")) >= 4)

    badges = {
        "runbooks": endpoint("runbooks", str(n), "blue"),
        "agents": endpoint("agent compatibility", f"{len(universal)}/{len(SUPPORTED_AGENTS)}", "blueviolet"),
        "validation": endpoint("validation", "passing" if failed == 0 else f"{failed} failing", "brightgreen" if failed == 0 else "red"),
        "health": endpoint("repo health", f"{health_score}" if health_score is not None else "n/a", color_for(health_score or 0)),
        "docs-coverage": endpoint("docs coverage", f"{docs_cov}%" if docs_cov is not None else "n/a", color_for(docs_cov or 0)),
        "contributors": endpoint("contributors", str(contributors()), "informational"),
        "security": endpoint("security review", f"L{sec_level} {sec_name}" if sec_level else "n/a", "brightgreen" if (sec_level or 0) >= 4 else "yellow"),
        "automation": endpoint("automation", f"{round(automation)}%", color_for(automation)),
        "quality": endpoint("quality score", f"{mean_score}" if mean_score is not None else "n/a", color_for(mean_score or 0)),
        "maturity": endpoint("enterprise-ready", f"{maturity_l5}/{n}", "brightgreen"),
    }

    for name, payload in badges.items():
        write_json(BADGE_DIR / f"{name}.json", payload)

    # Ready-to-paste markdown.
    lines = ["# Badges", "", "Paste these into `README.md` (replace OWNER/REPO if forked).", ""]
    for name, payload in badges.items():
        url = f"https://img.shields.io/endpoint?url={RAW_BASE}/{name}.json"
        lines.append(f"- **{payload['label']}**: `![{payload['label']}]({url})`")
    lines.append("")
    (BADGE_DIR / "BADGES.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")

    print(bold(f"Generated {len(badges)} badge endpoint(s) in .github/badges/"))
    for name, payload in badges.items():
        print(f"  {payload['label']:<22} {payload['message']}")
    print(green("Wrote .github/badges/*.json and BADGES.md"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
