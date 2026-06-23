# Demo 2 (new way) — Unified Studio notebook (Spark)

**~5 minutes.** Run the same full-scale Spark pipeline from a managed Unified
Studio project notebook — none of the EMR plumbing.

## Learning objectives
- Attach a notebook to project Spark compute (Glue interactive session / EMR
  Serverless) and run the pipeline interactively.
- See that **the same shared code** the EMR job ran also runs here (via `addPyFile`).
- Appreciate the governance/iteration win over hand-submitted EMR jobs.

## Prerequisites / starting state
- Module 0 complete; shared module at `s3://.../code/taxi_transforms.py`.
- A Unified Studio project (domain `domain-06-22-2026-112138`) with a Spark
  connection available.
- Cross-reference: same logic as [Demo 2 old way — EMR](../old-emr/WALKTHROUGH.md).

## The 5-minute script (console)
1. **Unified Studio → project → Build → JupyterLab.** Open
   [`taxi_pipeline_notebook.ipynb`](taxi_pipeline_notebook.ipynb) (upload it into
   the project, or recreate the cells live).
2. Pick a **Spark connection** in the kernel picker (Glue / EMR Serverless).
3. Run cells top to bottom:
   - Config paths → `addPyFile` + import (the "same code" reveal) → `build_pipeline`
     → `df.show()`.
   - The **avg tip % by borough** aggregation — the interactive payoff.
   - Write to `processed/notebook/`.
4. Point at the project's **Data / lineage** panel to show the run is governed and
   discoverable — something the raw EMR submit never gives you.

## Old vs new — talking points
- **Same Spark, less ceremony.** No `create_application`, no `start_job_run`, no
  `--py-files`, no S3 log spelunking.
- **Governed by default.** The project supplies the role, the catalog, lineage,
  and Git — versus the DIY EMR submit where you wire all that yourself.
- **One code path.** `addPyFile` imports the exact module the EMR job used, so you
  can literally show "same function, two front doors."

## Cost & cleanup
Project Spark compute is serverless and idles down. Stop the notebook's session
when done; the project itself has no standing cost beyond what you run.
