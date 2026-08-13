"""Shared library for awesome-ai-runbooks tooling (Phase 2 platform).

This module is the single source of truth for locating, parsing, and reasoning
about runbooks. Every tool under ``tools/`` imports from here so behavior stays
consistent across validation, scoring, search, metrics, and reporting.

Design goals:
  * Zero *required* third-party dependencies. PyYAML is used when available for
    robust front-matter parsing, otherwise a capable stdlib fallback is used.
  * Deterministic, fast, and safe to run in CI.
  * A stable public API (see ``__all__``) that other tools and tests rely on.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:  # Prefer PyYAML when present.
    import yaml as _yaml  # type: ignore
except Exception:  # pragma: no cover - fallback path
    _yaml = None

__all__ = [
    "REPO_ROOT",
    "RUNBOOKS_DIR",
    "REQUIRED_SECTIONS",
    "REQUIRED_METADATA_KEYS",
    "OPTIONAL_METADATA_KEYS",
    "SUPPORTED_AGENTS",
    "MATURITY_LEVELS",
    "Runbook",
    "load_runbooks",
    "load_runbook",
    "parse_front_matter",
    "split_front_matter",
    "difficulty_from_risk",
    "maturity_level_number",
]

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNBOOKS_DIR = REPO_ROOT / "runbooks"

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

# Metadata keys that must be present on every runbook (original v1 contract).
REQUIRED_METADATA_KEYS: list[str] = [
    "id",
    "title",
    "category",
    "maturity",
    "risk_level",
    "estimated_duration",
    "supported_agents",
    "required_access",
    "human_in_the_loop",
    "owner",
    "version",
    "last_reviewed",
    "tags",
]

# Extended metadata keys introduced by the Phase 2 metadata system.
OPTIONAL_METADATA_KEYS: list[str] = [
    "difficulty",
    "domain",
    "platform",
    "agent_type",
    "author",
    "reviewers",
    "required_tools",
    "compliance_tags",
    "status",
    "maturity_level",
]

SUPPORTED_AGENTS: list[str] = [
    "devin",
    "claude-code",
    "github-copilot-agent",
    "openai-codex",
    "cursor",
    "openhands",
    "autogen",
    "crewai",
    "langgraph",
    "mcp-agent",
]

# Maturity model (Phase 26). Maps textual maturity/status to a 1-5 level.
MATURITY_LEVELS: dict[str, int] = {
    "draft": 1,
    "validated": 2,
    "reviewed": 2,
    "production": 3,
    "stable": 3,
    "enterprise": 4,
    "reference": 5,
    "reference-standard": 5,
}

_FM_RE = re.compile(r"^\ufeff?---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_MERMAID_RE = re.compile(r"```mermaid\b(.*?)```", re.DOTALL)
_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


def split_front_matter(text: str) -> tuple[str, str]:
    """Return ``(front_matter_yaml, body)``; front matter may be empty."""
    m = _FM_RE.match(text)
    if not m:
        return "", text
    return m.group(1), text[m.end():]


def _coerce_scalar(value: str) -> Any:
    v = value.strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
    if (v.startswith("'") and v.endswith("'")) or (v.startswith('"') and v.endswith('"')):
        return v[1:-1]
    return v


def _fallback_parse(fm: str) -> dict[str, Any]:
    """Minimal YAML parser for our flat front matter (scalars + lists)."""
    result: dict[str, Any] = {}
    current: str | None = None
    for raw in fm.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        if re.match(r"^\s*-\s+", line) and current:
            item = line.strip()[2:].strip().strip("'\"")
            if not isinstance(result.get(current), list):
                result[current] = []
            result[current].append(item)
            continue
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2)
            # Strip trailing inline comments for scalars (not inside quotes/brackets).
            if val and not val.strip().startswith("[") and "#" in val:
                if not (val.strip().startswith("'") or val.strip().startswith('"')):
                    val = val.split("#", 1)[0]
            current = key
            result[key] = _coerce_scalar(val) if val.strip() else None
    return result


def parse_front_matter(text: str) -> dict[str, Any]:
    """Parse YAML front matter into a dict (PyYAML if available)."""
    fm, _ = split_front_matter(text)
    if not fm:
        return {}
    if _yaml is not None:
        try:
            data = _yaml.safe_load(fm)
            return _normalize(data) if isinstance(data, dict) else {}
        except Exception:
            pass
    return _fallback_parse(fm)


def _normalize(value: Any) -> Any:
    """Coerce YAML-native scalars (dates, ints) to strings for schema stability.

    Front matter is authored as text; YAML may promote ``2026-08-13`` to a date
    or ``1.0`` to a float. We keep lists/dicts but stringify leaf scalars that
    are not already str/bool so downstream schema validation is deterministic.
    """
    import datetime as _dt

    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    if isinstance(value, (_dt.date, _dt.datetime)):
        return value.isoformat()
    return value


def difficulty_from_risk(risk_level: str | None) -> str:
    return {
        "low": "beginner",
        "medium": "intermediate",
        "high": "advanced",
        "critical": "expert",
    }.get((risk_level or "").lower(), "intermediate")


def maturity_level_number(maturity: str | None, status: str | None = None) -> int:
    for key in (status, maturity):
        if key and key.lower() in MATURITY_LEVELS:
            return MATURITY_LEVELS[key.lower()]
    return 1


@dataclass
class Runbook:
    """A parsed runbook with cached derived properties."""

    path: Path
    text: str
    meta: dict[str, Any] = field(default_factory=dict)

    # ---- identity -------------------------------------------------------
    @property
    def rel(self) -> str:
        return str(self.path.relative_to(REPO_ROOT)).replace("\\", "/")

    @property
    def slug(self) -> str:
        return self.path.stem

    @property
    def category(self) -> str:
        return str(self.meta.get("category") or self.path.parent.name)

    @property
    def title(self) -> str:
        return str(self.meta.get("title") or self.slug)

    # ---- content --------------------------------------------------------
    @property
    def body(self) -> str:
        return split_front_matter(self.text)[1]

    @property
    def body_no_fences(self) -> str:
        return _FENCE_RE.sub(" ", self.body)

    @property
    def h1s(self) -> list[str]:
        return _H1_RE.findall(_FENCE_RE.sub("", self.text))

    @property
    def sections(self) -> list[str]:
        return _H2_RE.findall(_FENCE_RE.sub("", self.text))

    def section_body(self, name: str) -> str:
        starts: list[tuple[int, str]] = []
        for sec in self.sections:
            m = re.search(rf"^##\s+{re.escape(sec)}\s*$", self.text, re.MULTILINE)
            if m:
                starts.append((m.start(), sec))
        starts.sort()
        for i, (pos, sec) in enumerate(starts):
            if sec != name:
                continue
            heading_end = self.text.index("\n", pos) if "\n" in self.text[pos:] else len(self.text)
            end = starts[i + 1][0] if i + 1 < len(starts) else len(self.text)
            return self.text[heading_end:end]
        return ""

    def word_count(self) -> int:
        return len(re.findall(r"\b\w[\w'-]*\b", self.body_no_fences))

    def mermaid_blocks(self) -> list[str]:
        return [b.strip() for b in _MERMAID_RE.findall(self.text)]

    def mermaid_count(self) -> int:
        return len(self.mermaid_blocks())

    def code_fence_count(self) -> int:
        return len(_FENCE_RE.findall(self.text))

    def checklist_count(self) -> int:
        return len(re.findall(r"^\s*-\s+\[[ xX]\]", self.text, re.MULTILINE))

    def table_count(self) -> int:
        return len(re.findall(r"^\s*\|.*\|\s*$", self.text, re.MULTILINE))

    def has_example(self) -> bool:
        return len(self.section_body("Example Execution").strip()) > 40

    # ---- metadata helpers ----------------------------------------------
    @property
    def supported_agents(self) -> list[str]:
        v = self.meta.get("supported_agents") or self.meta.get("agent_type") or []
        return v if isinstance(v, list) else [v]

    @property
    def tags(self) -> list[str]:
        v = self.meta.get("tags") or []
        return v if isinstance(v, list) else [v]

    @property
    def maturity_level(self) -> int:
        return maturity_level_number(self.meta.get("maturity"), self.meta.get("status"))

    def to_index_entry(self) -> dict[str, Any]:
        return {
            "id": self.meta.get("id", self.slug),
            "title": self.title,
            "path": self.rel,
            "category": self.category,
            "domain": self.meta.get("domain", self.category),
            "tags": self.tags,
            "difficulty": self.meta.get("difficulty", difficulty_from_risk(self.meta.get("risk_level"))),
            "risk_level": self.meta.get("risk_level"),
            "maturity": self.meta.get("maturity"),
            "maturity_level": self.maturity_level,
            "status": self.meta.get("status", "approved"),
            "estimated_duration": self.meta.get("estimated_duration"),
            "supported_agents": self.supported_agents,
            "platform": self.meta.get("platform", "cross-platform"),
            "required_tools": self.meta.get("required_tools", []),
            "compliance_tags": self.meta.get("compliance_tags", []),
            "human_in_the_loop": self.meta.get("human_in_the_loop"),
            "version": self.meta.get("version"),
            "last_reviewed": self.meta.get("last_reviewed"),
            "word_count": self.word_count(),
            "mermaid_count": self.mermaid_count(),
        }


def load_runbook(path: Path) -> Runbook:
    text = path.read_text(encoding="utf-8")
    return Runbook(path=path, text=text, meta=parse_front_matter(text))


def load_runbooks(root: Path | None = None) -> list[Runbook]:
    root = root or RUNBOOKS_DIR
    out: list[Runbook] = []
    if not root.exists():
        return out
    for p in sorted(root.rglob("*.md")):
        if p.name.lower() in {"readme.md", "index.md"}:
            continue
        out.append(load_runbook(p))
    return out


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# --- tiny ANSI helpers (shared) -----------------------------------------
def green(s: str) -> str:
    return f"\033[92m{s}\033[0m"


def red(s: str) -> str:
    return f"\033[91m{s}\033[0m"


def yellow(s: str) -> str:
    return f"\033[93m{s}\033[0m"


def bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"
