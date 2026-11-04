# Tail losses, drawdown optimization and hierarchy

Input `R` is a T × N chronological matrix of per-period **simple total returns**. The baseline library in `scripts/models.py` implements empirical CVaR and HRP; `scripts/advanced_models.py` implements Mean-CVaR and additive-P&L CDaR. Refer to [original sources](source-catalog.md).

## Empirical CVaR / Expected Shortfall [EN-05]

For scenario portfolio losses `l_t=-R_t w`, with confidence `alpha∈(0,1)`:

`CVaR_alpha(l)=min_eta [ eta + (1/(T*(1-alpha)))sum_t max(l_t-eta,0) ]`.

The linear program has `u_t>=-R_t w-eta`, `u_t>=0` and minimizes `eta + sum_t u_t/[T(1-alpha)]`. `cvar(R, alpha=.9)` minimizes this loss over feasible weights; optional `min_expected_return` creates the **nominal** mean-return constraint. **At alpha=.90, only 10% of a short sample determines the tail.** Report tail sample size and stress tests.

## Mean-CVaR [EN-05]

`max_w mu'w - lambda*CVaR_alpha(-R w)`, `lambda>0`; exact scenario LP with both terms in objective. `mean_cvar(R, alpha=.90, risk_aversion=2.)`. This does *not* mean a minimum-CVaR portfolio subject to a return target unless parameters are calibrated to an equivalent efficient-frontier point. **Check:** zero-lambda limit with a separate direct expected-return optimizer, and compare LP objective to direct tail calculation at resulting weights.

## Conditional Drawdown at Risk (CDaR) [EN-20]

The **implemented** objective is CDaR of *additive cumulative P&L* at constant capital weights: `S_t=sum_{i<=t} R_i w`, `M_t=max(0,S_1,...,S_t)`, `D_t=M_t-S_t`. Minimize empirical `CVaR_alpha(D_1,...,D_T)` with running-maximum LP epigraph (`M_t>=M_{t-1}`, `M_t>=S_t`, `M_t>=0`). `minimum_cdar(R)` and `mean_cdar(R, risk_aversion=2.)` are exact for this **explicit definition**. Compounded NAV drawdown is `NAV_t/max_{j<=t}NAV_j-1`, a different, generally nonlinear quantity, especially with leverage/rebalancing; never label the additive CDaR result as compounded NAV CDaR. Input ordering is mathematically essential.

## Hierarchical Risk Parity (HRP) [EN-06]

Compute `distance_ij = sqrt((1-corr_ij)/2)`; cluster using single linkage (original-style) or average linkage with optimal leaf ordering; recursively bisect the dendrogram order and allocate between clusters inversely proportional to their inverse-diagonal-variance proxy. `hrp(R, linkage_method='single')` selects original-style single linkage; `hrp(R)` retains the default average-linkage variant for compatibility. **Neither is guaranteed to reproduce every implementation detail of the author's algorithm.** Hierarchical weights do not require expected returns and are sensitive to clustering choice, lookback and asset selection.

## Risk budgeting / Equal Risk Contribution (ERC) [EN-16]

For positive-definite covariance, use `risk_budgeting` / `equal_risk_contribution` from `advanced_models.py`; see [diversification models](models-extended.md) for the exact convex log-barrier objective and validation of risk-contribution fractions. Risk parity is a risk-exposure method, not a guarantee of low tail loss.

## Why tail metrics can disagree

Variance penalizes both positive and negative deviations, CVaR focuses on *cross-sectional* scenario loss magnitudes, and CDaR explicitly uses the **chronological order** of the path. Two return samples with the same histogram but different order have the same empirical CVaR and can have different CDaR. Report sample/tail counts and crisis liquidity; monthly-index CVaR cannot detect forced liquidations inside the month.
