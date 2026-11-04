# Diversification, downside and implementation-aware optimization

**Notation:** `R` is `T × N` simple returns, `mu` sample per-period return vector, `S` PSD per-period covariance, `w >= 0`, `1'w=1`. All methods here use **per-period** units. Call `advanced_models.py` after importing the scripts directory. Full bibliography IDs in [source catalog](source-catalog.md).

## Shrinkage GMV: Ledoit-Wolf / OAS [EN-02, EN-15]

**Purpose:** stabilize covariance estimation when the observation count is small relative to the asset count. Optimize `min_w w'S_shrunk w`, where `S_shrunk=(1-delta)S_sample+delta F` and the target `F` and `delta` depend on the estimator. Our callable uses `sklearn.covariance.LedoitWolf` (scaled identity target) or `OAS` (Gaussian-reference shrinkage) and returns the estimated intensity. These are distinct from a fixed user-chosen diagonal shrinkage rule. **API:** `shrinkage_minimum_variance(R, method='ledoit_wolf')` or `method='oas'`. **Check:** covariance PSD, shrinkage in [0,1], sample window contains no future data. OAS's Gaussian reference need not hold in financial tails.

## Maximum expected Sharpe / tangency [EN-01]

**Purpose:** maximize `(mu'r-rf)/sqrt(w'Sw)`, written `(mu-rf*1)'w / sqrt(w'Sw)`. **Exact long-only transformation for a positive maximum:** `min_{y>=0} y'Sy` subject to `(mu-rf*1)'y=1`; normalize `w=y/(1'y)`. Requires at least one strictly positive expected excess return; the equivalent QP here has **no upper-weight caps**. **API:** `maximum_sharpe(R, risk_free=0.005)`. **Check:** positive Sharpe, positive variance, unit-consistent rf. Past sample mean should not be assumed a reliable forecast.

## Inverse volatility, ERC and risk budgets [EN-07, EN-16]

- **Inverse volatility:** `w_i ∝ 1/sigma_i`; accounts for individual asset risk but ignores cross-correlations. `inverse_volatility(R)`.
- **ERC:** `RC_i=w_i(Sw)_i / sqrt(w'Sw)`, with `RC_i / sum_j RC_j = 1/N`. **Risk budgeting:** replace `1/N` with positive budgets `b_i` summing to 1. Solve strictly convex unnormalized problem `min_{y>0} 0.5*y'Sy - sum_i b_i log(y_i)`; normalize `w=y/sum(y)`. `risk_budgeting(R, budgets=b)` and `equal_risk_contribution(R)`. Requires positive-definite covariance and **no upper-weight caps**; the library validates final budget errors. Risk parity is *not* equal capital weights and not automatically a defensive strategy.

## Maximum Diversification [EN-17]

**Purpose:** maximize diversification ratio `DR=(sum_i w_i*sigma_i)/sqrt(w'Sw)`. With long-only weights and positive asset volatilities, globally solve `min_{y>=0} y'Sy` subject to `sigma'y=1`, then normalize. **API:** `maximum_diversification(R)`. This convex transformation does not preserve an extra arbitrary `w_i <= cap`; use the formulation as documented. **Check:** compare with inverse volatility in a diagonal covariance toy case.

## Mean-Semivariance [EN-01]

**Purpose:** penalize downside variability relative to target `h` instead of upside variance: `max_w mu'w - (lambda/2T)sum_t min(R_t w-h,0)^2`. **API:** `mean_semivariance(R, risk_aversion=5., target=0.)`. **Check:** target in decimal per-period units; `h=0` is not the same as downside below the mean. Convex negative objective under long-only budget bounds; numerical SLSQP validates convergence.

## Entropic risk [EN-18]

**Purpose:** minimize the convex risk functional `rho_gamma(-w'R)=1/gamma * log[(1/T)sum_t exp(-gamma R_t w)]`, `gamma>0`. **API:** `entropic_risk(R, gamma=5.)`. `gamma` has units inverse-return; increasing it emphasizes losses. **Check:** log-sum-exp stabilization and limiting behavior as gamma tends to zero (approaching negative sample mean). This is a fixed-parameter *entropic risk*, **not EVaR** (which separately optimizes the exponential parameter).

## Benchmark tracking [EN-01]

**Purpose:** minimize sample variance of active return `min_w (w-b)'S(w-b)`, with benchmark capital weights `b`. **API:** `tracking_error_minimum(R, benchmark=b)`. **Check:** zero tracking error if benchmark is feasible; tracking error ignores mean active underperformance.

## Turnover-regularized GMV [EN-19]

**Purpose:** avoid costly unnecessary reallocation: `min_w w'Sw + lambda*sum_i |w_i - w_previous,i|`. Exact epigraph formulation uses auxiliary `t_i >= ±(w_i-w_prev,i)`, solved as convex quadratic program with SLSQP. **API:** `turnover_regularized_minimum_variance(R, previous, turnover_penalty=0.001)`. This lambda is in **variance / absolute-weight units** and is **not** the same numerical quantity as a transaction fee in dollars. **Check:** lambda→0 approaches GMV; large lambda tends to no trade. `sum(abs(delta_w))` is two-sided absolute turnover, with one-sided traded notional typically half that when self-financing.

## Implementation checks

- All return/covariance matrices must be point-in-time, PSD where required and in consistent frequency units.
- Compare methods with identical feasible sets; the homogeneous tangency/diversification transforms and log-barrier risk budgeting intentionally do not accept arbitrary per-asset caps.
- Record nonconvergence and infeasibility. Results are long-only capital weights, **not** derivative positions or executable orders.
- Consult [worked examples](worked-examples.md) and run `python -m pytest -q tests` locally.
