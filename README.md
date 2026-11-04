# Portfolio Models — Quantitative Portfolio Optimization & Risk Management

[![Agent Skills](https://img.shields.io/badge/Agent_Skills-open_standard-008B8B)](https://agentskills.io/specification) [![Python](https://img.shields.io/badge/Python-3.10%2B-303f4f)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-555555)](LICENSE)

**English** · [简体中文](docs/i18n/README.zh-CN.md) · [Русский](docs/i18n/README.ru-RU.md)

An open-source Agent Skill for **evidence-based asset allocation, portfolio optimization and risk management**. It combines explicit mathematical assumptions, auditable Python reference optimizers, primary academic sources in English, Russian and Chinese, and a point-in-time benchmark protocol. The skill provides task-specific context on demand instead of loading a full quant-finance textbook into every agent turn.

## Install

```bash
npx skills add KaigorodovTuskul/portfolio-models-agent-skill --skill portfolio-models
```

Or copy `skills/portfolio-models/` into a supported client's local skills directory (typically `.agents/skills/portfolio-models/`). The portable entry point is [`SKILL.md`](skills/portfolio-models/SKILL.md).

## Coverage and execution status

**More than twenty executable optimizers and defined variants** are implemented as executable Python functions, with documented exact variants:

| Family | Implemented variants |
|---|---|
| Classical | Equal capital weights, Global Minimum Variance, Markowitz MVO, maximum Sharpe, Black–Litterman posterior + constrained MVO |
| Covariance estimation | Ledoit–Wolf GMV, Oracle Approximating Shrinkage (OAS) GMV |
| Diversification | Inverse volatility, Equal Risk Contribution, general Risk Budgeting, Hierarchical Risk Parity (single and average linkage), Maximum Diversification |
| Downside / path risk | Mean-Semivariance, CVaR, Mean-CVaR, Minimum CDaR and Mean-CDaR (additive cumulative-P&L formulation) |
| Robust optimization | Ellipsoidal mean-uncertainty MVO, Frobenius covariance-uncertainty MVO, 1-Wasserstein DRO-CVaR with specified ground metric and support |
| Growth and allocation mandates | Scenario Kelly, fixed-gamma entropic risk, minimum tracking error, turnover-regularized GMV |

This is **not** a claim that distinct mathematical variants represent 24 independent investment discoveries. It is an auditable implementation collection. Every optimizer operates on **sample scenarios**; historical returns, brokerage execution, derivative rolls and expected live performance are **not included**.

## Architecture: progressive disclosure

```text
skills/portfolio-models/
  SKILL.md                      Compact agent procedure and conditional pointers
  references/
    model-map.md                 Choose by objective, risk and available estimates
    models-classical.md          Markowitz, GMV, Black–Litterman
    models-extended.md           ERC, maximum diversification, shrinkage, tracking, costs
    models-tail.md               CVaR, Mean-CVaR, CDaR, HRP
    models-robust.md             Mean/covariance robust MVO, exact Wasserstein special case
    convexity-and-growth.md     Kelly, convexity, options and antifragility
    notation-and-data.md        Total returns, units, proxies and timestamps
    metrics-and-inference.md    Risk metrics and statistical testing
    backtest-protocol.md        Point-in-time research and execution assumptions
    source-catalog.md           Annotated primary literature (EN/RU/ZH)
    formula-trace.md            Formula to reference to executable test
    implementation-reference.md Method APIs and exact numerical scope
    worked-examples.md         Hand-checkable calculations
  scripts/
    models.py                    Foundational numerical implementations
    advanced_models.py          Diversification, drawdown and growth optimizers
    portfolio_cli.py            Fit methods to chronological user-supplied return CSV
    demo.py, comparison_demo.py  Reproducible synthetic calculations
    walkforward_demo.py         Chronological accounting demonstration
```

The main skill is a router: a one-paragraph conceptual question does not require loading a covariance solver, the full source catalog or the backtest protocol. Computation triggers model-specific equations and code; empirical claims trigger point-in-time data and statistical validation.

## Quick start

Requires Python 3.10+.

```bash
python -m pip install -r requirements.txt
python skills/portfolio-models/scripts/demo.py
python skills/portfolio-models/scripts/comparison_demo.py
python skills/portfolio-models/scripts/walkforward_demo.py
python -m pytest -q tests
python scripts/stress_solvers.py
python scripts/goal_workflow.py check
```

### Fit a model to return observations

Provide a UTF-8 CSV with an ISO `date` column and one **simple decimal total-return** column per asset. All observations must share the same base currency and calendar. Fit-to-sample output is **not** an out-of-sample strategy performance estimate.

```bash
python skills/portfolio-models/scripts/portfolio_cli.py datasets/synthetic_monthly_returns.csv --model erc
python skills/portfolio-models/scripts/portfolio_cli.py datasets/synthetic_monthly_returns.csv --model mean-cvar --alpha 0.90 --lambda-risk 3
python skills/portfolio-models/scripts/portfolio_cli.py datasets/synthetic_monthly_returns.csv --model robust-cov-mvo --rho 0.0005
```

Standalone skill installs also carry `skills/portfolio-models/requirements.txt` for their numerical dependencies. The included CSV contains deterministic **synthetic** returns and is explicitly identified as such. All numerical methods are locally testable; **no tests run in GitHub Actions**. See [local numerical validation](docs/NUMERICAL_VALIDATION.md) and [API and exact limitations](skills/portfolio-models/references/implementation-reference.md).

## Research integrity

- **Exact objectives:** do not confuse sample CVaR with its DRO counterpart, mean uncertainty with covariance uncertainty, or additive CDaR with compounded NAV drawdown.
- **Reproducibility:** state input frequency and units, solver parameters, confidence levels, feasible constraints, sample dates and benchmark construction.
- **Point-in-time:** fit and tune using earlier data; account for dividend/coupon reinvestment, index composition, price availability and execution constraints.
- **Economic value:** compare each sophisticated method against simple feasible baselines at common dates and comparable realized risk, net of realistic costs.
- **Source provenance:** the [annotated catalog](skills/portfolio-models/references/source-catalog.md) distinguishes full papers from abstracts and method-specific derived cases. Original publications are linked rather than copied.

## Evaluation and maintenance

The repository includes deterministic tests and a [four-axis review protocol](workflows/goal-workflow.md): architecture, sources, mathematics and applied examples. An independent quality claim requires **four genuine isolated reviewer results, mean score strictly above 8.5/10, no blockers and passing local tests**. The review aggregator rejects missing, fabricated or stale inputs; the repository does not prepackage reviewer results. Run `python scripts/goal_workflow.py prepare --round 1` to export pinned review instructions for an external agent orchestrator, then evaluate submitted reports as documented.

## License and scope

Licensed under [MIT](LICENSE). Use for research, education, model auditing and quantitative prototyping. Nothing here implies a broker connection, trade execution, verified historical strategy profitability, or suitability for any individual portfolio. Follow the documented uncertainty and source restrictions before using outputs for investment decisions.
