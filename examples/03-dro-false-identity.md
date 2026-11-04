# Agent task: is DRO-CVaR = empirical CVaR + epsilon*norm(weight)?

**Input:** researcher proposes epsilon*||w||_1 on a long-only fully invested portfolio, claims "this creates robust diversification under L∞ ground metric".

**Expected agent:** open `models-robust.md`; explain that `||w||_1 = 1` is *constant*, thus it adds a constant and cannot change weights for fully invested long-only; identify ground-norm/dual-norm and support; verify epsilon unit, α and no arbitrary penalty claim; require κ=0/ε=0 tests.
