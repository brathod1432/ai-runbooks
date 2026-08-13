# Automation & Tooling

Lightweight, standard-library-only Python tooling that enforces the repository's
quality bar. No third-party Python packages are required (Python 3.10+).

## Scripts

| Script | Purpose | Fails build? |
|--------|---------|--------------|
| `validate_structure.py` | Ensures required directories and governance files exist | Yes |
| `validate_runbooks.py` | Validates front matter, sections, word count, diagrams, placeholders | Yes |
| `check_links.py` | Checks relative Markdown links and images resolve | Yes |
| `doc_coverage.py` | Reports per-section, per-category documentation coverage | Optional (`--min`) |
| `score_repository.py` | Scores runbooks against the QA rubric (/100) | Optional (`--min`) |
| `run_all_checks.py` | Runs everything above and summarizes | Yes |
| `common.py` | Shared helpers (parsing, constants) — not run directly | — |

## Usage

```bash
# Run the whole suite (what CI runs, minus markdown lint)
python scripts/run_all_checks.py

# Individual checks
python scripts/validate_structure.py
python scripts/validate_runbooks.py
python scripts/check_links.py
python scripts/doc_coverage.py --min 95
python scripts/score_repository.py --min 80

# Markdown lint (Node-based, run via npx)
npx --yes markdownlint-cli2 "**/*.md"
```

## Exit codes

- `0` — success.
- `1` — a required check failed (structure, runbook spec, or broken links), or an
  optional check fell below a `--min` threshold you supplied.

## Design principles

- **Zero heavy dependencies** so it runs in any CI with Python.
- **Deterministic** and fast; safe to run on every commit.
- **Informative** output with a clear PASS/FAIL summary.
- The mechanical scoring mirrors [`docs/QUALITY_ASSURANCE.md`](../docs/QUALITY_ASSURANCE.md);
  qualitative judgement remains with human reviewers.
