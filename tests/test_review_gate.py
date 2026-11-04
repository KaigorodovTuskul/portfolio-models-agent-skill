import sys
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]


def test_missing_independent_reports_denies_release(tmp_path):
    p=subprocess.run([sys.executable,'scripts/goal_workflow.py','evaluate',
                      '--input',str(tmp_path),'--round','777'],cwd=ROOT,
                     text=True,capture_output=True)
    assert p.returncode==2
    assert 'missing ARCHITECT' in p.stdout
    assert 'missing QUANT' in p.stdout


def test_formula_trace_and_provenance_assets():
    doc=(ROOT/'skills/portfolio-models/references/formula-trace.md').read_text(encoding='utf-8')
    for name in ['Markowitz','CVaR','Wasserstein','HRP','Robust MVO','Black–Litterman']:
        assert name in doc
    import json
    schema=json.loads((ROOT/'skills/portfolio-models/assets/dataset-schema.json').read_text(encoding='utf-8'))
    assert schema['type']=='object'
    assert 'return_kind' in schema['required']
    assert 'trading_halt_policy' in schema['required']
