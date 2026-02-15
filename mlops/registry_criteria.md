# AI Model Registry & Promotion Criteria

This document defines the criteria for promoting an AI model from **Experiment** to **Staging** and **Production**.

## 1. Registry Stages

| Stage | Description | Access Level |
|---|---|---|
| **None** (Experiment) | Metric logging only. Failed or preliminary runs. | Data Scientists only |
| **Staging** | Candidates for production. Must pass unit tests and metric thresholds. | QA / Admin |
| **Production** | Live model serving real traffic. | Public User |
| **Archived** | Old production models. Kept for rollback. | Admin |

## 2. Promotion Criteria (Staging)

A model is automatically promoted to **Staging** if:
1. **Training Completion**: Successfully trained without errors.
2. **Metric Thresholds**:
   - `R2 Score` >= 0.70
   - `MAE` <= 4,000,000 KRW (400만원)
3. **Artifacts**: Model file (`model.pkl`) is saved and valid.

## 3. Promotion Criteria (Production)

A model is promoted to **Production** if:
1. **A/B Test Success**:
   - Outperforms current Production model in **Conversion Rate** or **Click Rate** for 7 days.
   - OR
   - Manually approved by Admin via Dashboard.
2. **Safety Check**:
   - No bias detected in sensitive districts.
   - Inference latency < 200ms.

## 4. Automation Pipeline

- **Trigger**: `train_model.py` automatically registers models meeting Staging criteria.
- **Approval**: Admin uses `pages/admin_mlops.py` to click "Promote to Production".
