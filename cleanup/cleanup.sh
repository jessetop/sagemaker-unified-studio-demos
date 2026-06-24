#!/usr/bin/env bash
# Tear down resources created by the SageMaker Unified Studio demo series.
# Safe to re-run. Only touches resources named/tagged for this demo.
#
#   ./cleanup.sh                  # delete jobs/apps/endpoints, keep bucket+role
#   ./cleanup.sh --include-bucket # also empty + delete the S3 bucket
#   ./cleanup.sh --include-role   # also delete the shared IAM role
set -u
PROFILE="${PROFILE:-roitraining}"
REGION="${REGION:-us-east-2}"
BUCKET="roi-smdemo-029331796573-us-east-2"
ROLE="roi-smdemo-exec-role"
INCLUDE_BUCKET=false; INCLUDE_ROLE=false
for a in "$@"; do
  [ "$a" = "--include-bucket" ] && INCLUDE_BUCKET=true
  [ "$a" = "--include-role" ] && INCLUDE_ROLE=true
done

echo "== Deleting Glue job, crawler, and demo database =="
aws glue delete-job --job-name roi-smdemo-taxi-visual-etl --profile "$PROFILE" --region "$REGION" 2>/dev/null
aws glue delete-crawler --name roi-smdemo-taxi-crawler --profile "$PROFILE" --region "$REGION" 2>/dev/null
aws glue delete-database --name taxi_demo --profile "$PROFILE" --region "$REGION" 2>/dev/null

echo "== Deleting Feature Store group =="
aws sagemaker delete-feature-group --feature-group-name roi-smdemo-taxi-features --profile "$PROFILE" --region "$REGION" 2>/dev/null

echo "== Deleting Pipeline, Model Registry, Experiment =="
aws sagemaker delete-pipeline --pipeline-name roi-smdemo-taxi-pipeline --profile "$PROFILE" --region "$REGION" 2>/dev/null
for pkg in $(aws sagemaker list-model-packages --model-package-group-name roi-smdemo-taxi-models --profile "$PROFILE" --region "$REGION" --query "ModelPackageSummaryList[].ModelPackageArn" --output text 2>/dev/null); do
  aws sagemaker delete-model-package --model-package-name "$pkg" --profile "$PROFILE" --region "$REGION" 2>/dev/null
done
aws sagemaker delete-model-package-group --model-package-group-name roi-smdemo-taxi-models --profile "$PROFILE" --region "$REGION" 2>/dev/null
aws sagemaker delete-model --model-name roi-smdemo-taxi-model --profile "$PROFILE" --region "$REGION" 2>/dev/null
aws sagemaker delete-experiment --experiment-name roi-smdemo-taxi-experiment --profile "$PROFILE" --region "$REGION" 2>/dev/null

echo "== Deleting MLflow tracking server + its teardown schedule =="
aws sagemaker delete-mlflow-tracking-server --tracking-server-name roi-smdemo-mlflow --profile "$PROFILE" --region "$REGION" 2>/dev/null
aws scheduler delete-schedule --name roi-smdemo-mlflow-teardown --profile "$PROFILE" --region "$REGION" 2>/dev/null

echo "== Stopping + deleting EMR Serverless applications =="
for a in $(aws emr-serverless list-applications --profile "$PROFILE" --region "$REGION" \
            --query "applications[?name=='roi-smdemo-taxi-emr'].id" --output text); do
  aws emr-serverless stop-application --application-id "$a" --profile "$PROFILE" --region "$REGION" 2>/dev/null
  aws emr-serverless delete-application --application-id "$a" --profile "$PROFILE" --region "$REGION" 2>/dev/null
  echo "  deleted app $a"
done

echo "== Deleting SageMaker endpoints (modules 3-7) =="
for e in $(aws sagemaker list-endpoints --profile "$PROFILE" --region "$REGION" \
            --query "Endpoints[?starts_with(EndpointName,'roi-smdemo')].EndpointName" --output text); do
  aws sagemaker delete-endpoint --endpoint-name "$e" --profile "$PROFILE" --region "$REGION" 2>/dev/null
  echo "  deleted endpoint $e"
done

if $INCLUDE_BUCKET; then
  echo "== Emptying + deleting bucket $BUCKET =="
  aws s3 rm "s3://$BUCKET" --recursive --profile "$PROFILE" 2>/dev/null
  aws s3api delete-bucket --bucket "$BUCKET" --profile "$PROFILE" --region "$REGION" 2>/dev/null
else
  echo "== Keeping bucket; clearing derived data only =="
  for p in processed tmp logs; do
    aws s3 rm "s3://$BUCKET/$p/" --recursive --profile "$PROFILE" 2>/dev/null
  done
fi

if $INCLUDE_ROLE; then
  echo "== Deleting shared IAM role $ROLE =="
  aws iam delete-role-policy --role-name "$ROLE" --policy-name demo-permissions --profile "$PROFILE" 2>/dev/null
  aws iam detach-role-policy --role-name "$ROLE" --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess --profile "$PROFILE" 2>/dev/null
  aws iam delete-role --role-name "$ROLE" --profile "$PROFILE" 2>/dev/null
fi

echo "Cleanup complete."
