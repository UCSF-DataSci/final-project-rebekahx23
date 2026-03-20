# Evaluation Report: dq-manual-simple-p10-pro-20260320T050147Z

Generated at: 2026-03-20 05:03:09 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T045722Z.json`
Evaluation mode: `delta_vs_baseline`
Baseline DB: `sqlite:///./runs/db/healthcare_clean.sqlite`

## Micro Average (Selected Mode)
- TP: **2220**
- FP: **50**
- FN: **1091**
- Precision: **0.9780**
- Recall: **0.6705**
- F1: **0.7956**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **50**
- FN: **1091**
- Precision: **0.9780**
- Recall: **0.6705**
- F1: **0.7956**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **50**
- FN: **1091**
- Precision: **0.9780**
- Recall: **0.6705**
- F1: **0.7956**

## Per-Check Metrics
| Test | Status | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| unrealistic_patient_age | FAIL | id_fragmentation,numeric_outlier | delta | yes | 1129 | 0 | 1129 | 1110 | 19 | 0 | 0.9832 | 1.0000 | 0.9915 |
| missing_patient_name | FAIL | id_fragmentation,nullify,numeric_outlier | delta | yes | 1141 | 0 | 1141 | 1110 | 31 | 1091 | 0.9728 | 0.5043 | 0.6643 |
| missed_issue_ids(sample) | - | - | - | - | - | - | - | - | - | - | - | - | `6, 20, 82, 118, 135, 164, 176, 292, 414, 451, 503, 524, 526, 872, 933, 943, 983, 1021, 1036, 1037` |
