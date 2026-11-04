# Deterministic synthetic data

`synthetic_monthly_returns.csv` contains 72 chronological monthly observations, 2018–2023, of **four synthetic factor-style asset returns**. The figures are decimal simple returns, with no claim of real asset prices, investability, dividend reinvestment, or historical calibration. The date column is a synthetic calendar key for chronological validation; it does not refer to an actual trade date.

Generation is deterministic: NumPy's `default_rng(20261104)` produces three independent Gaussian factors and four Gaussian idiosyncratic noise series. The scenario return matrix uses:

```python
rng = np.random.default_rng(20261104)
factors = rng.standard_normal((72, 3))
noise = rng.standard_normal((72, 4))
loadings = np.array([[.04, .02, .01], [.01, .027, .015],
                     [.018, -.01, .042], [.002, .001, 0.]])
means = np.array([.008, .005, .007, .004])
returns = factors @ loadings.T + .006 * noise + means
```

This file supports executable CLI examples and deterministic regression checks. It is **not** a historical backtest or a source for financial projections. To use real data, supply a newly collected, licensed, point-in-time total-return dataset following [`dataset-schema.json`](../skills/portfolio-models/assets/dataset-schema.json) and the [data protocol](../skills/portfolio-models/references/notation-and-data.md).
