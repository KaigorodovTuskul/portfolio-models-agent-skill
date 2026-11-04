# Performance and statistical inference

Let monthly net returns `p_t` and reference cash monthly returns `c_t` be *aligned on exact dates*. No annual percentage can be inserted into this formula unconverted.

| Statistic | Exact calculation / caveat |
|---|---|
| Wealth | `NAV_t = NAV_{t-1}(1+p_t)`, with initial NAV=1 included in drawdown |
| CAGR | `(∏(1+p_t))^(12/T)-1`; invalid when NAV<=0 |
| Annual vol | `sqrt(12)*std(p_t, ddof=1)`; trailing/intra-month peaks differ |
| Excess Sharpe | `sqrt(12)*mean(p_t-c_t)/std(p_t-c_t,ddof=1)` (time-varying cash); zero denominator → undefined |
| Max drawdown | `min_t(NAV_t / max_{s≤t} NAV_s - 1)` including initial NAV; measure with daily NAV when available |
| Calmar | `CAGR/abs(MaxDD)`; zero DD → **undefined**, not +∞ or `0` |
| CVaR / ES | average of upper `(1−α)` **loss** tail; fractional tail weights for finite samples |
| Omega | gain/loss probability weighted relative to specified return threshold; disclose it |
| Turnover | `sum(abs(target - drifted_weights))` on each trade; one-way factor 1/2 must be specified |
| Gross / net | show both; commissions, spreads, impact, taxes, FX, funding explicitly identified |

**Inference requirements:** select *one* primary metric and test horizon before running; report net cash-adjusted and risk-matched differences, drawdown recovery, expected shortfall and conditional performance. Use paired block bootstrap preserving autocorrelation, block length sensitivity, confidence intervals for *differences* (not overlap of standalone intervals), and multiple-comparison correction (Holm or similar; Deflated Sharpe for search bias [EN-13]). A strategy winning one ranking has **no** statistical priority if CI includes zero.

**Risk-matching feasibility:** for no-leverage long-only portfolios, reducing risk with cash may be possible; increasing a low-risk model's risk to match another may not. Compare only feasible pairs, disclose coverage and selection effects. Realised volatility and drawdown are not interchangeable risk units.

**Acceptance:** metrics can be reproduced from stored net monthly returns; date/count discrepancies or inconsistent cash conventions fail validation.
