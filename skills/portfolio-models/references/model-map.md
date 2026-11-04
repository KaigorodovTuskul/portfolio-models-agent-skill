# Portfolio model selection — decision map

Select models by economic loss function and the availability of reliable inputs; do not rank algorithms by name.

| Primary decision | Model / implementation | Inputs | Where to read |
|---|---|---|---|
| Transparent baseline | Equal weight / fixed allocation | Asset list, weights | `models-classical.md` |
| Variance floor | Global Minimum Variance | PSD covariance | `models-classical.md` |
| Estimation-error control | Ledoit-Wolf or OAS shrinkage GMV | Return matrix | `models-extended.md` |
| Mean vs variance | Markowitz MVO | Forecast mean, covariance, risk aversion | `models-classical.md` |
| Maximize expected excess Sharpe | Tangency / max Sharpe | Mean excess returns, PSD covariance | `models-extended.md` |
| Prior plus investor views | Black-Litterman posterior + MVO | Prior, P, Q, Omega, tau, covariance | `models-classical.md` |
| Spread total risk | ERC / risk budgeting | Positive-definite covariance, budgets | `models-extended.md` |
| Volatility-based budget | Inverse volatility / HRP | Volatilities, correlations | `models-extended.md`, `models-tail.md` |
| Maximize diversification ratio | Maximum Diversification | Covariance, individual volatilities | `models-extended.md` |
| Limit negative deviation | Mean-Semivariance | Return scenarios, threshold, lambda | `models-extended.md` |
| Protect tail losses | CVaR / Mean-CVaR | Scenarios, alpha, optional lambda | `models-tail.md` |
| Protect *path* losses | Minimum CDaR / Mean-CDaR | Ordered returns; additive-P&L path | `models-tail.md` |
| Robustify estimated expected mean | Ellipsoidal Robust MVO | Mean, covariance of mean error, kappa | `models-robust.md` |
| Robustify covariance estimate | Frobenius-ball Robust Covariance MVO | Covariance, radius rho | `models-robust.md` |
| Robustify tail distribution | 1-Wasserstein DRO-CVaR | Scenarios, ground metric, epsilon, support | `models-robust.md` |
| Growth objective | Scenario Kelly | Full one-period scenario returns | `convexity-and-growth.md` |
| Penalize exponential downside | Entropic risk | Scenarios, exponential gamma | `models-extended.md` |
| Index mandate | Minimum tracking error | Benchmark weights, covariance | `models-extended.md` |
| Reduce trading | Turnover-regularized GMV | Current weights, lambda | `models-extended.md` |

**Process:** start with a transparent baseline and GMV; then use the loss-function-specific optimizer. Prefer CVaR when extreme one-period losses matter, CDaR when *ordered drawdowns* matter, and robust formulations when uncertainty sets are defensible. Include HRP/risk budgets as independent diversification families. Benchmark with equal risk, dates, costs and restrictions before declaring improvement.

**Read next:** [precise formulas](models-classical.md), [diversification and regularization](models-extended.md), [tails](models-tail.md), [robust](models-robust.md), [growth](convexity-and-growth.md).
