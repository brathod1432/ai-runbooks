# Reviewer Guide

This guide is for maintainers reviewing pull requests to
**awesome-ai-runbooks**, with an emphasis on runbook PRs. It complements the
rubrics in [`docs/QUALITY_ASSURANCE.md`](docs/QUALITY_ASSURANCE.md): that
document defines the *scoring*; this one defines *how to review*. Our goal is a
library of runbooks that autonomous agents can execute reliably and safely, so
reviews are thorough and safety-biased.

## What every review must check

A runbook is more than prose — it is an operational contract an agent will act
on. Work through these dimensions in order.

### 1. Structure and completeness

Confirm the PR was copied from
[`templates/runbook-template.md`](templates/runbook-template.md) and that **all
25 sections are present, in order, with unchanged headings**. Missing or
reordered sections are an automatic request-changes. Verify the content is real:
no placeholders, no `TODO`, no fabricated tools or APIs, and at least ~1000
words of substantive material.

### 2. Metadata schema

Open the YAML front matter and validate every required key: `id` (must match the
filename), `title`, `category`, `maturity`, `risk_level`, `estimated_duration`,
`supported_agents`, `required_access`, `human_in_the_loop`, `owner`, `version`,
`last_reviewed`, and `tags`. The category must be one of the recognized library
categories, and `supported_agents` must list only real, validated platforms.

### 3. Safety and defensive posture

This is the highest-priority check. Confirm the runbook is **defensive only** —
it detects, hardens, and remediates rather than enabling attacks. Verify
read-only and observation steps come *before* any mutating steps, and that
destructive or production-mutating actions are gated behind explicit
human-in-the-loop approval. There must be no secrets, tokens, private keys, or
internal hostnames anywhere in the diff.

### 4. Least privilege

Check the "Required Access" table. Access requested must be the minimum needed,
scoped read-only wherever possible, with any write or production access flagged
explicitly and justified. Reject over-broad grants (for example, admin roles
where a read scope suffices).

### 5. Evidence quality

The runbook should teach the agent to reason from evidence: which signals to
collect, thresholds that matter, how to rank hypotheses, and how to avoid
confirmation bias. Validation steps must be deterministic — success or failure
verifiable objectively — and the Example Execution must include a realistic
sample report excerpt, not a hand-wave.

### 6. Diagrams

Confirm at least **two Mermaid diagrams** render correctly: an Investigation
Workflow and a Decision Tree. The decision tree must cover the realistic
branches, including an explicit **escalate** path.

### 7. Links and formatting

Verify internal links resolve (relative paths correct for the runbook's
location), external references are credible and relevant, and markdownlint is
clean. Confirm `risk_level` and `human_in_the_loop` are consistent with
[QUALITY_ASSURANCE §3](docs/QUALITY_ASSURANCE.md).

## Reviewer checklist

| # | Check | Pass condition |
|---|-------|----------------|
| 1 | Structure | All 25 sections present, in order, headings unchanged |
| 2 | Metadata | All front-matter keys valid; `id` matches filename; category valid |
| 3 | Depth | ≥ 1000 words; no placeholders/TODO; no fabricated tools |
| 4 | Safety | Defensive only; read-only before mutating; HITL gates on high risk |
| 5 | Least privilege | Minimal, scoped access; write/prod access flagged |
| 6 | Evidence | Deterministic validation; realistic worked example |
| 7 | Diagrams | ≥ 2 Mermaid diagrams render; decision tree has escalate path |
| 8 | Rollback & escalation | Both real, specific, and verifiable |
| 9 | Links & lint | Links resolve; markdownlint clean; risk fields consistent |

## Review SLAs

- **First response:** within **2 business days** of a PR becoming review-ready
  (CI green, not draft).
- **Full review:** median **≤ 5 business days**; complex or high-risk runbooks
  may take longer, but tell the author and set an expectation.
- **Re-review after changes:** within **2 business days** of the author pushing
  requested changes.
- **Security-category PRs:** prioritized; do not let them sit longer than the
  standard SLA.

## Approve / request-changes rubric

- **Approve** when the completeness score is ≥ 75, agent-readiness is ≥ 42, all
  checklist rows pass, and there are no unresolved safety concerns.
- **Request changes** for any safety or least-privilege violation, missing or
  reordered sections, invalid metadata, non-rendering diagrams, missing rollback
  or escalation, or fabricated content. Be specific: quote the line and state
  the required fix.
- **Comment (no verdict)** for optional style suggestions that should not block
  merge.

Leave actionable, kind feedback. Distinguish blocking issues ("must fix before
merge") from nits ("consider"). Prefer suggested edits over vague critique.

## Second-review triggers for security

A **second, independent maintainer review is mandatory** when any of the
following apply:

- The runbook's `category` is `security` or `soc`.
- `risk_level` is `high` or `critical`.
- The change touches `SECURITY.md`, `/security/`, or `/runbooks/security/`.
- The runbook introduces any irreversible or production-mutating action.

The second reviewer should ideally be on the security team. Merge only after
both reviewers approve and CI is green; then update `CHANGELOG.md`. For the full
scoring model, acceptance criteria, and process diagram, see
[`docs/QUALITY_ASSURANCE.md`](docs/QUALITY_ASSURANCE.md).
