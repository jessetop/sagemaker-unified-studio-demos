# Tear down all resources created by the SageMaker Unified Studio demo series.
# Safe to re-run. Only touches resources named/tagged for this demo.
#
#   pwsh cleanup/cleanup.ps1                 # delete jobs/apps/endpoints, keep bucket+role
#   pwsh cleanup/cleanup.ps1 -IncludeBucket  # also empty + delete the S3 bucket
#   pwsh cleanup/cleanup.ps1 -IncludeRole    # also delete the shared IAM role
#
param(
    [string]$Profile = "roitraining",
    [string]$Region  = "us-east-2",
    [switch]$IncludeBucket,
    [switch]$IncludeRole
)

$ErrorActionPreference = "Continue"
$Bucket = "roi-smdemo-029331796573-us-east-2"
$Role   = "roi-smdemo-exec-role"

Write-Host "== Deleting Glue job, crawler, and demo database =="
aws glue delete-job --job-name roi-smdemo-taxi-visual-etl --profile $Profile --region $Region 2>$null
aws glue delete-crawler --name roi-smdemo-taxi-crawler --profile $Profile --region $Region 2>$null
aws glue delete-database --name taxi_demo --profile $Profile --region $Region 2>$null

Write-Host "== Deleting Feature Store group =="
aws sagemaker delete-feature-group --feature-group-name roi-smdemo-taxi-features --profile $Profile --region $Region 2>$null

Write-Host "== Deleting Pipeline, Model Registry, Experiment =="
aws sagemaker delete-pipeline --pipeline-name roi-smdemo-taxi-pipeline --profile $Profile --region $Region 2>$null
$pkgs = aws sagemaker list-model-packages --model-package-group-name roi-smdemo-taxi-models --profile $Profile --region $Region --query "ModelPackageSummaryList[].ModelPackageArn" --output text 2>$null
foreach ($pkg in ($pkgs -split "\s+" | Where-Object { $_ })) {
    aws sagemaker delete-model-package --model-package-name $pkg --profile $Profile --region $Region 2>$null
}
aws sagemaker delete-model-package-group --model-package-group-name roi-smdemo-taxi-models --profile $Profile --region $Region 2>$null
aws sagemaker delete-model --model-name roi-smdemo-taxi-model --profile $Profile --region $Region 2>$null
# Experiment runs/trial-components must be deleted before the experiment; the
# SageMaker SDK's experiment cleanup is easiest for this — see note in cleanup.sh.
aws sagemaker delete-experiment --experiment-name roi-smdemo-taxi-experiment --profile $Profile --region $Region 2>$null

Write-Host "== Stopping + deleting EMR Serverless applications =="
$apps = aws emr-serverless list-applications --profile $Profile --region $Region `
    --query "applications[?name=='roi-smdemo-taxi-emr'].id" --output text
foreach ($a in ($apps -split "\s+" | Where-Object { $_ })) {
    aws emr-serverless stop-application --application-id $a --profile $Profile --region $Region 2>$null
    aws emr-serverless delete-application --application-id $a --profile $Profile --region $Region 2>$null
    Write-Host "  deleted app $a"
}

Write-Host "== Deleting SageMaker endpoints tagged for this demo (modules 3-7) =="
$eps = aws sagemaker list-endpoints --profile $Profile --region $Region `
    --query "Endpoints[?starts_with(EndpointName,'roi-smdemo')].EndpointName" --output text
foreach ($e in ($eps -split "\s+" | Where-Object { $_ })) {
    aws sagemaker delete-endpoint --endpoint-name $e --profile $Profile --region $Region 2>$null
    Write-Host "  deleted endpoint $e"
}

if ($IncludeBucket) {
    Write-Host "== Emptying + deleting bucket $Bucket =="
    aws s3 rm "s3://$Bucket" --recursive --profile $Profile 2>$null
    aws s3api delete-bucket --bucket $Bucket --profile $Profile --region $Region 2>$null
} else {
    Write-Host "== Keeping bucket (use -IncludeBucket to delete). Clearing derived data only =="
    aws s3 rm "s3://$Bucket/processed/" --recursive --profile $Profile 2>$null
    aws s3 rm "s3://$Bucket/tmp/" --recursive --profile $Profile 2>$null
    aws s3 rm "s3://$Bucket/logs/" --recursive --profile $Profile 2>$null
}

if ($IncludeRole) {
    Write-Host "== Deleting shared IAM role $Role =="
    aws iam delete-role-policy --role-name $Role --policy-name demo-permissions --profile $Profile 2>$null
    aws iam detach-role-policy --role-name $Role --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess --profile $Profile 2>$null
    aws iam delete-role --role-name $Role --profile $Profile 2>$null
}

Write-Host "Cleanup complete."
