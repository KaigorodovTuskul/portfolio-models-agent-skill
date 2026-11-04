# Robust MVO vs Distributionally Robust Optimization (DRO)

## Robust MVO: ellipsoidal uncertainty in estimated **mean** ([EN-08])

Assume estimated means belong to `U_μ={μ_hat + C_μ^(1/2) u : ||u||_2 ≤ κ}`, with `C_μ` PSD and in squared-return units. Then:

`min_{μ∈U_μ} μ'w = μ_hat'w − κ sqrt(w'C_μ w)`.

**Concrete objective:**

`max_w μ_hat'w − κ sqrt(w'C_μ w) − (λ/2)w'Σw`, with `1'w=1`, bounds, etc.

`C_μ=Σ/T` is an *iid estimator approximation*; overlapping / heteroskedastic financial returns need block bootstrap or HAC covariance for mean uncertainty. When `κ=0`, model reduces **exactly** to standard MVO with the same λ. A robust mean-uncertainty term cannot be called *robust covariance*.

**Calibration:** select λ, κ on nested historical folds, report distribution of selected values including zero; test the same λ for κ=0 vs κ>0; compare fixed vs tuned, risk-matched, 4- vs 6-asset universes and crisis exposure. No full-sample look-ahead or tuning to final holdout.

**Another family:** uncertainty in covariance `U_Σ`, e.g. `max_w min_{μ∈Uμ} μ'w − (λ/2) max_{Σ∈UΣ}w'Σw`; formulation depends on `UΣ` PSD structure and is **not** implemented by just adding a bigger λ. Refer to Goldfarb–Iyengar for principled conic formulations.

## 1-Wasserstein DRO-CVaR: exact special case ([EN-09], [EN-10])

Let historical return vectors be `r_i`, empirical distribution `P_hat`, ground distance `d(r,s)=||r−s||_1` (dimensionless returns), and `W_1(Q,P_hat)≤ε`. Assume **unbounded R^N support**, finite 1st moment, linear portfolio loss `L=−w'r`, and no scenario-dependent nonlinear costs. The dual norm is `||w||_∞`; one tractable worst-case risk formulation is:

`sup_{Q: W1≤ε} CVaR_α^Q(−w'r) = CVaR_α^{P_hat}(−w'r) + ε ||w||_∞/(1−α)` under the interchange/regularity assumptions of this special case.

Equivalent LP for nonnegative long-only weights: minimize

`η + [Σ_i u_i/T + ε z]/(1−α)`

subject to `u_i≥−r_i'w−η`, `u_i≥0`, `z≥w_j` for all uncertain coordinates `j`, `1'w=1`, `w≥0`, bounds. To model a perfectly deterministic cash coordinate, restrict uncertainty to a support where that coordinate is fixed, and constrain `z` only for uncertain returns; **document the support**. If all uncertain coordinates have 100% cash `w_cash=1`, the penalty will incorrectly assign cash risk unless cash truly is uncertain in the chosen ambiguity set.

**Warning:** Different **ground norm** changes the dual norm and therefore the penalty; L∞ ground → L1 dual and constant penalty for long-only fully invested weights (no selection effect). Finite support, covariance ambiguity, Wasserstein-2, extra linear constraints, nonlinear payoff and mean-CVaR give **different reformulations**. Never call a generic `ε||w||` an exact DRO model without deriving its assumptions.

**Radius ε is in return units** (monthly 0.01 = 1 percentage point in the L1 ground metric). Choose by nested validation or a documented statistical calibration; the `ε=0` control must recover empirical CVaR exactly. Compare `ε` sensitivity and effective cash / max weight concentration.

## Minimum audit for an RO/DRO implementation

1. Write explicit uncertainty set, support, ground norm, dimensions and hypothesis.
2. Derive robust counterpart; state whether **exact or surrogate**.
3. Check κ=0 / ε=0 baseline equivalence to machine precision.
4. Validate dual objective with tiny brute-force or LP toy cases.
5. Repeat with equal OOS and risk, costs, and simple cash baselines; inspect selected hyperparameters and post-shock weights.

**Scale discipline:** feature scaling or multiplying one asset's return series changes the Wasserstein ground distance and radius meaning; the geometry must be stated in original or explicitly standardized coordinate units. A high-dimensional asset universe with very different volatilities needs a justified weighted ground norm, not arbitrary normalization.

## Covariance-uncertain Robust MVO — exact Frobenius special case ([EN-08], [EN-21])

In addition to uncertain means, specify a symmetric PSD covariance ambiguity set `U_Sigma={S_hat+Delta : Delta symmetric, ||Delta||_F<=rho, S_hat+Delta PSD}` for `rho>=0`. For any fixed `w`, the maximum quadratic variance over this set is:

`max_{S∈U_Sigma} w'Sw = w'S_hat w + rho*||w||_2^2`.

Proof: `w'Delta w = <Delta,ww'> <= ||Delta||_F ||ww'||_F = rho||w||_2²`; the upper bound is attained by a PSD rank-one `Delta = rho ww'/||w||²`. Thus optimize `max_w mu_hat'w - (lambda/2) w'(S_hat+rho I)w`. **API:** `robust_covariance_mvo(R, risk_aversion=3., radius=0.001)`. Here rho is **variance-unit** (squared decimal return per observation); this is *not* the same as ellipsoidal mean uncertainty `kappa` or Wasserstein radius `epsilon`. For `rho=0` it reduces to ordinary MVO.

It is a genuine exact robust counterpart for this **specific Frobenius covariance set**, not the broad set of robust covariance models. Choosing rho without historical calibration can make it little more than ridge regularization. For a meaningful test compare constrained Sharpe, sample GMV, shrinkage GMV, mean uncertainty and joint uncertainty under nested OOS validation.
