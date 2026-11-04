# Failure modes: audit before a leaderboard

| Failure | Detect | Correct |
|---|---|---|
| Wrong Sharpe baseline | uses constant 0 instead of risk-free returns | align actual investable short-term return per observation |
| Price vs total-return | corporate index is price-only; ignored coupons | use TR/reconstruct cashflows |
| κ=0 selected repeatedly | tuned robust model collapses to baseline | inspect fold loss and shrinkage strength; report κ distribution |
| Ground metric not specified | calls penalty on w “DRO” | declare Wasserstein p, norm, support, derive dual |
| Dollars vs RUB | FX return counted twice or missing carry | explicitly choose reporting currency, funding, conversion |
| Correlation blow-up | zero-vol `Σ` or stale zero returns | reject/review assets; regularize and record |
| Worst loss ≠ drawdown | compares CVaR with MDD as if equal | calculate path NAV and daily MDD |
| Trading during halt | rebalances at month-end price closed to investor | enforce market calendar, earliest executable fills |
| Best performer selected ex post | hundreds of variants and one test | nested walk-forward, holdout, paired bootstrap and multiple-testing control |
| Different OOS ranges | different lookback starts lead different evaluation intervals | align dates and benchmark throughout |
| Robust MVO sign/scale | wrong λ or covariance units | κ=0 equivalence, λ→large convergence to GMV |
| Low risk models win due to cash | 80% cash optimizer compared to all-equity | common investable constraints + simple fixed/cash benchmarks |
| Historical options priced synthetically | claims realized hedge returns from BSM prices | contract history, bid/ask volume, exercise, roll, IV crush, margin |
| Source verification absent | generated citations without actual papers | provenance ID, original publisher, full paper or abstract status |
