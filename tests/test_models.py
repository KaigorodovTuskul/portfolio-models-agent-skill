import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/portfolio-models/scripts'))
from models import (minimum_variance,mean_variance,robust_mean_variance,cvar,
                    wasserstein_dro_cvar,hrp,black_litterman_mean,
                    expected_shortfall,performance,risk_contributions,returns_matrix)
from walkforward_demo import walk_forward

R=np.array([[.04,.01],[-.02,.02],[.03,-.01],[-.08,.01]],float)


def test_hand_calculated_gmv():
    cov=np.array([[.04,.012],[.012,.09]])
    result=minimum_variance(R,cov=cov)
    assert np.isclose(result.weights[0],.078/.106,atol=1e-6)
    assert np.isclose(result.weights.sum(),1)
    assert result.objective < .04


def test_cvar_fixed_weights_and_fractional_tail():
    assert expected_shortfall(-R@np.array([.5,.5]),.75)==pytest.approx(.035)
    assert expected_shortfall(np.array([10.,3.,2.,1.]),.625)==pytest.approx((10+3*.5)/1.5)


def test_cvar_matches_brute_grid():
    from models import expected_shortfall
    result=cvar(R,alpha=.75)
    values=[]
    for a in np.linspace(0,1,1001):
        w=np.array([a,1-a]);values.append(expected_shortfall(-R@w,.75))
    assert min(values)-1e-4 <= result.objective <= min(values)+1e-8


def test_dro_limit_equals_cvar():
    assert np.allclose(cvar(R,alpha=.75).weights,wasserstein_dro_cvar(R,alpha=.75,epsilon=0).weights)
    assert cvar(R,alpha=.75).objective == pytest.approx(wasserstein_dro_cvar(R,alpha=.75,epsilon=0).objective)


def test_dro_objective_dual_manual_and_monotone():
    e=wasserstein_dro_cvar(R,alpha=.75,epsilon=.01)
    w=e.weights
    manual=expected_shortfall(-R@w,.75)+.01*max(w)/(.25)
    assert e.objective==pytest.approx(manual,abs=1e-8)
    assert wasserstein_dro_cvar(R,alpha=.75,epsilon=.02).objective>=e.objective-1e-10


def test_robust_kappa_zero_is_classical_mvo():
    m=mean_variance(R,risk_aversion=3.0)
    r=robust_mean_variance(R,risk_aversion=3.0,kappa=0)
    assert np.allclose(m.weights,r.weights,atol=1e-7)
    assert m.objective==pytest.approx(r.objective,abs=1e-10)


def test_robust_surcharge_grows_with_kappa_fixed_w():
    a=robust_mean_variance(R,risk_aversion=3,kappa=.5)
    b=robust_mean_variance(R,risk_aversion=3,kappa=1.5)
    assert a.weights.sum()==pytest.approx(1)
    assert b.weights.sum()==pytest.approx(1)


def test_hrp_and_simplex():
    a=np.column_stack([R[:,0],R[:,1],np.array([.01,.015,.02,-.005])])
    h=hrp(a)
    assert np.all(h.weights>=0)
    assert np.isclose(h.weights.sum(),1)


def test_bl_no_views_returns_prior():
    prior=np.array([.01,.02]);s=np.array([[.04,.012],[.012,.09]])
    m=black_litterman_mean(prior,s,np.zeros((0,2)),np.array([]),np.zeros((0,0)))
    assert np.allclose(m,prior)


def test_bl_single_view_moves_to_view():
    prior=np.array([.01,.02]);s=np.eye(2)*.04
    m=black_litterman_mean(prior,s,np.array([[1.,0.]]),np.array([.06]),np.array([[.0001]]))
    assert .01 < m[0] < .06
    assert m[1]==pytest.approx(.02)


def test_risk_contribution_analytic():
    s=np.diag([.04,.09]);w=np.array([.6,.4])
    rc=risk_contributions(w,s)
    assert rc[0]==pytest.approx(rc[1])
    assert rc.sum()==pytest.approx(np.sqrt(w@s@w))


def test_portfolio_metrics_includes_initial_nav():
    m=performance(np.array([-.2,.25]))
    assert m['max_drawdown']==pytest.approx(-.2)
    assert m['cagr']==pytest.approx(0)
    assert np.isnan(performance(np.array([.01,.01]))['calmar'])


def test_walkforward_no_lookahead():
    rng=np.random.default_rng(42)
    a=np.column_stack([rng.normal(.01,.01,40),rng.normal(.007,.015,40)])
    ra,ha=walk_forward(a,lookback=12,rebalance=3)
    changed=a.copy();changed[12,0]=.5
    rb,hb=walk_forward(changed,lookback=12,rebalance=3)
    assert np.allclose(ha[0][3],hb[0][3]) # weights cannot see current period shock
    assert ra[0] != rb[0] # realized holding return should feel it
    assert all(tprev < t for t,tprev,*_ in ha)


def test_unusable_data_or_constraints_fail():
    with pytest.raises(ValueError):minimum_variance(np.full((4,2),np.nan))
    with pytest.raises(ValueError):minimum_variance(R,cap=.4)
    with pytest.raises(ValueError):returns_matrix(np.array([[.01,-1.], [.0,.01], [.01,.01], [.02,.02]]))


def test_dro_must_have_uncertain_dimensions_if_positive_eps():
    with pytest.raises(ValueError):wasserstein_dro_cvar(R,epsilon=.01,uncertain=[])
