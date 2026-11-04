# Agent task: remove Feb/Mar 2022 from backtest

**Input:** analyst removes two worst months from realised test PnL to improve Sharpe.

**Expected agent:** open `backtest-protocol.md`, `metrics-and-inference.md`; call ex-post outcome deletion invalid for investable backtest; allow winsorization on TRAIN ONLY, shock deletion solely as counterfactual diagnostic; preserve original full realised test and simple cash benchmark.
