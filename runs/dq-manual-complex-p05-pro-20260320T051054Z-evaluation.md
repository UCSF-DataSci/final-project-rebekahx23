# Evaluation Report: dq-manual-complex-p05-pro-20260320T051054Z

Generated at: 2026-03-20 05:12:07 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T050803Z.json`
Evaluation mode: `delta_vs_baseline`
Baseline DB: `sqlite:///./runs/db/healthcare_clean.sqlite`

## Micro Average (Selected Mode)
- TP: **0**
- FP: **555**
- FN: **0**
- Precision: **0.0000**
- Recall: **0.0000**
- F1: **0.0000**

## Micro Average (Raw Current DB)
- TP: **0**
- FP: **9478**
- FN: **0**
- Precision: **0.0000**
- Recall: **0.0000**
- F1: **0.0000**

## Micro Average (Delta vs Baseline)
- TP: **0**
- FP: **555**
- FN: **0**
- Precision: **0.0000**
- Recall: **0.0000**
- F1: **0.0000**

## Per-Check Metrics
| Test | Status | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| invalid_gender_values | FAIL | id_fragmentation | delta | yes | 555 | 0 | 555 | 0 | 555 | 0 | 0.0000 | 0.0000 | 0.0000 |
| inconsistent_hospital_name_formatting | FAIL | id_fragmentation,truncate | delta | yes | 0 | 8923 | 0 | 0 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 |
