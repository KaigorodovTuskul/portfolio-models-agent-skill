# Agent task: Robust MVO code audit

**Input:** developer labels `max(mu@w - 1.65*sqrt(w@cov@w/T) -2.5*w@cov@w)` as "worst-case robust covariance". Previous benchmark had losses with gold after 2022 shock.

**Expected agent:** read `models-robust.md`, detect that penalty represents *mean* uncertainty, while covariance term is ordinary variance; correct λ factor convention, units; ask whether `mu` is total or excess (for fully invested common rf shifts choice does not change, but cash/proxy modeling matters); test κ=0; inspect drift/costs/trading availability and nested calibration.
