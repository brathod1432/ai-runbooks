# Future Runbook Roadmap

This document catalogs the planned expansion of the runbook library across
high-value themes. It complements [`docs/planning/ROADMAP.md`](./planning/ROADMAP.md)
(which tracks *project* milestones) by enumerating the *content* pipeline. Each
entry lists the proposed runbook, its intended category, and the operational
value it delivers.

Status legend: 🔜 planned · 🧭 scoping · 🧪 drafting.

## Theme index

- [AI Security](#ai-security)
- [MCP Ecosystem](#mcp-ecosystem)
- [AIOps](#aiops)
- [Agent Governance](#agent-governance)
- [Agent Safety](#agent-safety)
- [FinOps](#finops)
- [Data Engineering](#data-engineering)
- [Platform Engineering](#platform-engineering)
- [Cloud Architecture Reviews](#cloud-architecture-reviews)
- [DevSecOps](#devsecops)
- [Incident Response](#incident-response)
- [SOC Automation](#soc-automation)
- [Threat Modeling](#threat-modeling)
- [Threat Hunting](#threat-hunting)
- [Compliance Automation](#compliance-automation)

---

## AI Security

Extends `runbooks/security/ai-system-security-review` and `model-risk-assessment`.

| Runbook | Category | Value | Status |
|---------|----------|-------|:------:|
| `llm-prompt-injection-defense-review` | security | Assess and harden against direct/indirect prompt injection | 🔜 |
| `model-supply-chain-audit` | security | Verify model/weight provenance, signing, and integrity | 🔜 |
| `ai-data-leakage-assessment` | security | Detect PII/secret exposure via training data and outputs | 🧭 |
| `agent-tool-permission-audit` | security | Minimize and review tool/action scopes granted to agents | 🔜 |

## MCP Ecosystem

Extends `runbooks/ai-ml/mcp-server-diagnostics`.

| Runbook | Category | Value | Status |
|---------|----------|-------|:------:|
| `mcp-tool-security-review` | security | Threat-model MCP tools; validate auth, scopes, input handling | 🔜 |
| `mcp-registry-hygiene` | ai-ml | Audit installed MCP servers for trust, versions, and drift | 🧭 |
| `mcp-latency-and-reliability-review` | ai-ml | SLOs for MCP transports (stdio/SSE/HTTP) | 🔜 |

## AIOps

| Runbook | Category | Value | Status |
|---------|----------|-------|:------:|
| `anomaly-triage` | reliability | Standardize agent-driven anomaly investigation | 🔜 |
| `automated-remediation-guardrails` | reliability | Safe auto-remediation with rollback + blast-radius limits | 🧭 |
| `alert-correlation-review` | observability | Reduce alert noise via correlation and dedup | 🔜 |

## Agent Governance

Extends [`ENTERPRISE_GUIDE.md`](../ENTERPRISE_GUIDE.md).

| Runbook | Category | Value | Status |
|---------|----------|-------|:------:|
| `agent-access-review` | security | Periodic review of agent identities and privileges | 🔜 |
| `action-approval-policy-audit` | security | Verify R2/R3 gating is enforced and logged | 🔜 |
| `agent-audit-log-integrity-review` | security | Validate completeness/immutability of audit trails | 🧭 |

## Agent Safety

| Runbook | Category | Value | Status |
|---------|----------|-------|:------:|
| `agent-red-team-exercise` | security | Structured adversarial testing of agent behavior | 🔜 |
| `agent-sandbox-review` | security | Verify isolation, egress controls, and blast radius | 🔜 |
| `tool-permission-minimization` | security | Drive toward least privilege for agent tools | 🧭 |

## FinOps

Extends the `cloud-cost` runbooks.

| Runbook | Category | Value | Status |
|---------|----------|-------|:------:|
| `commitment-planning-review` | cloud-cost | Optimize RIs/SPs/CUDs against forecasted demand | 🔜 |
| `unit-economics-review` | cloud-cost | Cost per request/tenant/feature analysis | 🧭 |
| `kubernetes-cost-allocation-review` | cloud-cost | Namespace/team chargeback and rightsizing | 🔜 |

## Data Engineering

New `runbooks/data/` category.

| Runbook | Category | Value | Status |
|---------|----------|-------|:------:|
| `data-pipeline-reliability-review` | data | SLAs, backfills, idempotency, and failure handling | 🔜 |
| `data-quality-audit` | data | Freshness, completeness, validity, and lineage checks | 🔜 |
| `schema-evolution-review` | data | Safe schema changes with contracts and compatibility | 🧭 |

## Platform Engineering

Extends `runbooks/architecture/platform-engineering-review`.

| Runbook | Category | Value | Status |
|---------|----------|-------|:------:|
| `golden-path-audit` | architecture | Assess paved-road coverage and adoption | 🔜 |
| `idp-reliability-review` | architecture | Reliability of the internal developer platform itself | 🧭 |
| `developer-experience-metrics-review` | architecture | DORA + SPACE instrumentation review | 🔜 |

## Cloud Architecture Reviews

| Runbook | Category | Value | Status |
|---------|----------|-------|:------:|
| `multi-region-resilience-review` | architecture | Failover, data replication, and RTO/RPO across regions | 🔜 |
| `landing-zone-review` | architecture | Account/org structure, guardrails, and baseline controls | 🧭 |
| `well-architected-review` | architecture | Structured pillar-based review (all clouds) | 🔜 |

## DevSecOps

| Runbook | Category | Value | Status |
|---------|----------|-------|:------:|
| `supply-chain-slsa-review` | security | Provenance, signing, and SLSA-level assessment | 🔜 |
| `secrets-management-audit` | security | Detect hardcoded secrets; verify vault usage/rotation | 🔜 |
| `sast-dast-coverage-review` | security | Assess scanning coverage and triage discipline | 🧭 |

## Incident Response

Extends `runbooks/reliability/incident-postmortem`.

| Runbook | Category | Value | Status |
|---------|----------|-------|:------:|
| `sev1-incident-command` | reliability | Agent-assisted incident command and coordination | 🔜 |
| `incident-comms-and-status-page` | reliability | Consistent stakeholder comms and status updates | 🔜 |
| `error-budget-policy-review` | reliability | Enforce and review error-budget policy | 🧭 |

## SOC Automation

New `runbooks/soc/` category.

| Runbook | Category | Value | Status |
|---------|----------|-------|:------:|
| `alert-triage-automation` | soc | Standardized enrichment and triage of SIEM alerts | 🔜 |
| `detection-tuning-review` | soc | Reduce false positives; improve detection efficacy | 🔜 |
| `phishing-report-triage` | soc | Consistent handling of reported phishing | 🧭 |

## Threat Modeling

| Runbook | Category | Value | Status |
|---------|----------|-------|:------:|
| `stride-threat-model-facilitation` | security | Agent-facilitated STRIDE workshop and output | 🔜 |
| `trust-boundary-review` | security | Identify and validate trust boundaries in a design | 🔜 |
| `attack-surface-mapping` | security | Enumerate and prioritize external attack surface | 🧭 |

## Threat Hunting

| Runbook | Category | Value | Status |
|---------|----------|-------|:------:|
| `hypothesis-driven-hunt` | soc | Structured, hypothesis-led threat hunt | 🔜 |
| `ioc-sweep` | soc | Systematic indicator-of-compromise sweep | 🔜 |
| `lateral-movement-hunt` | soc | Detect lateral movement patterns | 🧭 |

## Compliance Automation

| Runbook | Category | Value | Status |
|---------|----------|-------|:------:|
| `control-evidence-collection` | security | Automate collection of audit evidence | 🔜 |
| `compliance-drift-detection` | security | Detect drift from a compliant baseline | 🔜 |
| `access-recertification-review` | security | Periodic least-privilege recertification | 🧭 |

---

## Prioritization

New runbooks are prioritized by the same criteria as the project roadmap:
impact, risk reduction, reusability, and community demand. To propose or reorder
an item, open an issue with the `roadmap` label (see
[CONTRIBUTING](../CONTRIBUTING.md)).
