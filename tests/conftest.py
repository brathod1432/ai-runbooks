"""Pytest configuration and shared fixtures for awesome-ai-runbooks."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
# Make the shared tooling library importable in tests.
sys.path.insert(0, str(REPO_ROOT / "tools"))

from runbook_lib import load_runbooks  # type: ignore  # noqa: E402


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def runbooks():
    rbs = load_runbooks()
    assert rbs, "no runbooks found under runbooks/"
    return rbs


def pytest_generate_tests(metafunc):
    """Parametrize any test that takes a ``runbook`` argument over all runbooks."""
    if "runbook" in metafunc.fixturenames:
        rbs = load_runbooks()
        metafunc.parametrize("runbook", rbs, ids=[rb.slug for rb in rbs])
