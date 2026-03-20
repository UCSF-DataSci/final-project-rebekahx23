# Data Quality Report - dq-manual-simple-p10-flash-20260320T060442Z

Generated at: 2026-03-20 06:05:07 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P10-FLASH`
- Event log: `runs/dq-manual-simple-p10-flash-20260320T060442Z.jsonl`

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
| HIGH | FAIL | healthcare_dataset | invalid_date_format_check | 1135 |
| MEDIUM | FAIL | healthcare_dataset | hospital_naming_clutter_check | 27506 |

## Detailed Findings
### 1. [HIGH/FAIL] invalid_date_format_check (healthcare_dataset)
- Why this matters: The admission and discharge dates are stored as TEXT. This query identifies rows where the date fields do not conform to the required YYYY-MM-DD format (missing leading zeros for months/days or improper length) or represent invalid calendar dates.
- Issue count: **1135**
- Output truncated: **yes**

```sql
SELECT * 
FROM healthcare_dataset 
WHERE date_of_admission NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
   OR discharge_date NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
   OR date(date_of_admission) IS NULL
   OR date(discharge_date) IS NULL
   OR julianday(discharge_date) < julianday(date_of_admission);
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
    "name": "bRADlEY coMbS",
    "age": 52,
    "gender": "Male",
    "blood_type": "AB-",
    "medical_condition": "Hypertension",
    "date_of_admission": "2099-12-31",
    "doctor": "Christopher Butler",
    "hospital": "Stout-Brown",
    "insurance_provider": "Cigna",
    "billing_amount": 37734.74218038699,
    "room_number": 251,
    "admission_type": "Elective",
    "discharge_date": "2021-06-06",
    "medication": "Penicillin",
    "test_results": "Abnormal"
  },
  {
    "name": "JAMEs Ross",
    "age": 83,
    "gender": "Female",
    "blood_type": "A+",
    "medical_condition": "Diabetes",
    "date_of_admission": "2099-12-31",
    "doctor": "Michael Baker",
    "hospital": "Cox-Hester",
    "insurance_provider": "Blue Cross",
    "billing_amount": 10352.20848674086,
    "room_number": 394,
    "admission_type": "Urgent",
    "discharge_date": "2024-01-22",
    "medication": "Aspirin",
    "test_results": "Abnormal"
  }
]
```

### 2. [MEDIUM/FAIL] hospital_naming_clutter_check (healthcare_dataset)
- Why this matters: Hospital names contain noise such as "and", "Inc", "LLC", or stray commas. This test flags records containing these patterns, which prevents accurate entity resolution and categorical grouping of hospitals.
- Issue count: **27506**
- Output truncated: **yes**

```sql
SELECT * 
FROM healthcare_dataset 
WHERE LOWER(hospital) LIKE '%and %'
   OR LOWER(hospital) LIKE '%inc%'
   OR LOWER(hospital) LIKE '%llc%'
   OR hospital LIKE '%,%'
   OR hospital LIKE 'and %'
   OR hospital LIKE '%,';
```

Example rows:
```json
[
  {
    "name": "Bobby JacksOn",
    "age": 30,
    "gender": "Male",
    "blood_type": "B-",
    "medical_condition": "Cancer",
    "date_of_admission": "2024-01-31",
    "doctor": "Matthew Smith",
    "hospital": "Sons and Miller",
    "insurance_provider": "Blue Cross",
    "billing_amount": 18856.281305978155,
    "room_number": 328,
    "admission_type": "Urgent",
    "discharge_date": "2024-02-02",
    "medication": "Paracetamol",
    "test_results": "Normal"
  },
  {
    "name": "LesLie TErRy",
    "age": 62,
    "gender": "Male",
    "blood_type": "A+",
    "medical_condition": "Obesity",
    "date_of_admission": "2019-08-20",
    "doctor": "Samantha Davies",
    "hospital": "Kim Inc",
    "insurance_provider": "Medicare",
    "billing_amount": 33643.327286577885,
    "room_number": 265,
    "admission_type": "Emergency",
    "discharge_date": "2019-08-26",
    "medication": "Ibuprofen",
    "test_results": "Inconclusive"
  },
  {
    "name": "andrEw waTtS",
    "age": 28,
    "gender": "Female",
    "blood_type": "O+",
    "medical_condition": "Diabetes",
    "date_of_admission": "2020-11-18",
    "doctor": "Kevin Wells",
    "hospital": "Hernandez Rogers and Vang,",
    "insurance_provider": "Medicare",
    "billing_amount": 37909.78240987528,
    "room_number": 450,
    "admission_type": "Elective",
    "discharge_date": "2020-12-18",
    "medication": "Ibuprofen",
    "test_results": "Abnormal"
  }
]
```

## Supervisor Narrative
### Data Quality Execution Summary: `healthcare_dataset`

**Overall Verdict:** RED (Significant data integrity issues requiring remediation)

#### Critical/High Issues
*   **Temporal Data Corruption:** The `invalid_date_format_check` (High Severity) flagged 1,135 records. A major discovery is the prevalence of the sentinel date `2099-12-31` in the `date_of_admission` field. This indicates a system-level default that renders temporal analysis unreliable for this subset of data.
*   **Entity Resolution Obstacles:** The `hospital_naming_clutter_check` (Medium Severity) flagged 27,506 records. The dataset contains inconsistent, non-normalized hospital names containing noise (e.g., 'and', 'Inc', 'LLC', trailing punctuation), making accurate grouping and master data management impossible without a robust normalization pipeline.

#### Test Coverage Notes
*   **Coverage:** Current tests cover foundational integrity (date validity) and categorical cleanup (hospital naming).
*   **Limitations:** Further analysis is required for other categorical fields (e.g., `doctor`, `gender`, `insurance_provider`) and numerical outlier detection in `billing_amount`.

#### Suggested Production Guardrails (SQL Validation Rules)
To prevent these issues during future ingestion, implement the following checks at the load-balancing/ELT layer:
1.  **Date Integrity Check:**
    ```sql
    -- Reject records where admission date is a known sentinel or outside expected range
    SELECT COUNT(*) FROM table WHERE date_of_admission = '2099-12-31' OR date_of_admission > CURRENT_DATE;
    ```
2.  **Naming Normalization Check (for staging):**
    ```sql
    -- Identify records requiring string scrubbing before loading into production dimensions
    SELECT COUNT(*) FROM table WHERE hospital REGEXP '[[:punct:]]|(Inc|LLC|and)\\b';
    ```
3.  **Schema Enforcement:** Explicitly cast `date_of_admission` and `discharge_date` to `DATE` types and enforce non-null constraints on critical identifiers like `name` and `hospital`.
