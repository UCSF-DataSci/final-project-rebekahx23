# Evaluation Report: dq-manual-complex-p10-flash-20260320T050856Z

Generated at: 2026-03-20 05:09:41 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T050803Z.json`
Evaluation mode: `delta_vs_baseline`
Baseline DB: `sqlite:///./runs/db/healthcare_clean.sqlite`

## Micro Average (Selected Mode)
- TP: **0**
- FP: **0**
- FN: **0**
- Precision: **0.0000**
- Recall: **0.0000**
- F1: **0.0000**

## Micro Average (Raw Current DB)
- TP: **0**
- FP: **55417**
- FN: **0**
- Precision: **0.0000**
- Recall: **0.0000**
- F1: **0.0000**

## Micro Average (Delta vs Baseline)
- TP: **0**
- FP: **0**
- FN: **0**
- Precision: **0.0000**
- Recall: **0.0000**
- F1: **0.0000**

## Per-Check Metrics
| Test | Status | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discharge_before_admission | PASS | future_date,id_fragmentation,nullify,temporal_inversion,truncate | raw | no | 0 | 0 | 0 | 0 | 0 | 555 | 0.0000 | 0.0000 | 0.0000 |
| reason | - | - | - | - | - | - | - | - | - | - | - | - | `rowid_query_failed: (sqlite3.OperationalError) incomplete input
[SQL: SELECT rowid AS _dq_rowid FROM healthcare_dataset WHERE date_of_admission IS NOT NULL AND discharge_date IS NOT NULL AND -- Basic check for YYYY-MM-DD format before comparison date_of_admission GLOB '____-__-__' AND discharge_date GLOB '____-__-__' AND julianday(discharge_date) < julianday(date_of_admission)]
(Background on this error at: https://sqlalche.me/e/20/e3q8)` |
| missed_issue_ids(sample) | - | - | - | - | - | - | - | - | - | - | - | - | `5, 84, 186, 294, 542, 578, 720, 877, 1035, 1130, 1143, 1187, 1424, 1427, 1479, 1624, 1649, 1712, 1901, 1918` |
| name_inconsistent_casing | FAIL | duplicate_rows,id_fragmentation,nullify | delta | yes | 0 | 55417 | 0 | 0 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 |
