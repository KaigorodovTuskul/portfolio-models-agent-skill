import sys
from pathlib import Path
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/portfolio-models/scripts'))
from models import (cvar,wasserstein_dro_cvar,minimum_variance,robust_mean_variance,
                    mean_variance,expected_shortfall,hrp,performance,black_litterman_mean)


def generated():
    rng=np.random.default_rng(57)
    return rng.normal(.006,.023,(100,5))


def test_feasible_constraints_across_models():
    a=generated()
    for x in [minimum_variance(a,cap=.3),mean_variance(a,cap=.3),
              robust_mean_variance(a,kappa=1,cap=.3),cvar(a,alpha=.9,cap=.3),
              wasserstein_dro_cvar(a,epsilon=.004,alpha=.9,cap=.3)]:
        assert abs(x.weights.sum()-1)<1e-8
        assert min(x.weights)>-1e-8 and max(x.weights)<.3000001


def test_more_robust_uncertainty_cannot_improve_robust_objective_value():
    a=generated()
    values=[robust_mean_variance(a,kappa=k).objective for k in [0,.5,1,2]]
    assert np.all(np.diff(values)<1e-8)


def test_cvar_return_target_feasible():
    a=generated()
    target=np.mean(a,axis=0).min() + .5*(np.mean(a,axis=0).max()-np.mean(a,axis=0).min())
    z=cvar(a,alpha=.8,min_expected_return=target)
    assert a.mean(axis=0)@z.weights>=target-1e-8


def test_cvar_infeasible_return_target_errors():
    with pytest.raises(RuntimeError):cvar(generated(),min_expected_return=1.0)


def test_epsilon_large_discourages_concentration():
    a=generated()
    x=wasserstein_dro_cvar(a,alpha=.9,epsilon=1.0)
    assert np.max(x.weights)<.205


def test_robust_mean_cov_custom_shape_rejection():
    with pytest.raises(ValueError):robust_mean_variance(generated(),mean_cov=np.eye(4))


def test_hrp_near_zero_variance_asset():
    a=generated();a[:,-1]=.0004
    x=hrp(a);assert np.isfinite(x.weights).all() and x.weights.sum()==pytest.approx(1)


def test_bl_view_uncertainty_softens_posterior():
    p=np.array([.02,.03]);cov=np.eye(2)*.02
    P=np.array([[1,0]]);Q=np.array([.07])
    tight=black_litterman_mean(p,cov,P,Q,np.array([[.00001]]))[0]
    loose=black_litterman_mean(p,cov,P,Q,np.array([[.2]]))[0]
    assert .02 < loose < tight < .07


def test_es_tail_frac_100_percent():
    assert expected_shortfall([-.01,.0,.03,.10],alpha=.75)==pytest.approx(.1)
    assert expected_shortfall([-.01,.0,.03,.10],alpha=.875)==pytest.approx(.1)


def test_cvar_positive_and_negative_sign_convention():
    p=np.array([.01,.03,-.05,.02,.01])
    assert performance(p)['cvar_90_loss']==pytest.approx(.05)


def test_no_free_everlasting_annualization():
    p=np.array([.02]*12)
    assert performance(p)['cagr']==pytest.approx(1.02**12-1)


def test_source_reference_catalog_and_evals():
    import json
    d=json.loads((ROOT/'evals/tasks.json').read_text(encoding='utf-8'))
    assert len(d['cases'])>=5
    assert len({x['id'] for x in d['cases']})==len(d['cases'])
    for x in d['cases']:assert (ROOT/x['task']).exists()
