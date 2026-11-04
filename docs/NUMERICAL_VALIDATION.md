# Local numerical validation

Validated against release source using Python 3.13, NumPy, SciPy, scikit-learn, PyYAML and pytest on 2026-11-04. No remote CI service or brokerage data is required.

## Deterministic unit and analytical tests

```bash
python -m pytest -q tests
python scripts/goal_workflow.py check
```

The suite covers feasibility, analytic GMV weights, empirical CVaR fractional tails, DRO-CVaR zero-radius equivalence, robust MVO zero-uncertainty equivalence, mean-CVaR and additive CDaR against 2-asset brute-force grids, expected Sharpe against a dense grid, covariance ambiguity's rank-one worst case, risk-budget contributions, Kelly's objective, Black–Litterman posterior boundary conditions, log-sum-exp limits, shrinkage covariance, turnover penalties, code routing, and all three README language paths.

## Randomized numerical stress sweep

```bash
python scripts/stress_solvers.py
```

The deterministic sweep uses twenty seed values from 100 through 119, five assets and thirty-six monthly **synthetic** observations per seed; twelve solver configurations per seed. The sweep checks numerical convergence, finite weights, long-only bounds and unit budget, for a total of 240 calls. It does not measure market profitability, robustness of forecasting, or future investment outcomes.

## All command-line models

```bash
python skills/portfolio-models/scripts/portfolio_cli.py datasets/synthetic_monthly_returns.csv --model erc
python skills/portfolio-models/scripts/portfolio_cli.py datasets/synthetic_monthly_returns.csv --model hrp-single
python skills/portfolio-models/scripts/portfolio_cli.py datasets/synthetic_monthly_returns.csv --model mean-cvar --alpha 0.9 --lambda-risk 3
python skills/portfolio-models/scripts/portfolio_cli.py --help
```

A completed fit reports `status="in_sample_fit_only"`; that status is intentional. A historical OOS claim requires independently sourced, point-in-time, executable data and the dedicated [backtest protocol](../skills/portfolio-models/references/backtest-protocol.md).

## Independent methodological approval

A passing test suite establishes numerical consistency of the documented sample formulations; it is **not** an independent expert sign-off or an 8.5/10 external reviewer score. See [GOAL review protocol](../workflows/goal-workflow.md). The release contains no manufactured reviewer reports.
