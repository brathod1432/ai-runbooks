# Competitive & Ecosystem Analysis — awesome-ai-runbooks

This analysis maps the existing landscape of runbooks, playbooks, SOP systems,
and AI operational workflows, then positions this project against them. The goal
is to learn from proven systems and identify the gap we uniquely fill.

## 1. Existing runbook & SRE ecosystems

### Google SRE (SRE Book / Workbook)

- **What it is:** The foundational discipline of reliability engineering: SLIs,
  SLOs, error budgets, toil reduction, blameless postmortems.
- **Strengths:** Rigorous, battle-tested, principle-driven.
- **Gap for agents:** Written for humans; not structured for machine execution
  or agent reasoning. No per-procedure machine-checkable contract.
- **What we borrow:** SLO/error-budget thinking, blameless postmortem culture,
  evidence-first investigation.

### PagerDuty Incident Response & Runbook practices

- **What it is:** Operational incident-response process, severity models, and
  runbook automation (PagerDuty Rundeck / Process Automation).
- **Strengths:** Strong on roles, severity, comms, and automation of routine
  operational actions.
- **Gap for agents:** Automation is deterministic scripting, not reasoning
  agents; runbooks aren't standardized for LLM agents' plan/act/validate loop.
- **What we borrow:** Severity mapping, escalation discipline, comms structure.

### Atlassian / Opsgenie & GitLab/Microsoft runbook docs

- **What it is:** Incident management processes and runbook templates.
- **Strengths:** Good templates and lifecycle guidance.
- **Gap for agents:** Human-oriented prose; no agent persona, decision trees, or
  rollback contracts tuned for autonomous execution.

### "awesome-*" lists and runbook template repos

- **What they are:** Curated link lists and generic markdown runbook templates.
- **Strengths:** Discoverability; low barrier.
- **Gap:** Shallow — links without depth, or templates without real content,
  standards, scoring, or agent-specific structure.

## 2. Cloud & architecture governance frameworks

### AWS Well-Architected Framework (and Azure/GCP equivalents)

- **What it is:** Pillars (operational excellence, security, reliability,
  performance, cost, sustainability) with review questions.
- **Strengths:** Comprehensive, authoritative, review-driven.
- **Gap for agents:** Assessment questionnaire for humans/consultants; not an
  executable procedure an agent follows step-by-step with validation.
- **What we borrow:** Pillar thinking, structured review, prioritized findings.

### CIS Benchmarks, NIST frameworks, OWASP Top 10 families

- **What they are:** Security baselines and control catalogs.
- **Strengths:** Authoritative controls and mappings.
- **Gap for agents:** Controls, not procedures — they tell you *what* to check,
  not *how an agent should investigate, decide, validate, and report*.
- **What we borrow:** Control mappings referenced directly in security runbooks.

## 3. Incident response & engineering SOP systems

- **Blameless postmortem templates** (Google, Etsy, PagerDuty): excellent
  culture and structure; not agent-native.
- **Enterprise Confluence/Notion SOP wikis:** organization-specific, unversioned
  prose, quality varies wildly, no automated conformance.

## 4. AI operational workflows & agent patterns

### Prompt libraries and "awesome-prompts"

- **Strengths:** Breadth of examples.
- **Gap:** One-shot prompts, not operational procedures with planning,
  validation, rollback, escalation, and reporting contracts.

### Agent framework docs (LangGraph, AutoGen, CrewAI, OpenHands)

- **Strengths:** Show *how to build* agents and orchestrate tools.
- **Gap:** Framework-specific; they don't provide vendor-neutral *what the agent
  should do* SOPs for real engineering domains.

### Vendor agent guidance (OpenAI, Anthropic, GitHub, Cognition/Devin)

- **Strengths:** Best practices for prompting and safe tool use.
- **Gap:** Tied to a single platform; not a shared, cross-vendor operational
  standard.

### Emerging agent patterns

- ReAct (reason+act), Plan-and-Execute, Reflexion/self-critique, tool-use with
  MCP, human-in-the-loop gating, evaluator-optimizer loops.
- **What we borrow:** These patterns are encoded directly into the runbook
  sections (Planning Instructions, Investigation Workflow, Analysis Framework,
  Validation Steps) and in `docs/AI_AGENT_STANDARDS.md`.

## 5. Feature comparison

| Capability | Google SRE | AWS WAF | PagerDuty | Prompt libraries | Agent frameworks | **awesome-ai-runbooks** |
|-----------|:---------:|:-------:|:---------:|:----------------:|:----------------:|:-----------------------:|
| Vendor-neutral | ✅ | ⚠️ AWS | ⚠️ | ⚠️ | ❌ | ✅ |
| Agent-native structure | ❌ | ❌ | ⚠️ | ⚠️ | ✅ | ✅ |
| Executable step-by-step procedure | ⚠️ | ❌ | ✅ (scripts) | ❌ | ✅ | ✅ |
| Evidence-first reasoning | ✅ | ⚠️ | ⚠️ | ❌ | ⚠️ | ✅ |
| Rollback & escalation contracts | ⚠️ | ❌ | ✅ | ❌ | ⚠️ | ✅ |
| Standard report output | ⚠️ | ⚠️ | ✅ | ❌ | ❌ | ✅ |
| Machine-checkable conformance | ❌ | ❌ | ⚠️ | ❌ | ❌ | ✅ |
| Depth of real content | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ |
| Cross-domain breadth | ⚠️ | ✅ | ⚠️ | ✅ | ⚠️ | ✅ |
| Open source / forkable | ⚠️ | ❌ | ❌ | ✅ | ✅ | ✅ |

Legend: ✅ strong · ⚠️ partial · ❌ absent.

## 6. The gap we uniquely fill

Every existing system is either (a) human-oriented and not structured for agent
execution, (b) a control/questionnaire rather than a procedure, or (c)
framework/vendor-specific. **None provides a vendor-neutral, machine-checkable,
evidence-first, cross-domain library of operational procedures designed
specifically for how autonomous AI agents plan, act, validate, and report.**

That is our category: **agent-native operational runbooks.**

## 7. Positioning statement

> awesome-ai-runbooks is to AI agents what the SRE Book and the Well-Architected
> Framework are to human engineers — an open, rigorous, cross-vendor operational
> standard, purpose-built for autonomous execution.

## 8. Risks & how we counter them

| Risk | Counter |
|------|---------|
| "Just another prompt list" perception | Enforced spec + scoring + CI + depth |
| Vendor fragmentation | Cross-platform `supported_agents` contract |
| Content rot | Versioning, `last_reviewed`, roadmap cadence |
| Trust barrier for enterprises | Governance, HITL gates, audit patterns |
| Contributor quality variance | Template + validation + review checklist |
