"""Quality-scoring and tooling smoke tests (Phase 22)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "quality"))

import runbook_quality_engine as qe  # type: ignore  # noqa: E402
import runbook_validator as rv  # type: ignore  # noqa: E402


def test_validator_scores_are_reasonable(runbook):
    score = rv.score_runbook(runbook)
    assert 0 <= score <= 100
    assert score >= 75, f"{runbook.rel}: completeness score {score} < 75"


def test_no_hard_validation_errors(runbook):
    schema = rv._load_schema()
    errors, _warnings = rv.validate_runbook(runbook, schema)
    assert not errors, f"{runbook.rel}: {errors}"


def test_quality_dimensions_bounds(runbook):
    for name, fn in qe.DIMENSIONS.items():
        val = fn(runbook)
        assert 0 <= val <= 100, f"{runbook.rel}: dimension {name}={val} out of bounds"


def test_composite_meets_bar(runbook):
    scores = {name: fn(runbook) for name, fn in qe.DIMENSIONS.items()}
    composite = qe.composite(scores)
    assert composite >= 80, f"{runbook.rel}: composite {composite} < 80"


def test_repository_mean_is_high(runbooks):
    scores = [rv.score_runbook(rb) for rb in runbooks]
    mean = sum(scores) / len(scores)
    assert mean >= 85, f"repository mean completeness {mean} < 85"
