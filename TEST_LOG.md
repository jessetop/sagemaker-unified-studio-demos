# Live Test Log — what was actually run against the account

Account `029331796573`, region `us-east-2`, profile `roitraining`. All resources
tagged `Project=sagemaker-unified-studio-demos`.

| Module | What was tested | Result |
|---|---|---|
| 0 Setup | Stage NYC taxi (parquet + zones) to S3 | ✅ `raw/` populated, 2,964,624 rows verified |
| 1 Visual ETL (new) | Created + ran Glue 4.0 job from the canvas-equivalent script | ✅ SUCCEEDED, wrote `processed/visual-etl/` |
| 2 EMR (old) | Created EMR Serverless app, submitted Spark job | ✅ SUCCESS after `TIMESTAMP_NTZ` fix, wrote `processed/emr/` |
| 1↔2 cross-check | Compared Glue vs EMR outputs | ✅ **identical: 2,858,161 rows, 20 cols** |
| ML data prep | `prepare_ml_data.py` → train/val/test CSVs | ✅ 150k sampled, 18 features, 76% positive |
| 4 Training (logic) | Ran `train.py` locally on real splits (free) | ✅ acc=0.766, auc=0.608, model.joblib saved |
| 4 Training (cloud) | SageMaker `SKLearn` job, `ml.m5.large` | ✅ acc=0.7664, auc=0.6078, **155 billable sec** |
| 3 Feature Store | Create group + ingest 2k records | ✅ group `roi-smdemo-taxi-features`, offline store on S3 |
| 5 Tuning | 4-job Bayesian HPO, `max_parallel=2` | ✅ best lr=0.055/depth=5, **auc=0.6073** |
| 7 Deployment | Serverless endpoint → 3 inferences → delete | ✅ P(high_tip)=0.68/0.70/0.92, endpoint deleted |
| 6 Clarify | bias + SHAP processing jobs (300-row sample) | ✅ both Completed; `report.html` + `explanations_shap/out.csv` |

### Bugs found & fixed while testing (good teaching material)
1. **TIMESTAMP_NTZ** cast — EMR Spark 3.5 vs Glue 3.3 (fixed: `unix_timestamp()`).
2. **get_dummies → bool** — Feature Store rejects bool dtype + breaks CSV inference
   (fixed: cast one-hot cols to int in `prepare_ml_data.py`).
3. **Feature name regex** — `pickup_borough_N/A`/`Staten Island` had `/` and space
   (fixed: sanitize names in `feature_store_ingest.py`).
4. **Offline store ACL** — role needed `s3:GetBucketAcl`/`PutObjectAcl` (added).
5. **Inference 1D array** — container parses a CSV row to 1D; `predict_proba`
   needs 2D (fixed: reshape in `predict_fn`).
6. **Clarify output `//`** — trailing slash produced an illegal `clarify//` key
   (fixed: drop trailing slash).
7. **Clarify SHAP cost** — running on the full 22.5k-row test set × 100 samples is
   millions of inferences via a shadow endpoint (slow/costly). Fixed: `--analysis-rows`
   default 300. Lesson: SHAP cost scales with rows × samples; sample for demos.

## Notes / honest caveats
- **AUC ≈ 0.61**: tip% is genuinely weakly predictable from trip features; the
  point is the *workflow*, not model quality. Good teaching honesty.
- **TIMESTAMP_NTZ**: identical PySpark failed on EMR Spark 3.5 but passed on Glue
  Spark 3.3 — fixed with `unix_timestamp()`. Captured as a teaching moment.
- **Local SDK install**: the `sagemaker` SDK hits a Windows MAX_PATH error in the
  store-Python; install it in a short-path venv (`C:\smv`) instead. Not relevant
  to the demos themselves (they run in SageMaker), only to local driving.
