# GOAL review rubric — strict, unanchored to author's self-confidence

**Four independently rated axes, 1–10 with anchors:** 4 = starting point, 6 = ordinary usable skill, 8 = high-quality sophisticated production-level candidate, **8.5+** = aspirational SOTA-DFS/enterprise-grade *only with direct evidence*. Never reward number of files. Assign evidence-backed score to one decimal.

| Role | Inspect | 8.5+ must demonstrate |
|---|---|---|
| ARCHITECT | SKILL.md invocation, context budget, pointers, goal gates, repository packaging, security | compact routing, spec compliance, no redundant context, checkable stop conditions, clean CI |
| SOURCES | trace mathematical and market claims to authentic EN/RU/ZH sources, DOI, year, accessibility, exclusions | no fabricated references, originals prioritized, rights and source limitations, source -> formula traceability |
| QUANT | exact optimization objective, units, uncertainty sets, sign, constraints, risk metrics, numerical stability | analytically verified boundary cases, solver failure handling, no look-ahead, precise DRO theorem assumptions |
| PRACTICE | runnable Python, worked examples, risk tests, synthetic/real labeling, data provenance, simplicity | reproducible examples with negative cases, feasible constraints, realistic backtest rules, test observability |

**Blocking defects regardless of arithmetic mean:** invalid primary math, failed tests, invented citations, look-ahead, false historical investability, unsafe credentials, broken SKILL.md. If any blocker exists, RELEASE DENIED.

**Independent reviewers:** each must use isolated LLM run/model or another independent reviewer. Include run ID, model and file hashes. One model pretending to be four reviewers is NOT independent and cannot pass the requested external score gate.

**Decision:** `mean(score_4)>8.5` **AND** all four independent, no blockers, tests pass. `>=8.5` alone is not sufficient. Iterate unbounded in external harness; preserve logs of every round (no rounding up).
