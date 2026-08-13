# Examples

Worked, end-to-end examples of AI agents executing runbooks in this repository.
Each example shows the inputs, an abridged agent trajectory (plan → investigate →
validate), and the resulting standard report produced from the
[report template](../templates/report-template.md).

These examples are **illustrative and fictional** — all service names, metrics,
hostnames, and identifiers are synthetic. They demonstrate the *shape* of a
high-quality execution, not real incidents.

## Available examples

| Example | Runbook | Persona |
|---------|---------|---------|
| [`root-cause-analysis-checkout-latency.md`](./root-cause-analysis-checkout-latency.md) | [`root-cause-analysis`](../runbooks/reliability/root-cause-analysis.md) | [`root-cause-analysis-agent`](../prompts/root-cause-analysis-agent.md) |

## How to read an example

1. **Inputs** — what the operator handed the agent.
2. **Plan** — the agent's externalized plan (read-only first, gated mutations).
3. **Investigation** — evidence gathered, hypotheses tested.
4. **Report** — the deliverable a human reviews.

Contributions of additional examples are welcome — see
[CONTRIBUTING](../CONTRIBUTING.md).
