# Module 2 — Scalable processing: EMR Spark vs Unified Studio notebook

The same pipeline at full scale (~2.96M rows), run as raw Spark two ways.

| | Folder | Status |
|---|---|---|
| **Old way** — EMR Spark (EMR Serverless) | [`old-emr/`](old-emr/) | **job tested ✅** (2,858,161 rows out) |
| **New way** — Unified Studio notebook | [`new-unified-studio/`](new-unified-studio/) | notebook + walkthrough |

Both call the same [`shared/taxi_transforms.py`](../shared/taxi_transforms.py).

**Verified cross-engine:** identical output (2,858,161 rows, 20 cols) from Glue
Spark 3.3 *and* EMR Spark 3.5 — after fixing a real `TIMESTAMP_NTZ` portability
bug (see [`old-emr/WALKTHROUGH.md`](old-emr/WALKTHROUGH.md)). That gotcha is itself
a teaching moment: managed runtimes differ; the unified experience pins them.

**Teaching arc:** EMR = you own the app/submit/log plumbing. Unified Studio
notebook = same engine and code, run interactively from a governed project.
