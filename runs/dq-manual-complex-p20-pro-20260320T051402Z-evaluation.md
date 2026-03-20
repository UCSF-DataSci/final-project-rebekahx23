# Evaluation Report: dq-manual-complex-p20-pro-20260320T051402Z

Generated at: 2026-03-20 05:15:22 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T050803Z.json`
Evaluation mode: `delta_vs_baseline`
Baseline DB: `sqlite:///./runs/db/healthcare_clean.sqlite`

## Micro Average (Selected Mode)
- TP: **555**
- FP: **0**
- FN: **1650**
- Precision: **1.0000**
- Recall: **0.2517**
- F1: **0.4022**

## Micro Average (Raw Current DB)
- TP: **855**
- FP: **10165**
- FN: **1350**
- Precision: **0.0776**
- Recall: **0.3878**
- F1: **0.1293**

## Micro Average (Delta vs Baseline)
- TP: **555**
- FP: **0**
- FN: **1650**
- Precision: **1.0000**
- Recall: **0.2517**
- F1: **0.4022**

## Per-Check Metrics
| Test | Status | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discharge_before_admission | FAIL | future_date,id_fragmentation,temporal_inversion,truncate | delta | yes | 555 | 0 | 555 | 555 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| malformed_hospital_name | FAIL | all_corruptions | delta | yes | 0 | 10465 | 0 | 0 | 0 | 1650 | 0.0000 | 0.0000 | 0.0000 |
| missed_issue_ids(sample) | - | - | - | - | - | - | - | - | - | - | - | - | `5, 57, 84, 96, 156, 186, 225, 250, 262, 271, 276, 290, 294, 421, 456, 542, 558, 561, 578, 581` |
