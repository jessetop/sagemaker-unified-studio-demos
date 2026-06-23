"""
Associate the demo's SageMaker artifacts with the Unified Studio PROJECT so they
appear in the project's ML views (the same Experiments / Pipelines / Models /
Training the Studio Classic panels show).

Unified Studio decides what belongs to a project by **resource tags**. We read the
project's tag values from its backing SageMaker domain and stamp the same tags onto
our training jobs, experiment, pipeline, model package group, model, and feature
group. Pure tagging — no compute.

Project (default): admin-project of domain-06-22-2026.

Usage:
    python associate_with_unified_studio.py --profile roitraining --region us-east-2
"""

import argparse
import sys

import boto3

# Project association tags — YOUR project: admin-project of Default_06222026_Domain
# (read from backing SageMaker domain d-yhfnr1notr3m).
DZ_TAGS = [
    {"Key": "AmazonDataZoneProject", "Value": "azjpw3giqinpux"},
    {"Key": "AmazonDataZoneDomain", "Value": "dzd-6jlg4btaz2tp49"},
    {"Key": "AmazonDataZoneEnvironment", "Value": "cuv9xh4sdcppyh"},
]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", default="roitraining")
    p.add_argument("--region", default="us-east-2")
    args = p.parse_args()

    sess = boto3.Session(profile_name=args.profile, region_name=args.region)
    sm = sess.client("sagemaker")
    acct = sess.client("sts").get_caller_identity()["Account"]
    base = f"arn:aws:sagemaker:{args.region}:{acct}"

    arns = []

    # Training jobs (baseline + HPO trials).
    for pref in ("roi-smdemo-taxi-train", "roi-smdemo-taxi-hpo"):
        for j in sm.list_training_jobs(NameContains=pref, MaxResults=10)[
            "TrainingJobSummaries"
        ]:
            arns.append(f"{base}:training-job/{j['TrainingJobName']}")

    # HPO tuning job, experiment, pipeline, model package group, model, feature group.
    arns += [
        f"{base}:hyper-parameter-tuning-job/roi-smdemo-taxi-hpo-260622-1253",
        f"{base}:experiment/roi-smdemo-taxi-experiment",
        f"{base}:pipeline/roi-smdemo-taxi-pipeline",
        f"{base}:model-package-group/roi-smdemo-taxi-models",
        f"{base}:model/roi-smdemo-taxi-model",
        f"{base}:feature-group/roi-smdemo-taxi-features",
        f"{base}:automl-job/roi-smdemo-autopilot",
    ]

    ok, failed = 0, 0
    for arn in arns:
        try:
            sm.add_tags(ResourceArn=arn, Tags=DZ_TAGS)
            print(f"  tagged {arn.split(':')[-1]}")
            ok += 1
        except Exception as exc:  # resource may not exist; keep going
            print(f"  SKIP {arn.split(':')[-1]}: {str(exc)[:80]}")
            failed += 1

    project = next(t["Value"] for t in DZ_TAGS if t["Key"] == "AmazonDataZoneProject")
    print(f"\ntagged {ok} resources to project {project} ({failed} skipped)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
