"""Template + generator tests (Phase 22)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from runbook_lib import REQUIRED_SECTIONS  # type: ignore  # noqa: E402


def test_runbook_template_exists_and_complete():
    p = REPO_ROOT / "templates" / "runbook-template.md"
    assert p.exists()
    text = p.read_text(encoding="utf-8")
    for sec in REQUIRED_SECTIONS:
        assert f"## {sec}" in text, f"template missing section: {sec}"


def test_report_template_exists():
    p = REPO_ROOT / "templates" / "report-template.md"
    assert p.exists()
    text = p.read_text(encoding="utf-8")
    for heading in ["Executive Summary", "Findings", "Recommendations", "Validation Results"]:
        assert heading in text


def test_runbook_config_parses():
    yaml = pytest.importorskip("yaml")
    p = REPO_ROOT / "templates" / "runbook-config.yaml"
    assert p.exists()
    cfg = yaml.safe_load(p.read_text(encoding="utf-8"))
    for key in ("id", "title", "category"):
        assert cfg.get(key)


def test_generator_produces_all_sections(tmp_path):
    """The generator output must contain every canonical section."""
    yaml = pytest.importorskip("yaml")
    sys.path.insert(0, str(REPO_ROOT / "tools" / "runbook_generator"))
    import generate_runbook  # type: ignore

    cfg = yaml.safe_load((REPO_ROOT / "templates" / "runbook-config.yaml").read_text(encoding="utf-8"))
    content = generate_runbook.build_front_matter(cfg) + "\n\n" + generate_runbook.build_body(cfg)
    for sec in REQUIRED_SECTIONS:
        assert f"## {sec}" in content, f"generated runbook missing section: {sec}"
    assert content.count("```mermaid") >= 2
