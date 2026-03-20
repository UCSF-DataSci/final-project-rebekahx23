# Data Quality Report - dq-manual-simple-p10-flash-20260320T045820Z

Generated at: 2026-03-20 04:59:06 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P10-FLASH`
- Event log: `runs/dq-manual-simple-p10-flash-20260320T045820Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | age_out_of_realistic_range | 1129 |
| HIGH | FAIL | healthcare_dataset | patient_name_is_null_or_empty | 1141 |

## Detailed Findings
### 1. [CRITICAL/FAIL] age_out_of_realistic_range (healthcare_dataset)
- Why this matters: An age value of 23000 was observed, which is clearly erroneous and represents an impossible human age. This test identifies records where the 'age' column falls outside a realistic human age range (e.g., 0 to 120 years), indicating critical data entry errors that could severely impact analysis and patient care decisions.
- Issue count: **1129**
- Output truncated: **yes**

```sql
SELECT * FROM healthcare_dataset WHERE age IS NOT NULL AND (age < 0 OR age > 120);
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

### 2. [HIGH/FAIL] patient_name_is_null_or_empty (healthcare_dataset)
- Why this matters: The 'name' column was observed to contain NULL values. A patient's name is a critical identifier for record linkage, accurate communication, and proper patient management. Missing or empty patient names significantly hinder data usability and integrity in a healthcare context.
- Issue count: **1141**
- Output truncated: **yes**

```sql
SELECT * FROM healthcare_dataset WHERE name IS NULL OR TRIM(name) = '';
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
Overall Verdict: Red 🔴

**Top Critical and High Issues:**

*   **Critical:** `age_out_of_realistic_range`
    *   **Description:** Impossible age values detected in the `age` column (e.g., 23000 years).
    *   **Issues Found:** 1129
*   **High:** `patient_name_is_null_or_empty`
    *   **Description:** Missing or empty patient names found in the `name` column.
    *   **Issues Found:** 1141

**Test Coverage Notes:**
A targeted set of 2 data quality tests were executed, focusing on critical issues identified during profiling. Specifically, the tests covered the realistic range of patient ages and the presence of patient names. While important, this run did not include tests for other potential data quality issues such as inconsistent name formatting (e.g., mixed casing, prefixes like "DR."), or nullability checks on other potentially critical fields beyond the patient name, which were noted in the initial profile summary. All columns are defined as nullable in the schema, indicating broader null checks could be beneficial in future runs.

**Suggested Production Guardrails (SQL checks to schedule for each load):**

To prevent these critical and high-risk data quality issues from recurring in future data loads, the following SQL checks should be implemented as automated guardrails:

1.  **Age out of realistic range check:**
    ```sql
    SELECT * FROM healthcare_dataset WHERE age IS NOT NULL AND (age < 0 OR age > 120);
    ```
    *   *Purpose:* Ensures that all patient ages fall within a realistic human lifespan.

2.  **Patient name null or empty check:**
    ```sql
    SELECT * FROM healthcare_dataset WHERE name IS NULL OR TRIM(name) = '';
    ```
    *   *Purpose:* Verifies that the `name` column contains a non-null and non-empty value, which is crucial for patient identification.
