---
report_type: agent-execution-report
runbook_id: <runbook-id>
agent: <devin | claude-code | ... >
run_id: <unique-run-id>
started_at: <ISO-8601>
completed_at: <ISO-8601>
environment: <prod | staging | dev>
risk_level: <low | medium | high | critical>
priority: <P0 | P1 | P2 | P3>
status: <complete | partial | escalated>
human_reviewer: <name-or-pending>
---

<!--
  awesome-ai-runbooks :: Agent Report Template
  The standard deliverable format produced by an AI agent at the end of a
  runbook execution. Keep headings stable; they are consumed by reviewers and
  by scripts/score_repository.py for reporting-quality checks.
-->

# Agent Execution Report — <Runbook Title>

## Executive Summary

Three to five sentences a busy executive or on-call lead can read in 30 seconds.
State what was investigated, the headline finding, the business impact, and the
single most important recommended action.

## Environment

| Attribute | Value |
|-----------|-------|
| Service / System | |
| Environment | prod / staging / dev |
| Region(s) | |
| Time window analyzed | |
| Agent & version | |
| Runbook & version | |

## Observations

Objective, factual signals gathered during execution — no interpretation yet.
Timestamps, metric values, log excerpts, config states.

## Findings

Interpreted conclusions drawn from the observations. Each finding should link
back to specific evidence. Number them for cross-reference.

1. **F1 — <short title>.** Description.
2. **F2 — <short title>.** Description.

## Evidence

Concrete proof for each finding. Include command output, metric snapshots,
queries, and diagrams. Redact secrets.

```text
<evidence excerpt>
```

## Impact

Quantify the business and technical impact: users affected, error budget burned,
dollars, latency, risk exposure, compliance implications.

## Recommendations

| ID | Recommendation | Rationale | Effort | Risk if ignored |
|----|----------------|-----------|--------|-----------------|
| R1 | | | S/M/L | |

## Risk Level

State the overall risk level (low / medium / high / critical) with a one-line
justification and the primary risk driver.

## Priority

State the overall priority (P0–P3) and the SLA implied by that priority.

## Action Plan

Ordered, assignable next steps with owners and suggested timelines.

- [ ] **Now (P0/P1):** ...
- [ ] **This week:** ...
- [ ] **This quarter:** ...

## Validation Results

Evidence that the actions taken (if any) achieved the intended effect without
regression. Include before/after metrics.

| Check | Expected | Actual | Pass? |
|-------|----------|--------|-------|
| | | | ✅ / ❌ |

## Appendix

Supporting material: full command logs, extended queries, raw data, alternative
hypotheses considered and rejected, and references consulted.
