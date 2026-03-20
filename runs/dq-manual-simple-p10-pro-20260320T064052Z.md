# Data Quality Report - dq-manual-simple-p10-pro-20260320T064052Z

Generated at: 2026-03-20 06:41:58 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **1**
- Failed: **1**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P10-PRO`
- Event log: `runs/dq-manual-simple-p10-pro-20260320T064052Z.jsonl`

## Coverage Breakdown
| Severity | Count |
|---|---:|
| Critical | 1 |
| High | 1 |
| Medium | 0 |
| Low | 0 |

## Top Findings
| Severity | Status | Table | Test | Issue Count |
|---|---|---|---|---:|
| CRITICAL | FAIL | healthcare_dataset | unrealistic_age | 1135 |

## Detailed Findings
### 1. [CRITICAL/FAIL] unrealistic_age (healthcare_dataset)
- Why this matters: The `age` column contains extreme outliers (e.g., 38500, 49000) that are physiologically impossible for humans. These values are certainly data entry errors and will severely skew any statistical analysis, making this a critical issue to fix. This test flags any age greater than 120.
- Issue count: **1135**
- Output truncated: **yes**

```sql
SELECT
  *
FROM
  healthcare_dataset
WHERE
  age > 120;
```

Example rows:
```json
[
  {
    "name": "NICOLE HUGhes",
    "age": 20000,
    "gender": "Male",
    "blood_type": "O+",
    "medical_condition": "Arthritis",
    "date_of_admission": "2020-12-04",
    "doctor": "Lori Sanchez",
    "hospital": "Shaw-Young",
    "insurance_provider": "Blue Cross",
    "billing_amount": 34617.788344937246,
    "room_number": 320,
    "admission_type": "Emergency",
    "discharge_date": "2020-12-08",
    "medication": "Ibuprofen",
    "test_results": "Abnormal"
  },
  {
    "name": "jOHN GarciA",
    "age": 29500,
    "gender": "Female",
    "blood_type": "A+",
    "medical_condition": "Diabetes",
    "date_of_admission": "2023-08-29",
    "doctor": "Jesse Thomas",
    "hospital": "Sons Miller and",
    "insurance_provider": "UnitedHealthcare",
    "billing_amount": 1150.8749860875837,
    "room_number": 408,
    "admission_type": "Urgent",
    "discharge_date": "2023-09-07",
    "medication": "Penicillin",
    "test_results": "Abnormal"
  },
  {
    "name": "sHaUN LonG",
    "age": 41000,
    "gender": "Female",
    "blood_type": "A+",
    "medical_condition": "Obesity",
    "date_of_admission": "2024-02-09",
    "doctor": "Jenny Griffith",
    "hospital": "Fritz Henderson Stanton, and",
    "insurance_provider": "UnitedHealthcare",
    "billing_amount": 45902.70764469024,
    "room_number": 126,
    "admission_type": "Urgent",
    "discharge_date": "2024-02-19",
    "medication": "Aspirin",
    "test_results": "Normal"
  }
]
```

## Supervisor Narrative
Supervisor narrative was not available as plain text. See JSONL event logs for details.
