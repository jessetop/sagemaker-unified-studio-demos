"""
A realistic SageMaker Pipeline for the taxi demo — so the Studio/Unified Studio
**Pipelines** view shows a full ML DAG, not just train->register.

DAG:
  1. PreprocessTaxiData  (Processing)    ingest raw parquet -> clean -> split
  2. DataBiasCheck       (Clarify)       pre-training bias on the facet
  3. TrainTaxiModel      (Training)      custom train.py on the splits
  4. RegisterTaxiModel   (RegisterModel) versioned, approved model

We **upsert** the definition (create/update only — free, no compute). Run it live
for the demo with --start (each step is a short, cheap job). The Clarify data-bias
step uses skip_check=True + register_new_baseline=True so the first run needs no
prior baseline.

Post-training SHAP / model-explainability is demoed standalone in Module 6
(`06-clarify-debugger-groundtruth/`) — adding it as an in-pipeline ModelStep +
ClarifyCheck is possible but finicky (model<->check coupling), so it's kept out of
this clean, reliably-upserting definition.

Usage:
    python build_pipeline.py --bucket roi-smdemo-029331796573-us-east-2 \
        --role-arn arn:aws:iam::029331796573:role/roi-smdemo-exec-role \
        --profile roitraining --region us-east-2 [--start]
"""

import argparse
import sys

import boto3
import sagemaker
from sagemaker.clarify import BiasConfig, DataConfig
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.inputs import TrainingInput
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.workflow.check_job_config import CheckJobConfig
from sagemaker.workflow.clarify_check_step import ClarifyCheckStep, DataBiasCheckConfig
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.pipeline_context import PipelineSession
from sagemaker.workflow.steps import ProcessingStep, TrainingStep
from sagemaker.workflow.step_collections import RegisterModel

PIPELINE_NAME = "roi-smdemo-taxi-pipeline"
MODEL_PACKAGE_GROUP = "roi-smdemo-taxi-models"

# Fixed schema written by preprocess.py (headerless CSVs, label first).
LABEL = "high_tip"
FEATURES = [
    "trip_distance", "trip_duration_min", "trip_speed_mph", "pickup_hour",
    "passenger_count", "fare_amount", "is_airport_trip",
]
HEADERS = [LABEL] + FEATURES
FACET = "is_airport_trip"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--bucket", required=True)
    p.add_argument("--role-arn", required=True)
    p.add_argument("--profile", default="roitraining")
    p.add_argument("--region", default="us-east-2")
    p.add_argument("--start", action="store_true", help="also start one execution")
    args = p.parse_args()

    boto_sess = boto3.Session(profile_name=args.profile, region_name=args.region)
    pipe_sess = PipelineSession(boto_session=boto_sess)
    b = args.bucket
    role = args.role_arn

    # ---- 1) Preprocess (data ingestion + cleanup) -------------------------
    sklearn_processor = SKLearnProcessor(
        framework_version="1.2-1",
        role=role,
        instance_type="ml.m5.2xlarge",
        instance_count=1,
        sagemaker_session=pipe_sess,
        base_job_name="roi-smdemo-preprocess",
    )
    proc_args = sklearn_processor.run(
        code="08-pipelines/preprocess.py",
        inputs=[
            ProcessingInput(
                source=f"s3://{b}/raw/trips/", destination="/opt/ml/processing/input"
            )
        ],
        outputs=[
            ProcessingOutput(output_name="train", source="/opt/ml/processing/output/train",
                             destination=f"s3://{b}/pipeline/train"),
            ProcessingOutput(output_name="validation", source="/opt/ml/processing/output/validation",
                             destination=f"s3://{b}/pipeline/validation"),
            ProcessingOutput(output_name="test", source="/opt/ml/processing/output/test",
                             destination=f"s3://{b}/pipeline/test"),
        ],
    )
    step_process = ProcessingStep(name="PreprocessTaxiData", step_args=proc_args)
    out = step_process.properties.ProcessingOutputConfig.Outputs
    train_uri = out["train"].S3Output.S3Uri
    val_uri = out["validation"].S3Output.S3Uri

    # ---- 2) Data bias (pre-training Clarify) ------------------------------
    check_job_config = CheckJobConfig(
        role=role, instance_count=1, instance_type="ml.m5.large",
        sagemaker_session=pipe_sess,
    )
    data_bias_config = DataBiasCheckConfig(
        data_config=DataConfig(
            s3_data_input_path=train_uri,
            s3_output_path=f"s3://{b}/pipeline/clarify/databias",
            label=LABEL,
            headers=HEADERS,
            dataset_type="text/csv",
        ),
        data_bias_config=BiasConfig(
            label_values_or_threshold=[1], facet_name=FACET
        ),
    )
    step_data_bias = ClarifyCheckStep(
        name="DataBiasCheck",
        clarify_check_config=data_bias_config,
        check_job_config=check_job_config,
        skip_check=True,
        register_new_baseline=True,
    )

    # ---- 3) Train ---------------------------------------------------------
    estimator = SKLearn(
        entry_point="train.py",
        source_dir="04-training",
        role=role,
        instance_type="ml.m5.large",
        instance_count=1,
        framework_version="1.2-1",
        sagemaker_session=pipe_sess,
        hyperparameters={"learning-rate": 0.1, "n-estimators": 150, "max-depth": 3},
        metric_definitions=[
            {"Name": "validation:auc", "Regex": "validation_auc=([0-9\\.]+)"}
        ],
    )
    train_args = estimator.fit({
        "train": TrainingInput(train_uri, content_type="text/csv"),
        "validation": TrainingInput(val_uri, content_type="text/csv"),
    })
    step_train = TrainingStep(name="TrainTaxiModel", step_args=train_args)

    # ---- 4) Register ------------------------------------------------------
    step_register = RegisterModel(
        name="RegisterTaxiModel",
        estimator=estimator,
        model_data=step_train.properties.ModelArtifacts.S3ModelArtifacts,
        content_types=["text/csv"],
        response_types=["text/csv"],
        inference_instances=["ml.m5.large"],
        transform_instances=["ml.m5.large"],
        model_package_group_name=MODEL_PACKAGE_GROUP,
        approval_status="Approved",
    )

    # DataBiasCheck has no data dependency on training, so pin order explicitly.
    step_train.add_depends_on([step_data_bias])

    pipeline = Pipeline(
        name=PIPELINE_NAME,
        steps=[step_process, step_data_bias, step_train, step_register],
        sagemaker_session=pipe_sess,
    )

    pipeline.upsert(role_arn=role)
    print(f"upserted pipeline '{PIPELINE_NAME}' with 4 steps (definition only — no run)")

    if args.start:
        execution = pipeline.start()
        print(f"started execution: {execution.arn}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
