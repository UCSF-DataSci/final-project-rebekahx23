# Evaluation Report: dq-manual-simple-p10-flash-20260320T045820Z

Generated at: 2026-03-20 04:59:09 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T045722Z.json`
Evaluation mode: `delta_vs_baseline`
Baseline DB: `sqlite:///./runs/db/healthcare_clean.sqlite`

## Micro Average (Selected Mode)
- TP: **2220**
- FP: **50**
- FN: **2182**
- Precision: **0.9780**
- Recall: **0.5043**
- F1: **0.6655**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **50**
- FN: **2182**
- Precision: **0.9780**
- Recall: **0.5043**
- F1: **0.6655**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **50**
- FN: **2182**
- Precision: **0.9780**
- Recall: **0.5043**
- F1: **0.6655**

## Per-Check Metrics
| Test | Status | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| age_out_of_realistic_range | FAIL | id_fragmentation,nullify,numeric_outlier | delta | yes | 1129 | 0 | 1129 | 1110 | 19 | 1091 | 0.9832 | 0.5043 | 0.6667 |
| missed_issue_ids(sample) | - | - | - | - | - | - | - | - | - | - | - | - | `22, 35, 65, 87, 145, 146, 276, 355, 371, 400, 407, 418, 455, 479, 593, 605, 630, 631, 645, 724` |
| patient_name_is_null_or_empty | FAIL | id_fragmentation,nullify,numeric_outlier | delta | yes | 1141 | 0 | 1141 | 1110 | 31 | 1091 | 0.9728 | 0.5043 | 0.6643 |
| missed_issue_ids(sample) | - | - | - | - | - | - | - | - | - | - | - | - | `6, 20, 82, 118, 135, 164, 176, 292, 414, 451, 503, 524, 526, 872, 933, 943, 983, 1021, 1036, 1037` |
