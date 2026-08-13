# Vision — awesome-ai-runbooks

## One-line vision

> Become the definitive, open-source library of operational runbooks that turn
> autonomous AI agents into reliable, auditable senior engineers.

## The problem we are solving

Autonomous coding and operations agents — Devin, GitHub Copilot Agent, Claude
Code, OpenAI Codex, Cursor Agents, OpenHands, AutoGen, CrewAI, LangGraph agents,
MCP-enabled agents, and internal enterprise agents — are now capable of
executing multi-step engineering work. But capability is not the bottleneck.
**Reliability, repeatability, and trust are.**

Today, agent behavior is largely improvised from a one-line prompt. The same
task ("investigate the latency spike") produces wildly different quality
depending on the phrasing, the model, and the day. Enterprises cannot safely
delegate high-stakes work — incident response, security review, cost
optimization, production migrations — to a process they cannot predict, audit,
or improve.

Human engineering organizations solved an analogous problem decades ago with
**runbooks, SOPs, and playbooks**: codified, reviewed, versioned procedures that
make outcomes consistent regardless of who is on call. The SRE discipline
(Google SRE), cloud governance (AWS Well-Architected), and incident management
(PagerDuty, Atlassian) all rest on this foundation.

**AI agents deserve the same operational discipline — designed for how agents
actually reason and act.**

## What we are building

A curated, rigorously standardized collection of **agent-native runbooks**: each
one a complete operational contract that tells an agent *what to achieve*, *how
to plan*, *how to investigate*, *how to decide*, *how to validate*, *when to
escalate*, and *how to report* — with the same rigor a Staff Engineer would
bring.

Every runbook is:

- **Structured** — a fixed, machine-checkable specification (see
  [`templates/runbook-template.md`](../../templates/runbook-template.md)).
- **Agent-portable** — written to work across every major agent platform.
- **Evidence-driven** — agents must justify findings with observations.
- **Human-governable** — explicit escalation, rollback, and approval gates.
- **Measurable** — each runbook carries metrics for its own effectiveness.

## Why now

1. **Agents crossed the capability threshold.** Multi-step tool use, planning,
   and long-context reasoning are now reliable enough to execute real SOPs.
2. **The Model Context Protocol (MCP)** standardized how agents reach tools and
   data, making cross-platform runbooks feasible.
3. **Enterprises are piloting agents in production** and urgently need
   governance, auditability, and consistency before scaling.
4. **The ecosystem lacks a canonical, vendor-neutral standard.** Prompts are
   scattered in gists and blog posts; nothing is versioned, reviewed, or scored.

## Guiding principles

| Principle | What it means in practice |
|-----------|---------------------------|
| Vendor-neutral | No runbook assumes a single agent vendor or model. |
| Evidence over assertion | Agents cite observations before conclusions. |
| Least privilege by default | Read-only first; writes are explicit and gated. |
| Human-in-the-loop where it matters | High-risk actions require approval. |
| Reversible by design | Every mutating step has a rollback. |
| Measured, not vibed | Completeness and quality are scored by tooling. |
| Open and composable | MIT-licensed, forkable, extendable for private use. |

## What success looks like

- A platform team can drop this repo into their agent stack and get consistent,
  senior-level execution on day one.
- A runbook here is trusted the way an AWS Well-Architected pillar is trusted.
- Contributions come from SREs, security engineers, and AI platform teams across
  companies, making it a living standard.
- "Point your agent at the `production-readiness-review` runbook" becomes common
  engineering vocabulary.

## Non-goals

- We are **not** building an agent, a framework, or a runtime.
- We are **not** shipping executable orchestration code that locks you into one
  platform.
- We are **not** replacing human judgment on high-severity decisions — we are
  structuring how agents support it.

## The north star

If Google's SRE book, the AWS Well-Architected Framework, OpenAI's agent
operations guidance, and GitHub's engineering standards had a single,
open-source offspring dedicated entirely to **how autonomous agents should
operate** — this repository is it.
