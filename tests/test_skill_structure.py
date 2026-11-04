from pathlib import Path
import subprocess
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/portfolio-models/SKILL.md'


def test_frontmatter_and_progressive_disclosure():
    t=SKILL.read_text(encoding='utf-8')
    assert t.startswith('---\n')
    front=yaml.safe_load(t.split('---',2)[1])
    assert front['name']=='portfolio-models'
    assert len(front['description'])<1024
    assert len(t.splitlines())<450
    for p in ['references/model-map.md','references/models-classical.md',
              'references/models-robust.md','references/source-catalog.md',
              'references/backtest-protocol.md']:
        assert p in t
        assert (SKILL.parent/p).exists()


def test_goal_workflow_gates():
    cmd=[sys.executable,'scripts/goal_workflow.py','check']
    run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    assert run.returncode==0,(run.stdout,run.stderr)


def test_bibliography_in_three_languages():
    txt=(SKILL.parent/'references/source-catalog.md').read_text(encoding='utf-8')
    for marker in ['EN-01','EN-05','EN-08','EN-09','RU-01','ZH-01','ZH-02']:
        assert marker in txt
    assert 'abstract-only' in txt
    assert 'doi.org/' in txt
