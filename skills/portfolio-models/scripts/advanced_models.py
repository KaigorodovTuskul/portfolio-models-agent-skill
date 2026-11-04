"""Auditable constrained portfolio optimizers beyond the baseline algorithms.

Inputs: T x N per-period simple total-return observations, decimal units.
All optimization methods are long-only, fully invested unless explicitly noted.
Each method states its exact sample objective; no forecasts or market data are bundled.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize, linprog
from scipy.special import logsumexp

from models import (SolveResult, returns_matrix, _cov, _limit, _feasible,
                    _slsqp, minimum_variance, mean_variance,
                    black_litterman_mean, risk_contributions)


def inverse_volatility(r: np.ndarray) -> SolveResult:
    a = returns_matrix(r)
    vol = a.std(axis=0, ddof=1)
    if np.any(vol <= 0):
        raise ValueError('inverse-volatility needs positive asset volatilities')
    w = 1/vol
    w = w/w.sum()
    return SolveResult(w, float(w@_cov(a)@w), 'inverse_volatility', {})


def shrinkage_minimum_variance(r: np.ndarray, method: str = 'ledoit_wolf', cap: float = 1.) -> SolveResult:
    a = returns_matrix(r)
    if method == 'ledoit_wolf':
        from sklearn.covariance import LedoitWolf
        estimator = LedoitWolf().fit(a)
    elif method == 'oas':
        from sklearn.covariance import OAS
        estimator = OAS().fit(a)
    else:
        raise ValueError('method must be ledoit_wolf or oas')
    result = minimum_variance(a, cap=cap, cov=estimator.covariance_)
    return SolveResult(result.weights, result.objective, f'{method}_gmv',
                       {'shrinkage': float(estimator.shrinkage_),
                        'covariance_ddof': 0.})


def maximum_sharpe(r: np.ndarray, risk_free: float = 0.) -> SolveResult:
    """Global nonnegative max-Sharpe solution when positive expected excess exists.

    Solve min_y y' S y, subject to excess_mu' y=1, y>=0. Then w=y/sum(y).
    No per-asset cap: applying it after normalization would invalidate equivalence.
    """
    a=returns_matrix(r)
    ex=a.mean(axis=0)-float(risk_free)
    if not np.isfinite(risk_free) or not np.any(ex>0):
        raise ValueError('positive mean excess return required for this formulation')
    s=_cov(a);n=a.shape[1]
    j=int(np.argmax(ex));y0=np.zeros(n);y0[j]=1/ex[j]
    ans=minimize(lambda y: float(y@s@y),y0,jac=lambda y: 2*s@y,
                 bounds=[(0,None)]*n,method='SLSQP',
                 constraints=[{'type':'eq','fun':lambda y: ex@y-1,
                               'jac':lambda y: ex}],
                 options={'maxiter':3000,'ftol':1e-12})
    if not ans.success or ex@ans.x < .999999:
        raise RuntimeError(f'max Sharpe solve failed: {ans.message}')
    w=np.maximum(ans.x,0);w=w/w.sum()
    vol=np.sqrt(max(float(w@s@w),0))
    if vol<=0:raise ValueError('zero-volatility Sharpe is undefined')
    return SolveResult(w,float(ex@w/vol),'maximum_sharpe',
                       {'mean_excess':float(ex@w),'volatility':vol})


def maximum_diversification(r: np.ndarray) -> SolveResult:
    """Long-only maximum diversification ratio, no per-asset cap.

    Equivalent convex QP: min_y y'Sy with sigma'y=1, y>=0.
    """
    a=returns_matrix(r);s=_cov(a);vol=np.sqrt(np.diag(s))
    if np.any(vol<=0):raise ValueError('all assets need positive volatility')
    n=a.shape[1];y0=(1/vol);y0/=vol@y0
    ans=minimize(lambda y:float(y@s@y), y0,jac=lambda y:2*s@y,
                 method='SLSQP',bounds=[(0,None)]*n,
                 constraints=[{'type':'eq','fun':lambda y:vol@y-1,
                               'jac':lambda y:vol}],
                 options={'ftol':1e-12,'maxiter':3000})
    if not ans.success:raise RuntimeError(f'max diversification: {ans.message}')
    w=np.maximum(ans.x,0);w/=w.sum()
    div=float((w@vol)/np.sqrt(w@s@w))
    return SolveResult(w, div, 'maximum_diversification', {})


def risk_budgeting(r: np.ndarray, budgets: np.ndarray | None = None) -> SolveResult:
    """Convex log-barrier risk budgeting (no upper-weight bounds).

    Solve min_{y>0} 0.5*y' Sigma y - sum_i b_i log(y_i);
    w=y/sum(y) satisfies w_i(Sigma w)_i / (w'Sigma w)=b_i.
    Requires positive definite covariance and positive budgets.
    """
    a=returns_matrix(r);s=_cov(a);n=a.shape[1]
    b=np.full(n,1/n) if budgets is None else np.asarray(budgets,float).reshape(-1)
    if b.shape!=(n,) or np.any(~np.isfinite(b)) or np.any(b<=0) or abs(b.sum()-1)>1e-8:
        raise ValueError('strictly positive risk budgets must sum to one')
    if np.linalg.eigvalsh(s).min()<=1e-13:
        raise ValueError('risk budgeting needs a positive-definite covariance')
    def f(y):return float(.5*y@s@y-b@np.log(y))
    def grad(y):return s@y-b/y
    y0=np.sqrt(b/np.diag(s))
    ans=minimize(f,y0,jac=grad,method='L-BFGS-B',bounds=[(1e-10,None)]*n,
                 options={'maxiter':3000,'ftol':1e-14,'gtol':1e-11})
    if not ans.success and np.linalg.norm(ans.jac,ord=np.inf)>1e-5:
        raise RuntimeError(f'risk budget solve failed: {ans.message}')
    y=ans.x;w=y/y.sum();rc=risk_contributions(w,s)
    fractions=rc/rc.sum()
    if np.max(np.abs(fractions-b))>5e-5:
        raise RuntimeError(f'risk budget residual {fractions-b}')
    return SolveResult(w,float(w@s@w),'risk_budgeting',
                       {'max_risk_budget_error':float(np.max(np.abs(fractions-b)))})


def equal_risk_contribution(r:np.ndarray)->SolveResult:
    s=risk_budgeting(r)
    return SolveResult(s.weights,s.objective,'equal_risk_contribution',s.diagnostics)


def mean_semivariance(r: np.ndarray, risk_aversion: float = 5.,
                      target: float = 0., cap: float = 1.) -> SolveResult:
    """Max mu'w - lambda/2 * E[min(r'w - target,0)^2]."""
    a=returns_matrix(r)
    if risk_aversion<=0 or not np.isfinite(target):raise ValueError('invalid parameters')
    mu=a.mean(axis=0)
    def fun(w):
        z=np.minimum(a@w-target,0)
        return float(-mu@w+0.5*risk_aversion*np.mean(z*z))
    def jac(w):
        z=np.minimum(a@w-target,0)
        return -mu+risk_aversion*(a.T@z)/len(a)
    w=_slsqp(fun,jac,a.shape[1],cap)
    return SolveResult(w,-fun(w),'mean_semivariance',
                       {'target':float(target),'lambda':float(risk_aversion)})


def mean_cvar(r: np.ndarray, alpha: float = .9, risk_aversion: float = 2.,
              cap: float = 1., min_expected_return: float | None = None) -> SolveResult:
    """LP for max sample mean - lambda * empirical CVaR_alpha(loss)."""
    a=returns_matrix(r);t,n=a.shape;_limit(n,cap)
    if not 0<alpha<1 or risk_aversion<=0:raise ValueError('invalid alpha/lambda')
    mu=a.mean(axis=0);dim=n+1+t
    c=np.r_[-mu,risk_aversion,np.ones(t)*risk_aversion/((1-alpha)*t)]
    up=[];ub=[]
    for ret in a:
        row=np.zeros(dim);row[:n]=-ret;row[n]=-1;row[n+1+len(up)]=-1
        up.append(row);ub.append(0.)
    if min_expected_return is not None:
        row=np.zeros(dim);row[:n]=-mu;up.append(row);ub.append(-float(min_expected_return))
    eq=np.zeros((1,dim));eq[0,:n]=1
    sol=linprog(c,A_ub=np.asarray(up),b_ub=ub,A_eq=eq,b_eq=[1],
                bounds=[(0,cap)]*n+[(None,None)]+[(0,None)]*t,method='highs')
    if not sol.success:raise RuntimeError(sol.message)
    w=_feasible(sol.x[:n],cap)
    from models import expected_shortfall
    es=expected_shortfall(-a@w,alpha)
    return SolveResult(w,float(mu@w-risk_aversion*es),'mean_cvar',
                       {'alpha':float(alpha),'lambda':float(risk_aversion),
                        'expected_return':float(mu@w),'cvar':float(es)})


def robust_covariance_mvo(r: np.ndarray, risk_aversion: float = 3.,
                          radius: float = .001, cap: float = 1.) -> SolveResult:
    """Exact Frobenius-ball covariance uncertainty around sample PSD Sigma.

    max_{||Delta||_F<=rho,Sigma+Delta PSD} w'(Sigma+Delta)w
        =w'Sigma w + rho*||w||_2^2 (since rank-one PSD Delta attains supremum).
    
    rho must have squared-return units per observation.
    """
    a=returns_matrix(r);s=_cov(a);mu=a.mean(axis=0)
    if risk_aversion<=0 or radius<0:raise ValueError('invalid lambda/radius')
    adjusted=s+radius*np.eye(a.shape[1])
    f=lambda w: float(-mu@w+.5*risk_aversion*w@adjusted@w)
    j=lambda w: -mu+risk_aversion*adjusted@w
    w=_slsqp(f,j,a.shape[1],cap)
    return SolveResult(w,-f(w),'robust_covariance_mvo',
                       {'lambda':float(risk_aversion),'covariance_radius':float(radius)})


def black_litterman_portfolio(r: np.ndarray, prior: np.ndarray,
                               P: np.ndarray, Q: np.ndarray, omega: np.ndarray,
                               tau:float=.05, risk_aversion:float=3., cap:float=1.) -> SolveResult:
    """Black-Litterman posterior mean optimized under *sample* covariance.

    Prior, views and omega have the same per-period units as the return matrix.
    """
    a=returns_matrix(r);s=_cov(a)
    post=black_litterman_mean(prior,s,P,Q,omega,tau)
    if risk_aversion<=0:raise ValueError('lambda must be positive')
    f=lambda w:float(-post@w+.5*risk_aversion*w@s@w)
    j=lambda w:-post+risk_aversion*s@w
    w=_slsqp(f,j,a.shape[1],cap)
    return SolveResult(w,-f(w),'black_litterman_mvo',
                       {'risk_aversion':float(risk_aversion),'posterior_norm':float(np.linalg.norm(post))})


def growth_optimal_kelly(r: np.ndarray, cap:float=1.)->SolveResult:
    """Scenario-based fully invested Kelly: maximize mean log(1+r_i'w)."""
    a=returns_matrix(r)
    def f(w):
        p=1+a@w
        if np.any(p<=0):return 1e6
        return -float(np.log(p).mean())
    def j(w):
        p=1+a@w
        if np.any(p<=0):return np.ones(a.shape[1])*1e6
        return -(a/p[:,None]).mean(axis=0)
    w=_slsqp(f,j,a.shape[1],cap)
    return SolveResult(w,-f(w),'growth_optimal_kelly',{})


def entropic_risk(r:np.ndarray, gamma:float=5.,cap:float=1.)->SolveResult:
    """Min (1/gamma) log(mean(exp(-gamma * portfolio_return)))."""
    a=returns_matrix(r)
    if gamma<=0:raise ValueError('gamma>0')
    def weights(w):
        z=-gamma*(a@w);z=np.exp(z-logsumexp(z));return z
    def f(w):return float(logsumexp(-gamma*(a@w))-np.log(len(a)))/gamma
    def j(w):return -a.T@weights(w)
    w=_slsqp(f,j,a.shape[1],cap)
    return SolveResult(w,f(w),'entropic_risk',{'gamma':float(gamma)})


def _cdar_lp(r:np.ndarray, alpha:float, cap:float,
             risk_aversion:float|None)->SolveResult:
    """CDaR of *additive cumulative P&L*, fixed holdings: S_t=sum_{i<=t}r_i'w.

    Variables w, running peak m_t, VaR eta, shortfall u_t.
    This is NOT compounded NAV drawdown, and is not a rebalanced backtest.
    """
    a=returns_matrix(r);T,n=a.shape;_limit(n,cap)
    if not 0<alpha<1 or (risk_aversion is not None and risk_aversion<=0):
        raise ValueError('invalid alpha/lambda')
    lam=1. if risk_aversion is None else float(risk_aversion)
    dim=n+T+1+T;peak=n;eta=n+T;shortfall=eta+1
    mu=a.mean(axis=0)
    c=np.zeros(dim);c[:n]=-mu if risk_aversion is not None else 0.
    c[eta]=lam;c[shortfall:]=lam/((1-alpha)*T)
    cumulative=np.cumsum(a,axis=0)
    up=[];ub=[]
    for t in range(T):
        # running peak >= total cumulative wealth (relative to initial), and >=0
        row=np.zeros(dim);row[:n]=cumulative[t];row[peak+t]=-1
        up.append(row);ub.append(0.)
        if t>0:
            row=np.zeros(dim);row[peak+t-1]=1;row[peak+t]=-1
            up.append(row);ub.append(0.)
        # shortfall >= drawdown - eta = peak - cumulative - eta
        row=np.zeros(dim);row[:n]=-cumulative[t];row[peak+t]=1
        row[eta]=-1;row[shortfall+t]=-1
        up.append(row);ub.append(0.)
    eq=np.zeros((1,dim));eq[0,:n]=1
    bounds=[(0,cap)]*n+[(0,None)]*T+[(None,None)]+[(0,None)]*T
    res=linprog(c,A_ub=np.asarray(up),b_ub=ub,A_eq=eq,b_eq=[1],
                bounds=bounds,method='highs')
    if not res.success:raise RuntimeError(res.message)
    w=_feasible(res.x[:n],cap)
    from models import expected_shortfall
    pnl=cumulative@w
    draw=np.maximum.accumulate(np.r_[0.,pnl])[1:]-pnl
    cdar=expected_shortfall(draw,alpha)
    obj=float(mu@w-lam*cdar if risk_aversion is not None else cdar)
    return SolveResult(w,obj,'mean_cdar' if risk_aversion is not None else 'minimum_cdar',
                       {'alpha':float(alpha),'cdar_additive_pnl':float(cdar),
                        'expected_return':float(mu@w)})


def minimum_cdar(r:np.ndarray,alpha:float=.9,cap:float=1.)->SolveResult:
    return _cdar_lp(r,alpha,cap,None)


def mean_cdar(r:np.ndarray,alpha:float=.9,risk_aversion:float=2.,cap:float=1.)->SolveResult:
    return _cdar_lp(r,alpha,cap,risk_aversion)


def tracking_error_minimum(r:np.ndarray,benchmark:np.ndarray,cap:float=1.)->SolveResult:
    """Minimize sample variance of active returns (w-b)'Sigma(w-b)."""
    a=returns_matrix(r);n=a.shape[1];b=np.asarray(benchmark,float).reshape(-1)
    if b.shape!=(n,) or not np.all(np.isfinite(b)) or abs(b.sum()-1)>1e-8:
        raise ValueError('benchmark weights must sum to 1')
    s=_cov(a)
    f=lambda w:float((w-b)@s@(w-b))
    j=lambda w:2*s@(w-b)
    w=_slsqp(f,j,n,cap)
    return SolveResult(w,f(w),'tracking_error_minimum',{})


def turnover_regularized_minimum_variance(r:np.ndarray,previous:np.ndarray,
                                           turnover_penalty:float=.001,
                                           cap:float=1.)->SolveResult:
    """Exact QP epigraph for sample variance plus L1 turnover penalty.

    min w'Sigma w + lambda*sum(abs(w-w_prev)), t>=+/- (w-w_prev).
    The penalty is risk/weight-unit calibrated, not necessarily a fee estimate.
    """
    a=returns_matrix(r);n=a.shape[1];_limit(n,cap)
    p=np.asarray(previous,float).reshape(-1)
    if p.shape!=(n,) or not np.all(np.isfinite(p)) or np.any(p<0) or abs(p.sum()-1)>1e-8 or turnover_penalty<0:
        raise ValueError('invalid previous weights / turnover penalty')
    s=_cov(a)
    def f(x):return float(x[:n]@s@x[:n]+turnover_penalty*x[n:].sum())
    def j(x):return np.r_[2*s@x[:n],np.full(n,turnover_penalty)]
    cons=[{'type':'eq','fun':lambda x:x[:n].sum()-1,
           'jac':lambda x:np.r_[np.ones(n),np.zeros(n)]}]
    for i in range(n):
        plus=np.zeros(2*n);plus[n+i]=1;plus[i]=-1
        minus=np.zeros(2*n);minus[n+i]=1;minus[i]=1
        cons.extend([{'type':'ineq','fun':lambda x,v=plus,q=p[i]:float(v@x+q),
                      'jac':lambda x,v=plus,q=p[i]:v},
                     {'type':'ineq','fun':lambda x,v=minus,q=p[i]:float(v@x-q),
                      'jac':lambda x,v=minus,q=p[i]:v}])
    sol=minimize(f,np.r_[p,np.zeros(n)],jac=j,method='SLSQP',
                 bounds=[(0,cap)]*n+[(0,None)]*n,constraints=cons,
                 options={'maxiter':3000,'ftol':1e-12})
    if not sol.success:raise RuntimeError(f'turnover solver: {sol.message}')
    w=_feasible(sol.x[:n],cap)
    return SolveResult(w,float(w@s@w+turnover_penalty*np.abs(w-p).sum()),
                       'turnover_regularized_gmv',
                       {'one_way_weight_turnover':float(np.abs(w-p).sum())})
