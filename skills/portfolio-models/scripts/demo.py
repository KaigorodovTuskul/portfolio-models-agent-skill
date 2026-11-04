#!/usr/bin/env python3
"""Deterministic toy data only. Not a backtest and not a return forecast."""
import numpy as np
from models import (minimum_variance,mean_variance,robust_mean_variance,cvar,
                    wasserstein_dro_cvar,hrp,expected_shortfall)

SCENARIOS=np.array([[.04,.01],[-.02,.02],[.03,-.01],[-.08,.01]],dtype=float)
FIXED=np.array([.5,.5]);loss=-SCENARIOS@FIXED
print("2-asset example (decimal returns, four equally weighted historical scenarios)")
print("Fixed 50/50: empirical CVaR(75%)=",round(expected_shortfall(loss,.75),5))
print("Fixed 50/50: Wasserstein DRO-CVaR(75%, eps=.01, L1 ground)=",
      round(expected_shortfall(loss,.75)+.01*max(FIXED)/.25,5))
for method,fun in [
 ("GMV",lambda:minimum_variance(SCENARIOS)),
 ("MVO",lambda:mean_variance(SCENARIOS,risk_aversion=3)),
 ("Robust MVO",lambda:robust_mean_variance(SCENARIOS,risk_aversion=3,kappa=1.65)),
 ("CVaR",lambda:cvar(SCENARIOS,alpha=.75)),
 ("DRO-CVaR",lambda:wasserstein_dro_cvar(SCENARIOS,alpha=.75,epsilon=.01)),
 ("HRP",lambda:hrp(SCENARIOS))]:
    x=fun();print(f"{method:12s} w={np.round(x.weights,4)} objective={x.objective:.6f}")
print("Note: training sample of four is insufficient for deployment or validation.")
