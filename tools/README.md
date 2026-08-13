# Platform Tooling

The `tools/` package is the automation and quality backbone of
awesome-ai-runbooks. Everything shares one library, `runbook_lib.py`, so
parsing, scoring, and metadata semantics stay consistent across the platform.

## Quick start

```bash
pip install -r requirements-dev.txt      # PyYAML, jsonschema, pytest (optional but recommended)
python tools/run_platform.py             # run the whole toolchain, regenerate artifacts
python tools/run_platform.py --check     # CI mode: fail on any required error
```

## Tool index

| Tool | Phase | Purpose | Output |
|------|:-----:|---------|--------|
| `runbook_lib.py` | — | Shared parsing/model library (single source of truth) | — |
| `metadata_enrich.py` | 15 | Add/verify extended metadata on every runbook | in-place |
| `quality/runbook_validator.py` | 13 | Sections, schema, content, diagrams, examples + score | `quality/quality-score.json` |
| `quality/runbook_quality_engine.py` | 13 | 5-dimension quality scoring | `quality/quality-dimensions.json` |
| `health/repository_health.py` | 13 | Coverage, docs, automation, structure, maintainability | `quality/repository-health.json` |
| `maturity_engine.py` | 26 | Evidence-based maturity level (L1–L5) | `quality/maturity.json` |
| `search/build_index.py` | 16 | Search index + taxonomy | `catalog/runbook-index.json`, `catalog/taxonomy.json` |
| `search/search_runbooks.py` | 16 | Query the index (keyword + filters) | stdout / `--json` |
| `recommendation_engine.py` | 28 | Related / follow-up / dependency recommendations + graph | `catalog/runbook-graph.json` |
| `content_audit.py` | 29 | Missing examples/validation, thin sections, duplicates, obsolete refs | `quality/content-audit.json` |
| `../metrics/repository_metrics.py` | 25 | Repository analytics | `metrics/repository-metrics.json`, `metrics/DASHBOARD.md` |
| `security/secret_scanner.py` | 23 | Defensive secret scanning | `security/secret-scan.json` |
| `security/dependency_scanner.py` | 23 | Supply-chain hygiene | `security/dependency-scan.json` |
| `security/security_score.py` | 23 | Security maturity score | `security/security-score.json` |
| `runbook_generator/generate_runbook.py` | 14 | Generate a runbook from YAML config | `runbooks/<cat>/<id>.md` |
| `runbook_generator/runbook_scaffolder.py` | 14 | Category READMEs, example stubs | READMEs / examples |
| `release/release_manager.py` | 30 | Semver, release notes, changelog | stdout |
| `badges.py` | 19 | shields.io endpoint badges | `.github/badges/*.json` |
| `run_platform.py` | — | Orchestrate the entire toolchain | all of the above |

## Design principles

- **Zero required third-party deps** for the core: `runbook_lib.py` runs on the
  stdlib. PyYAML and jsonschema are used when installed for robustness; a
  fallback parser keeps everything working without them.
- **Deterministic & fast** — safe to run on every commit; used by CI.
- **Single source of truth** — required sections, metadata keys, agent list,
  and maturity mapping live in `runbook_lib.py` only.
- **Artifacts are reproducible** — `run_platform.py` regenerates every JSON
  report and badge from the runbooks themselves.

## Examples

```bash
# Search
python tools/search/search_runbooks.py kafka lag
python tools/search/search_runbooks.py --category security --agent devin

# Recommend
python tools/recommendation_engine.py incident-postmortem

# Generate a new runbook
cp templates/runbook-config.yaml my.yaml   # edit it
python tools/runbook_generator/generate_runbook.py --config my.yaml

# Plan a release
python tools/release/release_manager.py --plan
```
