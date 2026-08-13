# Roadmap — awesome-ai-runbooks

This roadmap describes the phased evolution of the project. Dates are indicative;
the project is milestone-driven, not date-driven. Status legend: ✅ done ·
🚧 in progress · 🔜 planned.

## Milestone 0 — Foundation (v0.1) ✅

- ✅ Repository architecture and governance (LICENSE, CoC, CONTRIBUTING, SECURITY)
- ✅ Runbook specification (`templates/runbook-template.md`)
- ✅ Report specification (`templates/report-template.md`)
- ✅ AI agent execution standards (`docs/AI_AGENT_STANDARDS.md`)
- ✅ Planning docs (vision, scope, audience, competitive analysis, this roadmap)

## Milestone 1 — Core runbook library (v1.0) ✅

- ✅ 48+ production-grade runbooks across reliability, observability, databases,
  messaging, security, kubernetes, cloud-cost, migrations, architecture, CI/CD,
  and AI/ML.
- ✅ Prompt library (`prompts/`) with 9 agent personas.
- ✅ Quality assurance & maturity framework (`docs/QUALITY_ASSURANCE.md`).
- ✅ Automation: validators, scorers, CI workflows.
- ✅ Enterprise adoption guide (`ENTERPRISE_GUIDE.md`).
- ✅ World-class README with architecture diagrams.

## Milestone 2 — Adoption & ergonomics (v1.1) 🚧

- 🚧 Runbook index/catalog generation (auto-built from front matter).
- 🔜 Per-runbook "quick copy" agent-ready bundles (runbook + persona + report).
- 🔜 JSON Schema for runbook front matter + schema-based validation.
- 🔜 VS Code snippet pack and `gh` extension for scaffolding new runbooks.
- 🔜 Localization guidelines.

## Milestone 3 — Ecosystem integration (v1.2) 🔜

- 🔜 MCP server reference that serves runbooks to agents as tools/resources.
- 🔜 Adapters/examples for Devin, Claude Code, Copilot Agent, Cursor, OpenHands,
  AutoGen, CrewAI, LangGraph.
- 🔜 Example CI recipes that invoke agents against runbooks in dry-run mode.

## Milestone 4 — Evaluation & trust (v1.3) 🔜

- 🔜 Agent evaluation harness aligned with `agent-evaluation-framework` runbook.
- 🔜 Golden-trajectory fixtures for regression-testing agent behavior.
- 🔜 Public maturity scorecard badge generated in CI.

## Milestone 5 — Governance at scale (v2.0) 🔜

- 🔜 Private/enterprise overlay pattern (fork + private runbook packs).
- 🔜 Approval-workflow reference implementations (human-in-the-loop).
- 🔜 Audit-log schema and retention guidance.
- 🔜 Compliance mapping packs (SOC 2, ISO 27001, NIST, PCI where relevant).

## Themed runbook expansion (rolling)

See [`docs/planning`](.) and the README "Future Direction" section. High-level
themes queued for new runbooks:

| Theme | Sample upcoming runbooks |
|-------|--------------------------|
| AI Security | model supply-chain audit, agent sandbox review |
| MCP Ecosystem | MCP tool security review, MCP registry hygiene |
| AIOps | anomaly triage, automated remediation guardrails |
| Agent Governance | agent access review, action-approval policy audit |
| Agent Safety | prompt-injection red-team, tool-permission minimization |
| FinOps | commitment planning, unit-economics review |
| Data Engineering | pipeline reliability, data-quality audit, schema evolution |
| Platform Engineering | golden-path audit, IDP reliability review |
| Cloud Architecture | multi-region resilience, landing-zone review |
| DevSecOps | supply-chain (SLSA) review, secrets-management audit |
| Incident Response | SEV1 command runbook, comms & status-page runbook |
| SOC Automation | alert triage, detection-tuning review |
| Threat Modeling | STRIDE workshop facilitation, trust-boundary review |
| Threat Hunting | hypothesis-driven hunt, IOC sweep |
| Compliance Automation | control-evidence collection, drift detection |

## How priorities are set

1. **Impact** — how many personas/scenarios a runbook unblocks.
2. **Risk reduction** — does it prevent costly incidents or breaches?
3. **Reusability** — does it establish patterns others build on?
4. **Community demand** — issues and 👍 reactions.

## Contributing to the roadmap

Open an issue with the `roadmap` label to propose additions or reprioritization.
Accepted changes are reflected here and in `CHANGELOG.md`.
