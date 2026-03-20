# Evaluation Report: dq-manual-simple-p20-flash-20260320T045919Z

Generated at: 2026-03-20 05:00:09 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T045722Z.json`
Evaluation mode: `delta_vs_baseline`
Baseline DB: `sqlite:///./runs/db/healthcare_clean.sqlite`

## Micro Average (Selected Mode)
- TP: **2220**
- FP: **54**
- FN: **2162**
- Precision: **0.9763**
- Recall: **0.5066**
- F1: **0.6671**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **54**
- FN: **2162**
- Precision: **0.9763**
- Recall: **0.5066**
- F1: **0.6671**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **54**
- FN: **2162**
- Precision: **0.9763**
- Recall: **0.5066**
- F1: **0.6671**

## Per-Check Metrics
| Test | Status | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| admission_after_discharge_date | FAIL | future_date,id_fragmentation,temporal_inversion,truncate | delta | yes | 1133 | 0 | 1133 | 1110 | 23 | 1074 | 0.9797 | 0.5082 | 0.6693 |
| missed_issue_ids(sample) | - | - | - | - | - | - | - | - | - | - | - | - | `18, 228, 348, 424, 429, 497, 612, 613, 615, 622, 636, 660, 667, 681, 694, 698, 715, 720, 747, 798` |
| missing_patient_name | FAIL | future_date,id_fragmentation,nullify,temporal_inversion | delta | yes | 1141 | 0 | 1141 | 1110 | 31 | 1088 | 0.9728 | 0.5050 | 0.6649 |
| missed_issue_ids(sample) | - | - | - | - | - | - | - | - | - | - | - | - | `123, 171, 248, 261, 275, 299, 439, 493, 586, 640, 684, 763, 851, 896, 936, 957, 1004, 1069, 1106, 1277` |
