"""Shared helpers for awesome-ai-runbooks tooling.

Pure standard-library so the scripts run anywhere with Python 3.10+.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# Repository root (parent of the scripts/ directory).
REPO_ROOT = Path(__file__).resolve().parent.parent
RUNBOOKS_DIR = REPO_ROOT / "runbooks"
TEMPLATES_DIR = REPO_ROOT / "templates"

# The canonical, ordered list of section headings every runbook must contain.
REQUIRED_SECTIONS: list[str] = [
    "Objective",
    "Business Context",
    "Problem Statement",
    "Success Criteria",
    "Trigger Conditions",
    "Inputs Required",
    "Required Access",
    "Assumptions",
    "Risks",
    "Constraints",
    "Agent Persona",
    "Planning Instructions",
    "Execution Instructions",
    "Investigation Workflow",
    "Analysis Framework",
    "Decision Tree",
    "Validation Steps",
    "Expected Outputs",
    "Deliverables",
    "Escalation Process",
    "Rollback Strategy",
    "Post-Execution Review",
    "Metrics",
    "Example Execution",
    "References",
]

# Required YAML front-matter keys.
REQUIRED_FRONT_MATTER_KEYS: list[str] = [
    "id",
    "title",
    "category",
    "maturity",
    "risk_level",
    "supported_agents",
    "required_access",
    "human_in_the_loop",
    "owner",
    "version",
    "last_reviewed",
    "tags",
]

MIN_WORDS = 1000
MIN_MERMAID_DIAGRAMS = 2

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
H2_RE = re.compile(r"^##\s+(.*?)\s*$", re.MULTILINE)
H1_RE = re.compile(r"^#\s+(.*?)\s*$", re.MULTILINE)
MERMAID_RE = re.compile(r"```mermaid\b")


@dataclass
class RunbookDoc:
    path: Path
    text: str
    front_matter: dict[str, str] = field(default_factory=dict)
    sections: list[str] = field(default_factory=list)

    @property
    def rel(self) -> str:
        return str(self.path.relative_to(REPO_ROOT)).replace("\\", "/")

    @property
    def body(self) -> str:
        """Document text with the front matter removed."""
        return FRONT_MATTER_RE.sub("", self.text, count=1)

    def word_count(self) -> int:
        # Count words in the body, excluding code fences to keep it about prose.
        body = re.sub(r"```.*?```", " ", self.body, flags=re.DOTALL)
        return len(re.findall(r"\b\w[\w'-]*\b", body))

    def mermaid_count(self) -> int:
        return len(MERMAID_RE.findall(self.text))


def parse_front_matter(text: str) -> dict[str, str]:
    """Minimal YAML front-matter parser (flat keys, lists on one line or block)."""
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}
    result: dict[str, str] = {}
    current_key: str | None = None
    for raw in match.group(1).splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if re.match(r"^\s*-\s+", line) and current_key:
            # Block list item -> append.
            result[current_key] = (result.get(current_key, "") + " " + line.strip()[2:]).strip()
            continue
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if m:
            current_key = m.group(1)
            result[current_key] = m.group(2).strip()
    return result


def load_runbook(path: Path) -> RunbookDoc:
    text = path.read_text(encoding="utf-8")
    doc = RunbookDoc(path=path, text=text)
    doc.front_matter = parse_front_matter(text)
    # Detect H2 section headings, ignoring any '##' inside fenced code blocks.
    text_no_fences = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    doc.sections = H2_RE.findall(text_no_fences)
    return doc


def iter_runbooks() -> list[RunbookDoc]:
    docs: list[RunbookDoc] = []
    if not RUNBOOKS_DIR.exists():
        return docs
    for path in sorted(RUNBOOKS_DIR.rglob("*.md")):
        # Skip category index/readme files if any.
        if path.name.lower() in {"readme.md", "index.md"}:
            continue
        docs.append(load_runbook(path))
    return docs


# Simple ANSI helpers (no dependency on colorama).
def green(s: str) -> str:
    return f"\033[92m{s}\033[0m"


def red(s: str) -> str:
    return f"\033[91m{s}\033[0m"


def yellow(s: str) -> str:
    return f"\033[93m{s}\033[0m"


def bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"
