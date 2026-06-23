# Module 5 — Experiments & Tuning: SageMaker AI vs Unified Studio

**~5 minutes.** Run a small Bayesian hyperparameter tuning job and compare trials,
then show the same tracking in Unified Studio's managed MLflow.

## Learning objectives
- Launch a cost-capped Automatic Model Tuning job over the custom `train.py`.
- Read the best trial's hyperparameters and objective value.
- Contrast classic SageMaker Experiments with Unified Studio's managed MLflow.

## Prerequisites / starting state
- `ml/taxi/` splits exist; Module 4 understood (same `train.py`).
- Cross-reference: training contract from [Module 4](../04-training/WALKTHROUGH.md).

## Old way — SageMaker AI (SDK)
```bash
python launch_tuning.py \
  --bucket roi-smdemo-029331796573-us-east-2 \
  --role-arn arn:aws:iam::029331796573:role/roi-smdemo-exec-role \
  --profile roitraining --region us-east-2
```
- **Search space** (Kiro Req 6.1): `learning-rate` (continuous) + `max-depth`
  (integer). **Objective**: maximize `validation:auc` (Req 6.2).
- **Cost cap** (Req 6.4): `max_jobs=4`, `max_parallel_jobs=2`, `ml.m5.large`.
- After it finishes, the script prints the **best job, its hyperparameters, and
  final AUC** (Req 6.3).
- Instructor note (Req 6.6): Bayesian search uses prior trials to pick the next
  point — fewer jobs than grid/random for the same quality; early stopping kills
  unpromising trials.

## New way — Unified Studio (managed MLflow)
SageMaker provides **managed MLflow**; in a project you set the tracking URI and
log params/metrics, then browse runs in the MLflow UI launched from the project.
The tuning job itself is the same API; the difference is trials land in a managed,
governed MLflow tracking server instead of you standing one up.

## Old vs new — talking points
| | SageMaker AI | Unified Studio |
|---|---|---|
| Track runs | Experiments SDK | managed MLflow |
| Compare trials | analytics dataframe | MLflow UI |
| The tuner | **same HPO job** | **same HPO job** |

## Cost & cleanup
4 short jobs × `ml.m5.large` ≈ cents total; all instances auto-terminate.
