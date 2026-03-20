# Data Quality Report - dq-manual-complex-p20-flash-20260320T050952Z

Generated at: 2026-03-20 05:10:42 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **1**
- Failed: **1**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P20-FLASH`
- Event log: `runs/dq-manual-complex-p20-flash-20260320T050952Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | discharge_before_admission_date | 555 |

## Detailed Findings
### 1. [CRITICAL/FAIL] discharge_before_admission_date (healthcare_dataset)
- Why this matters: The 'discharge_date' cannot logically occur before the 'date_of_admission'. This indicates a critical data entry error or logical flaw, making the patient's record of stay inconsistent and unreliable for analysis related to duration of stay or timelines.
- Issue count: **555**
- Output truncated: **yes**

```sql
SELECT *
FROM healthcare_dataset
WHERE
  date_of_admission IS NOT NULL AND discharge_date IS NOT NULL
  AND julianday(discharge_date) < julianday(date_of_admission);
```

Example rows:
```json
[
  {
    "name": "adrIENNE bEll",
    "age": 43,
    "gender": "Female",
    "blood_type": "AB+",
    "medical_condition": "Cancer",
    "date_of_admission": "2022-09-19",
    "doctor": "Kathleen Hanna",
    "hospital": "White-White",
    "insurance_provider": "Aetna",
    "billing_amount": 14238.317813937623,
    "room_number": 458,
    "admission_type": "Urgent",
    "discharge_date": "2022-09-18",
    "medication": "Penicillin",
    "test_results": "Abnormal"
  },
  {
    "name": "DIAnE brAnch",
    "age": 44,
    "gender": "Male",
    "blood_type": "O+",
    "medical_condition": "Obesity",
    "date_of_admission": "2020-05-30",
    "doctor": "Juan Acevedo",
    "hospital": "Perez and Sons",
    "insurance_provider": "Cigna",
    "billing_amount": 22841.363876905678,
    "room_number": 410,
    "admission_type": "Emergency",
    "discharge_date": "2020-05-29",
    "medication": "Aspirin",
    "test_results": "Inconclusive"
  },
  {
    "name": "TrACy BUrke",
    "age": 76,
    "gender": "Male",
    "blood_type": "A+",
    "medical_condition": "Obesity",
    "date_of_admission": "2020-12-05",
    "doctor": "Emily Thomas",
    "hospital": "Wilkins Group",
    "insurance_provider": "Medicare",
    "billing_amount": 5714.748017914666,
    "room_number": 238,
    "admission_type": "Elective",
    "discharge_date": "2020-12-04",
    "medication": "Lipitor",
    "test_results": "Abnormal"
  }
]
```

## Supervisor Narrative
**Data Quality Report for `healthcare_dataset`**

**Overall Verdict: 🔴 Red**

The data quality run indicates a critical issue within the `healthcare_dataset` table, requiring immediate attention.

**Top Critical/High Issues:**

*   **Critical:** The `discharge_before_admission_date` test failed with 555 issues. This indicates that for a significant number of records, the patient's discharge date is recorded *before* their admission date, which is a logical impossibility and severely impacts the reliability of duration-of-stay calculations and overall patient timeline integrity.

**Test Coverage Notes:**

*   Two data quality tests were executed.
*   The test for `invalid_date_format` passed, indicating that the date columns (`date_of_admission`, `discharge_date`) generally adhere to a recognizable date format.
*   However, the `discharge_before_admission_date` test failed, highlighting a critical logical inconsistency despite the format being correct.

**Suggested Production Guardrails:**

To prevent similar issues from entering production data in the future, the following SQL checks should be implemented and scheduled to run before each data load into the `healthcare_dataset` table:

1.  **Prevent discharge date before admission date:**
    ```sql
    -- SQL Check to ensure discharge_date is not before date_of_admission
    SELECT COUNT(*)
    FROM healthcare_dataset
    WHERE
      date_of_admission IS NOT NULL AND discharge_date IS NOT NULL
      AND julianday(discharge_date) < julianday(date_of_admission);
    -- This query should return 0 issues. If > 0, the load should be blocked.
    ```
