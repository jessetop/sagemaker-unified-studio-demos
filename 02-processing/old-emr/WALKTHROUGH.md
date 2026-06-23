# Demo 2 (old way) — EMR Spark (EMR Serverless)

**~5 minutes.** Scale the taxi pipeline with raw Spark on managed EMR — the
data-engineering path that predates the studio experience.

## Learning objectives
- Run the full ~3M-row pipeline on serverless Spark (no sampling, no cluster mgmt).
- See the **plumbing you own** in the old way: application, role, submit call,
  `--py-files` shipping, and an S3 log destination.
- Set up the contrast with the new way ([Unified Studio notebook](../new-unified-studio/WALKTHROUGH.md)),
  which runs the same Spark from a managed notebook.

## Prerequisites / starting state
- Module 0 complete (data in `raw/`); shared exec role exists.
- Code shipped to `s3://roi-smdemo-029331796573-us-east-2/code/`.
- Cross-reference: same logic as Demo 1; this just runs it at full scale.

## The 5-minute script
One command does the whole lifecycle (create app → submit → poll → done):

```bash
python emr_serverless_submit.py \
  --bucket roi-smdemo-029331796573-us-east-2 \
  --role-arn arn:aws:iam::029331796573:role/roi-smdemo-exec-role \
  --profile roitraining --region us-east-2
```

Talk through what it does while it runs:
1. **create_application** — a SPARK app on `emr-7.1.0` with 5-min auto-stop.
2. **start_job_run** — `entryPoint` = [`emr_taxi_job.py`](emr_taxi_job.py),
   `--py-files` ships [`taxi_transforms.py`](../../shared/taxi_transforms.py).
3. Poll `get_job_run` until `SUCCESS`; output lands in `processed/emr/`.

## Teaching note — a real cross-engine gotcha
This job initially **failed** on EMR's Spark 3.5 with
`Cannot cast TIMESTAMP_NTZ to BIGINT`, even though the identical code **succeeded**
on Glue's Spark 3.3. Newer Spark reads the Parquet timestamps as `TIMESTAMP_NTZ`
and forbids a direct cast-to-long. The fix (use `unix_timestamp()` — see T3 in
the shared module) works on both engines. Great live lesson: **managed ≠ identical;
runtime versions matter**, and the new unified experience pins them for you.

## Old vs new — talking points
| | EMR Spark (old) | Unified Studio notebook (new) |
|---|---|---|
| Setup | you create app, role, submit | project provides compute |
| Code shipping | `--py-files` to S3 | files live in the project |
| Iteration | submit → wait → read S3 logs | interactive cells |
| Governance | none built-in | project catalog, lineage, Git |

## Cost & cleanup
EMR Serverless bills only for vCPU/memory-seconds used (this run ≈ cents) and
auto-stops after 5 min idle. The application is deleted by the series cleanup
script.
