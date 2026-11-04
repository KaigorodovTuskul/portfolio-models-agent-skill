# Formula → claim → literature → executable invariant

This is the **reviewer's minimal trace**; do not mistake a citation for a proof. Implemented variants are explicitly separated from source families. Full bibliography: [source catalog](source-catalog.md).

| Implemented item | Formula / proposition | Basis (literature) | Executable check |
|---|---|---|---|
| Markowitz | `max μ'w − λ/2 w'Σw` with constraints | [EN-01] foundational mean–variance framework; this exact penalized convention is a common equivalent parameterization | `test_robust_kappa_zero_is_classical_mvo`; feasibility |
| GMV | `min w'Σw`, closed-form for unconstrained 2 assets | [EN-01], shrinkage caveat [EN-02] | `test_hand_calculated_gmv`, `test_feasible_constraints_across_models` |
| Scenario CVaR | `min_eta η + E[(L−η)+]/(1−α)`; LP u constraints | [EN-05] original Rockafellar–Uryasev | `test_cvar_fixed_weights_and_fractional_tail`, `test_cvar_matches_brute_grid`, `test_cvar_return_target_feasible` |
| HRP | correlation-derived hierarchical distance and recursive bisection; **average linkage** chosen here | [EN-06] original HRP *family*; code declares average-linkage variant, not exact paper preset | `test_hrp_and_simplex`, `test_hrp_near_zero_variance_asset` |
| Robust MVO mean ambiguity | `min_{||u||2<=κ}(μ+Cμ^1/2u)'w=μ'w−κ sqrt(w'Cμw)` | [EN-08] uncertainty structures; equality follows directly from Cauchy–Schwarz | `test_robust_kappa_zero_is_classical_mvo`, monotonicity of robust objective |
| 1-Wasserstein DRO-CVaR | unbounded-support W1 with **L1 ground norm**, linear loss → `empirical CVaR + ε||w||∞/(1−α)` | [EN-09] Wasserstein DRO duality; **special-case application derived here**, not asserted as an equation quoted verbatim from that paper | `test_dro_limit_equals_cvar`, `test_dro_objective_dual_manual_and_monotone`, large ε concentration test |
| Black–Litterman posterior | `π+τΣP'(PτΣP'+Ω)^−1(Q−Pπ)` | [EN-03] foundation; [TOOL-03] implementation cross-check | `test_bl_no_views_returns_prior`, `test_bl_single_view_moves_to_view` |
| Excess Sharpe & drawdown | mean excess return / its SD, path NAV trough from running peak | standard performance accounting; see [EN-13] selection bias; not an optimizer theorem | `test_portfolio_metrics_includes_initial_nav`, annualization check |

## Critical mathematical qualifications

- The RO `C_μ=Σ/T` default only estimates *uncertainty of the estimated mean* under iid-style assumptions. It is neither a distributional ambiguity set nor a covariance robust optimization.
- The stated DRO counterpart needs **specified unbounded support, full first-moment transport ambiguity, linear scenario losses** and no unmodelled nonlinear trading frictions. With cash fixed support, only eligible return dimensions enter the dual norm. Norm and ε units determine the result; alternative ambiguity sets are not this implementation.
- The chosen DRO objective is a worst-case **tail risk**, not worst-case expected return. Optimizing a risk-only objective normally picks low-risk assets; test return floors and fixed cash benchmarks before claiming added value.
- ES (tail expectation) is a one-period loss statistic; max drawdown is path-dependent. Historical scenarios and their ordering serve different purposes.
- A mathematical proof of an optimizer's feasibility does not validate historical execution at prices from an index or on a halted exchange.

## Version 1.0 mathematical implementations

| Model and exact variant | Source | Code entry point | Executable verification |
|---|---|---|---|
| Ledoit-Wolf / OAS shrinkage covariance GMV | EN-02 / EN-15 | `advanced_models.shrinkage_minimum_variance` | shrinkage bounds and feasible weights (`test_advanced_models.py`) |
| Maximum Sharpe via homogeneous positive-excess QP | EN-01 / EN-23 | `advanced_models.maximum_sharpe` | direct 2-asset Sharpe grid comparison |
| Inverse volatility and ERC / strict risk budgets | EN-07 / EN-16 | `advanced_models.inverse_volatility`, `risk_budgeting`, `equal_risk_contribution` | analytical inverse-vol and normalized risk contributions |
| Maximum Diversification under homogeneous long-only transform | EN-17 / EN-23 | `advanced_models.maximum_diversification` | diagonal analytic solution |
| Mean-semivariance to a fixed per-period threshold | EN-01 / EN-23 | `advanced_models.mean_semivariance` | explicit downside objective at optimum |
| Mean-CVaR scenario linear program | EN-05 | `advanced_models.mean_cvar` | 2-asset grid objective and infeasible mean floor |
| Minimum and Mean CDaR of **additive cumulative P&L** | EN-20; derived LP | `advanced_models.minimum_cdar`, `mean_cdar` | grid enumeration, path-order sensitivity, direct drawdown ES |
| Covariance-uncertain MVO under a PSD Frobenius norm ball | EN-08 / EN-21; derived rank-one support | `advanced_models.robust_covariance_mvo` | rho=0 MVO equivalence, rank-one adversarial perturbation |
| Black-Litterman posterior mean / MVO choice | EN-03 | `advanced_models.black_litterman_portfolio` | zero-view reduction to mean-variance |
| Scenario Kelly growth | EN-11 | `advanced_models.growth_optimal_kelly` | direct log-wealth grid |
| Fixed-gamma entropic risk (distinct from EVaR) | EN-18 / EN-23 | `advanced_models.entropic_risk` | log-sum-exp, small-gamma limit |
| Tracking error minimum | EN-01 / EN-23 | `advanced_models.tracking_error_minimum` | exact benchmark recovery |
| L1 turnover penalized minimum variance, convex QP | EN-19 / EN-23 | `advanced_models.turnover_regularized_minimum_variance` | zero penalty GMV / high penalty hold |

The code optimizes stated **sample** objectives. Neither theoretical optimality in the sample nor numerical test passage establishes out-of-sample investment superiority.
