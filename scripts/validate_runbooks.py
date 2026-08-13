#!/usr/bin/env python3
"""Validate every runbook against the awesome-ai-runbooks specification.

Checks, per runbook:
  * valid YAML front matter with all required keys
  * `id` matches the filename
  * exactly one H1 title
  * all required H2 sections present, in the canonical order
  * >= MIN_WORDS words of prose
  * >= MIN_MERMAID_DIAGRAMS mermaid diagrams
  * no obvious placeholders (TODO / FIXME / lorem ipsum)

Exit code 0 on success, 1 if any runbook fails.
"""

from __future__ import annotations

import sys

from common import (
    MIN_MERMAID_DIAGRAMS,
    MIN_WORDS,
    REQUIRED_FRONT_MATTER_KEYS,
    REQUIRED_SECTIONS,
    RunbookDoc,
    bold,
    green,
    iter_runbooks,
    red,
    yellow,
)

PLACEHOLDER_TOKENS = ("TODO", "FIXME", "lorem ipsum", "XXX", "PLACEHOLDER")


def validate(doc: RunbookDoc) -> list[str]:
    errors: list[str] = []

    # Front matter.
    if not doc.front_matter:
        errors.append("missing or unparseable YAML front matter")
    else:
        for key in REQUIRED_FRONT_MATTER_KEYS:
            if key not in doc.front_matter or not doc.front_matter[key].strip():
                errors.append(f"front matter missing key: {key}")
        expected_id = doc.path.stem
        if doc.front_matter.get("id") and doc.front_matter["id"] != expected_id:
            errors.append(
                f"front matter id '{doc.front_matter['id']}' != filename '{expected_id}'"
            )

    # Exactly one H1 (ignore '#' comments inside fenced code blocks).
    import re as _re

    from common import H1_RE

    text_no_fences = _re.sub(r"```.*?```", "", doc.text, flags=_re.DOTALL)
    h1s = H1_RE.findall(text_no_fences)
    if len(h1s) != 1:
        errors.append(f"expected exactly 1 H1 title, found {len(h1s)}")

    # Sections present and ordered.
    present = doc.sections
    missing = [s for s in REQUIRED_SECTIONS if s not in present]
    if missing:
        errors.append("missing sections: " + ", ".join(missing))
    else:
        # Order check: required sections should appear in canonical relative order.
        indices = [present.index(s) for s in REQUIRED_SECTIONS]
        if indices != sorted(indices):
            errors.append("required sections are out of canonical order")

    # Word count.
    wc = doc.word_count()
    if wc < MIN_WORDS:
        errors.append(f"only {wc} words (< {MIN_WORDS})")

    # Diagrams.
    md = doc.mermaid_count()
    if md < MIN_MERMAID_DIAGRAMS:
        errors.append(f"only {md} mermaid diagram(s) (< {MIN_MERMAID_DIAGRAMS})")

    # Placeholders.
    lowered = doc.text.lower()
    for token in PLACEHOLDER_TOKENS:
        if token.lower() in lowered:
            errors.append(f"contains placeholder token: {token}")

    return errors


def main() -> int:
    docs = iter_runbooks()
    if not docs:
        print(yellow("No runbooks found under runbooks/. Nothing to validate."))
        return 0

    failures = 0
    print(bold(f"Validating {len(docs)} runbook(s)...\n"))
    for doc in docs:
        errors = validate(doc)
        if errors:
            failures += 1
            print(red(f"FAIL  {doc.rel}"))
            for e in errors:
                print(f"        - {e}")
        else:
            print(green(f"PASS  {doc.rel}") + f"  ({doc.word_count()} words, {doc.mermaid_count()} diagrams)")

    print()
    if failures:
        print(red(bold(f"{failures} of {len(docs)} runbook(s) failed validation.")))
        return 1
    print(green(bold(f"All {len(docs)} runbook(s) passed validation.")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
