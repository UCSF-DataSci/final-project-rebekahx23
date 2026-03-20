# Data Quality Report - dq-manual-simple-p05-pro-20260320T050019Z

Generated at: 2026-03-20 05:01:34 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **1**
- Failed: **1**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P05-PRO`
- Event log: `runs/dq-manual-simple-p05-pro-20260320T050019Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | discharge_before_admission | 1133 |

## Detailed Findings
### 1. [CRITICAL/FAIL] discharge_before_admission (healthcare_dataset)
- Why this matters: A patient's discharge date must be after their admission date. Records where the discharge date is on or before the admission date represent a logical impossibility and will lead to incorrect calculations for metrics like length of stay. This is a critical data integrity failure.
- Issue count: **1133**
- Output truncated: **yes**

```sql
SELECT
  *
FROM healthcare_dataset
WHERE
  date_of_admission IS NOT NULL
  AND discharge_date IS NOT NULL
  AND julianday(discharge_date) <= julianday(date_of_admission);
```

Example rows:
```json
[
  {
    "name": "Jeffrey tuRNER",
    "age": 85,
    "gender": "Female",
    "blood_type": "O+",
    "medical_condition": "Obesity",
    "date_of_admission": "2099-12-31",
    "doctor": "Matthew Carter",
    "hospital": "Kim Rosario, and Hammond",
    "insurance_provider": "Aetna",
    "billing_amount": 39957.94062222976,
    "room_number": 211,
    "admission_type": "Urgent",
    "discharge_date": "2020-06-01",
    "medication": "Ibuprofen",
    "test_results": "Normal"
  },
  {
    "name": "jEssiCa GoNzAleS",
    "age": 57,
    "gender": "Female",
    "blood_type": "O+",
    "medical_condition": "Hypertension",
    "date_of_admission": "2099-12-31",
    "doctor": "Kimberly Gonzalez",
    "hospital": "Jones and Jones, Turner",
    "insurance_provider": "Cigna",
    "billing_amount": 20545.871762829884,
    "room_number": 198,
    "admission_type": "Urgent",
    "discharge_date": "2023-09-16",
    "medication": "Penicillin",
    "test_results": "Abnormal"
  },
  {
    "name": "dr. MATthEW wilkinS",
    "age": 80,
    "gender": "Male",
    "blood_type": "A-",
    "medical_condition": "Cancer",
    "date_of_admission": "2099-12-31",
    "doctor": "Seth Nelson",
    "hospital": "PLC Anderson",
    "insurance_provider": "Blue Cross",
    "billing_amount": 22401.550353437575,
    "room_number": 242,
    "admission_type": "Elective",
    "discharge_date": "2021-07-24",
    "medication": "Lipitor",
    "test_results": "Inconclusive"
  }
]
```

## Supervisor Narrative
Data Quality Run Summary: **RED**

A critical data quality issue was found in the `healthcare_dataset` table, indicating a high risk of incorrect analysis if this data is used in its current state.

### Top Issues
- **CRITICAL**: `discharge_before_admission`
  - **1,133 records** have a discharge date that is on or before the admission date. This represents a fundamental logical error in the patient admission timeline.
  - Observing the sample data, many failing records share a `date_of_admission` of `2099-12-31`, suggesting a potential default value or data entry error that needs immediate investigation.

### Test Coverage Notes
- This data quality run focused on validating the date fields within the `healthcare_dataset` table.
- The test for valid date formats (`invalid_date_format`) passed, confirming that all date columns can be correctly parsed.
- Other potential risks identified during initial profiling, such as inconsistent casing in `name` and `hospital` columns, and null values in `name`, were not covered in this run.

### Suggested Production Guardrails
To prevent this issue from recurring, the following SQL check should be implemented as a blocking guardrail on all future data loads for the `healthcare_dataset` table:

```sql
-- Guardrail: Ensure discharge_date is always after date_of_admission
SELECT
  count(*)
FROM
  healthcare_dataset
WHERE
  julianday(discharge_date) <= julianday(date_of_admission);
```

This query should return 0 for the data load to proceed.
