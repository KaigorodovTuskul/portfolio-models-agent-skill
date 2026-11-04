"""Analytical, metamorphic and solver-consistency tests for documented models."""
import sys
from pathlib import Path
import numpy as np
import pytest
from scipy.optimize import minimize_scalar

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/portfolio-models/scripts'))
from models import minimum_variance, mean_variance, cvar, expected_shortfall
from advanced_models import (
    inverse_volatility, shrinkage_minimum_variance, maximum_sharpe,
    maximum_diversification, risk_budgeting, equal_risk_contribution,
    mean_semivariance, mean_cvar, robust_covariance_mvo,
    black_litterman_portfolio, growth_optimal_kelly, entropic_risk,
    minimum_cdar, mean_cdar, tracking_error_minimum,
    turnover_regularized_minimum_variance)

R = np.array([[.04, .01],[-.02,.02],[.03,-.01],[-.08,.01], [.02,.03],[.01,.01]],float)


def generated(seed=44):
    rng=np.random.default_rng(seed)
    a=rng.normal([.012,.006,.009],[.055,.025,.038],(100,3))
    return a


def check_weights(*items):
    for x in items:
        assert np.isfinite(x.weights).all()
        assert x.weights.sum()==pytest.approx(1,abs=1e-7)
        assert x.weights.min()>-1e-8
        assert x.weights.max()<1+1e-8


def test_inverse_vol_analytical():
    a=np.array([[.1,.2],[-.1,-.2],[.1,.2],[-.1,-.2]])
    x=inverse_volatility(a)
    assert x.weights==pytest.approx([2/3,1/3],abs=1e-8)


def test_shrinkage_estimators_psd_and_simplex():
    a=generated()
    for kind in ('ledoit_wolf','oas'):
        x=shrinkage_minimum_variance(a,kind)
        check_weights(x)
        assert 0<=x.diagnostics['shrinkage']<=1
    with pytest.raises(ValueError):shrinkage_minimum_variance(a,'made-up')


def test_max_sharpe_diagonal_analytic():
    a=np.array([[.08,.04],[.00,.00],[.06,.08],[.02,-.04], [.08,.04],[.00,.00]])
    x=maximum_sharpe(a,risk_free=0)
    mu=a.mean(0);cov=np.cov(a,rowvar=False)
    candidates=[]
    for p in np.linspace(0,1,10001):
        w=np.array([p,1-p]);candidates.append(float(mu@w/np.sqrt(w@cov@w)))
    assert x.objective>=max(candidates)-1e-6
    check_weights(x)


def test_max_sharpe_requires_positive_excess():
    with pytest.raises(ValueError):maximum_sharpe(R,risk_free=1.)


def test_maximum_diversification_analytical_uncorrelated():
    a=np.array([[.1,0.],[0.,.2],[-.1,0],[0,-.2], [.1,0],[0,.2],[-.1,0],[0,-.2]])
    x=maximum_diversification(a)
    vol=a.std(0,ddof=1)
    expected=(1/vol);expected/=expected.sum()
    assert x.weights==pytest.approx(expected,abs=1e-6)


def test_risk_budget_risk_contributions():
    a=generated();b=np.array([.2,.3,.5]);x=risk_budgeting(a,b)
    cov=np.cov(a,rowvar=False)
    frac=x.weights*(cov@x.weights)/(x.weights@cov@x.weights)
    assert frac==pytest.approx(b,abs=1e-5)
    check_weights(x,equal_risk_contribution(a))


def test_risk_budget_excludes_singular_and_zero_budget():
    r=np.column_stack([R[:,0],R[:,0]])
    with pytest.raises(ValueError):risk_budgeting(r)
    with pytest.raises(ValueError):risk_budgeting(R,[1,0])


def test_mean_cvar_matches_direct_objective_and_grid():
    alpha=.75;lam=1.8
    x=mean_cvar(R,alpha,lam)
    objective=float((R@x.weights).mean()-lam*expected_shortfall(-R@x.weights,alpha))
    assert x.objective==pytest.approx(objective,abs=1e-8)
    grid=[]
    for q in np.linspace(0,1,2001):
        w=np.array([q,1-q]);grid.append((R@w).mean()-lam*expected_shortfall(-R@w,alpha))
    assert x.objective>=max(grid)-1e-7


def test_mean_cvar_infeasible_floor():
    with pytest.raises(RuntimeError):mean_cvar(R,min_expected_return=1.)


def test_robust_covariance_rho_zero_equal_mvo():
    a=generated();m=mean_variance(a,risk_aversion=4.)
    q=robust_covariance_mvo(a,risk_aversion=4.,radius=0)
    assert q.weights==pytest.approx(m.weights,abs=1e-7)
    assert q.objective==pytest.approx(m.objective,abs=1e-9)


def test_robust_covariance_rank_one_worst_case():
    a=generated();rho=.0012;w=np.array([.2,.3,.5])
    cov=np.cov(a,rowvar=False)
    delta=rho*np.outer(w,w)/np.linalg.norm(w)**2
    assert np.linalg.norm(delta,'fro')==pytest.approx(rho)
    assert w@(cov+delta)@w==pytest.approx(w@cov@w+rho*sum(w*w))
    assert np.linalg.eigvalsh(cov+delta).min()>-1e-10


def test_robust_covariance_worst_utility_is_nonincreasing_with_radius():
    a=generated()
    val=[robust_covariance_mvo(a,risk_aversion=2.,radius=r).objective for r in [0,.001,.01]]
    assert np.all(np.diff(val)<1e-7)


def test_bl_portfolio_no_views_matches_mean_forecast_objective():
    a=generated();pi=a.mean(0);n=a.shape[1]
    bl=black_litterman_portfolio(a,pi,np.zeros((0,n)),np.empty(0),np.zeros((0,0)))
    mv=mean_variance(a)
    assert bl.weights==pytest.approx(mv.weights,abs=1e-6)


def test_mean_semivariance_objective_and_upside_irrelevance():
    a=R;lam=2.5
    x=mean_semivariance(a,risk_aversion=lam,target=0)
    downside=np.minimum(a@x.weights,0)
    assert x.objective==pytest.approx((a@x.weights).mean()-lam/2*np.mean(downside**2))


def test_kelly_log_optimality_vs_bruteforce():
    x=growth_optimal_kelly(R)
    grid=[np.log1p(R@np.array([p,1-p])).mean() for p in np.linspace(0,1,5001)]
    assert x.objective>=max(grid)-1e-9


def test_entropic_risk_limit_to_negative_mean():
    r=generated();x=entropic_risk(r,gamma=1e-4)
    from scipy.special import logsumexp
    direct=float(logsumexp(-1e-4*r@x.weights)-np.log(len(r)))/1e-4
    assert x.objective==pytest.approx(direct,abs=1e-8)
    assert x.objective==pytest.approx(-float(r.mean(0)@x.weights),abs=2e-6)


def manual_cdar(r,w,alpha):
    pnl=np.cumsum(r@w)
    draw=np.maximum.accumulate(np.r_[0,pnl])[1:]-pnl
    return expected_shortfall(draw,alpha)


def test_cdar_lp_matches_bruteforce():
    x=minimum_cdar(R,alpha=.75)
    grid=[manual_cdar(R,np.array([p,1-p]),.75) for p in np.linspace(0,1,2001)]
    assert x.objective<=min(grid)+1e-7
    assert x.objective==pytest.approx(manual_cdar(R,x.weights,.75),abs=1e-8)


def test_mean_cdar_matches_direct_and_grid():
    lam=2.5;x=mean_cdar(R,alpha=.75,risk_aversion=lam)
    val=(R@x.weights).mean()-lam*manual_cdar(R,x.weights,.75)
    assert x.objective==pytest.approx(val,abs=1e-8)
    grid=[(R@np.array([p,1-p])).mean()-lam*manual_cdar(R,np.array([p,1-p]),.75)
          for p in np.linspace(0,1,2001)]
    assert x.objective>=max(grid)-1e-7


def test_cdar_depends_on_path_order_but_cvar_does_not():
    x=np.array([[-.1,.01],[.07,.01],[.06,.01],[-.08,.01],[.05,.01]])
    y=x[[0,3,1,2,4]]
    w=np.array([1,0])
    assert expected_shortfall(-x@w,.6)==pytest.approx(expected_shortfall(-y@w,.6))
    assert manual_cdar(x,w,.6)!=pytest.approx(manual_cdar(y,w,.6))


def test_tracking_error_exact_benchmark():
    a=generated();b=np.array([.15,.25,.6]);x=tracking_error_minimum(a,b)
    assert x.weights==pytest.approx(b,abs=1e-6)
    assert x.objective==pytest.approx(0,abs=1e-9)


def test_turnover_regularization_prevents_trade_high_lambda():
    a=generated();p=np.array([.2,.3,.5])
    x=turnover_regularized_minimum_variance(a,p,turnover_penalty=1.)
    assert x.weights==pytest.approx(p,abs=1e-6)


def test_turnover_regularization_recovers_gmv_at_zero_penalty():
    a=generated();p=np.ones(3)/3
    x=turnover_regularized_minimum_variance(a,p,turnover_penalty=0.)
    y=minimum_variance(a)
    assert x.weights==pytest.approx(y.weights,abs=1e-5)


def test_numerical_feasibility_across_advanced_models():
    a=generated()
    items=[inverse_volatility(a),shrinkage_minimum_variance(a),maximum_sharpe(a),
           maximum_diversification(a),risk_budgeting(a),mean_semivariance(a),
           mean_cvar(a),robust_covariance_mvo(a),growth_optimal_kelly(a),
           entropic_risk(a),minimum_cdar(a),mean_cdar(a)]
    check_weights(*items)


def test_not_permitted_to_invent_covariance_or_risk_budget():
    a=generated()
    with pytest.raises(ValueError):risk_budgeting(a,np.array([.5,.6,-.1]))
    with pytest.raises(ValueError):robust_covariance_mvo(a,radius=-.01)
    with pytest.raises(ValueError):entropic_risk(a,gamma=0)


def test_original_style_single_linkage_hrp_and_average_variant():
    from models import hrp
    a=generated()
    single=hrp(a,linkage_method='single')
    avg=hrp(a,linkage_method='average')
    check_weights(single,avg)
    assert single.diagnostics['linkage_single']==1
    assert avg.diagnostics['linkage_average']==1
    with pytest.raises(ValueError):hrp(a,linkage_method='unknown')
