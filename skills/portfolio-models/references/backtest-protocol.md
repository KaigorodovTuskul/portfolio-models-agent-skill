# Point-in-time benchmark protocol

## Control before computation

1. Fix universe and **historical tradability**: what existed/was accessible at each `as_of`, ticker genealogy, underlying index rules, coupon/dividend reinvestment, corporate actions, closures, delistings, tax status.
2. Snapshot raw data: provider, URL, query, retrieval date, source revision, time zone, checksum; audit coverage, holes, stale values and currency conversions.
3. Separate **A: analytical proxies** from **B: investable security-level** experiments. A cannot claim real trading/replicability.
4. Fix training `lookback`, outer walk-forward test, inner nested hyperparameter validation; no search on final test. Signal from end `t−1` trades earliest available session `t`. Timestamp publication lags.
5. Freeze feasible common constraints for model comparison: long-only/short, leverage, asset max, liquidity, vol/ES cap, concentration, rebalancing trigger, trade schedule and cash.
6. Ensure drifted holdings, transaction fees, spread, slippage, FX conversion, issue-specific coupons and stock splits; failed trades become unfilled and held, not ideal trades.
7. Report *gross and net*, simple benchmark 1/N, GMV, all-cash, fixed cash/risk, buy-and-hold, real risk-matched peers. Do not choose cash cap because cash happened to win.
8. Stress pre-specified periods: 2008, 2014, COVID, Feb/Mar 2022, high-rate 2024–26 if each comparable universe has actual coverage; do not extrapolate missing proxies.
9. Diagnose tail: **(i)** full realised observations, **(ii)** winsorized **training only**, **(iii)** *counterfactual* deleting shock months from reporting (never sold as achievable investment result), **(iv)** shock-injection / liquidity halts.
10. Test against predeclared score/risk and blocked bootstrap. Preserve failures, no cherry-picked leader; no testing after holdout disclosure unless independently new holdout period.

## Common traps

- Comparing 60-month training with 24-month training using different test start dates: OOS performance windows must align for direct comparison.
- Using key rate as investable daily cash yield or official USD/RUB as fee-free FX trade.
- Using only monthly drawdown to claim crisis resilience: the intramonth NAV and forced liquidation can be radically worse.
- Selecting a profile's risk cap after seeing full-sample returns.
- Soft hyperparameter penalty and hard common risk cap counted as the same protection; they are different.
- Calibrating Wasserstein ε with **all** data or using arbitrary penalty magnitude without specifying norm.
- Claiming model performance from index TR without transaction model and venue.

**Reporting schema:** universe, asset series IDs, start/end & as-of, training/validation/test folds, execution lags, objective and λ/κ/ε, cap, cost bps, synthetic/real, gross and net CAGR, excess Sharpe, vol, daily/monthly MDD, CVaR, turnover, crisis conditional PnL, confidence interval vs simple baseline, warnings.

**Data pipeline tasks** can use `references/data-sources.md`; **code tests** in `tests/` guard only numerical primitives, not market liquidity.

**Machine-readable provenance contract:** [`assets/dataset-schema.json`](../assets/dataset-schema.json). **Deterministic executable input:** [`datasets/synthetic_monthly_returns.csv`](../../../datasets/synthetic_monthly_returns.csv); this synthetic dataset is not historical exchange performance.
