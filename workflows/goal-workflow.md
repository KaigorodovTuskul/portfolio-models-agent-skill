# GOAL workflow — evidence-led model and skill review

Use this portable protocol with a harness that can execute independent reviewer tasks. The workflow is self-contained and **does not require GitHub Actions**.

1. **GOAL:** freeze the target source tree, scope and acceptance rules. Four axes: `ARCHITECT`, `SOURCES`, `QUANT`, `PRACTICE`. Anchor scores at 4 (starting), 6 (normal), 8 (high quality), >8.5 (release threshold, only with direct evidence).
2. **BUILD:** implement or change the mathematical models, source trace and documentation; run `python -m pytest -q tests` and `python scripts/goal_workflow.py check` locally. Record implementation failures honestly.
3. **PIN:** run `python scripts/goal_workflow.py prepare --round 1` on a frozen revision. The resulting manifest contains a SHA256 of the source and the reviewer briefs.
4. **REVIEW:** launch four genuinely independent, fresh review contexts in a capable orchestration environment. Give each the same pinned repository, rubric and role-specific brief. Reviewers must not read other reviewer scores or same-round assessments. Collect evidence-backed JSON in `reviews/round-01/ARCHITECT.json`, `SOURCES.json`, `QUANT.json`, `PRACTICE.json` following `evals/review-schema.json`.
5. **SCORE:** `python scripts/goal_workflow.py evaluate --input reviews/round-01 --round 1`. This fails closed on incomplete evidence, reused reviewer IDs, wrong artifact SHA, blockers, invalid scores or local tests. The mean must be **strictly greater** than 8.5/10; 8.5 exactly is insufficient.
6. **IMPROVE:** resolve every mathematical/source blocker, fix review findings, pin a new immutable revision, repeat from step 3 with round 2 or higher. Do not alter the reviewed revision after pinning; do not silently substitute local self-ratings for independent evidence.
7. **RELEASE:** package a tested immutable source tree and its authentic reviewer evidence. Publishing or modifying an existing remote repository is a separate, authorized action.

## Local invocation

```bash
python -m pytest -q tests
python scripts/goal_workflow.py check
python scripts/goal_workflow.py prepare --round 1
python scripts/goal_workflow.py evaluate --input reviews/round-01 --round 1
```

The last command is expected to reject incomplete review collections. A model's apparent historical success is not itself proof of generalization; financial-model validation additionally follows the [point-in-time backtest protocol](../skills/portfolio-models/references/backtest-protocol.md).
