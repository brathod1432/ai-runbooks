# Runbook Approval Process

Approval is the control that moves a runbook from a reviewed proposal into a
**production-eligible** artifact and, separately, promotes it up the autonomy
ladder. This document defines who approves, the criteria they apply, how
sign-off is recorded, and how autonomy-stage promotion works. It builds on the
[review process](./review-process.md), the
[lifecycle](./runbook-lifecycle.md), and the risk framework in
[`../docs/AI_AGENT_STANDARDS.md`](../docs/AI_AGENT_STANDARDS.md#8-risk-framework).

## Two distinct approvals

Do not conflate these — they answer different questions:

1. **Content approval.** Is this runbook correct, safe, and complete enough to be
   `Approved` (production status)? Granted per PR.
2. **Autonomy-stage promotion.** How much may an agent do *unattended* when
   executing this runbook? Granted per runbook after an observation window.

## Who approves

| Decision | Approver | Quorum |
|----------|----------|--------|
| Content approval — standard runbook | 1 maintainer (technical reviewer) | 1 |
| Content approval — `security/` or `risk_level: high\|critical` | technical + security reviewer | 2 (four-eyes) |
| Autonomy-stage promotion (Stage 0→1→2) | Runbook owner + one board member | 2 |
| Autonomy-stage promotion (Stage 3→4) | Agent Operations Review Board | Board quorum |
| Emergency deprecation | Any board member or security on-call | 1 (ratified later) |

Approvers must be distinct from the author (no self-approval). CODEOWNERS
enforces reviewer routing mechanically — see
[change-management.md](./change-management.md).

## Content approval criteria

An approver signs off only when **all** hold (aligned with
[`../docs/QUALITY_ASSURANCE.md`](../docs/QUALITY_ASSURANCE.md#5-acceptance-criteria)):

- [ ] Automated checks pass: structure, front matter, lint, links, scoring.
- [ ] Completeness score ≥ 75; agent-readiness score ≥ 42.
- [ ] `risk_level` and `human_in_the_loop` are consistent with the action set.
- [ ] Least-privilege `required_access`; every mutating step has a rollback.
- [ ] Escalation triggers and routing are precise and realistic.
- [ ] No placeholders, no `TODO`, no fabricated tools or APIs.
- [ ] Example execution is realistic and uses the report template.
- [ ] Second (security) review completed where required.

Approval is recorded as a PR review approval plus a signed merge commit. The
merge event, approver identity, and commit SHA become the immutable record of
content approval (see [audit-framework.md](./audit-framework.md)).

## Approval flow

```mermaid
flowchart TD
    PR[PR opened by author] --> CI{Automated checks pass?}
    CI -->|No| FIX[Return to author]
    CI -->|Yes| TR[Technical review]
    TR -->|changes| FIX
    TR -->|ok| RISK{security/ or high\|critical?}
    RISK -->|Yes| SR[Security second review]
    RISK -->|No| SIGN[Maintainer sign-off]
    SR -->|changes| FIX
    SR -->|ok| SIGN
    SIGN --> MERGE[Merge + changelog + status: Approved]
    MERGE --> CAT[Enter catalog at Stage 0]
```

New runbooks always enter the catalog at **Stage 0 (read-only, advisory)**
regardless of content approval. Higher autonomy is earned separately.

## Autonomy-stage promotion

The autonomy stages mirror [`../ENTERPRISE_GUIDE.md`](../ENTERPRISE_GUIDE.md#1-adoption-model).
Promotion is a governed decision, not an author choice.

| From → To | Gate criteria |
|-----------|---------------|
| Stage 0 → 1 (gated actions) | ≥ 10 clean advisory runs; findings accuracy verified; owner requests |
| Stage 1 → 2 (bounded autonomy) | Zero unsafe-action attempts over the window; rollbacks proven; board member co-signs |
| Stage 2 → 3 (supervised) | Guardrail metrics green for ≥ 30 days; drift monitoring live; sampled review passes |
| Stage 3 → 4 (managed) | Policy-as-code enforced; exception-only review sustained; full board approval |

Every promotion requires:

1. A **promotion request** citing the observation window and metrics.
2. Evidence pulled from the audit log (run outcomes, escalations, blocked
   actions).
3. A named approver (or board quorum) recorded against the runbook.
4. A **demotion trigger** defined up front (e.g. any unsafe action, any SEV
   caused, or drift alert) that automatically returns the runbook to a lower
   stage pending re-review.

Promotions expire if the runbook enters `In-Review` for a material change; the
runbook re-enters at the stage appropriate to the change's risk class.

## Sign-off record

Each approval — content or promotion — captures a minimal, tamper-evident
record:

- Runbook `id` and version (semver).
- Decision type and outcome (approved / rejected / demoted).
- Approver identity and role; second approver where applicable.
- Criteria checklist result and links to evidence.
- Timestamp and, for promotions, the effective autonomy stage.

## Rejection and appeal

A rejected runbook returns to `Draft` with specific, actionable review comments.
Authors may appeal a rejection to the review board, which either upholds the
decision or assigns a different reviewer. Emergency deprecations (a runbook found
to induce unsafe behavior) may be enacted by a single board member or security
on-call and are ratified at the next board meeting. All appeals and emergency
actions are logged.

## Anti-patterns to avoid

- **Blanket approvals.** Approve specific content/versions and specific stages,
  never "all future changes."
- **Self-approval.** The author never approves their own runbook.
- **Stage-skipping.** Do not jump from Stage 0 to Stage 3; each hop earns trust.
- **Silent promotion.** No autonomy change without a recorded board decision and
  a defined demotion trigger.
