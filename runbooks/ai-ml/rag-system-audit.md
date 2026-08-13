---
id: rag-system-audit
title: RAG System Audit
category: ai-ml
maturity: stable
risk_level: medium
estimated_duration: 3h-6h
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
  - read-only-source
  - vector-store-read
  - eval-dataset-access
human_in_the_loop: recommended
owner: awesome-ai-runbooks-maintainers
version: 1.0.0
last_reviewed: 2026-08-13
tags:
  - ai-ml
  - rag
  - retrieval
  - embeddings
  - reranking
  - groundedness
  - evaluation
difficulty: intermediate
domain: ai-ml
platform: ai-platform
agent_type: [devin, claude-code, github-copilot-agent, openai-codex, cursor, openhands, autogen, crewai, langgraph, mcp-agent]
author: awesome-ai-runbooks-maintainers
reviewers: [awesome-ai-runbooks-maintainers]
required_tools: [python, curl]
compliance_tags: [nist-ai-rmf]
status: approved
maturity_level: 3
---
# RAG System Audit

> An end-to-end audit of a Retrieval-Augmented Generation pipeline — chunking,
> embeddings, retrieval quality, reranking, groundedness, and evaluation — that
> pinpoints where relevance or faithfulness breaks and delivers a measured,
> prioritized improvement plan.

## Objective

Quantify the quality of a RAG system stage-by-stage and identify the dominant
failure mode (retrieval vs generation), then deliver a measured remediation
plan. "Done" means retrieval metrics (recall@k, precision@k, MRR, nDCG) are
computed against a labeled eval set, generation metrics (faithfulness/
groundedness, answer relevance, context precision/recall) are computed with an
eval harness (Ragas or equivalent), the bottleneck stage is isolated with
evidence, and improvements are ranked by expected impact.

## Business Context

RAG is the workhorse pattern for grounding LLMs in proprietary knowledge —
support bots, internal search, doc Q&A, and agent memory. When RAG quality is
poor, the business consequences are concrete: hallucinated answers erode user
trust and create legal/compliance exposure (wrong medical/financial/policy
guidance), low retrieval recall makes the assistant "dumb" and drives users back
to humans (defeating the cost case), and unmeasured pipelines silently regress
after every embedding-model or chunking change. A disciplined audit tells you
*exactly* where to spend engineering effort — better chunking vs a stronger
embedding model vs a reranker vs prompt changes — instead of guessing. This
protects answer quality, user trust, and the ROI of the whole GenAI investment.

## Problem Statement

RAG systems fail in stage-specific ways that look identical from the outside
("the bot gave a wrong answer"). The root cause could be: chunks too large/small
so the right passage is diluted or split; an embedding model that doesn't
capture domain semantics; missing reranking so relevant-but-lower-ranked chunks
never reach the context window; a top-k too small to include the answer; or a
generation prompt that lets the model answer from parametric memory instead of
the retrieved context. Without stage-level metrics, teams tune blindly.

This runbook audits one RAG pipeline against a labeled evaluation set. **Out of
scope:** building the eval set from nothing (though the agent can bootstrap a
starter set), fine-tuning embedding models, and production traffic replay
(recommended as follow-up).

## Success Criteria

- [ ] Retrieval metrics (recall@k, precision@k, MRR, nDCG@k) are computed on a
      labeled eval set with confidence intervals.
- [ ] Generation metrics (faithfulness, answer relevance, context precision,
      context recall) are computed via an eval harness.
- [ ] The dominant failure mode is isolated as retrieval-bound vs
      generation-bound with quantitative evidence.
- [ ] Chunking, embedding, top-k, and reranking configs are documented and each
      assessed for fitness.
- [ ] Groundedness/hallucination rate is measured and hallucinated answers are
      traced to their stage cause.
- [ ] A ranked, effort-estimated improvement plan is delivered with expected
      metric lift per change.

## Trigger Conditions

- Alert: user-reported hallucinations or a drop in thumbs-up rate.
- Schedule: pre-release regression gate after any pipeline change.
- Manual: onboarding a new corpus or switching embedding models.
- Event: eval-set nDCG or faithfulness drops below threshold in CI.

## Inputs Required

| Input | Description | Example | Required |
|-------|-------------|---------|----------|
| `pipeline_name` | RAG pipeline id | `support-kb-rag` | Yes |
| `eval_set` | Labeled QA + ground-truth chunks | `evalset_v3.jsonl` | Yes |
| `vector_store` | Vector DB + collection | `qdrant://kb_v2` | Yes |
| `embedding_model` | Current embedder | `text-embedding-3-large` | Yes |
| `reranker` | Reranker if any | `bge-reranker-v2-m3` | No |
| `top_k` | Retrieval depth | `8` | Yes |
| `judge_model` | LLM judge for eval | `gpt-4o` | Yes |

## Required Access

| Scope | Purpose | Read/Write | Sensitivity |
|-------|---------|-----------|-------------|
| Vector store | Query embeddings + retrieve | Read | Medium |
| Eval dataset | Ground-truth QA pairs | Read | Medium |
| Source repo | Inspect chunking/prompt code | Read | Low |
| LLM API (judge) | Score faithfulness/relevance | Invoke | Medium |
| Traces/logs | Inspect live RAG requests | Read | Medium |

## Assumptions

- A labeled eval set with questions, gold answers, and (ideally) gold chunk IDs
  exists or can be bootstrapped to at least ~50 items.
- The vector store is queryable read-only and returns scores.
- The generation prompt and chunking code are available in source.
- A judge LLM is available for reference-free metrics.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Eval set too small/biased | High | High | Report CIs; expand set; stratify by topic |
| LLM-judge bias inflates scores | Medium | Medium | Calibrate judge vs human labels on a subset |
| Eval sends sensitive corpus to external API | Medium | High | Use approved endpoints; redact PII in eval items |
| Overfitting to the eval set | Medium | Medium | Hold out a test split; rotate eval items |

## Constraints

- Read-only against the vector store and corpus; no re-indexing during the audit.
- Only approved LLM endpoints for judging; respect data-residency for the corpus.
- Bound judge-LLM spend with a per-run token budget.
- Do not modify the production pipeline; deliver recommendations only.

## Agent Persona

Adopt the persona of a **Principal AI/ML Engineer specializing in information
retrieval and RAG evaluation**. You separate retrieval quality from generation
quality religiously, because conflating them wastes weeks. Tone: empirical,
metric-driven, skeptical of vibes and demos. You never claim an improvement
without a measured lift on a held-out set, and you always report confidence
intervals. Follow
[`docs/AI_AGENT_STANDARDS.md`](../../docs/AI_AGENT_STANDARDS.md) for data
handling and evidence standards.

## Planning Instructions

1. Load the eval set; verify it has questions, gold answers, and (if present)
   gold chunk IDs. If chunk IDs are missing, plan to derive them or use
   reference-free context metrics.
2. Snapshot the current config: chunk size/overlap, embedding model, top-k,
   reranker, and the generation prompt.
3. Plan the two-phase evaluation: retrieval-only metrics first, then end-to-end
   generation metrics — so you can attribute failures to a stage.
4. Externalize the plan and token budget; when `human_in_the_loop` is
   `required`, get approval before spending on judge-LLM calls.

## Execution Instructions

Compute retrieval metrics (recall@k, MRR, nDCG) against gold chunk IDs:

```python
# retrieval_eval.py — stage 1: retrieval-only quality
import numpy as np

def recall_at_k(retrieved_ids, gold_ids, k):
    hit = len(set(retrieved_ids[:k]) & set(gold_ids))
    return hit / max(1, len(gold_ids))

def mrr(retrieved_ids, gold_ids):
    for rank, rid in enumerate(retrieved_ids, start=1):
        if rid in gold_ids:
            return 1.0 / rank
    return 0.0

def ndcg_at_k(retrieved_ids, gold_ids, k):
    dcg = sum((1.0 / np.log2(i + 2)) for i, rid in enumerate(retrieved_ids[:k]) if rid in gold_ids)
    idcg = sum(1.0 / np.log2(i + 2) for i in range(min(k, len(gold_ids))))
    return dcg / idcg if idcg else 0.0

# aggregate over the eval set -> mean +/- 95% CI
```

Run the Ragas harness for generation-side metrics:

```python
# rag_eval.py — stage 2: end-to-end generation quality
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness, answer_relevancy, context_precision, context_recall,
)

ds = Dataset.from_list([
    {"question": q, "answer": a, "contexts": ctxs, "ground_truth": gt}
    for q, a, ctxs, gt in eval_rows
])

result = evaluate(ds, metrics=[faithfulness, answer_relevancy,
                               context_precision, context_recall])
print(result)  # {'faithfulness': 0.71, 'answer_relevancy': 0.83, ...}
```

Probe chunking and inspect a failing case's retrieved context:

```python
# Diagnose: is the gold passage even retrievable at higher k?
for k in (5, 10, 20, 50):
    print(k, mean_recall_at_k(eval, k))
# If recall@50 >> recall@8, the answer exists but ranking/top-k is the problem.
```

Query the vector store directly to inspect scores and neighbors:

```bash
# Qdrant: retrieve neighbors + scores for a known question embedding
curl -s "$QDRANT_URL/collections/kb_v2/points/search" \
  -H "Content-Type: application/json" \
  -d '{"vector": [/* query embedding */], "limit": 20, "with_payload": true}' \
  | jq '.result[] | {id, score, title: .payload.title}'
```

Compare with and without reranking to isolate reranker value:

```python
# A/B: base retrieval vs reranked top-k -> delta in nDCG@8 and faithfulness
base = evaluate_pipeline(reranker=None)
rerank = evaluate_pipeline(reranker="bge-reranker-v2-m3")
print("nDCG@8 delta:", rerank.ndcg8 - base.ndcg8)
```

## Investigation Workflow

```mermaid
flowchart TD
    A[Start audit] --> B[Load eval set + snapshot config]
    B --> C[Stage 1: retrieval-only metrics]
    C --> D{recall@k adequate?}
    D -->|No| E[Sweep k + inspect chunk sizes]
    E --> F{recall@50 >> recall@k?}
    F -->|Yes| G[Ranking/top-k bound -> add reranker/raise k]
    F -->|No| H[Corpus/chunking/embedding bound]
    D -->|Yes| I[Stage 2: generation metrics]
    G --> I
    H --> I
    I --> J{faithfulness adequate?}
    J -->|No| K{context recall high but faithfulness low?}
    K -->|Yes| L[Generation-bound -> fix prompt/grounding]
    K -->|No| M[Retrieval-bound -> improve context]
    J -->|Yes| N[Measure hallucination rate + trace causes]
    L --> N
    M --> N
    N --> O[Rank improvements by expected lift + report]
```

## Analysis Framework

Score the pipeline and, crucially, **attribute** failure to a stage:

| Metric | Meaning | Healthy threshold |
|--------|---------|-------------------|
| recall@k | Gold chunk in top-k | > 0.85 |
| nDCG@k | Ranking quality | > 0.70 |
| MRR | Rank of first relevant | > 0.60 |
| context precision | Retrieved context is on-topic | > 0.70 |
| context recall | Retrieved context covers the answer | > 0.80 |
| faithfulness | Answer grounded in context | > 0.90 |
| answer relevancy | Answer addresses the question | > 0.85 |

Attribution logic:

- **High context recall + low faithfulness** → generation-bound: the model has
  the facts but ignores/contradicts them. Fix the prompt (force grounding,
  add "answer only from context"), lower temperature, or add citation
  requirements.
- **Low context recall** → retrieval-bound: the answer never reaches the model.
  Fix chunking (right-size, semantic/late chunking), embeddings (domain-tuned
  or stronger model), top-k, or add a reranker.
- **recall@50 ≫ recall@8** → ranking-bound: passages exist but rank too low. A
  reranker is the highest-leverage fix.
- Chunk size heuristic: start 256–512 tokens with 10–20% overlap; oversized
  chunks dilute embeddings, undersized chunks split answers.
- Always rank fixes by expected metric lift ÷ effort, and validate on a held-out
  split to avoid overfitting the eval set.

## Decision Tree

```mermaid
flowchart TD
    Start[Wrong/weak answers] --> Q1{context recall >= 0.80?}
    Q1 -->|No| Q2{recall@50 >> recall@k?}
    Q2 -->|Yes| A1[Add reranker / raise top-k]
    Q2 -->|No| Q3{chunks well-sized?}
    Q3 -->|No| A2[Re-chunk: 256-512 tok, semantic boundaries]
    Q3 -->|Yes| A3[Upgrade/domain-tune embedding model]
    Q1 -->|Yes| Q4{faithfulness >= 0.90?}
    Q4 -->|No| A4[Fix prompt: force grounding + citations, lower temp]
    Q4 -->|Yes| Q5{answer relevancy >= 0.85?}
    Q5 -->|No| A5[Improve query rewriting / prompt clarity]
    Q5 -->|Yes| A6[Pipeline healthy: monitor + regression-gate]
```

## Validation Steps

- [ ] Recompute all metrics on a held-out test split, not the tuning split.
- [ ] Calibrate the LLM judge against human labels on ~20 items; report agreement.
- [ ] Confirm each recommended change produced a measured lift in an A/B before
      claiming it.
- [ ] Verify no eval item leaked PII to an external judge endpoint.
- [ ] Reproduce the top hallucination case and confirm the assigned stage cause.

## Expected Outputs

- RAG audit report with retrieval and generation metric tables (with CIs).
- A stage-attribution verdict (retrieval-bound / generation-bound / ranking-bound).
- A/B results for candidate changes (reranker on/off, k sweep, chunk size).
- A hallucination case log with per-case root-cause stage.
- A ranked, effort-estimated improvement plan with expected lift.

## Deliverables

A single audit report following
[`templates/report-template.md`](../../templates/report-template.md), with
corpus PII redacted per
[`docs/AI_AGENT_STANDARDS.md`](../../docs/AI_AGENT_STANDARDS.md). Include the
metric tables, attribution verdict, A/B evidence, and ranked plan.

## Escalation Process

- **P1 (page):** Measured hallucination rate on high-stakes queries (medical/
  legal/financial) above the safety threshold. Notify the product owner + safety
  reviewer within 1 hour; recommend gating those query classes.
- **P2 (ticket):** Retrieval or faithfulness below target on general queries.
  File tickets tagged `rag` with the ranked plan.
- **P3 (backlog):** Marginal ranking/latency improvements.
- If the eval set is too small for a confident verdict, escalate to expand it
  rather than shipping an unreliable conclusion.

## Rollback Strategy

The audit is read-only and changes no production configuration, so no rollback
is required for the audit itself. If, during A/B testing, a temporary shadow
index or experimental collection was created, delete it and confirm the vector
store is back to its original collection set. Judge-LLM spend is bounded by the
pre-approved token budget; if exceeded, halt and report partial results.

## Post-Execution Review

- Was the failure retrieval- or generation-bound? Record it — teams routinely
  guess wrong and tune the wrong stage.
- Which single change delivered the largest measured lift per unit effort?
- Did the LLM judge agree with humans? If not, recalibrate before trusting it.
- Should these metrics become a CI regression gate (fail the build if nDCG or
  faithfulness drops > X%)?

## Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| recall@k | Gold-chunk hit rate in top-k | > 0.85 |
| faithfulness | Grounded-answer fraction | > 0.90 |
| hallucination rate | Unsupported-claim answers | < 3% |
| answer relevancy | On-question answers | > 0.85 |
| judge agreement | Judge vs human label match | > 0.80 |
| regression-gate coverage | % pipeline changes eval-gated | 100% |

## Example Execution

**Inputs:** `pipeline_name=support-kb-rag`, `eval_set=evalset_v3.jsonl` (120
items), `embedding_model=text-embedding-3-large`, `top_k=8`, no reranker,
`judge_model=gpt-4o`.

**Agent reasoning (abridged):** Stage 1 showed recall@8 = 0.62 but recall@50 =
0.94 — the gold passages exist but rank too low: a classic ranking-bound
signature. Chunk inspection revealed 1,200-token chunks (too large), diluting
embeddings. Stage 2: context recall = 0.66, faithfulness = 0.88. Adding a
`bge-reranker-v2-m3` reranker over top-50 lifted recall@8 to 0.89 and nDCG@8
from 0.58 to 0.79; faithfulness rose to 0.93 because better context reached the
model. Re-chunking to 400 tokens with 15% overlap added a further +0.04 recall.
Verdict: **ranking- and chunking-bound**, not generation-bound.

**Sample report excerpt:**

```text
RAG Audit — support-kb-rag (n=120, 95% CI)
  recall@8:        0.62 -> 0.89 (with reranker + rechunk)
  nDCG@8:          0.58 -> 0.79
  context recall:  0.66 -> 0.86
  faithfulness:    0.88 -> 0.93
  hallucination:   6.7% -> 2.5%

Verdict: ranking/chunking-bound (recall@50=0.94 >> recall@8=0.62).

Top improvements (ranked by measured lift/effort):
  R1 Add bge-reranker-v2-m3 over top-50  -> +0.27 recall@8   (S)
  R2 Re-chunk 1200 -> 400 tok, 15% overlap -> +0.04 recall   (M)
  R3 Add "answer only from context + cite" to prompt         (S)
  R4 Build CI regression gate: fail if faithfulness < 0.90   (M)
```

## References

- [`docs/AI_AGENT_STANDARDS.md`](../../docs/AI_AGENT_STANDARDS.md)
- [`templates/report-template.md`](../../templates/report-template.md)
- [Prompt Quality Review](./prompt-quality-review.md)
- [Agent Evaluation Framework](./agent-evaluation-framework.md)
- [Ragas documentation](https://docs.ragas.io/)
- [BEIR retrieval benchmark](https://github.com/beir-cellar/beir)
- [MTEB embedding leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
