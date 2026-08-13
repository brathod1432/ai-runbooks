"""Metadata + JSON-schema tests for every runbook (Phase 22)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from runbook_lib import (  # type: ignore  # noqa: E402
    OPTIONAL_METADATA_KEYS,
    REQUIRED_METADATA_KEYS,
    SUPPORTED_AGENTS,
)

SCHEMA_PATH = REPO_ROOT / "schemas" / "runbook.schema.json"


@pytest.fixture(scope="session")
def schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_required_metadata_present(runbook):
    for key in REQUIRED_METADATA_KEYS:
        assert runbook.meta.get(key) not in (None, "", [], {}), f"{runbook.rel}: missing {key}"


def test_extended_metadata_present(runbook):
    # Phase 15 extended fields must have been applied.
    for key in ["difficulty", "domain", "platform", "author", "reviewers", "required_tools", "status", "maturity_level"]:
        assert key in runbook.meta, f"{runbook.rel}: missing extended metadata {key}"


def test_id_matches_filename(runbook):
    assert runbook.meta.get("id") == runbook.slug, f"{runbook.rel}: id != filename"


def test_supported_agents_valid(runbook):
    for agent in runbook.supported_agents:
        assert agent in SUPPORTED_AGENTS, f"{runbook.rel}: unknown agent '{agent}'"


def test_risk_level_valid(runbook):
    assert runbook.meta.get("risk_level") in ("low", "medium", "high", "critical")


def test_schema_validation(runbook, schema):
    jsonschema = pytest.importorskip("jsonschema")
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(runbook.meta), key=lambda e: list(e.path))
    assert not errors, f"{runbook.rel}: " + "; ".join(
        f"{'/'.join(str(p) for p in e.path) or '(root)'}: {e.message}" for e in errors
    )


def test_optional_keys_are_known():
    # Guard against typos creeping into the extended metadata contract.
    assert "difficulty" in OPTIONAL_METADATA_KEYS
    assert "compliance_tags" in OPTIONAL_METADATA_KEYS
