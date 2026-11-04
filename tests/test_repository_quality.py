"""Public release contracts, documentation routing and CLI behavior."""
from pathlib import Path
import re
import subprocess
import sys
import json
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/portfolio-models/SKILL.md'
CLI=ROOT/'skills/portfolio-models/scripts/portfolio_cli.py'
DATA=ROOT/'datasets/synthetic_monthly_returns.csv'


def test_no_github_actions_workflows():
    d=ROOT/'.github/workflows'
    assert not d.exists(), 'all testing is local; GitHub Actions workflows are forbidden'


def test_canonical_english_and_two_real_translations():
    skill=SKILL.read_text(encoding='utf-8')
    assert 'language: "en"' in skill
    assert not re.search('[А-Яа-яЁё一-龥]',skill)
    for loc,terms in [('zh-CN',['组合','数学','安装','风险']),('ru-RU',['портфел','доходност','оптимизац'])]:
        p=ROOT/f'docs/i18n/README.{loc}.md'
        assert p.exists() and len(p.read_text(encoding='utf-8'))>1200
        assert all(t in p.read_text(encoding='utf-8').lower() for t in terms)
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    assert 'README.ru-RU.md' in readme and 'README.zh-CN.md' in readme
    assert not re.search('[А-Яа-яЁё]',re.sub(r'\[[^]]*\]\([^)]*\)','',readme))


def test_code_and_tests_linked_from_skill():
    t=SKILL.read_text(encoding='utf-8')
    assert 'advanced_models.py' in t
    assert 'models-extended.md' in t
    assert 'model-map.md' in t
    assert 'formula-trace.md' in t
    assert 'source-catalog.md' in t
    assert len(t.splitlines())<100


def test_review_schema_is_schema_not_an_invented_review():
    p=ROOT/'evals/review-schema.json'
    s=json.loads(p.read_text(encoding='utf-8'))
    assert s['$schema'].endswith('schema')
    assert 'score' in s['required']
    assert 'reviewer_model' in s['required']
    assert not (ROOT/'reviews/LOCAL_AUDIT.md').exists()
    assert not (ROOT/'evals/ready/round-03').exists()


def test_license_preserves_author():
    s=(ROOT/'LICENSE').read_text(encoding='utf-8')
    assert 'Tuskul Kaigorodov' in s
    assert s.startswith('MIT License')


def test_cli_fits_synthetic_csv_without_claiming_oos():
    out=subprocess.run([sys.executable,str(CLI),str(DATA),'--model','cvar','--alpha','.9'],
                       cwd=ROOT,text=True,capture_output=True)
    assert out.returncode==0,out.stderr
    z=json.loads(out.stdout)
    assert z['status']=='in_sample_fit_only'
    assert z['observations']==72
    assert abs(sum(z['weights'].values())-1)<1e-8


def test_cli_refuses_cap_not_supported():
    out=subprocess.run([sys.executable,str(CLI),str(DATA),'--model','erc','--cap','.5'],
                       cwd=ROOT,text=True,capture_output=True)
    assert out.returncode!=0
    assert 'does not implement' in out.stderr


def test_cli_refuses_unsorted_duplicate_dates(tmp_path):
    p=tmp_path/'bad.csv'
    p.write_text('date,a,b\n2026-03-31,.01,.02\n2026-02-28,.02,.01\n2026-03-31,.00,.01\n2026-04-30,.03,.02\n')
    out=subprocess.run([sys.executable,str(CLI),str(p),'--model','gmv'],
                       cwd=ROOT,text=True,capture_output=True)
    assert out.returncode!=0
    assert 'dates must be unique' in out.stderr


def test_source_bibliography_corresponds_to_extended_models():
    source=(ROOT/'skills/portfolio-models/references/source-catalog.md').read_text(encoding='utf-8')
    trace=(ROOT/'skills/portfolio-models/references/formula-trace.md').read_text(encoding='utf-8')
    for id in ['EN-01','EN-05','EN-08','EN-09','EN-15','EN-16','EN-17','EN-18','EN-19','EN-20','EN-21','ZH-01','RU-01']:
        assert id in source
    for model in ['Risk','Sharpe','Kelly','Black','CVaR','Wasserstein','HRP','Robust']:
        assert model.lower() in trace.lower()


def test_doc_links_exist():
    for p in ROOT.rglob('*.md'):
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            dest=link.split('#',1)[0]
            if dest and not dest.startswith(('https://','http://','mailto:')):
                assert (p.parent/dest).exists(),f'{p}: {dest}'
