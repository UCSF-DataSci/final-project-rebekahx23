# Evaluation Report: dq-manual-simple-p20-pro-20260320T050445Z

Generated at: 2026-03-20 05:06:04 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T045722Z.json`
Evaluation mode: `delta_vs_baseline`
Baseline DB: `sqlite:///./runs/db/healthcare_clean.sqlite`

## Micro Average (Selected Mode)
- TP: **2220**
- FP: **42**
- FN: **1091**
- Precision: **0.9814**
- Recall: **0.6705**
- F1: **0.7967**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **42**
- FN: **1091**
- Precision: **0.9814**
- Recall: **0.6705**
- F1: **0.7967**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **42**
- FN: **1091**
- Precision: **0.9814**
- Recall: **0.6705**
- F1: **0.7967**

## Per-Check Metrics
| Test | Status | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| unrealistic_patient_age | FAIL | id_fragmentation,nullify,numeric_outlier | delta | yes | 1129 | 0 | 1129 | 1110 | 19 | 1091 | 0.9832 | 0.5043 | 0.6667 |
| missed_issue_ids(sample) | - | - | - | - | - | - | - | - | - | - | - | - | `22, 35, 65, 87, 145, 146, 276, 355, 371, 400, 407, 418, 455, 479, 593, 605, 630, 631, 645, 724` |
| discharge_before_admission | FAIL | future_date,id_fragmentation,temporal_inversion | delta | yes | 1133 | 0 | 1133 | 1110 | 23 | 0 | 0.9797 | 1.0000 | 0.9897 |
