# Notation, units & data contracts

Read when working with numeric inputs, market data or return series.

| Symbol | Meaning | Unit |
|---|---|---|
| `R` | T×N realised **simple total-return** matrix | decimal / observation |
| `w` | N capital fractions at decision/holding start | sum 1, capital |
| `μ` | expected simple return E[R] | decimal / observation |
| `Σ` | return covariance | decimal² / observation |
| `r_f,t` | financing/benchmark return | decimal / observation |
| `L=-R w` | portfolio scenario loss (positive = loss) | decimal / observation |
| `α` | CVaR confidence, e.g. 0.90 (worst 10%) | probability |
| `κ` | ellipsoidal mean ambiguity multiplier | dimensionless |
| `ε` | Wasserstein radius in the ground norm of return vectors | **decimal returns** |
| `λ` | quadratic risk-aversion in `μ'w - (λ/2)w'Σw` | reciprocal return units |

- `R_t = P^TR_t/P^TR_{t-1}-1` only for **total-return adjusted** price series. Do not double-count coupons/dividends. For raw prices include all distributions and split/corporate-action adjustment.
- Currency is a *numeraire*. RUB value of a foreign total-return investment: `(1+R_FXasset)*(FX_t/FX_{t-1})-1`; spot FX alone has no carry/funding, FX futures have rolls/VM/margin.
- A floating interest **rate quote** RUSFAR/key-rate is not a return index. Daily synthetic cash return may use `product_d(1+quote_d/100*Δd/365)-1`; actual accessible yield needs haircuts, fees and availability. When series stops, classify it as missing, not `ffill` to infinity.
- `Σ_annual ≈ periods_per_year*Σ_period` and `μ_annual ≈ periods_per_year*μ_period` only under simplifying independence assumptions; compounded realised CAGR is different.
- Instrument availability: original issue date, coupons, tax, defaults, delisted securities, stale/bad quotes, market closure, bid/ask, maturity, split, constituent changes, liquidity and survivorship.
- Valuations vs execution: start-of-next-session executable trade; do not mark synthetic total-return index as tradeable. Preserve original raw source, timestamp, checksum and revisions.
- `σ=0` or singular `Σ` is a warning: a cash proxy that rises deterministically can dominate low-risk objectives; benchmark against **100% cash** and feasible fixed allocation separately.
- No free lunch through missing return observations. For halted markets record mark-to-market uncertainty, execution unavailable, and sensitivity to alternative valuation conventions.

**Read next:** [backtest protocol](backtest-protocol.md) for trading study; [MOEX/CBR sources](data-sources.md) to fetch and license data.
