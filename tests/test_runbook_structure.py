"""Structural tests for every runbook (Phase 22)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from runbook_lib import REQUIRED_SECTIONS  # type: ignore  # noqa: E402

MIN_WORDS = 1000
MIN_MERMAID = 2


def test_single_h1(runbook):
    assert len(runbook.h1s) == 1, f"{runbook.rel}: expected exactly one H1, got {runbook.h1s}"


def test_all_required_sections_present(runbook):
    present = set(runbook.sections)
    missing = [s for s in REQUIRED_SECTIONS if s not in present]
    assert not missing, f"{runbook.rel}: missing sections {missing}"


def test_sections_in_canonical_order(runbook):
    present = runbook.sections
    idx = [present.index(s) for s in REQUIRED_SECTIONS if s in present]
    assert idx == sorted(idx), f"{runbook.rel}: sections out of canonical order"


def test_minimum_word_count(runbook):
    wc = runbook.word_count()
    assert wc >= MIN_WORDS, f"{runbook.rel}: only {wc} words (< {MIN_WORDS})"


def test_minimum_mermaid_diagrams(runbook):
    md = runbook.mermaid_count()
    assert md >= MIN_MERMAID, f"{runbook.rel}: only {md} mermaid diagrams (< {MIN_MERMAID})"


def test_has_investigation_and_decision_diagrams(runbook):
    assert "Investigation Workflow" in runbook.sections
    assert "Decision Tree" in runbook.sections


def test_no_placeholder_tokens(runbook):
    lowered = runbook.text.lower()
    for tok in ("todo", "fixme", "lorem ipsum", "placeholder"):
        assert tok not in lowered, f"{runbook.rel}: contains placeholder token '{tok}'"


def test_has_table_and_checklist(runbook):
    assert runbook.table_count() >= 1, f"{runbook.rel}: no tables"
    assert runbook.checklist_count() >= 1, f"{runbook.rel}: no checklists"
