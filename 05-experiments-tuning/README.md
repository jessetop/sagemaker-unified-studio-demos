# Module 5 — Experiments & Tuning: SageMaker AI vs Unified Studio

A small, cost-capped Bayesian hyperparameter tuning job over the same `train.py`.

| | Path | Status |
|---|---|---|
| **Old way** — SDK HPO tuner | [`launch_tuning.py`](launch_tuning.py) | live-testable |
| **New way** — managed MLflow | [`WALKTHROUGH.md`](WALKTHROUGH.md) | walkthrough |

Cost cap: `max_jobs=4`, `max_parallel_jobs=2`, `ml.m5.large`. Same HPO job both
ways; Unified Studio adds managed MLflow tracking instead of you standing one up.
