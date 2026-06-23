"""
Module 5 — hyperparameter tuning (Kiro Req 6), the old way.

Launches a small, cost-capped SageMaker Automatic Model Tuning job over the same
custom train.py: Bayesian search across learning rate and depth, optimizing
validation AUC. The NEW way runs the identical tuner from a Unified Studio project
and tracks trials in managed MLflow (see WALKTHROUGH.md).

Cost control (Kiro Req 6.4): max_jobs=4, max_parallel_jobs=2, cheapest instance.

Usage:
    python launch_tuning.py --bucket roi-smdemo-029331796573-us-east-2 \
        --role-arn arn:aws:iam::029331796573:role/roi-smdemo-exec-role \
        --profile roitraining --region us-east-2
"""

import argparse
import sys

import boto3
import sagemaker
from sagemaker.inputs import TrainingInput
from sagemaker.parameter import ContinuousParameter, IntegerParameter
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.tuner import HyperparameterTuner


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--bucket", required=True)
    p.add_argument("--role-arn", required=True)
    p.add_argument("--profile", default="roitraining")
    p.add_argument("--region", default="us-east-2")
    p.add_argument("--instance-type", default="ml.m5.large")
    p.add_argument("--prefix", default="ml/taxi")
    args = p.parse_args()

    boto_sess = boto3.Session(profile_name=args.profile, region_name=args.region)
    sm_sess = sagemaker.Session(boto_session=boto_sess)
    b = args.bucket

    estimator = SKLearn(
        entry_point="train.py",
        source_dir="04-training",
        role=args.role_arn,
        instance_type=args.instance_type,
        instance_count=1,
        framework_version="1.2-1",
        sagemaker_session=sm_sess,
        base_job_name="roi-smdemo-taxi-hpo",
        hyperparameters={"n-estimators": 150},  # fixed; tune the two below
        metric_definitions=[
            {"Name": "validation:auc", "Regex": "validation_auc=([0-9\\.]+)"}
        ],
    )

    # Search space: at least two parameters (Kiro Req 6.1).
    ranges = {
        "learning-rate": ContinuousParameter(0.01, 0.3),
        "max-depth": IntegerParameter(2, 6),
    }

    tuner = HyperparameterTuner(
        estimator=estimator,
        objective_metric_name="validation:auc",
        objective_type="Maximize",  # Kiro Req 6.2
        metric_definitions=[
            {"Name": "validation:auc", "Regex": "validation_auc=([0-9\\.]+)"}
        ],
        hyperparameter_ranges=ranges,
        max_jobs=4,
        max_parallel_jobs=2,
        strategy="Bayesian",
        base_tuning_job_name="roi-smdemo-taxi-hpo",
        tags=[{"Key": "Project", "Value": "sagemaker-unified-studio-demos"}],
    )

    train_in = TrainingInput(f"s3://{b}/{args.prefix}/train/", content_type="text/csv")
    val_in = TrainingInput(
        f"s3://{b}/{args.prefix}/validation/", content_type="text/csv"
    )
    tuner.fit({"train": train_in, "validation": val_in})
    tuner.wait()

    # Report the winner (Kiro Req 6.3).
    best = tuner.best_training_job()
    desc = boto_sess.client("sagemaker").describe_training_job(TrainingJobName=best)
    print("best training job:", best)
    print("best hyperparameters:", desc["HyperParameters"])
    print(
        "best objective:",
        desc.get("FinalMetricDataList"),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
