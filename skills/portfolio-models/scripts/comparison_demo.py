#!/usr/bin/env python3
"""Deterministic synthetic-data comparison of documented portfolio objectives.

The listed objectives have different units and must not be ranked against each other.
No historical investment-performance claims are made from synthetic samples.
"""
import numpy as np
from models import (minimum_variance, mean_variance, robust_mean_variance,
                    cvar, wasserstein_dro_cvar, hrp, performance)
from advanced_models import (
    shrinkage_minimum_variance, maximum_sharpe, maximum_diversification,
    equal_risk_contribution, mean_cvar, minimum_cdar,
    mean_semivariance, robust_covariance_mvo, growth_optimal_kelly,
    entropic_risk, turnover_regularized_minimum_variance)


def main():
    rng = np.random.default_rng(2026)
    factors = rng.standard_normal((180, 2))
    beta = np.array([[.06, .01], [.015, .028], [.045, -.02], [.01, -.018]])
    R = factors @ beta.T + rng.standard_normal((180, 4)) * .01 + [.008, .005, .009, .004]
    methods = {
        'minimum_variance': lambda: minimum_variance(R),
        'ledoit_wolf_gmv': lambda: shrinkage_minimum_variance(R),
        'mean_variance': lambda: mean_variance(R),
        'maximum_sharpe': lambda: maximum_sharpe(R, risk_free=.002),
        'maximum_diversification': lambda: maximum_diversification(R),
        'equal_risk_contribution': lambda: equal_risk_contribution(R),
        'cvar': lambda: cvar(R),
        'mean_cvar': lambda: mean_cvar(R),
        'minimum_cdar': lambda: minimum_cdar(R),
        'mean_semivariance': lambda: mean_semivariance(R),
        'ellipsoidal_mean_robust_mvo': lambda: robust_mean_variance(R),
        'frobenius_covariance_robust_mvo': lambda: robust_covariance_mvo(R),
        'wasserstein_dro_cvar': lambda: wasserstein_dro_cvar(R),
        'hrp_average_linkage': lambda: hrp(R),
        'kelly': lambda: growth_optimal_kelly(R),
        'entropic_risk': lambda: entropic_risk(R),
        'turnover_aware_gmv': lambda: turnover_regularized_minimum_variance(R, np.full(4, .25))
    }
    print('Synthetic returns, T=180, N=4. In-sample fit only; NOT an OOS performance ranking.')
    for name, solver in methods.items():
        x = solver()
        print(f'{name:37s} weights={np.round(x.weights, 3).tolist()} '
              f'fit_sample_vol={np.std(R @ x.weights, ddof=1):.5f}')


if __name__ == '__main__':
    main()
