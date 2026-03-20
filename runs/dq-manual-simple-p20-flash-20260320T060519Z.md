# Data Quality Report - dq-manual-simple-p20-flash-20260320T060519Z

Generated at: 2026-03-20 06:05:43 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P20-FLASH`
- Event log: `runs/dq-manual-simple-p20-flash-20260320T060519Z.jsonl`

## Coverage Breakdown
| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 1 |
| Medium | 1 |
| Low | 0 |

## Top Findings
| Severity | Status | Table | Test | Issue Count |
|---|---|---|---|---:|
| HIGH | FAIL | healthcare_dataset | invalid_age_outliers | 1139 |
| MEDIUM | FAIL | healthcare_dataset | missing_patient_names | 1127 |

## Detailed Findings
### 1. [HIGH/FAIL] invalid_age_outliers (healthcare_dataset)
- Why this matters: The age column contains values that are biologically impossible (e.g., > 120), indicating data entry errors that invalidate age-based analysis.
- Issue count: **1139**
- Output truncated: **yes**

```sql
SELECT * 
FROM healthcare_dataset 
WHERE age < 0 OR age > 120;
```

Example rows:
```json
[
  {
    "name": "ChRISTopher BerG",
    "age": 39000,
    "gender": "Female",
    "blood_type": "AB-",
    "medical_condition": "Cancer",
    "date_of_admission": "2099-12-31",
    "doctor": "Heather Day",
    "hospital": "Padilla-Walker",
    "insurance_provider": "UnitedHealthcare",
    "billing_amount": 19784.63106221073,
    "room_number": 249,
    "admission_type": "Elective",
    "discharge_date": "2021-06-22",
    "medication": "Paracetamol",
    "test_results": "Inconclusive"
  },
  {
    "name": "aaRon MARtiNeZ",
    "age": 29000,
    "gender": "Female",
    "blood_type": "A-",
    "medical_condition": "Hypertension",
    "date_of_admission": "2023-08-13",
    "doctor": "Douglas Mayo",
    "hospital": "Lyons-Blair",
    "insurance_provider": "Medicare",
    "billing_amount": 7999.586879604188,
    "room_number": 288,
    "admission_type": "Urgent",
    "discharge_date": "2023-09-05",
    "medication": "Lipitor",
    "test_results": "Inconclusive"
  },
  {
    "name": "NicOlE RodriGUEz",
    "age": 25000,
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
  }
]
```

### 2. [MEDIUM/FAIL] missing_patient_names (healthcare_dataset)
- Why this matters: Missing values in the 'name' column prevent accurate patient identification and tracking across medical records.
- Issue count: **1127**
- Output truncated: **yes**

```sql
SELECT * 
FROM healthcare_dataset 
WHERE name IS NULL OR TRIM(name) = '';
```

Example rows:
```json
[
  {
    "name": null,
    "age": 49,
    "gender": "Female",
    "blood_type": "A-",
    "medical_condition": "Asthma",
    "date_of_admission": "2022-06-24",
    "doctor": "Matthew Thomas",
    "hospital": "and Howell Brooks, Rogers",
    "insurance_provider": "Cigna",
    "billing_amount": 25966.328610220968,
    "room_number": 418,
    "admission_type": "Elective",
    "discharge_date": "2022-07-18",
    "medication": "Paracetamol",
    "test_results": "Normal"
  },
  {
    "name": null,
    "age": 20,
    "gender": "Male",
    "blood_type": "B+",
    "medical_condition": "Hypertension",
    "date_of_admission": "2099-12-31",
    "doctor": "Tracey Spence",
    "hospital": "Lewis Livingston, Lowe and",
    "insurance_provider": "Blue Cross",
    "billing_amount": 10663.910005038557,
    "room_number": 104,
    "admission_type": "Emergency",
    "discharge_date": "2019-10-16",
    "medication": "Aspirin",
    "test_results": "Normal"
  },
  {
    "name": null,
    "age": 81,
    "gender": "Male",
    "blood_type": "B+",
    "medical_condition": "Hypertension",
    "date_of_admission": "2021-10-25",
    "doctor": "Elizabeth Morales",
    "hospital": "and Smith, Tucker Cross",
    "insurance_provider": "UnitedHealthcare",
    "billing_amount": 46377.86514923159,
    "room_number": 275,
    "admission_type": "Urgent",
    "discharge_date": "2021-11-22",
    "medication": "Lipitor",
    "test_results": "Normal"
  }
]
```

## Supervisor Narrative
The data quality assessment of the `healthcare_dataset` is complete. Both planned tests identified significant data quality issues.

### Overall Verdict: RED
The dataset contains critical integrity issues that render it unreliable for primary analysis. Immediate action is required to sanitize the data and patch the ingestion pipeline.

### Top Critical Issues
1.  **High Severity: `invalid_age_outliers` (Fail)**: 1,139 records feature biologically impossible ages (e.g., 23,500, 51,500), indicating a critical breakdown in data entry or transformation logic.
2.  **Medium Severity: `missing_patient_names` (Fail)**: 1,127 records are missing `name` values, severely impacting patient identity management and longitudinal tracking.

### Test Coverage Notes
*   Tests focused on primary identifiers and core demographic integrity (age).
*   Coverage is sufficient to flag the current state of degradation but highlights a need for broader validation (e.g., date of birth vs. admission date checks, billing amount validation).

### Suggested Production Guardrails (SQL Checks)
To be implemented as blocking checks in the ETL pipeline before committing data:

1.  **Age Validation:**
    ```sql
    -- Reject or flag rows where age is out of expected medical range
    SELECT COUNT(*) FROM healthcare_dataset WHERE age < 0 OR age > 120;
    ```
2.  **Completeness Validation:**
    ```sql
    -- Reject or flag rows where critical identifiers are missing
    SELECT COUNT(*) FROM healthcare_dataset WHERE name IS NULL OR TRIM(name) = '';
    ```
3.  **Cross-Field Logic (Suggested):**
    ```sql
    -- Flag records where admission date is logically inconsistent
    SELECT COUNT(*) FROM healthcare_dataset WHERE discharge_date < date_of_admission;
    ```

**Recommendation:** Halt downstream consumption of this dataset until the root cause of these anomalies is identified and mitigated.
