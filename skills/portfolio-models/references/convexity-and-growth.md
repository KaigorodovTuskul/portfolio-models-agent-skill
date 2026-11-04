# Geometric growth, regimes and (anti)fragility

## Kelly growth (1956, [EN-11])

Maximize `E[log(1+w'R)]` over feasible `w` with `1+w'R>0` in every modelled scenario. This optimizes *geometric long-horizon growth*, not one-period expected return. It is highly sensitive to missing disaster scenarios and estimation error. Compare fractional Kelly and leverage limits on realistic bankruptcy states.

## Antifragility ≠ low volatility ([EN-12])

A useful operational hypothesis is **positive convex response** to adverse shocks. A cash-heavy GMV or CVaR portfolio that falls less is *robust*, not demonstrably antifragile. Assess a strategy's **net** payoff as shock size `x` grows, e.g. convexity `Δ²P(x)=P(x+h)−2P(x)+P(x−h)` or finite-difference downside vega; require economically meaningful positive convexity after carrying/transaction costs, rebalancing and liquidity effects, not one profitable crisis month.

- **Purchased put:** convex downside payoff `max(K−S_T,0) − premium` (without accounting for option funding / carry). Requires historical chain, bid-ask, strike, expiry, volatility, contract multiplier and margin/settlement.
- **Purchased straddle:** convex to either direction but continuous premium cost.
- **Short futures:** mostly linear opposite price exposure plus variation margin; **not** inherently convex, may lose on rebound.
- **Managed futures/time-series momentum:** dynamic signs can profit from *sustained* trends; whipsaws and daily margin calls matter.
- **FX, gold and cash:** hedging/diversification candidates, correlations regime-dependent; none guaranteed to benefit from higher volatility.

**Experimental design:** calendar-specified (not cherry-picked) crises; conditional PnL for 5/10 worst months, symmetry of upside/downside, shock-size sweep, options cost vs payout, 1/3/6-month rebound, margin calls, inability to execute during halts. Compare risk-matched, net of premiums; use a *historical* option chain for claims about real option alpha.

**Safety:** variance reduction is not evidence of nonlinear convexity; a hypothetical Black–Scholes put is illustration, **not historical investability**.


**Implemented sample Kelly:** `advanced_models.growth_optimal_kelly(R)` maximizes `mean(log(1 + R_t w))` over nonnegative, fully invested weights. It uses finite scenario probabilities and no leveraged positions; it does not forecast future scenarios or implement fractional Kelly, multiperiod transaction costs, or options. Refer to the [five-scenario analytic example](worked-examples.md).
