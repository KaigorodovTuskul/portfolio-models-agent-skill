# Classical, shrinkage, Bayesian methods

All weights below refer to **capital fractions**; default `1'w=1`, `0≤w≤w_max` unless otherwise specified.

## Markowitz / mean–variance (1952, [EN-01])

- **Goal:** `max μ'w - (λ/2)w'Σw` or `min w'Σw` subject to `μ'w≥μ_target`. `λ` trade-off must match frequency; benchmark against 1/N.
- **Mechanics:** estimate `μ`, covariance `Σ`; solve convex QP for PSD `Σ`; realised OOS return must include trades, costs, drift.
- **Failure:** small error in `μ` can cause large weight changes; alternatives shrink μ, bound weights, use robust forecasts.
- **Test:** for identical μ and positive λ, unconstrained solution reduces to GMV; when λ→∞ weights approach GMV. `μ` and `Σ` both use same horizon.

## Global minimum variance (GMV) ([EN-01], shrinkage [EN-02])

- **Goal:** `min_w w'Σw`, `1'w=1`; unconstrained `w*=Σ⁻¹1/(1'Σ⁻¹1)`, requiring invertible covariance and *no binding bounds*. With bounds solve QP.
- **Covariance regularisation:** Ledoit–Wolf shrinkage `Σ_hat=(1-δ)S+δF` toward a structured target; `δ` is fitted on training data, not selected using holdout.
- **Failure:** covariance regime shifts, concentration in bond/cash proxies, missing tail risk. Explicitly report max holdings, gross/net, interest-rate dependence.
- **Test:** 2-asset closed form `w1=(σ2²-σ12)/(σ1²+σ2²−2σ12)` before bounds.

## Black–Litterman (1991/1992, [EN-03])

- **Goal:** estimate **posterior mean**, then feed it into an optimizer. Prior `π=δ Σ w_market`; views `P μ = Q`, confidence `Ω`, prior covariance `τΣ`.
- **Mean:** `μ_BL = π + τΣ P' (P τΣ P' + Ω)⁻¹(Q−Pπ)` (solve linear systems, do not explicitly invert numerically).
- **Failure:** views chosen with hindsight, inconsistent market cap weights, double-counting excess vs total returns, τ and Ω poorly identified.
- **Test:** `P` with zero rows returns prior exactly; increasing `Ω` weakens views.

## Simple baselines are mandatory ([EN-04])

`1/N`, buy-and-hold, calendar-rebalanced 1/N, 100% cash, fixed cash/risk allocation within common constraints. Different policies have different realised turnover — account for it. DeMiguel–Garlappi–Uppal (2009) is a caution about estimation error, **not** a theorem that 1/N always wins.


**Black-Litterman allocation implementation:** `advanced_models.black_litterman_portfolio(R, prior, P, Q, omega, tau, risk_aversion, cap)` applies the `models.black_litterman_mean` posterior to the explicit sample covariance MVO objective. An equilibrium prior must be supplied; this function does not silently infer market capitalization or the CAPM risk aversion. A zero-view test must reproduce MVO when the prior equals the sample mean.
