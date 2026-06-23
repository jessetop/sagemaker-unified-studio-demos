# The One Pipeline — Canonical Transformation Spec

Every demo in this series implements **the same pipeline** on **the same dataset**.
Only the *tool* changes. When you teach, you point at one slice ("the join", "the
outlier filter") and show how each environment expresses it. This file is the
contract all four implementations agree on.

## Dataset (open data, free)

| Item | Source | Size | Notes |
|---|---|---|---|
| NYC Yellow Taxi trips, 2024-01 | NYC TLC (CloudFront) | ~48 MB Parquet, **2,964,624 rows** | Big enough to make the "scale" story real; Data Wrangler auto-samples it |
| Taxi zone lookup | NYC TLC (CloudFront) | 12 KB CSV, 265 rows | The dimension table for the JOIN step |

Staged to `s3://roi-smdemo-029331796573-us-east-2/raw/` by `00-setup/stage_dataset.py`.

Raw trip schema (verified): `VendorID, tpep_pickup_datetime, tpep_dropoff_datetime,
passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID,
DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount,
improvement_surcharge, total_amount, congestion_surcharge, Airport_fee`.

## The transformations (15 steps + 1 optional ML label)

The single source of truth is [`shared/taxi_transforms.py`](shared/taxi_transforms.py)
(`build_pipeline()`), used unchanged by Visual ETL, EMR, and the Unified Studio
notebook. Data Wrangler reproduces the same steps as low-code GUI nodes.

| # | Step | Type | Data Wrangler node | Visual ETL node |
|---|---|---|---|---|
| T1 | Rename raw columns to snake_case | Schema | Manage columns → Rename | Change Schema |
| T2 | Drop rows missing pickup/dropoff/location | Cleaning | Handle missing → Drop rows | Drop Null Fields / Filter |
| T3 | Derive `trip_duration_min` from timestamps | Feature eng | Custom formula | Derived column |
| T4 | Filter duration to 1–120 min | Filter | Filter rows | Filter |
| T5 | Filter distance to 0–100 mi | Filter | Filter rows | Filter |
| T6 | Keep positive fare & total (revenue trips) | Filter | Filter rows | Filter |
| T7 | Derive `trip_speed_mph` | Feature eng | Custom formula | Derived column |
| T8 | Filter implausible speed (0–80 mph) | Filter | Filter rows | Filter |
| T9 | Extract `pickup_hour`, `pickup_dow`, `pickup_date` | Feature eng | Featurize datetime | Derived columns |
| T10 | Map `payment_type` code → label | Encode | Map values / categorical | Custom transform / Map |
| T11 | Derive `tip_pct` | Feature eng | Custom formula | Derived column |
| T12 | Bucket `trip_distance` (short/med/long/very_long) | Bin | Bin numeric | Conditional column |
| T13 | Flag `is_airport_trip` | Feature eng | Custom formula | Derived column |
| T14 | **Join** zone lookup twice (pickup + dropoff) | Join | Join datasets | Join |
| T15 | Final projection / column order | Schema | Manage columns | Change Schema |
| T16* | *(ML modules only)* add `high_tip` label | Label | — | — |

\* T16 (`add_ml_label`) turns the cleaned data into a supervised classification
target (`high_tip = tip_pct > 20`) reused by Feature Store, Training, Tuning, and
Deployment.

## Outputs

| Demo | Output prefix |
|---|---|
| Visual ETL (Glue) | `s3://.../processed/visual-etl/` (Parquet, partitioned by `pickup_date`) |
| EMR Serverless | `s3://.../processed/emr/` |
| Unified Studio notebook | `s3://.../processed/notebook/` |
| Data Wrangler | `s3://.../processed/data-wrangler/` |

Because every tool runs the same logic, the **outputs are identical** — a nice
thing to show learners: the result doesn't depend on the tool, only the
experience of building it does.
