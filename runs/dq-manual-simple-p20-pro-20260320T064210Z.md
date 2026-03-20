# Data Quality Report - dq-manual-simple-p20-pro-20260320T064210Z

Generated at: 2026-03-20 06:43:34 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P20-PRO`
- Event log: `runs/dq-manual-simple-p20-pro-20260320T064210Z.jsonl`

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
| HIGH | FAIL | healthcare_dataset | discharge_before_admission | 1131 |

## Detailed Findings
### 1. [CRITICAL/FAIL] unrealistic_age (healthcare_dataset)
- Why this matters: Based on the profile, at least one age value (29500) is impossibly high. This test identifies patients with ages outside a plausible human lifespan (e.g., 0-120) to flag extreme outliers and potential data entry errors.
- Issue count: **1135**
- Output truncated: **yes**

```sql
SELECT
      *
    FROM
      healthcare_dataset
    WHERE
      age < 0 OR age > 120;
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

### 2. [HIGH/FAIL] discharge_before_admission (healthcare_dataset)
- Why this matters: The profile indicates both admission and discharge dates are stored as text but in a sortable format. A patient's discharge date must logically be on or after their admission date. This test identifies records where this fundamental chronological order is violated, which could indicate data entry errors.
- Issue count: **1131**
- Output truncated: **yes**

```sql
SELECT
      *
    FROM
      healthcare_dataset
    WHERE
      julianday(discharge_date) < julianday(date_of_admission);
```

Example rows:
```json
[
  {
    "name": "jOhN hARTmAN",
    "age": 27,
    "gender": "Male",
    "blood_type": "B-",
    "medical_condition": "Hypertension",
    "date_of_admission": "2099-12-31",
    "doctor": "Jack Jackson",
    "hospital": "Bullock-Ramsey",
    "insurance_provider": "Cigna",
    "billing_amount": 49402.29837252711,
    "room_number": 263,
    "admission_type": "Elective",
    "discharge_date": "2023-01-27",
    "medication": "Lipitor",
    "test_results": "Inconclusive"
  },
  {
    "name": "HunTeR mckAy",
    "age": 85,
    "gender": "Male",
    "blood_type": "A-",
    "medical_condition": "Arthritis",
    "date_of_admission": "2099-12-31",
    "doctor": "Dominic Mitchell",
    "hospital": "Newton-White",
    "insurance_provider": "UnitedHealthcare",
    "billing_amount": 40014.7623484579,
    "room_number": 425,
    "admission_type": "Emergency",
    "discharge_date": "2021-06-03",
    "medication": "Aspirin",
    "test_results": "Abnormal"
  },
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
  }
]
```

## Supervisor Narrative
**Overall Verdict: RED**

This is a **red** quality run. Both tests failed, revealing significant, systemic data integrity issues that must be addressed before this data can be considered reliable.

### Top Issues Found

1.  **Critical: `unrealistic_age`**
    - **Finding:** 1,135 patient records have ages outside the plausible human range of 0-120 years.
    - **Impact:** This points to severe data entry or processing errors. Age is a fundamental field for almost any analysis, and these widespread errors make demographic-based queries untrustworthy.

2.  **High: `discharge_before_admission`**
    - **Finding:** 1,131 records show a discharge date that is earlier than the admission date, which is logically impossible.
    - **Impact:** This fundamental chronological error invalidates any analysis related to length of stay, treatment timelines, or billing cycles for the affected records.

### Test Coverage Notes

- **Covered:** The two most severe issues identified during profiling—impossible age values and chronological inconsistencies in admission/discharge dates—were tested and confirmed to be widespread problems.
- **Not Covered:** The initial data profile also noted cosmetic and formatting issues in text-based fields like `name` and `hospital`. While less critical than the logical errors found, these inconsistencies can still hinder record matching and analytics. These should be addressed in a subsequent data cleaning effort.

### Suggested Production Guardrails

To prevent these issues in future data loads, the following SQL checks should be integrated into your data pipeline. A non-zero count from either query should halt the pipeline or trigger an immediate alert.

1.  **Check for Unrealistic Ages:**
    ```sql
    SELECT COUNT(*)
    FROM healthcare_dataset
    WHERE age < 0 OR age > 120;
    ```

2.  **Check for Discharge Before Admission:**
    ```sql
    SELECT COUNT(*)
    FROM healthcare_dataset
    WHERE julianday(discharge_date) < julianday(date_of_admission);
    ```
