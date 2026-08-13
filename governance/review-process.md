# Runbook Review Process

Review is the human gate that stands between a proposed change and an approved,
production-eligible runbook. It has two tracks — **technical review** (always)
and **security review** (for sensitive runbooks) — with defined reviewer
responsibilities, service-level targets, and checklists. This document operates
the review step referenced by the [approval process](./approval-process.md) and
the QA review flow in
[`../docs/QUALITY_ASSURANCE.md`](../docs/QUALITY_ASSURANCE.md#4-review-process).

## Review tracks

```mermaid
flowchart LR
    PR[Pull request] --> CI{Automated checks}
    CI -->|fail| A[Author fixes]
    CI -->|pass| T[Technical review]
    T -->|standard| D{Approved?}
    T -->|security/ or high\|critical| S[Security review]
    S --> D
    D -->|changes| A
    D -->|yes| M[Sign-off + merge]
```

The automated gate (structure, front matter, markdown lint, links, scoring) must
be green **before** a human spends review time. Reviewers do not hand-check what
CI already enforces; they focus on judgment: accuracy, depth, safety, and
agent-readiness.

## When a security review is required

A second, security-focused review is mandatory when any of these are true:

- The runbook lives under `runbooks/security/`.
- Front matter declares `risk_level: high` or `risk_level: critical`.
- The runbook contains any `[mutating]` step against production.
- The runbook touches authentication, secrets, network policy, or data movement.

The security review process itself is detailed in
[`../security/security-review-process.md`](../security/security-review-process.md).

## Reviewer responsibilities

### Technical reviewer

- Verify **correctness**: commands, queries, and expected outputs are accurate
  and current; no fabricated tools or APIs.
- Verify **depth**: the runbook reflects senior-level reasoning, not a checklist
  skimmed off a blog post.
- Verify **agent-readiness**: objective and success criteria are unambiguous;
  steps are ordered and tagged `[read-only]` / `[mutating]`; the decision tree
  covers realistic branches including escalate.
- Verify **portability**: no single-vendor assumptions beyond declared
  `supported_agents`.
- Confirm the **example execution** is realistic and consistent with the steps.

### Security reviewer

- Confirm **defensive-only** intent and **least-privilege** access.
- Confirm every mutating action is **reversible** with a real rollback and gated
  by `human_in_the_loop` appropriate to its risk tier.
- Check for **secrets, hostnames, or customer data** — none permitted.
- Assess **prompt-injection and tool-abuse** exposure: could following this
  runbook literally cause an agent to act unsafely?
- Validate compliance-relevant claims (logging, redaction, data residency).

### Runbook owner

- Ensures the runbook is re-reviewed on cadence (`last_reviewed`).
- Triages review findings and shepherds fixes.
- Sponsors autonomy-stage promotion requests with evidence.

## Service-level targets (SLAs)

| Stage | Target | Notes |
|-------|--------|-------|
| First reviewer response | ≤ 2 business days | Acknowledge and begin review |
| Technical review complete | ≤ 5 business days | Median target for standard PRs |
| Security review complete | ≤ 7 business days | For sensitive runbooks |
| Author turnaround on changes | ≤ 5 business days | Stale PRs may be closed |
| Emergency security review | ≤ 4 business hours | For a runbook found unsafe in prod |
| Scheduled re-review cadence | Every 180 days | Or on upstream dependency change |

Time-to-review is tracked as a governance metric (median ≤ 5 days). Breached SLAs
are surfaced to the review board.

## Technical review checklist

- [ ] CI is green (structure, front matter, lint, links, scoring).
- [ ] Objective and success criteria are measurable and unambiguous.
- [ ] Every step is ordered and tagged read-only vs mutating.
- [ ] Commands/queries are correct, current, and language-tagged.
- [ ] Investigation workflow and decision tree diagrams render and are realistic.
- [ ] Validation uses before/after evidence and checks for regressions.
- [ ] Rollback and escalation are concrete and assignable.
- [ ] Example execution matches the documented procedure.
- [ ] Completeness ≥ 75 and agent-readiness ≥ 42.
- [ ] `CHANGELOG.md` entry is present (or batched per policy).

## Security review checklist

- [ ] Defensive-only; no attacker-enabling content.
- [ ] Least-privilege `required_access`; no broad "agent admin" role.
- [ ] `risk_level` and `human_in_the_loop` match the true blast radius.
- [ ] Every mutating step is reversible and gated.
- [ ] No secrets, credentials, private keys, hostnames, or customer data.
- [ ] Redaction guidance present where output may contain sensitive data.
- [ ] Prompt-injection / tool-abuse exposure assessed and acceptable.
- [ ] Compliance mappings (SOC 2 / ISO 27001 / NIST AI RMF / PCI) noted where
      relevant — see [audit-framework.md](./audit-framework.md).

## Reviewer conduct

- **Review the diff like privileged code.** A runbook change is a change to what
  agents will do against real systems.
- **Be specific and kind.** Actionable comments tied to lines; explain the risk,
  not just the rule.
- **Prefer requesting changes over silent rejection.** Return runbooks to
  `Draft` with clear next steps.
- **Escalate uncertainty.** If a reviewer cannot confidently assess safety, pull
  in a domain SME or the board rather than approving on faith.
- **No rubber-stamping.** An approval is a personal, auditable attestation that
  the criteria were met.

## Outcome and handoff

A completed review results in one of: **request changes** (back to `Draft`),
**approve** (proceed to sign-off in the [approval process](./approval-process.md)),
or **escalate** (route to board or SME). Every outcome, reviewer identity, and
timestamp is captured in the PR and mirrored to the audit trail.
