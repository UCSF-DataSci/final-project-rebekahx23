# Data Quality Report - dq-manual-complex-p20-flash-20260320T054124Z

Generated at: 2026-03-20 05:42:16 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P20-FLASH`
- Event log: `runs/dq-manual-complex-p20-flash-20260320T054124Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | healthcare_dataset_billing_amount_non_negative | 108 |
| HIGH | FAIL | healthcare_dataset | healthcare_dataset_discharge_date_after_admission_date | 555 |

## Detailed Findings
### 1. [CRITICAL/FAIL] healthcare_dataset_billing_amount_non_negative (healthcare_dataset)
- Why this matters: Billing amounts should always be non-negative. A negative billing amount indicates a significant data entry error or corruption, directly impacting financial accuracy and reporting.
- Issue count: **108**
- Output truncated: **no**

```sql
SELECT * FROM healthcare_dataset WHERE billing_amount < 0;
```

Example rows:
```json
[
  {
    "name": "ashLEy ERIcKSoN",
    "age": 32,
    "gender": "Female",
    "blood_type": "AB-",
    "medical_condition": "Cancer",
    "date_of_admission": "2019-11-05",
    "doctor": "Gerald Hooper",
    "hospital": "and Johnson Moore, Branch",
    "insurance_provider": "Aetna",
    "billing_amount": -502.50781270094785,
    "room_number": 376,
    "admission_type": "Urgent",
    "discharge_date": "2019-11-23",
    "medication": "Penicillin",
    "test_results": "Normal"
  },
  {
    "name": "CHRisTOPHer wEiss",
    "age": 49,
    "gender": "Female",
    "blood_type": "AB-",
    "medical_condition": "Asthma",
    "date_of_admission": "2023-02-16",
    "doctor": "Kelly Thompson",
    "hospital": "Hunter-Hughes",
    "insurance_provider": "Aetna",
    "billing_amount": -1018.2453712282881,
    "room_number": 204,
    "admission_type": "Elective",
    "discharge_date": "2023-03-09",
    "medication": "Penicillin",
    "test_results": "Inconclusive"
  },
  {
    "name": "AsHley WaRnER",
    "age": 60,
    "gender": "Male",
    "blood_type": "A+",
    "medical_condition": "Hypertension",
    "date_of_admission": "2021-12-21",
    "doctor": "Andrea Bentley",
    "hospital": "and Wagner, Lee Klein",
    "insurance_provider": "Aetna",
    "billing_amount": -306.3649251412676,
    "room_number": 426,
    "admission_type": "Elective",
    "discharge_date": "2022-01-11",
    "medication": "Ibuprofen",
    "test_results": "Normal"
  }
]
```

### 2. [HIGH/FAIL] healthcare_dataset_discharge_date_after_admission_date (healthcare_dataset)
- Why this matters: Logically, a patient's discharge date must be on or after their admission date. A discharge date preceding the admission date indicates a critical data entry error, leading to incorrect patient stay durations and operational reporting. The `julianday` function is used for robust date comparison in SQLite.
- Issue count: **555**
- Output truncated: **yes**

```sql
SELECT * FROM healthcare_dataset WHERE julianday(discharge_date) < julianday(date_of_admission);
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
**Data Quality Report**

**Overall Verdict: Red**
All 2 executed tests failed, indicating significant data quality issues.

**Top Critical/High Issues:**

*   **Critical**: 108 instances of non-negative billing amounts were found in the `healthcare_dataset` table. This is a critical financial data integrity issue.
*   **High**: 555 instances were identified where the `discharge_date` in the `healthcare_dataset` table precedes the `date_of_admission`. This is a high-severity issue affecting the logical consistency of patient stay durations.

**Test Coverage Notes:**
Two targeted data quality tests were executed on the `healthcare_dataset` table. These tests specifically focused on validating the non-negativity of billing amounts and ensuring the logical sequence of admission and discharge dates. Both tests failed, highlighting significant inconsistencies in the dataset.

**Suggested Production Guardrails (SQL checks to schedule each load):**

1.  **Billing Amount Non-Negative Check**:
    ```sql
    SELECT * FROM healthcare_dataset WHERE billing_amount < 0;
    ```
    This check ensures that all billing amounts are positive, preventing erroneous financial calculations.
2.  **Discharge Date After Admission Date Check**:
    ```sql
    SELECT * FROM healthcare_dataset WHERE julianday(discharge_date) < julianday(date_of_admission);
    ```
    This check verifies that a patient's discharge date never occurs before their admission date, maintaining the temporal integrity of patient records.
