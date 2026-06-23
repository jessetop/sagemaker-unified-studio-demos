# Module 4 — Training: SageMaker AI Estimator vs Unified Studio

Train the taxi `high_tip` classifier as a managed job — same custom `train.py`,
launched two ways.

| | Path | Status |
|---|---|---|
| Custom training script (Kiro Req 2) | [`train.py`](train.py) | — |
| **Old way** — SDK estimator | [`launch_training.py`](launch_training.py) | live-testable |
| **New way** — project notebook | [`new-unified-studio/train_notebook.ipynb`](new-unified-studio/train_notebook.ipynb) | walkthrough |

Punchline: the **CreateTrainingJob API is identical** old/new; Unified Studio adds
the role, bucket, tracking, and lineage for free. See [`WALKTHROUGH.md`](WALKTHROUGH.md).
`train.py` also provides `model_fn`/`predict_fn` reused by [Module 7](../07-deployment/).
