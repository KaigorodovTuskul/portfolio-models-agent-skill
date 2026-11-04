#!/usr/bin/env python3
"""A monthly walk-forward *accounting demonstration*, NOT executable exchange pricing.

Signal uses strictly prior monthly returns; trading assumes previous month-end
NAV is an executable reference at start of next month, which is only Level A.
"""
import numpy as np
from models import minimum_variance, performance


def walk_forward(returns, lookback=24, rebalance=3, trading_bps=10.0):
    a=np.asarray(returns,float)
    if a.ndim!=2 or a.shape[0]<=lookback or lookback<4 or rebalance<1:
        raise ValueError("not enough rows / invalid horizon")
    if not np.isfinite(a).all() or (a<=-1).any():raise ValueError("bad asset returns")
    n=a.shape[1]
    w=np.ones(n)/n
    net=[];hist=[]
    for t in range(lookback,len(a)):
        # At start of period t, only data [0, ..., t-1] exists.
        if (t-lookback)%rebalance==0:
            target=minimum_variance(a[t-lookback:t]).weights
            cost=trading_bps/10000*float(np.abs(target-w).sum())
            w=target.copy()
        else:
            cost=0.0
        period_return=float(w@a[t])
        net.append((1-cost)*(1+period_return)-1)
        hist.append((t,t-1,round(cost,9),w.copy()))
        w=w*(1+a[t])/(1+period_return) # drift after realised returns
    return np.asarray(net),hist


if __name__=='__main__':
    rng=np.random.default_rng(20261104)
    R=np.column_stack([rng.normal(.007,.06,84),rng.normal(.005,.025,84),rng.normal(.008,.015,84)])
    output,audit=walk_forward(R)
    print("Illustrative synthetic-only OOS months:",len(output))
    print("First decision at t, last observable index:",audit[0][:3])
    print("Metrics:",performance(output))
