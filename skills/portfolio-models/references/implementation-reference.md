# Numerical API and boundary contracts

Install from repository root: `python -m pip install -r requirements.txt`; if using a standalone installed skill directory, install from its `requirements.txt` instead. Source modules are located at `skills/portfolio-models/scripts/`. For a script executing outside that directory, add it to `sys.path` or invoke the provided command-line runner. `SolveResult` contains `weights`, a *model-specific* `objective`, `method`, and scalar `diagnostics`. **Objectives are not comparable across different models without transformation.**

| Method | Function | Objective returned | Key restriction |
|---|---|---|---|
| Equal capital | `models.equal_weight(n)` | weights only | Baseline |
| GMV | `models.minimum_variance(R)` | portfolio variance | PSD covariance |
| MVO | `models.mean_variance(R, risk_aversion)` | mean − ½lambda variance | lambda per frequency |
| Ellipsoidal mean RO | `models.robust_mean_variance(R,kappa=...)` | worst mean − risk | mean uncertainty set |
| CVaR | `models.cvar(R,alpha)` | minimum tail loss | linear loss |
| Wasserstein DRO CVaR | `models.wasserstein_dro_cvar(R,epsilon,alpha)` | worst-case tail loss | L1, W1, unbounded support |
| HRP | `models.hrp(R, linkage_method=...)` | variance, not HRP loss function | average/single linkage |
| Black-Litterman posterior | `models.black_litterman_mean(...)` | posterior mean vector | explicit prior and views |
| Inverse-volatility | `advanced_models.inverse_volatility(R)` | portfolio variance | positive vol |
| Shrunk GMV | `advanced_models.shrinkage_minimum_variance(R)` | shrunk variance | Ledoit-Wolf or OAS |
| Maximum Sharpe | `advanced_models.maximum_sharpe(R,risk_free)` | excess Sharpe | positive excess; no caps |
| Maximum diversification | `advanced_models.maximum_diversification(R)` | diversification ratio | no caps |
| Equal risk budget | `advanced_models.equal_risk_contribution(R)` | portfolio variance | PD covariance; no caps |
| General risk budgeting | `advanced_models.risk_budgeting(R,budgets)` | portfolio variance | strictly positive budgets |
| Mean-semivariance | `advanced_models.mean_semivariance(R,lambda,target)` | mean − downside penalty | threshold per period |
| Mean-CVaR | `advanced_models.mean_cvar(R,alpha,lambda)` | mean − lambda CVaR | scenario LP |
| Covariance RO | `advanced_models.robust_covariance_mvo(R,lambda,radius)` | worst-case mean/variance utility | Frobenius covariance ball |
| BL allocation | `advanced_models.black_litterman_portfolio(...)` | BL posterior mean/variance utility | views and prior supplied |
| Kelly | `advanced_models.growth_optimal_kelly(R)` | mean log(1+return) | positive gross return |
| Entropic | `advanced_models.entropic_risk(R,gamma)` | entropic loss functional | gamma>0 |
| Minimum CDaR | `advanced_models.minimum_cdar(R,alpha)` | additive-P&L CDaR | ordered paths |
| Mean-CDaR | `advanced_models.mean_cdar(R,alpha,lambda)` | mean − lambda additive CDaR | ordered paths |
| Minimum TE | `advanced_models.tracking_error_minimum(R,b)` | active variance | benchmark weights sum 1 |
| Turnover-aware GMV | `advanced_models.turnover_regularized_minimum_variance(R,previous,lambda)` | variance + L1 turnover | feasible previous weights |

**Conventions:** all weights long-only and sum to one; no derivatives, margin or short sale execution. Inputs are per-period decimal simple returns, oldest first. For a provided `cap`, feasibility requires `N*cap >= 1`. A full financial research result must additionally follow [point-in-time protocol](backtest-protocol.md).

**Run:** `python skills/portfolio-models/scripts/demo.py`; `python skills/portfolio-models/scripts/comparison_demo.py`; `python -m pytest -q tests`. For custom data `python skills/portfolio-models/scripts/portfolio_cli.py --help`.
