#!/usr/bin/env python3
"""Fit documented portfolio models to a chronological CSV of simple total returns.

CSV: `date,asset_1,asset_2,...` where numbers are decimal per-observation
returns, not prices. Fit-only output is IN-SAMPLE; the script does not claim
walk-forward performance or executable rebalancing.
"""
from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
from models import (minimum_variance, mean_variance, robust_mean_variance,
                    cvar, wasserstein_dro_cvar, hrp, returns_matrix)
from advanced_models import (
    inverse_volatility, shrinkage_minimum_variance, maximum_sharpe,
    maximum_diversification, equal_risk_contribution, mean_cvar, minimum_cdar,
    mean_cdar, mean_semivariance, robust_covariance_mvo, growth_optimal_kelly,
    entropic_risk)

SOLVERS = {
    'gmv': lambda r,a: minimum_variance(r,cap=a.cap),
    'lw-gmv': lambda r,a: shrinkage_minimum_variance(r,'ledoit_wolf',cap=a.cap),
    'oas-gmv': lambda r,a: shrinkage_minimum_variance(r,'oas',cap=a.cap),
    'inverse-vol': lambda r,a: inverse_volatility(r),
    'mvo': lambda r,a: mean_variance(r,a.lambda_risk,cap=a.cap),
    'max-sharpe': lambda r,a: maximum_sharpe(r,a.risk_free),
    'max-diversification': lambda r,a: maximum_diversification(r),
    'erc': lambda r,a: equal_risk_contribution(r),
    'hrp': lambda r,a: hrp(r),
    'hrp-single': lambda r,a: hrp(r,linkage_method='single'),
    'cvar': lambda r,a: cvar(r,a.alpha,cap=a.cap),
    'mean-cvar': lambda r,a: mean_cvar(r,a.alpha,a.lambda_risk,cap=a.cap),
    'min-cdar': lambda r,a: minimum_cdar(r,a.alpha,cap=a.cap),
    'mean-cdar': lambda r,a: mean_cdar(r,a.alpha,a.lambda_risk,cap=a.cap),
    'mean-semivar': lambda r,a: mean_semivariance(r,a.lambda_risk,cap=a.cap),
    'robust-mean-mvo': lambda r,a: robust_mean_variance(r,a.lambda_risk,kappa=a.kappa,cap=a.cap),
    'robust-cov-mvo': lambda r,a: robust_covariance_mvo(r,a.lambda_risk,radius=a.rho,cap=a.cap),
    'wasserstein-dro': lambda r,a: wasserstein_dro_cvar(r,a.alpha,a.epsilon,cap=a.cap),
    'kelly': lambda r,a: growth_optimal_kelly(r,cap=a.cap),
    'entropic-risk': lambda r,a: entropic_risk(r,gamma=a.gamma,cap=a.cap),
}


def load_csv(path: Path):
    with path.open(newline='',encoding='utf-8-sig') as f:
        reader=csv.reader(f)
        header=next(reader)
        if len(header)<3 or header[0].strip().lower()!='date':
            raise ValueError('CSV header must be date,asset_1,asset_2,...')
        names=header[1:]
        if len(set(names))!=len(names):
            raise ValueError('duplicate asset columns')
        dates=[]; observations=[]
        for row in reader:
            if len(row)!=len(header):raise ValueError('inconsistent row width')
            dates.append(row[0]);observations.append([float(x) for x in row[1:]])
    if len(set(dates))!=len(dates) or dates!=sorted(dates):
        raise ValueError('dates must be unique and chronologically sorted as ISO dates')
    return names,dates,returns_matrix(np.asarray(observations))


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('returns_csv',type=Path,help='chronological date + decimal asset-return columns')
    p.add_argument('--model',required=True,choices=sorted(SOLVERS))
    p.add_argument('--alpha',type=float,default=.9)
    p.add_argument('--lambda-risk',type=float,default=3.)
    p.add_argument('--risk-free',type=float,default=0.,help='per-observation decimal rate')
    p.add_argument('--kappa',type=float,default=1.65)
    p.add_argument('--rho',type=float,default=.001,help='per-observation squared-return covariance radius')
    p.add_argument('--epsilon',type=float,default=.01,help='W1 radius in decimal-return L1 ground units')
    p.add_argument('--gamma',type=float,default=5.)
    p.add_argument('--cap',type=float,default=1.,help='max capital weight (ignored by methods with no cap support)')
    a=p.parse_args(argv)
    unsupported={'max-sharpe','max-diversification','erc','inverse-vol','hrp','hrp-single'}
    if a.cap!=1 and a.model in unsupported:
        p.error(f'{a.model} does not implement an upper-weight cap; use --cap 1')
    try:
        names,dates,returns=load_csv(a.returns_csv)
        res=SOLVERS[a.model](returns,a)
    except (ValueError, RuntimeError, OSError) as exc:
        p.exit(2, f'error: {exc}\n')
    if abs(res.weights.sum()-1)>1e-6 or min(res.weights)<-1e-8:
        raise RuntimeError('infeasible model result')
    output={'model':res.method,'status':'in_sample_fit_only',
            'first_observation':dates[0],'last_observation':dates[-1],
            'observations':len(dates),'assets':names,
            'weights':dict(zip(names,map(float,res.weights))),
            'objective_value':res.objective,'diagnostics':res.diagnostics}
    print(json.dumps(output,indent=2,ensure_ascii=False))
    return 0


if __name__=='__main__':
    sys.exit(main())
