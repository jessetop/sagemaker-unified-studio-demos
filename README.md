# SageMaker AI → Unified Studio: "Old Way / New Way" Demo Series

A set of short (~5-minute) classroom demos that show the **same work done the old
way (standalone SageMaker AI: Data Wrangler, EMR, the SDK, individual consoles)
and the new way (SageMaker Unified Studio)**. One dataset, one pipeline, many
tools — so learners see that the *concepts* carry over and only the *experience*
changes.

> **Teaching model:** you build the full pipeline once in each environment, then
> demo *slices* of it as you teach a concept ("here's the join in Data Wrangler…
> here's the same join in Visual ETL…"). See [`PIPELINE_SPEC.md`](PIPELINE_SPEC.md)
> for the one canonical pipeline every demo implements.

> **👉 Start here for the side-by-side:** [`COMPARISON.md`](COMPARISON.md) is the
> Studio Classic ↔ Unified Studio crosswalk — "here's where this lives in Classic,
> here's where it lives in Unified Studio" for every capability.

## The comparison at a glance

| # | Capability | Old way — **SageMaker AI** | New way — **Unified Studio** | Live-tested |
|---|---|---|---|---|
| 0 | Setup + dataset | — shared NYC-taxi staging to S3 — | ✅ |
| 1 | Interactive data prep | **Data Wrangler** (`.flow`, low-code) | **Visual ETL** (Glue canvas) | ✅ Glue run |
| 2 | Scalable processing | **EMR Spark** (EMR Serverless) | **Unified Studio notebook** (same PySpark) | ✅ EMR run |
| 3 | Feature management | **Feature Store** via SDK | US Feature catalog / SDK in-project | ✅ group + ingest |
| 4 | Training | **Estimator** SDK training job | US project training (same job API) | ✅ job (155s) |
| 5 | Experiments + tuning | **Experiments** + **HPO** tuner | US / MLflow tracking | ✅ 4-job HPO |
| 6 | Labeling / bias / debug | **Ground Truth**, **Clarify**, **Debugger** | US equivalents | ✅ Clarify · ◻ GT (needs workforce) |
| 7 | Deployment | real-time **endpoint** SDK | US deploy | ✅ serverless + infer |

All modules are built; modules 0–5 and 7 plus Clarify are **live-tested** against
the account (see [`TEST_LOG.md`](TEST_LOG.md)). Ground Truth is conceptual (needs a
human workforce); the new-way (Unified Studio) console steps are documented in each
module's `WALKTHROUGH.md`.

## Dataset & cost

- **Dataset:** NYC Yellow Taxi (one month, ~2.96M rows) + taxi zone lookup —
  free, open, no credentials. See [`PIPELINE_SPEC.md`](PIPELINE_SPEC.md).
- **Cost posture:** everything uses the cheapest managed compute (Glue 2×G.1X,
  EMR Serverless, small SageMaker instances) and runs in minutes. Each live run
  costs **cents**. Tear everything down with [`cleanup/cleanup.ps1`](cleanup/cleanup.ps1).

## Account / environment

| Setting | Value |
|---|---|
| AWS profile | `roitraining` |
| Account | `029331796573` |
| Region | `us-east-2` |
| Demo bucket | `s3://roi-smdemo-029331796573-us-east-2` |
| Shared exec role | `arn:aws:iam::029331796573:role/roi-smdemo-exec-role` |
| Unified Studio domain | `domain-06-22-2026-112138` (`dzd-3hqzek2hjq1y3t`) |

All created resources are tagged `Project=sagemaker-unified-studio-demos` for easy
discovery and cleanup.

## Layout

```
sagemaker_demos/
├── README.md                  ← you are here
├── PIPELINE_SPEC.md           ← the one canonical pipeline (the contract)
├── shared/
│   ├── taxi_transforms.py     ← the pipeline logic, reused by every tool
│   └── iam/                   ← trust + permission policies for the exec role
├── 00-setup/                  ← stage the dataset to S3
├── 01-data-prep/
│   ├── old-data-wrangler/     ← Data Wrangler .flow + walkthrough
│   └── new-visual-etl/        ← Glue Visual ETL job + walkthrough  (TESTED)
├── 02-processing/
│   ├── old-emr/               ← EMR Serverless submit + walkthrough (TESTED)
│   └── new-unified-studio/    ← in-project notebook + walkthrough
├── 03-feature-store/ … 07-deployment/   ← ML modules (scaffold)
└── cleanup/                   ← tear-down scripts
```

## How to run a demo

Each module folder has a `WALKTHROUGH.md` with the ~5-minute script: what to click
/ run, what to point at, and the old-vs-new talking points. Start with
[`00-setup`](00-setup/) then [`01-data-prep`](01-data-prep/).
