# Agent task: model choice

**Input:** 6 RUB total-return series: Russian stocks, OFZ, short corporate bonds, cash, gold, FX. User requests least drawdown for 3-year horizon, no leverage/shorts, 40% max each risky class, 70% cash maximum.

**Expected agent:** read `SKILL.md` → notation/data → model-map → min variance and CVaR references → backtest protocol; clarify executable proxies and cash series; recommend GMV/CVaR with fixed 70% cash baseline; report risk-matching feasibility and no declared winner. Should not read Kelly/option details unless relevant.
