# Module 3 — Feature Store: SageMaker AI vs Unified Studio

Define + populate a feature group for the engineered taxi features, then show it as
a governed catalog asset.

| | Path | Status |
|---|---|---|
| **Old way** — SDK FeatureGroup | [`feature_store_ingest.py`](feature_store_ingest.py) | live-testable |
| **New way** — US catalog asset | [`WALKTHROUGH.md`](WALKTHROUGH.md) | walkthrough |

Same Feature Store underneath; Unified Studio makes the group **discoverable,
permissioned, and lineage-linked**. Offline store = S3 (pennies); online store
optional (`--online`).
