#!/usr/bin/env python3
"""Deterministic numerical smoke sweep across 20 independent synthetic regimes.

Covers feasibility/convergence only; it is NOT an empirical performance study.
Run from the repository root: python scripts/stress_solvers.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills/portfolio-models/scripts'))
from models import minimum_variance, cvar, robust_mean_variance, wasserstein_dro_cvar
from advanced_models import (maximum_sharpe, risk_budgeting, maximum_diversification,
                             mean_cvar, minimum_cdar, robust_covariance_mvo,
                             turnover_regularized_minimum_variance, entropic_risk)


def run():
    passed=0
    for seed in range(100,120):
        rng=np.random.default_rng(seed)
        n,t=5,36
        factors=rng.normal(0,.02,(t,2))
        r=factors@rng.normal(0,1,(2,n))+rng.normal(.01,.01,(t,n))
        solvers={
            'gmv':lambda:minimum_variance(r),
            'cvar':lambda:cvar(r),
            'robust_mean':lambda:robust_mean_variance(r,kappa=.8),
            'dro_cvar':lambda:wasserstein_dro_cvar(r,epsilon=.006),
            'max_sharpe':lambda:maximum_sharpe(r),
            'maximum_diversification':lambda:maximum_diversification(r),
            'risk_budgeting':lambda:risk_budgeting(r),
            'mean_cvar':lambda:mean_cvar(r),
            'additive_cdar':lambda:minimum_cdar(r),
            'robust_covariance':lambda:robust_covariance_mvo(r),
            'turnover_regularization':lambda:turnover_regularized_minimum_variance(r,np.full(n,1/n)),
            'entropic':lambda:entropic_risk(r)
        }
        for name,call in solvers.items():
            result=call()
            w=result.weights
            if not (np.all(np.isfinite(w)) and abs(w.sum()-1)<1e-7
                    and min(w)>-1e-7 and max(w)<1+1e-7):
                raise AssertionError(f'seed={seed} model={name}: infeasible weights')
            passed+=1
    print(f'PASS: {passed} numerical feasibility/convergence checks '
          'across 20 independent deterministic synthetic samples')
    return 0


if __name__=='__main__':
    sys.exit(run())
