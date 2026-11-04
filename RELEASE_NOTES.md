# Version 1.0.0 — expanded mathematical reference library

Release date: 2026-11-04.

- English as the canonical language for code, agent instructions and technical documentation. Localized README translations for Simplified Chinese (`zh-CN`) and Russian (`ru-RU`).
- Expanded with executable shrinkage covariance GMV, maximum Sharpe, inverse-volatility, ERC/risk budgeting, Maximum Diversification, Mean-Semivariance, Mean-CVaR, additive-P&L CDaR/Mean-CDaR, covariance-uncertainty Robust MVO, Black–Litterman allocation, Kelly, fixed-gamma entropic risk, tracking error and turnover-regularized GMV.
- Primary literature extended with verified academic and author-hosted sources; original papers linked, not copied.
- Improved source-to-formula-to-Python-to-test traceability, exact variant labeling and tested analytical boundary cases.
- Executable CLI for chronological CSV data and a deterministic synthetic dataset with full generation procedure.
- Local numerical testing; GitHub Actions testing removed. No packaged evaluator scores or unverified claims of external certification.
- Independent four-axis review remains an optional release-process gate and is not implied by a passing numerical test suite.

See [`CHANGELOG.md`](CHANGELOG.md) for chronological changes and [`docs/CHANGES_FROM_STABLE.md`](docs/CHANGES_FROM_STABLE.md) for the source snapshot comparison.

For reproducible validation commands, read [`docs/NUMERICAL_VALIDATION.md`](docs/NUMERICAL_VALIDATION.md).
