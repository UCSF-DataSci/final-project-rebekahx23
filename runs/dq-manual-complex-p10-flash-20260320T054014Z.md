# Data Quality Report - dq-manual-complex-p10-flash-20260320T054014Z

Generated at: 2026-03-20 05:41:12 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **1**
- Failed: **1**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P10-FLASH`
- Event log: `runs/dq-manual-complex-p10-flash-20260320T054014Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | discharge_before_admission | 555 |

## Detailed Findings
### 1. [CRITICAL/FAIL] discharge_before_admission (healthcare_dataset)
- Why this matters: Ensures that the discharge date logically occurs after or on the same day as the admission date. Records where the discharge date precedes the admission date indicate a fundamental logical error in the patient's record timeline. This test also implicitly checks for the basic parseability of both dates by `julianday()`, which returns NULL for malformed date strings, preventing comparisons on non-date values.
- Issue count: **555**
- Output truncated: **yes**

```sql
SELECT *
  FROM healthcare_dataset
  WHERE
      date_of_admission IS NOT NULL
      AND discharge_date IS NOT NULL
      AND julianday(discharge_date) < julianday(date_of_admission);
```

Example rows:
```json
[
  {
    "name": "CHrisTInA MARtinez",
    "age": 20,
    "gender": "Female",
    "blood_type": "A+",
    "medical_condition": "Cancer",
    "date_of_admission": "2021-12-28",
    "doctor": "Suzanne Thomas",
    "hospital": "Powell Robinson and Valdez,",
    "insurance_provider": "Cigna",
    "billing_amount": 45820.46272159459,
    "room_number": 277,
    "admission_type": "Emergency",
    "discharge_date": "2021-12-27",
    "medication": "Paracetamol",
    "test_results": "Inconclusive"
  },
  {
    "name": "JOsEph fOstER",
    "age": 59,
    "gender": "Female",
    "blood_type": "O+",
    "medical_condition": "Obesity",
    "date_of_admission": "2019-09-11",
    "doctor": "Daniel Smith",
    "hospital": "Alvarado-Deleon",
    "insurance_provider": "Blue Cross",
    "billing_amount": 27385.736227988127,
    "room_number": 427,
    "admission_type": "Emergency",
    "discharge_date": "2019-09-10",
    "medication": "Penicillin",
    "test_results": "Inconclusive"
  },
  {
    "name": "mIcHael anDeRson",
    "age": 64,
    "gender": "Female",
    "blood_type": "AB-",
    "medical_condition": "Arthritis",
    "date_of_admission": "2019-08-16",
    "doctor": "Charles Webb",
    "hospital": "Bass Inc",
    "insurance_provider": "Medicare",
    "billing_amount": 5549.785435792208,
    "room_number": 302,
    "admission_type": "Emergency",
    "discharge_date": "2019-08-15",
    "medication": "Ibuprofen",
    "test_results": "Inconclusive"
  }
]
```

## Supervisor Narrative
**Overall Verdict:**
🔴 Red

**Top Critical/High Issues:**
The most critical issue found is in the `healthcare_dataset` table, where the `discharge_before_admission` test failed. A significant **555 records** have a `discharge_date` that precedes the `date_of_admission`, indicating a severe logical inconsistency in the patient records.

**Test Coverage Notes:**
A total of 2 data quality tests were executed on the `healthcare_dataset` table:
- `discharge_before_admission`: **Failed** (Critical severity)
- `invalid_admission_date_format`: **Passed** (High severity)

**Suggested Production Guardrails (SQL checks to schedule each load):**
To prevent similar data integrity issues from entering the system in the future, the following SQL checks should be implemented and run on each data load:

**1. Prevent discharge dates before admission dates (Critical):**
```sql
SELECT *
FROM healthcare_dataset
WHERE
    date_of_admission IS NOT NULL
    AND discharge_date IS NOT NULL
    AND julianday(discharge_date) < julianday(date_of_admission);
```
This check ensures that the discharge date is always on or after the admission date. Any records failing this check should be immediately flagged and investigated.

The `invalid_admission_date_format` test passed, so no immediate guardrail is needed for that specific format, but the underlying columns `date_of_admission` and `discharge_date` are still `TEXT`. A more robust solution would involve migrating these columns to a proper `DATE` or `DATETIME` data type.
