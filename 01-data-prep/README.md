# Module 1 — Interactive data prep: Data Wrangler vs Visual ETL

The same taxi cleaning/enrichment pipeline built two ways.

| | Folder | Status |
|---|---|---|
| **Old way** — Data Wrangler (SageMaker AI / Studio Classic) | [`old-data-wrangler/`](old-data-wrangler/) | flow scaffold + walkthrough |
| **New way** — Visual ETL (Unified Studio, Glue-backed) | [`new-visual-etl/`](new-visual-etl/) | **Glue job tested ✅** (2,858,161 rows out) |

Both implement [`PIPELINE_SPEC.md`](../PIPELINE_SPEC.md). The headline live-demo
moment is the **zone join (T14)** — show it as a Data Wrangler Join node, then as
a Visual ETL Join node, then reveal the generated Spark.

**Teaching arc:** Data Wrangler = what learners may already know (interactive on a
*sample*, export to a job). Visual ETL = where it's going (serverless Glue on the
*full* dataset, governed inside a project). Same concepts, better home.
