---
id: vector-database-review
title: Vector Database Review
category: databases
maturity: stable
risk_level: high
estimated_duration: 2h-6h
supported_agents:
  - devin
  - claude-code
  - github-copilot-agent
  - openai-codex
  - cursor
  - openhands
  - autogen
  - crewai
  - langgraph
  - mcp-agent
required_access:
  - read-only-observability
  - vector-db-read
  - eval-dataset
  - index-config
human_in_the_loop: required
owner: awesome-ai-runbooks-maintainers
version: 1.0.0
last_reviewed: 2026-08-13
tags:
  - vector-database
  - pgvector
  - pinecone
  - weaviate
  - milvus
  - qdrant
  - hnsw
  - ivf
  - rag
difficulty: advanced
domain: databases
platform: database
agent_type: [devin, claude-code, github-copilot-agent, openai-codex, cursor, openhands, autogen, crewai, langgraph, mcp-agent]
author: awesome-ai-runbooks-maintainers
reviewers: [awesome-ai-runbooks-maintainers]
required_tools: [psql, mysql, redis-cli, mongosh]
compliance_tags: []
status: approved
maturity_level: 3
---
# Vector Database Review

> Review a vector database (pgvector, Pinecone, Weaviate, Milvus, or Qdrant) for
> recall, latency, and cost — diagnose index configuration (HNSW/IVF), distance
> metrics, and quantization — and deliver an evidence-backed tuning plan.

## Objective

Evaluate a vector search deployment against its recall and latency SLOs and
produce a prioritized tuning plan. "Done" means recall@k is measured against a
ground-truth set, p95/p99 query latency is captured under representative load,
index parameters (HNSW `M`/`ef`, IVF `nlist`/`nprobe`), distance metric, and
quantization are assessed, and each recommendation has an expected recall/latency
tradeoff and rollback.

## Business Context

Vector databases are the retrieval backbone of RAG systems, semantic search,
recommendations, and deduplication. Retrieval quality directly determines LLM
answer quality: if recall drops, the model is fed irrelevant context and
hallucinates, eroding user trust regardless of how good the model is. At the same
time, approximate-nearest-neighbor (ANN) indexes trade recall for latency and
cost — an over-tuned `ef_search` can triple latency and infrastructure spend,
while an under-tuned one silently degrades answer quality with no error ever
thrown. Because failures are *quiet* (wrong-but-plausible results, not
exceptions), disciplined, measurement-driven review is the only way to keep a
vector store both accurate and affordable.

## Problem Statement

The vector store shows degraded retrieval quality (users report irrelevant
results / RAG hallucinations), elevated query latency, high memory/cost, or
failed/stale index builds after ingestion. The agent must measure recall against
ground truth, profile latency, and attribute problems to index parameters,
distance metric mismatch, embedding drift, filtering strategy, or resource
limits — not guess. Symptoms are often silent, so evaluation must be explicit.

Out of scope: retraining or swapping the embedding model, redesigning the
chunking pipeline, and multi-region replication design — these may be
recommended but are not executed here.

## Success Criteria

- [ ] recall@k measured against a ground-truth (exact/brute-force) baseline on a held-out query set.
- [ ] p50/p95/p99 query latency captured at representative concurrency.
- [ ] Index type and parameters documented (HNSW `M`, `ef_construction`, `ef_search`; IVF `nlist`, `nprobe`; PQ/SQ quantization).
- [ ] Distance metric verified to match the embedding model (cosine vs dot vs L2).
- [ ] Memory/cost footprint of the index assessed.
- [ ] Prioritized tuning plan with recall/latency/cost tradeoffs and rollback.
- [ ] No production index rebuild without approval.

## Trigger Conditions

- Alert: `rag_answer_relevance` or offline `recall@10` below threshold.
- Alert: `vector_query_latency_p99 > 150ms` or QPS-driven CPU/memory saturation.
- Event: embedding model version bump or large re-ingestion completed.
- Schedule: quarterly retrieval-quality review.
- Manual: users report irrelevant search results or RAG hallucinations.

## Inputs Required

| Input | Description | Example | Required |
|-------|-------------|---------|----------|
| `engine` | Vector DB in use | `pgvector` / `pinecone` / `weaviate` / `milvus` / `qdrant` | Yes |
| `endpoint` | Connection/host | `vectors-ro.internal:6333` | Yes |
| `collection` | Collection/index/class name | `docs_v3` | Yes |
| `dim` | Embedding dimensionality | `1536` | Yes |
| `metric` | Distance metric | `cosine` | Yes |
| `k` | Top-k for recall eval | `10` | Yes |
| `eval_set` | Ground-truth query/label set | `s3://eval/queries.jsonl` | Yes |
| `slo_recall` / `slo_p99_ms` | Targets | `0.95` / `100` | Yes |

## Required Access

| Scope | Purpose | Read/Write | Sensitivity |
|-------|---------|-----------|-------------|
| Vector DB read/query | Run search + collection info | Read | Medium |
| Eval dataset (object store) | Ground-truth queries/labels | Read | Medium |
| Index/collection config | Inspect params & stats | Read | Low |
| Metrics dashboard | Latency/QPS/memory | Read | Low |
| Index rebuild / param change | Apply tuning | Write | High (approval gated) |

## Assumptions

- A ground-truth set exists or exact search can generate it (brute-force top-k).
- The embedding model and its expected distance metric are known.
- Vectors are already normalized if the metric assumes it (cosine/IP).
- A staging collection or shadow index can be used for rebuild experiments.
- Query load can be replayed representatively for latency measurement.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Metric mismatch (cosine vs dot) silently tanks recall | Medium | High | Verify normalization + metric against model card |
| Rebuilding index in place causes downtime/stale reads | Medium | High | Build a shadow index, then swap via alias |
| Aggressive quantization (PQ) destroys recall | Medium | High | A/B against non-quantized; measure recall delta |
| Raising `ef_search`/`nprobe` blows latency/cost budget | Medium | Medium | Sweep params; pick the Pareto knee, not the max |
| Eval set unrepresentative → misleading recall | Medium | High | Sample from real production query distribution |

## Constraints

- No in-place production index rebuilds without a shadow/alias swap and approval.
- Recommendations must report the recall/latency/cost tradeoff, not a single number.
- Respect data residency; do not export embeddings/documents off-network.
- Keep experiments on staging or a shadow index until validated.
- Honor active change freezes.

## Agent Persona

Adopt the persona of a **Principal Search / ML Platform Engineer** who is fluent
in ANN internals: HNSW graph construction (`M`, `ef_construction`) and search
breadth (`ef_search`); IVF partitioning (`nlist`) and probe count (`nprobe`);
product/scalar quantization (PQ/SQ) memory-vs-recall tradeoffs; and the critical
importance of matching the distance metric to how the embedding model was
trained. Insist on *measuring* recall against ground truth — never claim a tuning
"improves quality" without a recall number and a latency cost. Treat silent
quality regressions as first-class incidents. Follow
[`docs/AI_AGENT_STANDARDS.md`](../../docs/AI_AGENT_STANDARDS.md): measure on a
shadow index, promote only with approval.

## Planning Instructions

1. Restate the recall and latency SLOs and the value of `k`.
2. Confirm the ground-truth strategy (existing labels vs brute-force exact search).
3. Enumerate the current index config for the engine in use.
4. Design a parameter sweep (HNSW `ef_search` or IVF `nprobe`) and a recall/latency plot.
5. Mark read-only measurement vs mutating rebuilds (approval gated).
6. Externalize the plan; because `human_in_the_loop` is `required`, get approval
   before rebuilding indexes or changing quantization.

## Execution Instructions

Start by inventorying the index and building ground truth, then sweep.

```sql
-- pgvector: inspect the index and configure search breadth (read/inspect)
\d+ docs_v3
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'docs_v3';

-- HNSW search breadth (per-session, safe to test)
SET hnsw.ef_search = 100;
EXPLAIN ANALYZE
SELECT id, embedding <=> :qvec AS distance
FROM docs_v3
ORDER BY embedding <=> :qvec
LIMIT 10;   -- <=> is cosine distance; <#> neg inner product; <-> L2
```

```sql
-- pgvector: build/rebuild HNSW or IVFFlat (approval gated; prefer a shadow table)
CREATE INDEX CONCURRENTLY docs_v3_hnsw
  ON docs_v3 USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 200);

CREATE INDEX CONCURRENTLY docs_v3_ivf
  ON docs_v3 USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 2000);   -- rule of thumb: lists ~= rows/1000; probes ~= sqrt(lists)
SET ivfflat.probes = 40;
```

```bash
# Qdrant: collection config and HNSW / quantization params (read)
curl -s http://vectors-ro.internal:6333/collections/docs_v3 | jq '.result.config'
# Query with tunable search breadth (hnsw_ef)
curl -s -X POST http://vectors-ro.internal:6333/collections/docs_v3/points/search \
  -H 'content-type: application/json' \
  -d '{"vector": [/*...*/], "limit": 10, "params": {"hnsw_ef": 128, "exact": false}}'
```

```python
# Weaviate / Milvus / Pinecone: measure recall@k vs a brute-force ground truth
import numpy as np

def recall_at_k(approx_ids, truth_ids, k):
    hits = len(set(approx_ids[:k]) & set(truth_ids[:k]))
    return hits / k

# 1) ground truth: exact search (brute force) on a sample of N queries
# 2) approx search: query the ANN index with the same vectors
# 3) aggregate mean recall@k and record p50/p95/p99 latency per config
results = []
for ef in [40, 64, 100, 128, 200, 400]:
    recalls, latencies = [], []
    for q, truth in eval_set:              # truth = exact top-k ids
        t0 = time.perf_counter()
        approx = index.search(q, k=10, ef=ef)   # engine-specific call
        latencies.append((time.perf_counter() - t0) * 1000)
        recalls.append(recall_at_k(approx.ids, truth, 10))
    results.append({"ef": ef, "recall@10": np.mean(recalls),
                    "p95_ms": np.percentile(latencies, 95)})
```

```javascript
// Milvus (mongosh-style pseudo via SDK): index params for IVF_PQ / HNSW
// create_index(field="embedding", index_type="HNSW",
//   metric_type="COSINE", params={"M":16, "efConstruction":200})
// search(params={"ef": 128})  // HNSW
// create_index(index_type="IVF_PQ", params={"nlist":4096, "m":16, "nbits":8})
// search(params={"nprobe": 64})  // IVF
```

## Investigation Workflow

```mermaid
flowchart TD
    A[Trigger: quality/latency/cost alert] --> B[Inventory index config & metric]
    B --> C{Distance metric matches embedding model?}
    C -->|No| D[Fix metric + normalization; rebuild]
    C -->|Yes| E[Build ground truth via exact/brute-force top-k]
    E --> F[Sweep ef_search / nprobe: recall@k vs latency]
    F --> G{recall@k meets SLO?}
    G -->|No| H{Latency budget has headroom?}
    H -->|Yes| I[Raise ef_search/nprobe or M/ef_construction]
    H -->|No| J[Reduce quantization / increase index quality]
    G -->|Yes| K{Latency within SLO?}
    K -->|No| L[Lower ef/nprobe; add quantization; shard]
    K -->|Yes| M{Cost/memory acceptable?}
    M -->|No| N[Introduce PQ/SQ; measure recall delta]
    M -->|Yes| O[Lock in config]
    D --> E
    I --> F
    J --> F
    L --> F
    N --> F
    O --> P[Human approval gate]
    P --> Q[Shadow rebuild + alias swap + re-measure]
```

## Analysis Framework

Reason across these dimensions, always with a measured recall/latency/cost tuple:

1. **Distance metric correctness** — The metric must match how embeddings were
   trained. Cosine requires normalized vectors; dot/inner-product does not.
   OpenAI/e5/bge families are typically cosine. A mismatch produces plausible but
   wrong neighbors and quietly tanks recall.
2. **HNSW parameters** — `M` (graph degree) and `ef_construction` set index
   quality at build time (higher = better recall, more memory/build time);
   `ef_search`/`hnsw_ef` sets search breadth at query time (higher = better
   recall, higher latency). Sweep `ef_search` and pick the knee where recall
   plateaus.
3. **IVF parameters** — `nlist` (number of clusters; ~`rows/1000` to `sqrt(rows)`)
   and `nprobe` (clusters searched; recall/latency knob). Too-low `nprobe`
   misses neighbors near cluster boundaries.
4. **Quantization** — PQ/SQ cut memory dramatically but lose precision; always
   A/B recall against the non-quantized index and consider re-ranking exact
   top-N.
5. **Filtering strategy** — pre-filtering vs post-filtering with metadata changes
   both recall and latency; heavy filters can under-fill the candidate set.
6. **Embedding drift / staleness** — model version changes or partial
   re-ingestion mixing embedding versions corrupts the space.
7. **Resource limits** — index must fit in RAM for HNSW; spilling to disk or
   under-provisioned replicas inflate p99.

Choose the Pareto-optimal configuration: the lowest-latency, lowest-cost point
that still meets `slo_recall`.

## Decision Tree

```mermaid
flowchart TD
    Start[Retrieval degraded] --> Q1{Metric matches model & vectors normalized?}
    Q1 -->|No| A1[Correct metric/normalization; rebuild index]
    Q1 -->|Yes| Q2{recall@k below SLO?}
    Q2 -->|Yes| Q3{Latency headroom available?}
    Q3 -->|Yes| A2[Increase ef_search/nprobe or M/ef_construction]
    Q3 -->|No| A3[Reduce quantization; add exact re-rank of top-N]
    Q2 -->|No| Q4{Latency above SLO?}
    Q4 -->|Yes| A4[Lower ef/nprobe; enable quantization; shard/scale]
    Q4 -->|No| Q5{Memory/cost above budget?}
    Q5 -->|Yes| A5[Apply PQ/SQ; measure recall delta; keep if within SLO]
    Q5 -->|No| Q6{Recall unstable across queries?}
    Q6 -->|Yes| A6[Check embedding drift / mixed versions; re-embed]
    Q6 -->|No| A7[Lock config; document Pareto knee]
```

## Validation Steps

- [ ] recall@k on the held-out set meets or exceeds `slo_recall`.
- [ ] p95/p99 latency within `slo_p99_ms` at representative concurrency.
- [ ] Chosen parameters are the Pareto knee (recall plateau, minimal latency/cost).
- [ ] Metric/normalization verified against the embedding model card.
- [ ] Index fits in memory; no disk spill under load.
- [ ] Shadow index validated before alias swap; production reads unaffected.
- [ ] RAG end-to-end answer-quality metric improved or held (if applicable).

## Expected Outputs

- Recall@k vs latency sweep table/plot across parameter values.
- Current vs recommended index configuration.
- Metric/normalization verification result.
- Memory/cost footprint comparison.
- Prioritized tuning plan with tradeoffs and rollback.

## Deliverables

Produce a report using [`templates/report-template.md`](../../templates/report-template.md):
executive summary, recall/latency measurement methodology and ground-truth
description, sweep results, root-cause analysis, recommended configuration with
tradeoffs, applied changes with before/after metrics, and follow-ups (re-embed,
re-rank, sharding). Include exact index-build commands and rollback (alias swap
back).

## Escalation Process

- **Sev-2 (RAG quality incident):** notify the ML platform + product owners; if
  recall collapsed after a deploy, prioritize rollback of the offending change.
- **Model/pipeline issue** (wrong embedding version, chunking regression): route
  to the ML team; out of scope for index tuning.
- **Approval required:** production index rebuilds, quantization changes, and
  metric changes route to the change approver with the recall/latency tradeoff
  table and rollback.

## Rollback Strategy

- Shadow index + alias: keep the previous index live; if the new one regresses,
  point the alias/collection back to the prior index (near-instant).
- pgvector: `DROP INDEX CONCURRENTLY docs_v3_hnsw;` to revert to the prior index;
  reset `hnsw.ef_search`/`ivfflat.probes` at session/role scope.
- Qdrant/Milvus/Weaviate: restore the previous collection snapshot or recreate
  the index with the prior parameters from version control.
- Confirm rollback by re-running the recall@k eval and comparing to baseline.

## Post-Execution Review

- Was the regression silent? Add an offline recall@k canary to CI/CD.
- Is the eval set representative of production query distribution and refreshed?
- Should quantization + exact re-rank be the standard pattern for this workload?
- Are embedding-version tags enforced to prevent mixed-space corruption?

## Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| recall@k | Overlap with exact top-k on eval set | >= `slo_recall` |
| Query p99 latency | 99th percentile at target QPS | < `slo_p99_ms` |
| Index memory | RAM per million vectors | Within budget |
| Cost per 1k queries | Infra cost normalized | Trending down |
| Answer relevance | RAG end-to-end quality (if applicable) | Held or improved |
| Rebuild MTTR | Time to swap a corrected index | < 1h |

## Example Execution

**Input:** `engine=pgvector`, `collection=docs_v3`, `dim=1536`, `metric=cosine`,
`k=10`, `slo_recall=0.95`, `slo_p99_ms=100`. Trigger: users report irrelevant RAG
answers after a re-ingestion.

**Agent reasoning (abridged):** Verified vectors were normalized and the index
used `vector_cosine_ops` (metric correct). Built ground truth via exact search
(`ORDER BY embedding <=> q` with no index) on 500 sampled production queries.
Swept `hnsw.ef_search`. At the default `ef_search=40`, recall@10 was 0.86 —
below SLO — because the IVFFlat index had been built with too few `lists` during
the rushed re-ingestion. Rebuilt as HNSW and re-swept.

```text
Sweep results (HNSW, m=16, ef_construction=200):

 ef_search   recall@10   p95_ms
    40          0.912      9
    64          0.945     13
   100          0.969     19   <- Pareto knee (meets 0.95 SLO)
   200          0.981     34
   400          0.985     71

Chosen: ef_search = 100  (recall@10 = 0.969, p95 = 19ms, p99 = 41ms)
```

**Outcome:** Recall@10 rose from 0.86 to 0.969 while p99 stayed at 41ms (well
under the 100ms SLO). Index rebuilt as a shadow HNSW index and swapped via
`CREATE INDEX CONCURRENTLY` then dropping the old IVFFlat. Rollback documented as
re-pointing to the retained IVFFlat index. Follow-up: add an offline recall@10
canary to the ingestion pipeline so silent regressions fail the build.

## References

- [`docs/AI_AGENT_STANDARDS.md`](../../docs/AI_AGENT_STANDARDS.md)
- [`templates/report-template.md`](../../templates/report-template.md)
- [MongoDB Health Review runbook](./mongodb-health-review.md)
- Engine docs: pgvector (HNSW/IVFFlat), Pinecone, Weaviate (HNSW), Milvus (IVF/HNSW/PQ), Qdrant (HNSW + quantization); ANN-Benchmarks methodology.
