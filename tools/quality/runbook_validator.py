#!/usr/bin/env python3
"""Runbook validator (Phase 13).

Verifies mandatory sections, Markdown format, minimum content standards,
Mermaid diagrams, examples, and JSON-schema conformance of metadata; then
scores each runbook and writes ``quality/quality-score.json``.

Usage:
    python tools/quality/runbook_validator.py [--json quality/quality-score.json] [--strict]

Exit code 1 if any runbook fails a hard check (missing section, invalid schema,
too short, no diagrams). ``--strict`` also fails on warnings.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Bootstrap: make the shared library importable regardless of CWD.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runbook_lib import (  # type: ignore  # noqa: E402
    REPO_ROOT,
    REQUIRED_METADATA_KEYS,
    REQUIRED_SECTIONS,
    Runbook,
    bold,
    green,
    load_runbooks,
    red,
    write_json,
    yellow,
)

MIN_WORDS = 1000
MIN_MERMAID = 2
PLACEHOLDER_TOKENS = ("TODO", "FIXME", "lorem ipsum", "PLACEHOLDER", "XXX")

try:
    import jsonschema  # type: ignore

    _HAVE_JSONSCHEMA = True
except Exception:  # pragma: no cover
    _HAVE_JSONSCHEMA = False

_SCHEMA_PATH = REPO_ROOT / "schemas" / "runbook.schema.json"


def _load_schema() -> dict | None:
    if _SCHEMA_PATH.exists():
        return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    return None


def validate_runbook(rb: Runbook, schema: dict | None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    # --- metadata ---------------------------------------------------------
    if not rb.meta:
        errors.append("missing/unparseable front matter")
    else:
        for key in REQUIRED_METADATA_KEYS:
            if key not in rb.meta or rb.meta.get(key) in (None, "", [], {}):
                errors.append(f"front matter missing key: {key}")
        if rb.meta.get("id") and rb.meta["id"] != rb.slug:
            errors.append(f"id '{rb.meta['id']}' != filename '{rb.slug}'")
        if schema is not None and _HAVE_JSONSCHEMA:
            v = jsonschema.Draft202012Validator(schema)
            for e in sorted(v.iter_errors(rb.meta), key=lambda e: e.path):
                loc = "/".join(str(p) for p in e.path) or "(root)"
                errors.append(f"schema[{loc}]: {e.message}")

    # --- structure --------------------------------------------------------
    if len(rb.h1s) != 1:
        errors.append(f"expected exactly 1 H1, found {len(rb.h1s)}")
    present = rb.sections
    missing = [s for s in REQUIRED_SECTIONS if s not in present]
    if missing:
        errors.append("missing sections: " + ", ".join(missing))
    else:
        idx = [present.index(s) for s in REQUIRED_SECTIONS]
        if idx != sorted(idx):
            errors.append("required sections out of canonical order")

    # --- content standards ------------------------------------------------
    wc = rb.word_count()
    if wc < MIN_WORDS:
        errors.append(f"word count {wc} < {MIN_WORDS}")
    md = rb.mermaid_count()
    if md < MIN_MERMAID:
        errors.append(f"mermaid diagrams {md} < {MIN_MERMAID}")
    else:
        # Validate that mermaid blocks look like real diagrams.
        for i, block in enumerate(rb.mermaid_blocks(), 1):
            first = block.strip().splitlines()[0].strip() if block.strip() else ""
            if not any(first.startswith(k) for k in ("flowchart", "graph", "sequenceDiagram", "stateDiagram", "classDiagram", "erDiagram", "journey", "gantt", "mindmap")):
                warnings.append(f"mermaid block {i} has unrecognized diagram type '{first[:20]}'")

    if not rb.has_example():
        errors.append("Example Execution section is empty/too short")
    if rb.table_count() < 1:
        warnings.append("no Markdown tables found")
    if rb.checklist_count() < 1:
        warnings.append("no checklists found")

    lowered = rb.text.lower()
    for tok in PLACEHOLDER_TOKENS:
        if tok.lower() in lowered:
            errors.append(f"placeholder token present: {tok}")

    return errors, warnings


def score_runbook(rb: Runbook) -> int:
    """Lightweight completeness score /100 (mirrors QUALITY_ASSURANCE.md)."""
    present = set(rb.sections)
    section_ratio = sum(1 for s in REQUIRED_SECTIONS if s in present) / len(REQUIRED_SECTIONS)
    meta_ratio = sum(1 for k in REQUIRED_METADATA_KEYS if rb.meta.get(k)) / len(REQUIRED_METADATA_KEYS)
    score = 0
    score += round(25 * (0.6 * section_ratio + 0.4 * meta_ratio))
    score += min(20, round(20 * rb.word_count() / (MIN_WORDS * 2)))
    score += min(10, round(10 * rb.mermaid_count() / MIN_MERMAID))
    act = min(4, rb.code_fence_count()) + min(3, rb.checklist_count()) + min(3, rb.table_count())
    score += min(10, act)
    score += (5 if "Validation Steps" in present else 0) + (5 if "Expected Outputs" in present else 0)
    score += (4 if "Rollback Strategy" in present else 0) + (3 if "Escalation Process" in present else 0) + (3 if rb.meta.get("risk_level") else 0)
    score += 5 if rb.has_example() else 0
    score += 5 if "References" in present else 0
    clarity = 5
    if len(rb.h1s) != 1:
        clarity -= 2
    score += max(0, clarity)
    return min(100, score)


def band(score: int) -> str:
    return "exemplary" if score >= 90 else "solid" if score >= 75 else "draft" if score >= 60 else "rejected"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default="quality/quality-score.json")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    schema = _load_schema()
    if schema is None:
        print(yellow("WARN: schema not found; skipping schema validation"))
    elif not _HAVE_JSONSCHEMA:
        print(yellow("WARN: jsonschema not installed; skipping schema validation"))

    runbooks = load_runbooks()
    if not runbooks:
        print(yellow("No runbooks found."))
        return 0

    results = []
    hard_fail = 0
    warn_total = 0
    print(bold(f"Validating & scoring {len(runbooks)} runbook(s)\n"))
    for rb in runbooks:
        errors, warnings = validate_runbook(rb, schema)
        sc = score_runbook(rb)
        warn_total += len(warnings)
        entry = {
            "id": rb.meta.get("id", rb.slug),
            "path": rb.rel,
            "category": rb.category,
            "score": sc,
            "band": band(sc),
            "word_count": rb.word_count(),
            "mermaid_count": rb.mermaid_count(),
            "errors": errors,
            "warnings": warnings,
            "passed": not errors,
        }
        results.append(entry)
        if errors:
            hard_fail += 1
            print(red(f"FAIL  {rb.rel}  (score {sc})"))
            for e in errors:
                print(f"        - {e}")
        else:
            tag = green("PASS")
            print(f"{tag}  {rb.rel}  (score {sc} {band(sc)})")
            for w in warnings:
                print(yellow(f"        ~ {w}"))

    mean = round(sum(r["score"] for r in results) / len(results), 1)
    summary = {
        "generated_by": "tools/quality/runbook_validator.py",
        "runbook_count": len(results),
        "passed": sum(1 for r in results if r["passed"]),
        "failed": hard_fail,
        "warnings": warn_total,
        "mean_score": mean,
        "mean_band": band(round(mean)),
        "runbooks": results,
    }
    out_path = REPO_ROOT / args.json
    write_json(out_path, summary)

    print()
    print(bold(f"Mean completeness score: {mean}/100 ({band(round(mean))})"))
    print(bold(f"Report written to {out_path.relative_to(REPO_ROOT)}"))
    if hard_fail:
        print(red(bold(f"{hard_fail} runbook(s) failed validation.")))
        return 1
    if args.strict and warn_total:
        print(yellow(bold(f"{warn_total} warning(s) in strict mode.")))
        return 1
    print(green(bold("All runbooks passed validation.")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
