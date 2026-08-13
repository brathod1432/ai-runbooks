# Example — Root Cause Analysis: Checkout p99 Latency Spike

> **Fictional, illustrative example.** All names, metrics, and identifiers are
> synthetic. Runbook: [`root-cause-analysis`](../runbooks/reliability/root-cause-analysis.md).
> Persona: [`root-cause-analysis-agent`](../prompts/root-cause-analysis-agent.md).

## Inputs

```text
service_name: checkout-api
environment: prod
symptom: "p99 latency > 2s (baseline ~250ms) since 14:00 UTC"
time_window: 2026-08-13T13:30Z .. 2026-08-13T15:00Z
constraints: read-only investigation; propose any mutating action for approval
```

## Agent plan (externalized, approved)

```text
Objective: identify root cause of checkout-api p99 latency spike and recommend
           a prioritized remediation. Success = cause confirmed with evidence
           from >=2 independent signals; report + action plan delivered.

Assumptions to verify:
  A1. Spike is real (not a metrics artifact).
  A2. It correlates with a change ("what changed?").

Steps (all read-only [R0]):
  1. Confirm the spike (latency + traffic + error golden signals).
  2. Build a change timeline (deploys, config, flags) around 14:00 UTC.
  3. Correlate with traces (which span regressed?).
  4. Inspect dependency + resource state (DB, pool, CPU).
  5. Test top hypothesis with a falsifying query.

No mutating steps planned; will propose if remediation requires one.
```

## Investigation (abridged trajectory)

**Step 1 — Confirm the spike.**

```promql
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket{service="checkout-api"}[5m])) by (le))
```

Observation: p99 rose from ~250ms to ~2.3s at 14:02 UTC; traffic flat; error rate
unchanged (so it is latency, not failures). *A1 confirmed.*

**Step 2 — What changed?**

```bash
kubectl -n checkout rollout history deploy/checkout-api
# revision 148 rolled out 2026-08-13T14:01Z
```

Observation: deploy `rev 148` landed at 14:01 UTC — one minute before the spike.
*A2 supported.*

**Step 3 — Trace correlation.**

Jaeger p99 trace for `POST /checkout` shows the regressed span is
`db.query:select_cart_items` (was ~8ms, now ~1.9s). Upstream/downstream spans
unchanged.

**Step 4 — Dependency/resource state.**

```sql
SELECT query, calls, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC LIMIT 5;
-- select_cart_items: mean_exec_time 1875ms, calls up 3x
```

Observation: `select_cart_items` mean exec time jumped to ~1.9s. `EXPLAIN
ANALYZE` shows a **sequential scan** where rev 147 used an index.

**Step 5 — Falsifying test.**

Hypothesis: rev 148 changed the query and dropped the index usage. Falsifier:
if rev 147's query plan also seq-scans, the deploy is not the cause. Checked the
diff for rev 148 — an ORM change added a `LOWER(email)` predicate that made the
existing index on `email` unusable. Rev 147 plan used the index. *Hypothesis
confirmed; alternative (DB load) refuted since traffic was flat.*

## Deliverable — Standard Report (excerpt)

```markdown
# Agent Execution Report — Root Cause Analysis: checkout-api p99 latency

## Executive Summary
Deploy rev 148 (14:01 UTC) introduced a `LOWER(email)` predicate that disabled
use of the `idx_cart_email` index, forcing sequential scans on select_cart_items
and driving p99 from 250ms to 2.3s. No data loss or errors. Recommended action:
roll back rev 148 (fast) or ship a functional index (durable). Confidence: HIGH.

## Findings
1. F1 — ORM change in rev 148 broke index usage (root cause). Evidence: trace
   span + pg_stat_statements + EXPLAIN ANALYZE seq scan + code diff.
2. F2 — No error-rate impact; purely latency. Evidence: golden signals.

## Impact
Checkout p99 ~9x baseline for ~50 min; elevated cart-abandonment risk. Error
budget burn: ~12% of monthly budget in the window.

## Recommendations
| ID | Recommendation | Rationale | Effort | Risk if ignored |
|----|----------------|-----------|--------|-----------------|
| R1 | Roll back deploy rev 148 (R2, needs approval) | Immediate relief | S | Continued latency |
| R2 | Add functional index LOWER(email) or revert predicate | Durable fix | S | Recurs on redeploy |
| R3 | Add EXPLAIN-plan regression check to CI | Prevent class of bug | M | Repeat incidents |

## Risk Level: High (customer-facing) · Priority: P1
## Action Plan
- [ ] Now: request approval to roll back rev 148 (rollback: `kubectl rollout undo`).
- [ ] Today: ship functional index; re-run EXPLAIN ANALYZE to validate.
- [ ] This week: add query-plan regression gate to CI.

## Validation Results
| Check | Expected | Actual | Pass? |
|-------|----------|--------|-------|
| p99 after rollback | < 300ms | 240ms | ✅ |
| Index used (EXPLAIN) | Index Scan | Index Scan | ✅ |
```

## Notes

- Every mutating action (the rollback) was **proposed for approval**, not taken
  autonomously, per [AI Agent Standards §8](../docs/AI_AGENT_STANDARDS.md#8-risk-framework).
- The agent confirmed causation with **four independent signals** (metrics,
  trace, DB stats, code diff) and ran a **falsifying test** before concluding.
