# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- MCP reference server that serves runbooks to agents.
- Agent evaluation harness with golden trajectories.
- OpenSSF Scorecard automation and public maturity badge.

## [1.1.0] - 2026-08-13

### Added — Engineering platform (Phase 2)

- **Metadata system:** JSON Schema (`schemas/runbook.schema.json`) and extended
  front-matter (difficulty, domain, platform, agent_type, author, reviewers,
  required_tools, compliance_tags, status, maturity_level) on all 48 runbooks,
  applied idempotently by `tools/metadata_enrich.py`.
- **Quality & health tooling:** `runbook_validator.py` (schema + structure +
  content, writes `quality/quality-score.json`), `runbook_quality_engine.py`
  (5-dimension scoring), `repository_health.py` (coverage/docs/automation/
  structure/maintainability), and `maturity_engine.py` (L1–L5 maturity model).
- **Search & knowledge graph:** `tools/search/` build_index + search with
  keyword/tag/difficulty/domain/platform/agent filters, `catalog/taxonomy.json`,
  and `recommendation_engine.py` producing `catalog/runbook-graph.json`.
- **Analytics:** `metrics/repository_metrics.py` + `metrics/DASHBOARD.md`.
- **Security framework:** threat model, review process, guidelines, plus
  `secret_scanner.py`, `dependency_scanner.py`, and `security_score.py`.
- **Generation:** `runbook_generator/` generate + scaffold, `runbook-config.yaml`.
- **Release system:** `release/release_manager.py` (semver + notes + changelog).
- **Badges:** `tools/badges.py` shields.io endpoints in `.github/badges/`.
- **Testing:** 1016-test `pytest` suite under `tests/`.
- **CI:** 10 workflows (lint, links, validation, score, security, stale,
  dependency-review, docs, scheduled-audit, release).
- **Docs portal:** MkDocs Material (`mkdocs.yml`, `docs/` pages, 10 integration
  guides, knowledge-graph and agent-lifecycle docs).
- **Governance & agent framework:** `governance/` lifecycle/approval/review/
  audit/change-management/agent-governance and `agent-framework/` design specs.
- **Contributor experience:** issue forms, richer PR template, CODEOWNERS,
  `REVIEW_GUIDE.md`, `MAINTAINERS.md`, discussion guidelines.
- **Reports:** enterprise readiness, repository audit, open-source maturity,
  enterprise adoption guide, and GitHub growth strategy.

### Changed

- README refreshed with platform capabilities, live-badge references, and
  updated metrics.

## [1.0.0] - 2026-08-13

### Added

- **Governance & foundation:** `LICENSE` (MIT), `CODE_OF_CONDUCT.md`,
  `CONTRIBUTING.md`, `SECURITY.md`, and this changelog.
- **Planning suite** in `docs/planning/`: `VISION.md`, `PROJECT_SCOPE.md`,
  `TARGET_AUDIENCE.md`, `ROADMAP.md`, `COMPETITIVE_ANALYSIS.md`.
- **Runbook specification** (`templates/runbook-template.md`) and
  **report specification** (`templates/report-template.md`).
- **AI Agent Execution Standards** (`docs/AI_AGENT_STANDARDS.md`) covering
  behavior, planning, reasoning, investigation, validation, reporting, quality,
  risk, escalation, bias reduction, decision-making, and autonomy frameworks.
- **Quality Assurance framework** (`docs/QUALITY_ASSURANCE.md`) with
  completeness scoring, agent-readiness scoring, risk scoring, and a repository
  maturity model.
- **Core runbook library:** 48+ production-grade runbooks across reliability,
  observability, databases, messaging, security, kubernetes, cloud-cost,
  migrations, architecture, CI/CD, and AI/ML domains.
- **Prompt library** (`prompts/`) with 9 agent persona prompts.
- **Enterprise adoption guide** (`ENTERPRISE_GUIDE.md`).
- **Automation** (`scripts/`): runbook validation, structure validation,
  repository scoring, link checking, documentation coverage, markdown lint
  config, and an aggregate check runner.
- **CI** (`.github/workflows/`): markdown lint, link check, structure and
  runbook validation, and repository quality scoring on every push and PR.
- **World-class README** with architecture and workflow Mermaid diagrams.

[Unreleased]: https://github.com/awesome-ai-runbooks/awesome-ai-runbooks/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/awesome-ai-runbooks/awesome-ai-runbooks/releases/tag/v1.0.0
