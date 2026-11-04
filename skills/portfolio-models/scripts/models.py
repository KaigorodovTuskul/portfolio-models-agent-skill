"""Small, auditable portfolio-model reference implementations.

Input: T x N simple **total returns** in decimals per observation, ordered oldest
first; outputs: N capital weights summing to one, nonnegative and bounded.

Dependencies: numpy, scipy (Python >=3.10). These are numerical primitives,
not a market-data or production brokerage execution engine. See SKILL.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from scipy.cluster.hierarchy import leaves_list, linkage
from scipy.optimize import linprog, minimize
from scipy.spatial.distance import squareform


@dataclass(frozen=True)
class SolveResult:
    weights: np.ndarray
    objective: float
    method: str
    diagnostics: dict[str, float]


def returns_matrix(r: np.ndarray, min_obs: int = 4) -> np.ndarray:
    a = np.asarray(r, dtype=float)
    if a.ndim != 2 or a.shape[0] < min_obs or a.shape[1] < 1:
        raise ValueError("returns must be a T-by-N matrix with enough observations")
    if not np.isfinite(a).all() or (a <= -1).any():
        raise ValueError("nonfinite or bankrupt (-100% or worse) simple asset returns")
    return a


def _limit(n: int, cap: float) -> float:
    if not (0 < cap <= 1) or cap * n < 1 - 1e-10:
        raise ValueError("infeasible cap: n * cap must be >= 1")
    return float(cap)


def _feasible(w: np.ndarray, cap: float) -> np.ndarray:
    w = np.asarray(w, float)
    if not (np.isfinite(w).all() and abs(w.sum() - 1) < 1e-6
            and w.min() >= -1e-7 and w.max() <= cap + 1e-7):
        raise RuntimeError(f"optimizer produced infeasible weights: {w}")
    return np.clip(w, 0, cap) / np.clip(w, 0, cap).sum()


def _cov(r: np.ndarray) -> np.ndarray:
    cov = np.atleast_2d(np.cov(r, rowvar=False, ddof=1))
    return (cov + cov.T) / 2


def _slsqp(fun, jac, n: int, cap: float) -> np.ndarray:
    _limit(n, cap)
    x0 = np.ones(n) / n
    res = minimize(fun, x0=x0, jac=jac, method="SLSQP",
                   bounds=[(0, cap)] * n,
                   constraints=[{"type": "eq", "fun": lambda x: np.sum(x) - 1,
                                 "jac": lambda x: np.ones_like(x)}],
                   options={"ftol": 1e-12, "maxiter": 1500})
    if not res.success:
        raise RuntimeError(f"SLSQP failed: {res.message}")
    return _feasible(res.x, cap)


def equal_weight(n: int) -> np.ndarray:
    if not isinstance(n, (int, np.integer)) or n <= 0:
        raise ValueError("n must be positive")
    return np.full(n, 1 / n)


def minimum_variance(r: np.ndarray, cap: float = 1.0, cov: np.ndarray | None = None) -> SolveResult:
    a = returns_matrix(r)
    s = _cov(a) if cov is None else np.asarray(cov, float)
    if s.shape != (a.shape[1], a.shape[1]):
        raise ValueError("covariance has wrong shape")
    s = (s+s.T)/2
    if np.linalg.eigvalsh(s).min() < -1e-10:
        raise ValueError("covariance must be PSD")
    w = _slsqp(lambda x: float(x @ s @ x), lambda x: 2*s@x, a.shape[1], cap)
    return SolveResult(w, float(w@s@w), "minimum_variance", {})


def mean_variance(r: np.ndarray, risk_aversion: float = 3.0,
                  cap: float = 1.0) -> SolveResult:
    a = returns_matrix(r)
    if risk_aversion <= 0:
        raise ValueError("risk_aversion must be >0 and match return frequency")
    mu = a.mean(axis=0); s = _cov(a)
    f = lambda x: float(-mu@x + .5*risk_aversion*(x@s@x))
    j = lambda x: -mu + risk_aversion*(s@x)
    w = _slsqp(f, j, a.shape[1], cap)
    return SolveResult(w, -f(w), "mean_variance", {"risk_aversion": risk_aversion})


def robust_mean_variance(r: np.ndarray, risk_aversion: float = 3.0,
                         kappa: float = 1.65, cap: float = 1.0,
                         mean_cov: np.ndarray | None = None) -> SolveResult:
    """Ellipsoidal robust *mean* uncertainty; not robust covariance.

    Confidence set µ=µ_hat + C_mu^(1/2) u, ||u||_2 <= κ.
    Default C_mu=Sigma/T assumes iid observations; for serial dependence
    supply block-bootstrap / HAC covariance of estimated means.
    """
    a = returns_matrix(r)
    if kappa < 0 or risk_aversion <= 0:
        raise ValueError("kappa>=0; risk_aversion>0 required")
    mu = a.mean(axis=0); s = _cov(a)
    cm = s / a.shape[0] if mean_cov is None else np.asarray(mean_cov, float)
    if cm.shape != s.shape or np.linalg.eigvalsh((cm + cm.T)/2).min() < -1e-10:
        raise ValueError("mean_cov must be symmetric PSD N x N")
    cm = (cm+cm.T)/2
    def penalty(x):
        return np.sqrt(max(float(x@cm@x), 0.0))
    def f(x):
        return float(-mu@x + kappa*penalty(x) + .5*risk_aversion*x@s@x)
    def j(x):
        v=penalty(x)
        return -mu + (kappa*(cm@x)/v if v>1e-12 else 0) + risk_aversion*s@x
    w=_slsqp(f,j,a.shape[1],cap)
    return SolveResult(w,-f(w),"robust_mean_variance",
                       {"risk_aversion":risk_aversion,"kappa":kappa,
                        "mean_uncertainty_surcharge":float(kappa*penalty(w))})


def _tail_lp(r: np.ndarray, alpha: float, cap: float, eps: float,
             uncertain: Iterable[int] | None,
             min_expected_return: float | None,
             method: str) -> SolveResult:
    a=returns_matrix(r);t,n=a.shape
    _limit(n, cap)
    if not 0<alpha<1 or eps<0:
        raise ValueError("alpha in (0,1), epsilon >=0 required")
    uncertain=list(range(n)) if uncertain is None else list(uncertain)
    if len(uncertain)==0 and eps>0:
        raise ValueError("uncertain coordinates cannot be empty for eps>0")
    if any(not isinstance(k,(int,np.integer)) or k<0 or k>=n for k in uncertain):
        raise ValueError("uncertain indexes must be valid asset columns")
    # Variables: n weights; 1 unconstrained VaR threshold eta; t scenario hinges;
    # one z >= max(|w_j|) for a W1 ground L1 norm's dual L_inf.
    has_z=(eps>0)
    dim=n+1+t+int(has_z)
    c=np.zeros(dim);c[n]=1;c[n+1:n+1+t]=1/((1-alpha)*t)
    if has_z:c[-1]=eps/(1-alpha)
    eq=np.zeros((1,dim));eq[0,:n]=1
    up=[];ub=[]
    for i in range(t):
        row=np.zeros(dim);row[:n]=-a[i];row[n]=-1;row[n+1+i]=-1
        up.append(row);ub.append(0)
    if has_z:
        for j in uncertain:
            row=np.zeros(dim);row[j]=1;row[-1]=-1
            up.append(row);ub.append(0)
            # In long-only problems abs(w_j)=w_j. For shorts add two signs.
    if min_expected_return is not None:
        row=np.zeros(dim);row[:n]=-a.mean(axis=0)
        up.append(row);ub.append(-float(min_expected_return))
    bounds=[(0,cap)]*n+[(None,None)]+[(0,None)]*t+([(0,None)] if has_z else [])
    res=linprog(c,A_ub=np.asarray(up),b_ub=np.asarray(ub),A_eq=eq,b_eq=[1.0],
                bounds=bounds,method="highs")
    if not res.success:raise RuntimeError(f"linprog failed: {res.message}")
    w=_feasible(res.x[:n],cap)
    return SolveResult(w,float(res.fun),method,{"alpha":alpha,"epsilon":eps,
        "empirical_cvar":float(res.x[n]+res.x[n+1:n+1+t].sum()/((1-alpha)*t)),
        "var_threshold":float(res.x[n]),"max_uncertain_weight":float(max(w[uncertain])) if uncertain else 0.0})


def cvar(r: np.ndarray, alpha: float = .9, cap: float = 1.0,
         min_expected_return: float | None = None) -> SolveResult:
    return _tail_lp(r,alpha,cap,0,None,min_expected_return,"cvar")


def wasserstein_dro_cvar(r: np.ndarray, alpha: float = .9,
                          epsilon: float = .01, cap: float = 1.0,
                          uncertain: Iterable[int] | None = None,
                          min_expected_return: float | None = None) -> SolveResult:
    """1-Wasserstein, ground L1, unbounded return support, linear scenario loss.

    Objective = empirical CVaR + epsilon * ||w_uncertain||_infty/(1-alpha)
    under the specific ambiguity/support model. If cash is deterministic,
    exclude its column from the support of *uncertain* coordinates.
    """
    return _tail_lp(r,alpha,cap,epsilon,uncertain,min_expected_return,"wasserstein_dro_cvar")


def hrp(r: np.ndarray, linkage_method: str = 'average') -> SolveResult:
    """HRP with configurable single- or average-linkage clustering and bisection.

    The source algorithm uses single linkage; the default average variant is
    retained for backward compatibility. Method choice is in diagnostics.
    """
    a=returns_matrix(r);n=a.shape[1]
    if linkage_method not in ('average','single'):
        raise ValueError('linkage_method must be average or single')
    if n==1:return SolveResult(np.array([1.]),0.,'hrp',{'n':1})
    s=_cov(a);st=np.sqrt(np.maximum(np.diag(s),1e-18))
    corr=np.clip(s/np.outer(st,st),-1,1);np.fill_diagonal(corr,1)
    distance=np.sqrt(np.maximum((1-corr)/2,0));np.fill_diagonal(distance,0)
    order=leaves_list(linkage(squareform(distance,checks=False),method=linkage_method,optimal_ordering=True)).tolist()
    w=np.ones(n);clusters=[order]
    def cluster_var(indices):
        sub=s[np.ix_(indices,indices)];inv=1/np.maximum(np.diag(sub),1e-18)
        local=inv/inv.sum();return float(local@sub@local)
    while clusters:
        new=[]
        for cl in clusters:
            if len(cl)<=1:continue
            m=len(cl)//2;left,right=cl[:m],cl[m:]
            vl,vr=cluster_var(left),cluster_var(right)
            aleft=(vr/(vl+vr)) if vl+vr>1e-18 else .5
            w[left]*=aleft;w[right]*=(1-aleft)
            new.extend([left,right])
        clusters=new
    w=w/w.sum()
    return SolveResult(w,float(w@s@w),'hrp',{'linkage_average':float(linkage_method=='average'),
                                                  'linkage_single':float(linkage_method=='single')})


def risk_contributions(w: np.ndarray,cov: np.ndarray) -> np.ndarray:
    w=np.asarray(w,float);cov=np.asarray(cov,float)
    sigma=float(np.sqrt(max(w@cov@w,0)))
    if sigma<=0:raise ValueError("undefined risk contributions at zero volatility")
    return w*(cov@w)/sigma


def expected_shortfall(losses: np.ndarray, alpha: float=.9) -> float:
    """Fractional worst-tail mean matching the Rockafellar–Uryasev discrete LP."""
    x=np.asarray(losses,float).ravel()
    if not (x.size and np.isfinite(x).all() and 0<alpha<1):raise ValueError("bad losses/alpha")
    d=(1-alpha)*x.size;ordered=np.sort(x)[::-1]
    n=int(np.floor(d+1e-12));part=d-n
    total=ordered[:n].sum()+ (part*ordered[n] if part>1e-12 else 0)
    return float(total/d)


def black_litterman_mean(prior: np.ndarray, cov: np.ndarray, P: np.ndarray,
                          Q: np.ndarray, omega: np.ndarray, tau: float=.05) -> np.ndarray:
    pi=np.asarray(prior,float).reshape(-1);s=np.asarray(cov,float)
    P=np.asarray(P,float);Q=np.asarray(Q,float).reshape(-1);om=np.asarray(omega,float)
    n=pi.size
    if s.shape!=(n,n) or P.ndim!=2 or P.shape[1]!=n or Q.size!=P.shape[0] or om.shape!=(Q.size,Q.size) or tau<=0:
        raise ValueError("incompatible BL parameters")
    if Q.size==0:return pi.copy()
    tc=tau*s;v=P@tc@P.T+om
    correction=tc@P.T@np.linalg.solve(v,Q-P@pi)
    return pi+correction


def performance(monthly_returns: np.ndarray, cash: np.ndarray | float=0.0) -> dict[str,float]:
    p=np.asarray(monthly_returns,float).ravel()
    c=np.broadcast_to(np.asarray(cash,float),p.shape)
    if p.size<2 or not np.isfinite(p).all() or (p<=-1).any() or not np.isfinite(c).all():
        raise ValueError("bad return series")
    wealth=np.r_[1.0,np.cumprod(1+p)]
    mdd=float(np.min(wealth/np.maximum.accumulate(wealth)-1))
    ex=p-c;sd=ex.std(ddof=1)
    cagr=float(wealth[-1]**(12/p.size)-1)
    return {"cagr":cagr,"vol":float(p.std(ddof=1)*np.sqrt(12)),
            "max_drawdown":mdd,"calmar":float(cagr/abs(mdd)) if mdd<0 else float("nan"),
            "excess_sharpe":float(ex.mean()/sd*np.sqrt(12)) if sd>0 else float("nan"),
            "cvar_90_loss":expected_shortfall(-p,.90)}
