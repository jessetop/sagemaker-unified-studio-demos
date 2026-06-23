# Demo 1 (new way) — Visual ETL in Unified Studio

**~5 minutes.** The modern replacement for Data Wrangler: a drag-and-drop ETL
canvas inside SageMaker Unified Studio, backed by serverless **AWS Glue** Spark.

## Learning objectives
- Build the taxi pipeline visually on the Unified Studio ETL canvas.
- See that the canvas **generates a Glue Spark job** — low-code, but real Spark.
- Contrast with Data Wrangler: same transforms, but project-integrated, Git-backed,
  and scales to the full dataset (not a sample).

## Prerequisites / starting state
- Module 0 complete: data in `s3://roi-smdemo-029331796573-us-east-2/raw/`.
- A Unified Studio project (domain `domain-06-22-2026-112138`).
- Cross-reference: this reproduces the same steps as
  [Demo 1 old way — Data Wrangler](../old-data-wrangler/WALKTHROUGH.md).

## The 5-minute script (console)
1. **Open Unified Studio** → your project → **Build → Visual ETL** → new flow.
2. **Source 1**: Amazon S3 → `raw/trips/` (Parquet). Click **Infer schema**;
   point out the 19 raw columns.
3. **Source 2**: Amazon S3 → `raw/zones/taxi_zone_lookup.csv` (CSV, header).
4. Add transform nodes — demo a *slice*, not all 15:
   - **Filter** → `trip_duration_min between 1 and 120` (T4).
   - **Join** → trips `PULocationID` = zones `LocationID`, left join (T14). This
     is the headline step: "the same join you did in Data Wrangler, here as a node."
   - **Derived column** → `tip_pct` (T11).
5. **Target**: S3 `processed/visual-etl/`, Parquet.
6. Click **Script** (top-right) to reveal the **generated Glue code** — this is
   the punchline: *visual on top, Spark underneath*. Then **Run**.

## What's actually running (and how this was tested)
The canvas produces a Glue job equivalent to
[`glue_visual_etl_job.py`](glue_visual_etl_job.py), which calls the shared
[`taxi_transforms.build_pipeline`](../../shared/taxi_transforms.py). For repeatable
classroom setup (and to test without clicking), create + run it from the CLI:

```bash
# create the job (once)
aws glue create-job --name roi-smdemo-taxi-visual-etl \
  --role arn:aws:iam::029331796573:role/roi-smdemo-exec-role \
  --glue-version 4.0 --number-of-workers 2 --worker-type G.1X \
  --command Name=glueetl,ScriptLocation=s3://roi-smdemo-029331796573-us-east-2/code/glue_visual_etl_job.py,PythonVersion=3 \
  --default-arguments '{"--extra-py-files":"s3://roi-smdemo-029331796573-us-east-2/code/taxi_transforms.py",
    "--trips_path":"s3://roi-smdemo-029331796573-us-east-2/raw/trips/",
    "--zones_path":"s3://roi-smdemo-029331796573-us-east-2/raw/zones/taxi_zone_lookup.csv",
    "--output_path":"s3://roi-smdemo-029331796573-us-east-2/processed/visual-etl/"}' \
  --profile roitraining --region us-east-2

# run it
aws glue start-job-run --job-name roi-smdemo-taxi-visual-etl --profile roitraining --region us-east-2
```

## Old vs new — talking points
| | Data Wrangler (old) | Visual ETL (new) |
|---|---|---|
| Lives in | SageMaker Studio Classic | Unified Studio project (governed) |
| Engine | Studio instance (samples data) | Serverless Glue Spark (full data) |
| Output | export step / notebook | Glue job, scheduled & versioned |
| Sharing | `.flow` file | project asset + Git |

## Cost & cleanup
2×G.1X for a couple of minutes ≈ a few cents. The job auto-stops. Delete with the
series [`cleanup`](../../cleanup/) script.
