# Data Quality Report - dq-manual-complex-p50-flash-20260320T054229Z

Generated at: 2026-03-20 05:43:15 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P50-FLASH`
- Event log: `runs/dq-manual-complex-p50-flash-20260320T054229Z.jsonl`

## Coverage Breakdown
| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 2 |
| Medium | 0 |
| Low | 0 |

## Top Findings
| Severity | Status | Table | Test | Issue Count |
|---|---|---|---|---:|
| HIGH | FAIL | healthcare_dataset | admission_discharge_date_consistency | 555 |
| HIGH | FAIL | healthcare_dataset | billing_amount_non_negative | 108 |

## Detailed Findings
### 1. [HIGH/FAIL] admission_discharge_date_consistency (healthcare_dataset)
- Why this matters: The discharge date must logically be on or after the admission date. If the discharge date precedes the admission date, it indicates a critical data entry error that can impact patient stay calculations, billing, and reporting accuracy.
- Issue count: **555**
- Output truncated: **yes**

```sql
SELECT *
FROM healthcare_dataset
WHERE julianday(discharge_date) < julianday(date_of_admission);
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

### 2. [HIGH/FAIL] billing_amount_non_negative (healthcare_dataset)
- Why this matters: Billing amounts are expected to be positive values, representing a cost or charge. A negative or zero billing amount indicates a data entry error, a processing error, or an unaccounted adjustment, leading to incorrect financial records and potential revenue loss.
- Issue count: **108**
- Output truncated: **no**

```sql
SELECT *
FROM healthcare_dataset
WHERE billing_amount <= 0;
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

## Supervisor Narrative
**Data Quality Report: healthcare_dataset**

**Overall Verdict:** Red

**Top Critical/High Issues:**
*   **`admission_discharge_date_consistency` (High severity):** Found 555 rows where the discharge date is before the admission date, indicating critical data entry errors. This can severely impact patient stay calculations, billing, and reporting accuracy.
*   **`billing_amount_non_negative` (High severity):** Found 108 rows where the billing amount is zero or negative, indicating incorrect financial records and potential revenue discrepancies.

**Test Coverage Notes:**
Two critical data quality checks were executed on the `healthcare_dataset` table. These tests specifically targeted the logical consistency of `date_of_admission` and `discharge_date`, and the numerical validity of `billing_amount`. Both tests identified a substantial number of issues, highlighting significant data integrity problems within the dataset.

**Suggested Production Guardrails (SQL checks to schedule each load):**
To mitigate these recurring critical data quality issues, the following SQL checks should be implemented and scheduled to run automatically with every data load into the `healthcare_dataset` table:

1.  **Admission and Discharge Date Consistency:**
    ```sql
    SELECT *
    FROM healthcare_dataset
    WHERE julianday(discharge_date) < julianday(date_of_admission);
    ```
    This guardrail ensures that for every record, the discharge date is not earlier than the admission date, preventing illogical patient stay durations.

2.  **Billing Amount Non-Negative Validation:**
    ```sql
    SELECT *
    FROM healthcare_dataset
    WHERE billing_amount <= 0;
    ```
    This guardrail will identify any records where the billing amount is zero or negative, safeguarding financial data integrity.
