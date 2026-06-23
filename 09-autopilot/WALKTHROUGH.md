# Module 9 — AutoML / model ranking: Autopilot (SDK/Studio) vs Canvas

**~5 minutes.** Let AutoML train and **rank** many candidate models for `high_tip`,
shown the code/low-code way and the no-code way.

## The one engine, three front doors
**Autopilot** is the AutoML engine (`CreateAutoMLJobV2`). It's driven by:
- **SDK** (code) — `09-autopilot/launch_autopilot.py` (this demo's automated path).
- **Studio Classic → Autopilot UI** (low-code GUI).
- **SageMaker Canvas** (no-code GUI; the one surfaced in Unified Studio).

All three create the **same job** and the **same ranked leaderboard**. "Canvas is
the new way" really means "Canvas is the **no-code** way."

## Learning objectives
- Run a cost-capped Autopilot job and read the **candidate leaderboard** (ranking).
- Understand Autopilot vs Canvas as front doors to one engine.
- Contrast code/low-code (SageMaker AI) with no-code (Canvas / Unified Studio).

## Old way — Autopilot via SDK  ✅ tested
```bash
python launch_autopilot.py \
  --bucket roi-smdemo-029331796573-us-east-2 \
  --role-arn arn:aws:iam::029331796573:role/roi-smdemo-exec-role \
  --profile roitraining --region us-east-2 --sample-rows 15000 --max-candidates 10
# then, once Completed:
python launch_autopilot.py ... --leaderboard
```
- **Cost-capped** (see the script): 15k-row sample, ENSEMBLING mode, max 10
  candidates, 600s/job, 1h total → ~$2-6 (the one demo that costs dollars).
- Point at the **leaderboard**: candidates ranked by Accuracy; Autopilot also
  auto-generates an explainability report and a "best candidate" you can deploy.
- Also visible in **Studio Classic → Autopilot** (the low-code GUI for the same job).

## New way — SageMaker Canvas (no-code)
Live demo (no script — it's a GUI):
1. **Unified Studio / Studio → Canvas** → **My models → New model → Predictive**.
2. **Select dataset**: the taxi training CSV (`ml/taxi/autopilot/train.csv` or
   import from the `taxi_demo` catalog).
3. **Target column**: `high_tip` → Canvas detects **binary classification**.
4. **Quick build** (fast/cheap) or **Standard build** (full Autopilot).
5. Canvas shows the **model leaderboard + feature importance + what-if** — the same
   Autopilot ranking, no code.
6. **Stop the Canvas app** when done (Canvas → Log out / the admin Stop) — it's a
   billable running session (~$1.90/hr).

## Old vs new — talking points
| | Autopilot SDK / Studio (old) | Canvas (new) |
|---|---|---|
| Audience | data scientist / engineer | analyst / no-code |
| Interface | code / low-code GUI | fully no-code |
| Engine | **Autopilot** | **Autopilot** (same) |
| Output | leaderboard + deployable best model | leaderboard + what-if, 1-click deploy |
| Lives in | SageMaker AI | Canvas, integrated in Unified Studio |

## Cost & cleanup
SDK job is capped (~$2-6) and auto-stops. Canvas: **stop the app session** after
the demo. Delete the AutoML artifacts with the cleanup script (and any model/
endpoint you deploy from the best candidate).
