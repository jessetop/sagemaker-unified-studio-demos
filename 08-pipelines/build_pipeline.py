"""
Author a SageMaker Pipeline so the Studio Classic **Pipelines** panel is populated.

The pipeline chains the demo's own steps: Train the taxi classifier → Register the
resulting model into the model package group. We **upsert** it (create/update the
definition) but do NOT start an execution — so it shows up as a pipeline you can
open and inspect with **zero compute**. Start it live in class if you want to watch
it run (cheap: one ml.m5.large training step).

Usage:
    python build_pipeline.py --bucket roi-smdemo-029331796573-us-east-2 \
        --role-arn arn:aws:iam::029331796573:role/roi-smdemo-exec-role \
        --profile roitraining --region us-east-2 [--start]
"""

import argparse
import sys

import boto3
import sagemaker
from sagemaker.inputs import TrainingInput
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.pipeline_context import PipelineSession
from sagemaker.workflow.step_collections import RegisterModel
from sagemaker.workflow.steps import TrainingStep

PIPELINE_NAME = "roi-smdemo-taxi-pipeline"
MODEL_PACKAGE_GROUP = "roi-smdemo-taxi-models"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--bucket", required=True)
    p.add_argument("--role-arn", required=True)
    p.add_argument("--profile", default="roitraining")
    p.add_argument("--region", default="us-east-2")
    p.add_argument("--start", action="store_true", help="also start one execution")
    args = p.parse_args()

    boto_sess = boto3.Session(profile_name=args.profile, region_name=args.region)
    # PipelineSession makes estimator calls build pipeline steps instead of running.
    pipe_sess = PipelineSession(boto_session=boto_sess)
    b = args.bucket

    estimator = SKLearn(
        entry_point="train.py",
        source_dir="04-training",
        role=args.role_arn,
        instance_type="ml.m5.large",
        instance_count=1,
        framework_version="1.2-1",
        sagemaker_session=pipe_sess,
        hyperparameters={"learning-rate": 0.1, "n-estimators": 150, "max-depth": 3},
        metric_definitions=[
            {"Name": "validation:auc", "Regex": "validation_auc=([0-9\\.]+)"}
        ],
    )

    step_train = TrainingStep(
        name="TrainTaxiModel",
        step_args=estimator.fit(
            {
                "train": TrainingInput(
                    f"s3://{b}/ml/taxi/train/", content_type="text/csv"
                ),
                "validation": TrainingInput(
                    f"s3://{b}/ml/taxi/validation/", content_type="text/csv"
                ),
            }
        ),
    )

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

    pipeline = Pipeline(
        name=PIPELINE_NAME,
        steps=[step_train, step_register],
        sagemaker_session=pipe_sess,
    )

    # Upsert = create/update the definition only. No execution, no compute.
    pipeline.upsert(role_arn=args.role_arn)
    print(f"upserted pipeline '{PIPELINE_NAME}' (definition only — no run)")

    if args.start:
        execution = pipeline.start()
        print(f"started execution: {execution.arn}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
