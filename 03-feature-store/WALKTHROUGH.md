# Module 3 — Feature Store: SageMaker AI vs Unified Studio

**~5 minutes.** Define and populate a feature group for the engineered taxi
features, then show it as a governed catalog asset.

## Learning objectives
- Define a Feature Store schema from a DataFrame and ingest records via the SDK.
- Understand online vs offline store (and their cost trade-off).
- See how the same feature group becomes a **discoverable, governed asset** in the
  Unified Studio catalog.

## Prerequisites / starting state
- `shared/prepare_ml_data.py` has produced `ml/taxi/train/train.csv`.
- Shared exec role exists.
- Cross-reference: features from [PIPELINE_SPEC](../PIPELINE_SPEC.md).

## Old way — SageMaker AI (SDK)
```bash
python feature_store_ingest.py \
  --bucket roi-smdemo-029331796573-us-east-2 \
  --role-arn arn:aws:iam::029331796573:role/roi-smdemo-exec-role \
  --profile roitraining --region us-east-2 --rows 2000
```
Point at: `load_feature_definitions` (schema inferred), `create()` (online/offline
store), `ingest()`. Note the **record identifier** + **event time** requirements.

## New way — Unified Studio
In the project, open **Data → Feature groups** (or the catalog). The same
`roi-smdemo-taxi-features` group appears as an **asset**: searchable, permissioned,
with lineage back to the producing job. Add a description/glossary terms to show
governance. New feature groups can be created from a project notebook with the
identical SDK call — they're automatically catalogued.

## Old vs new — talking points
| | SageMaker AI | Unified Studio |
|---|---|---|
| Discover features | you know the name | searchable catalog |
| Access control | IAM on the API | project + catalog permissions |
| Lineage | manual | automatic to producing job |
| The store itself | **same Feature Store** | **same Feature Store** |

## Cost & cleanup
Offline store is just S3 (pennies). Online store bills small storage + request
fees — disabled by default here; pass `--online` to demo it, then delete the group
(`fg.delete()` / cleanup script).
