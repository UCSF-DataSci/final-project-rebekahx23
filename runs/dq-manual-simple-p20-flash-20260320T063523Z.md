# Data Quality Report - dq-manual-simple-p20-flash-20260320T063523Z

Generated at: 2026-03-20 06:36:12 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P20-FLASH`
- Event log: `runs/dq-manual-simple-p20-flash-20260320T063523Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | discharge_date_before_admission_date | 1131 |
| HIGH | FAIL | healthcare_dataset | patient_name_is_null | 1122 |

## Detailed Findings
### 1. [CRITICAL/FAIL] discharge_date_before_admission_date (healthcare_dataset)
- Why this matters: The discharge date cannot logically occur before the admission date. This indicates a severe data entry or processing error, making the patient record inconsistent and potentially unusable for chronological analysis or billing.
- Issue count: **1131**
- Output truncated: **yes**

```sql
SELECT name, date_of_admission, discharge_date, hospital
FROM healthcare_dataset
WHERE date_of_admission IS NOT NULL
  AND discharge_date IS NOT NULL
  AND julianday(discharge_date) < julianday(date_of_admission);
```

Example rows:
```json
[
  {
    "name": "jOhN hARTmAN",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2023-01-27",
    "hospital": "Bullock-Ramsey"
  },
  {
    "name": "wILLIAM hIlL",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2023-06-01",
    "hospital": "Lindsey Inc"
  },
  {
    "name": "DR. LaUreN ClaRk DDs",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2020-11-17",
    "hospital": "PLC Jimenez"
  }
]
```

### 2. [HIGH/FAIL] patient_name_is_null (healthcare_dataset)
- Why this matters: The 'name' column is critical for patient identification. A null value in this field means the patient record is incomplete and cannot be properly associated with an individual, leading to significant operational and reporting issues.
- Issue count: **1122**
- Output truncated: **yes**

```sql
SELECT *
FROM healthcare_dataset
WHERE name IS NULL;
```

Example rows:
```json
[
  {
    "name": null,
    "age": 23,
    "gender": "Male",
    "blood_type": "O-",
    "medical_condition": "Hypertension",
    "date_of_admission": "2022-09-21",
    "doctor": "Mrs. Lori Hurst PhD",
    "hospital": "Hall-Bentley",
    "insurance_provider": "Aetna",
    "billing_amount": 37951.66490984979,
    "room_number": 405,
    "admission_type": "Emergency",
    "discharge_date": "2022-09-25",
    "medication": "Ibuprofen",
    "test_results": "Inconclusive"
  },
  {
    "name": null,
    "age": 37,
    "gender": "Female",
    "blood_type": "O+",
    "medical_condition": "Asthma",
    "date_of_admission": "2019-12-02",
    "doctor": "Steven Adams",
    "hospital": "Group White",
    "insurance_provider": "Aetna",
    "billing_amount": 8521.214252671094,
    "room_number": 476,
    "admission_type": "Elective",
    "discharge_date": "2019-12-13",
    "medication": "Penicillin",
    "test_results": "Abnormal"
  },
  {
    "name": null,
    "age": 65,
    "gender": "Male",
    "blood_type": "B-",
    "medical_condition": "Asthma",
    "date_of_admission": "2020-02-20",
    "doctor": "Shane Morris",
    "hospital": "Gonzalez-King",
    "insurance_provider": "Aetna",
    "billing_amount": 49321.15763149177,
    "room_number": 167,
    "admission_type": "Emergency",
    "discharge_date": "2020-03-01",
    "medication": "Penicillin",
    "test_results": "Abnormal"
  }
]
```

## Supervisor Narrative
**Data Quality Report for `healthcare_dataset`**

**Overall Verdict: Red** 🔴

This verdict is issued because both of the planned data quality tests failed, identifying a significant number of critical and high-severity issues. Immediate attention is required to address these data integrity problems.

**Top Critical and High Issues:**

*   **Critical: `discharge_date_before_admission_date`**
    *   **Description:** This test identified **1131 records** in the `healthcare_dataset` table where the `discharge_date` occurs *before* the `date_of_admission`. This is a severe logical inconsistency, making these patient records unreliable for chronological analysis, billing, or any time-sensitive operations.
    *   **Impact:** Leads to incorrect reporting, potential billing errors, and undermines trust in the dataset's accuracy.

*   **High: `patient_name_is_null`**
    *   **Description:** This test found **1122 records** in the `healthcare_dataset` table where the `name` column is `NULL`. The patient name is a crucial identifier, and its absence makes these records incomplete and difficult to use for patient management or identification.
    *   **Impact:** Significant operational and reporting issues due to unidentified patient records.

**Test Coverage Notes:**

2 out of 2 planned data quality tests were executed, indicating 100% coverage of the defined checks. Both executed tests revealed failures, highlighting existing data quality deficiencies in the `healthcare_dataset` table.

**Suggested Production Guardrails (SQL checks to schedule with each data load):**

To prevent these issues from recurring, the following SQL checks should be implemented as guardrails and scheduled to run with every data load into the `healthcare_dataset` table:

1.  **Prevent discharge date before admission date:**
    ```sql
    SELECT name, date_of_admission, discharge_date, hospital
    FROM healthcare_dataset
    WHERE date_of_admission IS NOT NULL
      AND discharge_date IS NOT NULL
      AND julianday(discharge_date) < julianday(date_of_admission);
    ```
    *   **Action:** Records failing this check should be quarantined or flagged for immediate review and correction. Data loading should ideally be blocked if critical issues like this are detected.

2.  **Ensure patient name is not null:**
    ```sql
    SELECT *
    FROM healthcare_dataset
    WHERE name IS NULL;
    ```
    *   **Action:** Records with null names should trigger an alert and be moved to a staging area for manual enrichment, or the load process should prevent such records from entering the main table.

Addressing these findings promptly and implementing the suggested guardrails will significantly improve the data quality and reliability of the `healthcare_dataset` table.
