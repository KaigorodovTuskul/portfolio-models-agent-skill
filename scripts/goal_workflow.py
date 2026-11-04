#!/usr/bin/env python3
"""Offline GOAL checks/prompts/review aggregation. Does not spawn LLM agents."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/portfolio-models/SKILL.md'
ROLES=['ARCHITECT','SOURCES','QUANT','PRACTICE']

def manifest():
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts
                 and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts
                 and not p.name.endswith('.pyc') and not str(p.relative_to(ROOT)).startswith('reviews/round-')
                 and not str(p.relative_to(ROOT)).startswith('evals/ready/'))
    h=hashlib.sha256()
    for p in files:
        h.update(str(p.relative_to(ROOT)).encode()+b'\0');h.update(p.read_bytes())
    return {'root_sha256':h.hexdigest(),'files':len(files)}

def check():
    from yaml import safe_load
    errors=[];t=SKILL.read_text(encoding='utf-8')
    if not t.startswith('---\n'):errors.append('SKILL.md missing frontmatter')
    else:
        fm=safe_load(t.split('---',2)[1])
        if fm.get('name')!='portfolio-models':errors.append('incorrect skill name')
        if not fm.get('description') or len(fm['description'])>1024:errors.append('invalid trigger description')
    if len(t.splitlines())>450:errors.append('SKILL.md too large')
    src=(SKILL.parent/'references/source-catalog.md').read_text(encoding='utf-8')
    if len(re.findall(r'https?://',src))<20:errors.append('bibliography too sparse')
    for label in ('EN-01','EN-05','EN-06','EN-08','EN-09','RU-01','ZH-01','ZH-02'):
        if label not in src:errors.append('source missing '+label)
    for p in ROOT.rglob('*.md'):
        if '.git' in p.parts:continue
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            dest=link.split('#',1)[0]
            if not dest or dest.startswith(('http://','https://','mailto:','npx')):continue
            if not (p.parent/dest).exists():errors.append(f'broken link: {p.relative_to(ROOT)} -> {link}')
    if errors:
        for e in errors:print('FAIL:',e)
        return 1
    print('PASS: frontmatter, routing budget, multilingual sources, internal links; files:',manifest()['files'])
    return 0

def prepare(number:int):
    if number<1:raise ValueError('round >=1 required')
    d=ROOT/'evals/ready'/f'round-{number:02d}';d.mkdir(parents=True,exist_ok=True)
    m=manifest()
    for role in ROLES:
        (d/f'{role}.md').write_text(
            f'# Isolated reviewer {role} | round {number}\n\nSnapshot SHA256: {m["root_sha256"]}\n\n'
            f'Read `evals/RUBRIC.md`, role `{role}` in `evals/REVIEWER_PROMPTS.md`, and '
            '`evals/review-schema.json`. In a fresh independent LLM context audit the entire repo. '
            'Do not see other reviewers. Return JSON with actual model, run ID, evidence, '\
            f'score, blockers, findings to `reviews/round-{number:02d}/{role}.json`. '
            'Mark independent=true ONLY if the run was independent.\n',encoding='utf-8')
    (d/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    print('PREPARED:',d,'SHA256:',m['root_sha256'])

def evaluate(directory:Path,number:int):
    entries=[];errors=[]
    for role in ROLES:
        p=directory/(role+'.json')
        if not p.exists():errors.append('missing '+role);continue
        try:a=json.loads(p.read_text())
        except Exception as e:errors.append(role+' invalid JSON '+str(e));continue
        if a.get('role')!=role or a.get('round')!=number:errors.append(role+' role/round mismatch')
        score=a.get('score')
        if not isinstance(score,(int,float)) or not 1<=score<=10:errors.append(role+' invalid score')
        if a.get('independent') is not True:errors.append(role+' not independent')
        if not a.get('reviewer_model') or not a.get('reviewer_run_id') or not a.get('evidence') or not isinstance(a.get('findings'),list):errors.append(role+' missing evidence/identity')
        prepared=ROOT/'evals/ready'/f'round-{number:02d}'/'manifest.json'
        if not prepared.exists():errors.append('missing pinned manifest; run prepare first')
        else:
            pinned=json.loads(prepared.read_text()).get('root_sha256')
            if a.get('artifact_sha256')!=pinned:errors.append(role+' not reviewing pinned artifact')
            if manifest()['root_sha256']!=pinned:errors.append('repository changed since prepare')
        if a.get('blockers'):errors.append(role+' blockers: '+str(a['blockers']))
        entries.append(a)
    if len(set(x.get('reviewer_run_id') for x in entries))!=len(entries):errors.append('reused run IDs')
    if errors:
        for x in sorted(set(errors)):print('GATE FAIL:',x)
        return 2
    if check():errors.append('static quality checks failed')
    # Re-run numerical and structural tests at the exact review snapshot.
    import subprocess
    tests=subprocess.run([sys.executable,'-m','pytest','-q'],cwd=ROOT,capture_output=True,text=True)
    if tests.returncode!=0:errors.append('pytest failed: '+tests.stdout[-500:])
    if errors:
        for x in sorted(set(errors)):print('GATE FAIL:',x)
        return 2
    mean=sum(a['score'] for a in entries)/4
    print('INDEPENDENT MEAN:',round(mean,3),'RESULT:','PASS' if mean>8.5 else 'NEXT ROUND')
    return 0 if mean>8.5 else 1

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    sub=ap.add_subparsers(dest='command',required=True)
    sub.add_parser('check')
    p=sub.add_parser('prepare');p.add_argument('--round',type=int,required=True)
    p=sub.add_parser('evaluate');p.add_argument('--round',type=int,required=True);p.add_argument('--input',type=Path,required=True)
    args=ap.parse_args()
    if args.command=='check':return check()
    if args.command=='prepare':prepare(args.round);return 0
    return evaluate(args.input,args.round)
if __name__=='__main__':sys.exit(main())
