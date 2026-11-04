# Contributing

1. Specify the **exact mathematical model** and cite a primary journal paper, original author manuscript, institutional publication or official specification in [`source-catalog.md`](skills/portfolio-models/references/source-catalog.md). Record access limitations and provenance.
2. Keep [`SKILL.md`](skills/portfolio-models/SKILL.md) short. Add equations and conditional references in the correct topic file; add a source/formula/code/test record to [`formula-trace.md`](skills/portfolio-models/references/formula-trace.md).
3. Implement the precise optimization objective. State return units and input time frequency; distinguish exact reformulations from approximations, feasible constraints from solver defaults, and fit quality from out-of-sample behavior.
4. Add deterministic analytical or brute-force numerical checks, including zero-uncertainty and infeasible cases when applicable. Execute `python -m pytest -q tests` and `python scripts/goal_workflow.py check` **locally**. GitHub Actions is intentionally not used.
5. Update the English [`README.md`](README.md) and, for meaningful user-facing changes, its [`zh-CN`](docs/i18n/README.zh-CN.md) and [`ru-RU`](docs/i18n/README.ru-RU.md) translations.
6. Preserve reproducible source citations, original paper licensing and all security/data-rights restrictions. Do not commit credentials, private broker datasets, copyrighted full papers or purported third-party reviews that were not actually performed.

Maintaining source accuracy, reproducible numerical correctness and explicit method boundaries takes precedence over adding more model names.
