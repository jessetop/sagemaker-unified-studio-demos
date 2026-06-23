# Module 0 — Setup & shared dataset

The one-time setup every other module depends on. Stages the open NYC-taxi dataset
to S3 and (already done for this account) the demo bucket + shared exec role.

## What exists after setup

| Resource | Value |
|---|---|
| Demo bucket | `s3://roi-smdemo-029331796573-us-east-2` |
| Raw trips | `raw/trips/yellow_tripdata_2024-01.parquet` (~2.96M rows) |
| Raw zones | `raw/zones/taxi_zone_lookup.csv` |
| Shared code | `code/taxi_transforms.py`, `code/glue_visual_etl_job.py`, `code/emr_taxi_job.py` |
| Exec role | `arn:aws:iam::029331796573:role/roi-smdemo-exec-role` (Glue+EMR+SageMaker) |

## Re-run the dataset staging

```bash
python stage_dataset.py \
  --bucket roi-smdemo-029331796573-us-east-2 \
  --profile roitraining --region us-east-2
```

Downloads from the public NYC TLC distribution (no credentials), with retries on
download failure and explicit errors on upload failure. See
[`stage_dataset.py`](stage_dataset.py).

## Upload the shared code (if recreating from scratch)

```bash
B=roi-smdemo-029331796573-us-east-2
aws s3 cp ../shared/taxi_transforms.py s3://$B/code/taxi_transforms.py --profile roitraining
aws s3 cp ../01-data-prep/new-visual-etl/glue_visual_etl_job.py s3://$B/code/ --profile roitraining
aws s3 cp ../02-processing/old-emr/emr_taxi_job.py s3://$B/code/ --profile roitraining
```

## Cost
A few cents of S3 storage. Nothing here runs compute.
