# Data Quality Report - dq-manual-simple-p10-pro-20260320T050147Z

Generated at: 2026-03-20 05:03:07 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P10-PRO`
- Event log: `runs/dq-manual-simple-p10-pro-20260320T050147Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | unrealistic_patient_age | 1129 |
| HIGH | FAIL | healthcare_dataset | missing_patient_name | 1141 |

## Detailed Findings
### 1. [CRITICAL/FAIL] unrealistic_patient_age (healthcare_dataset)
- Why this matters: The profiler identified at least one age value of '30000', which is not a valid human age. This test checks for any ages outside the reasonable range of 0 to 120 to catch data entry errors or corruption.
- Issue count: **1129**
- Output truncated: **yes**

```sql
SELECT * FROM healthcare_dataset WHERE age < 0 OR age > 120;
```

Example rows:
```json
[
  {
    "name": "EMILY JOHNSOn",
    "age": 28000,
    "gender": "Male",
    "blood_type": "A+",
    "medical_condition": "Asthma",
    "date_of_admission": "2023-12-20",
    "doctor": "Taylor Newton",
    "hospital": "Nunez-Humphrey",
    "insurance_provider": "UnitedHealthcare",
    "billing_amount": 48145.11095104189,
    "room_number": 389,
    "admission_type": "Urgent",
    "discharge_date": "2023-12-24",
    "medication": "Ibuprofen",
    "test_results": "Normal"
  },
  {
    "name": "dANIEL schmIdt",
    "age": 41500,
    "gender": "Male",
    "blood_type": "B+",
    "medical_condition": "Asthma",
    "date_of_admission": "2022-11-15",
    "doctor": "Denise Galloway",
    "hospital": "Hammond Ltd",
    "insurance_provider": "Cigna",
    "billing_amount": 23762.203579059587,
    "room_number": 465,
    "admission_type": "Elective",
    "discharge_date": "2022-11-22",
    "medication": "Penicillin",
    "test_results": "Normal"
  },
  {
    "name": "ChAd MorEnO",
    "age": 43500,
    "gender": "Male",
    "blood_type": "AB+",
    "medical_condition": "Hypertension",
    "date_of_admission": "2020-08-26",
    "doctor": "Connie Boyd",
    "hospital": "Inc Skinner",
    "insurance_provider": "Aetna",
    "billing_amount": 46814.011195111656,
    "room_number": 134,
    "admission_type": "Urgent",
    "discharge_date": "2020-08-27",
    "medication": "Penicillin",
    "test_results": "Abnormal"
  }
]
```

### 2. [HIGH/FAIL] missing_patient_name (healthcare_dataset)
- Why this matters: The 'name' column serves as a key patient identifier. The profiler noted the presence of null values, which can compromise record linkage and patient identification. This test identifies all records where the patient name is missing.
- Issue count: **1141**
- Output truncated: **yes**

```sql
SELECT * FROM healthcare_dataset WHERE name IS NULL;
```

Example rows:
```json
[
  {
    "name": null,
    "age": 48,
    "gender": "Male",
    "blood_type": "B+",
    "medical_condition": "Asthma",
    "date_of_admission": "2020-01-21",
    "doctor": "Gregory Smith",
    "hospital": "Williams-Davis",
    "insurance_provider": "Aetna",
    "billing_amount": 17695.911622343818,
    "room_number": 295,
    "admission_type": "Urgent",
    "discharge_date": "2020-02-09",
    "medication": "Lipitor",
    "test_results": "Normal"
  },
  {
    "name": null,
    "age": 30,
    "gender": "Female",
    "blood_type": "AB+",
    "medical_condition": "Diabetes",
    "date_of_admission": "2020-01-17",
    "doctor": "Lynn Young",
    "hospital": "Poole Inc",
    "insurance_provider": "Blue Cross",
    "billing_amount": 8408.94935429195,
    "room_number": 285,
    "admission_type": "Emergency",
    "discharge_date": "2020-02-10",
    "medication": "Lipitor",
    "test_results": "Normal"
  },
  {
    "name": null,
    "age": 58,
    "gender": "Male",
    "blood_type": "A-",
    "medical_condition": "Hypertension",
    "date_of_admission": "2020-05-08",
    "doctor": "Jennifer Larson",
    "hospital": "Khan, and Rodriguez Fischer",
    "insurance_provider": "Medicare",
    "billing_amount": 19183.168885395542,
    "room_number": 378,
    "admission_type": "Emergency",
    "discharge_date": "2020-06-01",
    "medication": "Aspirin",
    "test_results": "Abnormal"
  }
]
```

## Supervisor Narrative
**Data Quality Run Summary**

**Overall Verdict:** RED

This data quality run resulted in a RED verdict due to multiple critical and high-severity failures. Immediate attention is required to address these significant data issues.

**Top Critical/High Issues:**

*   **`unrealistic_patient_age` (Critical):** A critical failure was detected with 1129 records showing patient ages outside the acceptable range of 0-120 years. This indicates a severe systemic issue with data entry or data processing that fundamentally corrupts patient records.
*   **`missing_patient_name` (High):** A high-severity failure was found in 1141 records where the patient's name is missing. This compromises the usability of the data for any patient-centric analysis or operations.

**Test Coverage Notes:**

*   The executed tests covered the most urgent issues identified during the initial data profiling.
*   However, several other potential issues were identified by the profiler but were not included in this test run. These include:
    *   Inconsistent capitalization and formatting in the `name` column.
    *   Dates stored as `TEXT`, which could lead to incorrect sorting and filtering.
    *   Trailing characters in the `hospital` column.
*   It is recommended to expand test coverage in subsequent runs to include these additional data quality dimensions.

**Suggested Production Guardrails:**

To prevent these data quality issues from recurring in future data loads, the following SQL checks should be implemented as production guardrails:

*   **Check for unrealistic patient ages:**
    ```sql
    SELECT * FROM healthcare_dataset WHERE age < 0 OR age > 120;
    ```
*   **Check for missing patient names:**
    ```sql
    SELECT * FROM healthcare_dataset WHERE name IS NULL;
    ```
These checks should be run on every new batch of data before it is loaded into the production environment. Any data that fails these checks should be quarantined for review.
