# Independent quality reviews

This directory is intentionally empty of reviewer assessments in the distributed release. Four fresh, isolated reviews may be collected after the exact target revision is pinned using `python scripts/goal_workflow.py prepare --round 1`.

Each reviewer must inspect the immutable, same-version archive, cite relevant paths and return the JSON structure in `evals/review-schema.json`. Submit the four signed-by-context review outputs under `reviews/round-01/` and run `python scripts/goal_workflow.py evaluate --input reviews/round-01 --round 1`.

A four-reviewer arithmetic mean greater than 8.5/10 is necessary but not sufficient: every review must be independent, every blocker must be resolved, and local tests must pass. A missing independent review is a failed quality gate, not a zero or an inferred score.
