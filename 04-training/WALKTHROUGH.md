# Module 4 — Training: SageMaker AI Estimator vs Unified Studio

**~5 minutes.** Train the taxi `high_tip` classifier as a managed SageMaker
training job — the same custom script, launched two ways.

## Learning objectives
- Run a custom training script ([`train.py`](train.py)) as a managed job on the
  cheapest practical instance, with hyperparameters, S3 channels, and scraped
  metrics.
- See that the **training job API is identical** old-way and new-way — the
  difference is *where it's launched and how it's governed*.

## Prerequisites / starting state
- `shared/prepare_ml_data.py` has written train/validation/test CSVs to
  `s3://roi-smdemo-029331796573-us-east-2/ml/taxi/`.
- Shared exec role exists.
- Cross-reference: features come from the Module 1/2 pipeline (`PIPELINE_SPEC` T16).

## Old way — SageMaker AI (SDK)
```bash
python launch_training.py \
  --bucket roi-smdemo-029331796573-us-east-2 \
  --role-arn arn:aws:iam::029331796573:role/roi-smdemo-exec-role \
  --profile roitraining --region us-east-2
```
Talk through the lifecycle as logs stream (Kiro Req 5.7): **provision instance →
download data from the S3 channels → run `train.py` → upload `model.tar.gz` to S3
→ tear down**. You pay only for the seconds the instance runs.

What to point at in `train.py`:
- Hyperparameters parsed from CLI args (`--learning-rate`, `--n-estimators`,
  `--max-depth`).
- `SM_CHANNEL_TRAIN` / `SM_CHANNEL_VALIDATION` reads, `SM_MODEL_DIR` write.
- `validation_accuracy=...` / `validation_auc=...` lines → scraped as metrics.

## New way — Unified Studio
Open a project notebook ([`new-unified-studio/train_notebook.ipynb`](new-unified-studio/train_notebook.ipynb))
and run the **same `SKLearn` estimator code**. The differences to call out:
- The project supplies the **execution role** and **default bucket** — no ARNs to
  paste.
- The run shows up in the project's **training jobs / experiment** view with
  lineage back to the input dataset asset.
- One governed place for data → notebook → training → model, instead of stitching
  the console + SDK + S3 yourself.

## Old vs new — talking points
| | SageMaker AI (old) | Unified Studio (new) |
|---|---|---|
| Launch from | SDK / notebook you wire up | governed project notebook |
| Role/bucket | you pass ARNs | project provides |
| Tracking | you add Experiments | catalog + lineage built in |
| The job itself | **identical CreateTrainingJob** | **identical CreateTrainingJob** |

## Cost & cleanup
One `ml.m5.large` for ~3-5 min ≈ a few cents; the instance is torn down
automatically when the job ends. No standing cost.
