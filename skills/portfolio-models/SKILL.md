---
name: portfolio-models
description: Select, formulate, implement, compare, or audit portfolio optimization models including MVO, GMV, Black-Litterman, CVaR, CDaR, risk budgeting, HRP, Kelly, robust covariance/mean MVO and Wasserstein DRO. Use for asset allocation, estimation-error control, stress testing, risk decomposition, and point-in-time backtesting.
license: MIT
metadata:
  version: "1.0.0"
  domain: "quantitative-finance"
  language: "en"
---

# Portfolio Models

**Contract:** Specify the economic objective, precise optimization problem, data assumptions, constraints and benchmark **before** selecting a model. Use only the references relevant to the task.

## Procedure

1. **Frame.** Record investor type, base currency, investable assets, evaluation frequency, return objective, losses tolerated, liquidity, shorts/leverage, turnover, per-asset limits and holding horizon. Determine whether the answer is conceptual, computational, or an empirical claim. **Complete when:** objective and constraints are explicit.
2. **Normalize.** For calculations involving prices, returns, bonds, FX, derivatives, rates or cash, load [notation and data](references/notation-and-data.md). Require point-in-time availability and total-return consistency. **Complete when:** all columns share currency and observation period; missing/stale values are identified.
3. **Route.** For model selection load [model map](references/model-map.md), then **only** the branch needed: [classical](references/models-classical.md), [diversification, risk budgets and regularization](references/models-extended.md), [tails and drawdowns](references/models-tail.md), [robustness and DRO](references/models-robust.md), or [Kelly and antifragility](references/convexity-and-growth.md). **Complete when:** exact mathematical variant, source and numerical method are specified.
4. **Compute.** For a runnable calculation consult [worked examples](references/worked-examples.md) and the executable modules `scripts/models.py` and `scripts/advanced_models.py`. Verify solver status, constraints, objective at returned weights, limiting cases and numerical units. **Complete when:** reproducible invocation and checks succeed.
5. **Validate.** For historical claims use [backtest protocol](references/backtest-protocol.md), [metrics and inference](references/metrics-and-inference.md), and [failure modes](references/failure-modes.md). **Complete when:** full out-of-sample chronology, trade assumptions, costs, simple benchmarks, stress and uncertainty are reported.
6. **Resolve disputes.** Follow [formula trace](references/formula-trace.md) to the [annotated source catalog](references/source-catalog.md). Read the original paper for theorem-specific support, ambiguity-set details and any material exception. **Complete when:** the actual formula is distinguished from approximations and implementations.

## Mathematical and empirical invariants

- Use decimal simple **total returns** with a consistent sampling frequency; annualize only at reporting time. A price index, official exchange rate or policy rate is not an investable, frictionless instrument.
- Optimize with only information available before the decision. Fit forecasting and hyperparameters on nested **past** data. Evaluate trading costs, drift, halts, margin and FX conversion as applicable.
- Give the exact uncertainty set before calling a model *robust*. The implemented Wasserstein DRO is a **specific** 1-Wasserstein, L1-ground, unbounded-support, linear-loss CVaR case—not a generic DRO engine.
- Report empirical monthly/daily drawdowns separately from **additive-P&L CDaR**, which is not equivalent to compounded NAV drawdown.
- Different methods need common dates, feasible universes, comparable realized risk and simple baselines. A high CAGR alone does not establish statistical superiority.
- An options hedge, trend-following short or a stable portfolio is not automatically antifragile. Evaluate convexity, carried cost, tail conditional returns and execution access separately.

## Output

For methodology: **model, objective/equations, constraints, estimators, hyperparameters, edge cases, source, executable illustration**. For a benchmark also report **as-of, available instruments, exact OOS dates, training/validation windows, transaction costs, baseline, CAGR, realized volatility, drawdown, CVaR, turnover, uncertainty intervals and data/execution limitations**.

The entry file routes work; it does not duplicate the math. Keep all new code, formulas and experiments in the appropriate reference or script rather than expanding this file.
