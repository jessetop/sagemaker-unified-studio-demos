# Class prep — what to open tomorrow (and cost safety)

**Account:** `029331796573` · **Region:** `us-east-2` · **Profile:** `roitraining`

## ✅ Overnight cost: nothing is running
Verified clean: **no endpoints, no Studio apps InService, no notebook instances, no
running jobs, EMR app STOPPED.** Nothing bills overnight. Standing cost is just S3
(data + reports + feature-store offline) ≈ **$0.006/mo**. Nothing to turn off
tonight.

> ⚠️ The ONE thing that bills if you leave it on: a **JupyterLab space / Studio app**
> you launch during class. When you're done demoing in an IDE, **stop the space**
> (Studio/Unified Studio → Running instances/Spaces → Stop). Endpoints too — the
> deploy demo auto-deletes its endpoint, but if you create one live, delete it.

## What you'll SEE in each environment

### SageMaker AI / Studio Classic  — already populated (no compute to view)
Open the **SageMaker AI console** (or Studio Classic) and point at:

| Capability | Where | Named resource |
|---|---|---|
| Training | Training → Training jobs | `roi-smdemo-taxi-train-2026-06-22-19-48-43-017` (+ 4 HPO trials) |
| Tuning | Training → Hyperparameter tuning jobs | `roi-smdemo-taxi-hpo-260622-1253` |
| **Experiments** | Experiments | `roi-smdemo-taxi-experiment` (4 runs to compare) |
| **Pipelines** | Pipelines | `roi-smdemo-taxi-pipeline` (Train → Register; not yet run) |
| **Model Registry** | Models → Model registry | `roi-smdemo-taxi-models` v1 (Approved) |
| Model (object) | Inference → Models | `roi-smdemo-taxi-model` |
| Feature Store | Feature Store → Feature groups | `roi-smdemo-taxi-features` |
| Bias/Explain | Processing jobs → (Clarify) | open `s3://roi-smdemo-…/clarify/report.html` |
| Data prep | Data Wrangler / Canvas | import `01-data-prep/old-data-wrangler/taxi.flow` |

> The Experiments / Pipelines / Model Registry panels were populated by
> `shared/populate_studio_classic.py` + `08-pipelines/build_pipeline.py` (metadata
> only — no compute). The pipeline is **defined but not run**; start it live in
> class (`build_pipeline.py --start`) to watch Train→Register execute (cheap).

### SageMaker Unified Studio — data catalogued + build live
Open **your** portal `https://dzd-6jlg4btaz2tp49.sagemaker.us-east-2.on.aws` →
domain **`Default_06222026_Domain`** → project **`azjpw3giqinpux`** (you'll need a
user profile in this domain to log in):

| Capability | Where | What's there |
|---|---|---|
| Data / catalog | Discover / **Query Editor** | `taxi_demo` DB → `trips`, `zones`, `emr` (queryable; project granted read) |
| Visual ETL | Build → **Visual ETL** | build the pipeline live (Glue-backed); job `roi-smdemo-taxi-visual-etl` exists |
| Notebooks | Build → **JupyterLab** | run `02-processing/new-unified-studio/taxi_pipeline_notebook.ipynb` (stop the space after!) |
| **ML — Training/Experiments/Models/Pipelines/AutoML** | project **ML** views | the same artifacts as Classic, **tagged to project `azjpw3giqinpux`** so they surface here |

> **Populated via tags** (`shared/associate_with_unified_studio.py`): the 12 ML
> artifacts (incl. the Autopilot job) carry `AmazonDataZoneProject=azjpw3giqinpux`
> / `Domain=dzd-6jlg4btaz2tp49` / `Environment=cuv9xh4sdcppyh` tags — how Unified
> Studio scopes resources to a project. The demo bucket grants
> `AmazonSageMakerAdminIAMExecutionRole` (this project's role) read access so Query
> Editor can read the data.
>
> ⚠️ **Confidence note:** tagging is the documented association mechanism, but I
> can't see your portal to confirm the ML views render these retroactively. If a
> panel looks empty in the project, the guaranteed fix is to **re-run one demo from
> inside the project** (brief compute), or have Claude **Playwright-verify** the
> exact views. The **data in Query Editor** is the most reliable thing to show.

## Suggested teaching flow (uses `COMPARISON.md`)
For each capability: show it in **Classic** → show the same in **Unified Studio** →
name the difference (governed vs loose · unified vs ML-only · same engine
underneath). The full crosswalk is in [`COMPARISON.md`](COMPARISON.md).

## If something needs a live run
Cheapest re-runs (each ≈ cents, auto-stop): `04-training/launch_training.py`,
`07-deployment/deploy_and_infer.py` (auto-deletes endpoint),
`02-processing/old-emr/emr_serverless_submit.py`.

## Full teardown after class
```powershell
pwsh cleanup/cleanup.ps1 -IncludeBucket -IncludeRole   # wipes everything
# also remove the catalog if you added it:
aws glue delete-crawler  --name roi-smdemo-taxi-crawler --profile roitraining --region us-east-2
aws glue delete-database --name taxi_demo               --profile roitraining --region us-east-2
```
