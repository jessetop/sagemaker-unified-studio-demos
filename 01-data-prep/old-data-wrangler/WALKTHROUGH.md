# Demo 1 (old way) — Data Wrangler in SageMaker AI

**~5 minutes.** The classic low-code data-prep experience in **SageMaker Studio
Classic**: import from S3, then click together transforms in a visual flow.

## Learning objectives
- Build the taxi pipeline as a Data Wrangler **flow** with no code.
- Understand how Data Wrangler **samples** data interactively and exports to a
  processing job / notebook for the full run.
- Set up the contrast with the new way ([Visual ETL](../new-visual-etl/WALKTHROUGH.md)).

## Prerequisites / starting state
- Module 0 complete: data in `s3://roi-smdemo-029331796573-us-east-2/raw/`.
- A SageMaker Studio Classic domain with a running app, OR the Data Wrangler entry
  inside SageMaker Canvas.

## The 5-minute script (console)
1. **Studio Classic → File → New → Data Wrangler Flow** (or **Canvas → Data prep**).
2. **Import → Amazon S3** → `raw/trips/yellow_tripdata_2024-01.parquet`. Note the
   banner: Data Wrangler **samples** ~50k rows for interactivity (contrast point —
   it does *not* process all 3M rows live).
3. Open the flow's **+ → Add transform** and demo a *slice* of the 15 steps:
   - **Handle missing → Drop rows** on pickup/dropoff/location (T2).
   - **Custom formula** → `trip_duration_min` (T3); then **Filter** 1–120 (T4).
   - **Featurize datetime** on `pickup_ts` → hour/day (T9).
   - **Join** → import `raw/zones/taxi_zone_lookup.csv` as a second dataset,
     join on `PULocationID = LocationID` (T14). *This is the same join you'll
     show in Visual ETL.*
4. **Data → Quick Model** or **Analysis → Table summary** to show the built-in
   profiling (a Data Wrangler selling point).
5. **Export** → "Save to S3 via processing job" → `processed/data-wrangler/`, or
   "Export to notebook" to reveal the generated SageMaker Processing code.

## The flow scaffold
[`taxi.flow`](taxi.flow) is an importable starting scaffold (S3 import + the first
transforms) you can open and extend live, so the demo starts from a known state
instead of a blank canvas. The full transform list it targets is in
[`PIPELINE_SPEC.md`](../../PIPELINE_SPEC.md).

## Old vs new — talking points
- **Same concepts, different home.** Every node here has a Visual ETL counterpart.
- **Sample vs full.** Data Wrangler is interactive on a sample then exports a job;
  Visual ETL runs serverless Glue on the full dataset directly.
- **Lifecycle.** Data Wrangler is being folded into the unified experience; new
  builds should prefer Unified Studio. Teach Data Wrangler as the thing learners
  may already have, and Visual ETL as where it's going.

## Cost & cleanup
The Studio Classic app/instance is the main cost — **stop the app** when done. The
processing-job export runs on a small instance for a few minutes (cents).
