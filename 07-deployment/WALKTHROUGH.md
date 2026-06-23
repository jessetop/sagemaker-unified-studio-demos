# Module 7 — Deployment & inference: SageMaker AI vs Unified Studio

**~5 minutes.** Deploy the trained taxi model to a real-time endpoint, score a few
requests, then delete it — using the cheapest serving option.

## Learning objectives
- Create a SageMaker Model from a training job's artifact and deploy a real-time
  endpoint (**Serverless Inference** — scales to zero).
- Send inference requests and read predictions; handle errors.
- Always delete the endpoint to avoid ongoing charges.

## Prerequisites / starting state
- A completed training job with a model artifact in S3 (Module 4).
- Test split at `ml/taxi/test/test.csv`.
- Cross-reference: model + features from [Module 4](../04-training/WALKTHROUGH.md).

## Old way — SageMaker AI (SDK)
```bash
python deploy_and_infer.py \
  --model-data s3://roi-smdemo-029331796573-us-east-2/.../output/model.tar.gz \
  --role-arn arn:aws:iam::029331796573:role/roi-smdemo-exec-role \
  --bucket roi-smdemo-029331796573-us-east-2 \
  --profile roitraining --region us-east-2
```
- `SKLearnModel` + `model.deploy(ServerlessInferenceConfig(...))` (Kiro Req 7.1-7.2).
- Sends **3 inference requests** from the held-out test set (Req 7.3).
- `finally:` block **deletes the endpoint** no matter what (Req 7.4) — the single
  most important cost-safety habit to teach.
- Instructor note (Req 7.6): serverless scales to zero (cheapest, cold starts) vs
  real-time instances (always-on, low latency) vs async (large payloads). Auto-
  scaling applies to instance endpoints.

## New way — Unified Studio
From the project, deploy the same model with one click / a project notebook cell.
Differences: the endpoint is a **governed asset** with lineage to the model and
training run; access is controlled by project membership; monitoring shows up in
the project. The serving API is identical.

## Old vs new — talking points
| | SageMaker AI | Unified Studio |
|---|---|---|
| Deploy | SDK `model.deploy()` | one-click / notebook in project |
| Govern | IAM + tags | project membership + catalog |
| Monitor | CloudWatch you wire | project monitoring view |
| The endpoint | **same InvokeEndpoint** | **same InvokeEndpoint** |

## Cost & cleanup
Serverless Inference bills per request + compute-duration with **no idle cost**;
this demo deletes the endpoint immediately. The cleanup script also sweeps any
`roi-smdemo*` endpoints as a safety net.
