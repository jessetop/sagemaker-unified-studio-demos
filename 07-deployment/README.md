# Module 7 — Deployment & inference: SageMaker AI vs Unified Studio

Deploy the trained model to a real-time endpoint, score a few requests, delete it.

| | Path | Status |
|---|---|---|
| **Old way** — SDK serverless endpoint | [`deploy_and_infer.py`](deploy_and_infer.py) | live-testable |
| **New way** — US one-click deploy | [`WALKTHROUGH.md`](WALKTHROUGH.md) | walkthrough |

Uses **Serverless Inference** (scales to zero, cheapest) and **always deletes the
endpoint** in a `finally` block. Same InvokeEndpoint API both ways; Unified Studio
governs and monitors it inside the project.
