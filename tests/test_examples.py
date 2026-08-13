"""Example-execution tests (Phase 22)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))


def test_example_execution_non_trivial(runbook):
    body = runbook.section_body("Example Execution")
    assert len(body.strip()) > 60, f"{runbook.rel}: Example Execution too short"


def test_example_has_concrete_content(runbook):
    body = runbook.section_body("Example Execution")
    # Should include either a code block, a report excerpt, or inputs.
    signals = ["```", "Input", "Report", "Finding", "Recommendation", "Executive"]
    assert any(s in body for s in signals), f"{runbook.rel}: Example lacks concrete content"


def test_examples_directory_present():
    ex = REPO_ROOT / "examples"
    assert ex.is_dir()
    assert list(ex.glob("*.md")), "examples/ has no markdown files"
