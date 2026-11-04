# Minimal calculations — hand-verifiable

Use decimals and **period-matched** units. Complete, executable demonstrations: `scripts/demo.py`; underlying implementation: `scripts/models.py`.

## Two-asset GMV

Given `σ_A²=0.04`, `σ_B²=0.09`, `Cov(A,B)=0.012` (in **same annual return variance units**), unconstrained long-only optimum:

`w_A=(0.09−0.012)/(0.04+0.09−2·0.012)=0.735849...`; `w_B=0.264151...`. Verify sum 1; neither weight violates `[0,1]`. `w'Σw` must be less than 0.04 and 0.09. This is not expected return optimization.

## Scenario CVaR at 75% (4 equiprobable observations)

`R=[(.04,.01),(-.02,.02),(.03,-.01),(-.08,.01)]`; `w=(.5,.5)`. Portfolio returns are `[.025,0,.01,-.035]`; losses `[-.025,0,-.01,.035]`. Worst 25% is one loss: `CVaR_0.75=0.035` (3.5%); VaR is quantile-definition dependent in a finite sample. If optimize CVaR across all possible weights, the optimizer may choose another allocation: example computes **risk of fixed w**.

## Exact 1-Wasserstein ambiguity surcharge (special case)

Same 4 scenarios; L1 ground return distance, unbounded return support, α=.75, `ε=.01`, `||w||∞=.5`:

`robust_CVaR = empirical_CVaR + ε*||w||∞/(1−α) = .035+.01*.5/.25=.055` (5.5% worst-case bound). This is **not** a statement about realistic 1% shock frequency: ε is a transport radius in return units, not an arbitrary CVaR margin. Change the ground norm and penalty changes.

## Risk contributions with zero correlation

`Σ=diag(.04,.09)` and `w=(.6,.4)`: contributions to portfolio **variance** are `.6²*.04=.0144` and `.4²*.09=.0144`; equal risk despite unequal capital weights. Risk contribution to volatility is each variance contribution divided by portfolio σ.

## Shock convexity illustration

A bought put at `K=100`, premium 5, expiry `S∈{100,90,70}` yields *net payoff* `{-5,+5,+25}`. Incremental gains increase as S falls beyond strike; buying the put each month imposes repeated premiums and cannot be backtested from this terminal-payoff table alone.

## Further hand-verifiable models

### Global minimum variance, two assets

For `Sigma=[[.04,.012],[.012,.09]]` the long-only unconstrained two-asset GMV first weight is `(.09-.012)/(.04+.09-2*.012) = .078/.106 = .7358490566`; second is `.2641509434`. Code: `minimum_variance(R,cov=Sigma)`; the return matrix only supplies dimension and sample validation in this call. Objective at optimum is `w'Sigma w` **per period**.

### Inverse-volatility and ERC, diagonal covariance

For uncorrelated assets with `sigma=[.2,.3]`, equal risk contribution requires `w_i ∝ 1/sigma_i`, giving `[.6,.4]`. Direct volatility contributions are `w_i²*sigma_i²`, each `.0144`; total portfolio variance `.0288`. This also maximizes the two-asset diversification ratio under a diagonal covariance, but the equivalence does not generally persist under correlations.

### Covariance uncertainty set

Let `w=[.6,.4]`, `Sigma=diag(.04,.09)`, `rho=.01` in **variance** units. Base variance is `.0288` and Frobenius worst-case variance is `.0288 + .01*(.6²+.4²) = .034`. This follows from the rank-one PSD perturbation `Delta=rho*(w w')/(w'w)`. For `rho=0`, the optimizer must exactly reproduce classical MVO at the same lambda.

### Scenario Kelly with a cash alternative

Five equally likely scenarios: risky asset returns `[+.5,+.5,+.5,-.5,-.5]`, cash `0` in every scenario. Let `f` be the risky weight. Solve `max_{0<=f<=1} [3 log(1+.5f)+2 log(1-.5f)]/5`; differentiation gives `3/(1+.5f)=2/(1-.5f)` after canceling common factors, hence `f=.4`. Python:

```python
import numpy as np
from advanced_models import growth_optimal_kelly
R = np.column_stack([[.5,.5,.5,-.5,-.5],np.zeros(5)])
assert np.allclose(growth_optimal_kelly(R).weights,[.4,.6],atol=1e-6)
```

### Additive-P&L CDaR versus standard tail loss

For a single asset with chronological returns `[-.10,+.07,+.06,-.08,+.05]`, cumulative **additive** P&L is `[-.10,-.03,.03,-.05,0]`; running peak including `0` is `[0,0,.03,.03,.03]`; drawdowns are `[.10,.03,0,.08,.03]`. At alpha=.8, CDaR is the worst one of five drawdowns: `.10`. Change the order of returns and the loss histogram / CVaR may be identical while the CDaR changes. This example is *not* compounded NAV drawdown.

### Execute the expanded example suite

```bash
python skills/portfolio-models/scripts/comparison_demo.py
python -m pytest -q tests/test_advanced_models.py
```

Every synthetic scenario has known provenance and makes no assertion about live portfolio returns.
