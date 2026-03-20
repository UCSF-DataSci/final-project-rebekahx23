# Evaluation Report: dq-manual-simple-p05-flash-20260320T045722Z

Generated at: 2026-03-20 04:58:10 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T045722Z.json`
Evaluation mode: `delta_vs_baseline`
Baseline DB: `sqlite:///./runs/db/healthcare_clean.sqlite`

## Micro Average (Selected Mode)
- TP: **1110**
- FP: **23**
- FN: **2184**
- Precision: **0.9797**
- Recall: **0.3370**
- F1: **0.5015**

## Micro Average (Raw Current DB)
- TP: **1110**
- FP: **23**
- FN: **2184**
- Precision: **0.9797**
- Recall: **0.3370**
- F1: **0.5015**

## Micro Average (Delta vs Baseline)
- TP: **1110**
- FP: **23**
- FN: **2184**
- Precision: **0.9797**
- Recall: **0.3370**
- F1: **0.5015**

## Per-Check Metrics
| Test | Status | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discharge_before_admission | FAIL | future_date,id_fragmentation,temporal_inversion,truncate | delta | yes | 1133 | 0 | 1133 | 1110 | 23 | 1074 | 0.9797 | 0.5082 | 0.6693 |
| missed_issue_ids(sample) | - | - | - | - | - | - | - | - | - | - | - | - | `18, 228, 348, 424, 429, 497, 612, 613, 615, 622, 636, 660, 667, 681, 694, 698, 715, 720, 747, 798` |
| inconsistent_gender_values | PASS | enum_encoding_drift,id_fragmentation,nullify | delta | yes | 0 | 0 | 0 | 0 | 0 | 1110 | 0.0000 | 0.0000 | 0.0000 |
| missed_issue_ids(sample) | - | - | - | - | - | - | - | - | - | - | - | - | `22, 35, 65, 87, 145, 146, 276, 355, 371, 400, 407, 418, 455, 479, 593, 605, 630, 631, 645, 724` |
