# Changes relative to the GitHub `stable` source snapshot

**Source:** `KaigorodovTuskul/portfolio-models-agent-skill`, default branch `stable`, Git tree `5fb7b0b2056e9423dff7441f9e35556bc7fc4503`, retrieved 2026-11-04. This document describes the differences between that snapshot and this archive; no remote commits are created by archive generation.

## Existing upstream adjustments retained

- GitHub default branch is `stable`; repository metadata and license name identify **Tuskul Kaigorodov**.
- English main README (the earlier local RC archive included Russian in its main README).
- `requirements.txt` already included PyYAML; this release retains it and adds scikit-learn for the named shrinkage estimators and pytest for local tests.
- GitHub Actions workflow previously removed upstream remains absent.
- The upstream `SKILL.md` had expanded route conditions and hard invariants, though its body was Russian. Those constraints are preserved in an English router.
- The upstream release and audit notes distinguished self-assessment from independent review; this release packages **no purported external ratings** or pre-filled review payloads.

## New in this release

- `SKILL.md`, working instructions and project documentation use English; localized README files are `docs/i18n/README.zh-CN.md` and `docs/i18n/README.ru-RU.md`.
- Extensive mathematical Python implementations in `advanced_models.py`, with direct analytical and brute-grid checks in restored `tests/`.
- Source and method extensions in `models-extended.md`, `models-tail.md`, `models-robust.md`, `source-catalog.md` and `formula-trace.md`.
- Functional user-data CLI, synthetic sample dataset with transparent generating code and executable comparison example.
- Replaced data-manifest template with a strict JSON Schema. Removed unused sample YAML, pre-packaged round material and draft review-score artifacts.
- Local test runner retained; **no** `.github/workflows/` directory is present.
