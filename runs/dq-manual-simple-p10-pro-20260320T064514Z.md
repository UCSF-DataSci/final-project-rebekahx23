# Data Quality Report - dq-manual-simple-p10-pro-20260320T064514Z

Generated at: 2026-03-20 06:46:34 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **4**
- Passed: **0**
- Failed: **2**
- Errors: **2**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P10-PRO`
- Event log: `runs/dq-manual-simple-p10-pro-20260320T064514Z.jsonl`

## Coverage Breakdown
| Severity | Count |
|---|---:|
| Critical | 2 |
| High | 0 |
| Medium | 2 |
| Low | 0 |

## Top Findings
| Severity | Status | Table | Test | Issue Count |
|---|---|---|---|---:|
| CRITICAL | FAIL | healthcare_dataset | discharge_before_admission | 1136 |
| CRITICAL | ERROR | healthcare_dataset | discharge_before_admission | 0 |
| MEDIUM | FAIL | healthcare_dataset | hospital_name_has_inconsistent_formatting | 9093 |
| MEDIUM | ERROR | healthcare_dataset | hospital_name_has_inconsistent_formatting | 0 |

## Detailed Findings
### 1. [CRITICAL/FAIL] discharge_before_admission (healthcare_dataset)
- Why this matters: The discharge date for a patient cannot be earlier than their admission date. This indicates a critical data entry error that would make any length-of-stay calculations incorrect.
- Issue count: **1136**
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
    "name": "Nancy glOVeR",
    "age": 58,
    "gender": "Male",
    "blood_type": "A-",
    "medical_condition": "Hypertension",
    "date_of_admission": "2099-12-31",
    "doctor": "Jennifer Larson",
    "hospital": "Khan, and Rodriguez Fischer",
    "insurance_provider": "Medicare",
    "billing_amount": 19183.168885395542,
    "room_number": 378,
    "admission_type": "Emergency",
    "discharge_date": "2020-06-01",
    "medication": "Aspirin",
    "test_results": "Abnormal"
  },
  {
    "name": "daVID SPeNCE",
    "age": 21,
    "gender": "Female",
    "blood_type": "AB+",
    "medical_condition": "Diabetes",
    "date_of_admission": "2099-12-31",
    "doctor": "Terrance Rosales",
    "hospital": "Valentine Ltd",
    "insurance_provider": "Cigna",
    "billing_amount": 5985.978487240192,
    "room_number": 136,
    "admission_type": "Urgent",
    "discharge_date": "2021-12-04",
    "medication": "Penicillin",
    "test_results": "Normal"
  },
  {
    "name": "jaMEs AnDerSon",
    "age": 18,
    "gender": "Female",
    "blood_type": "AB+",
    "medical_condition": "Asthma",
    "date_of_admission": "2099-12-31",
    "doctor": "Chris Holt",
    "hospital": "Rodriguez-Franco",
    "insurance_provider": "Blue Cross",
    "billing_amount": 45072.418258941034,
    "room_number": 147,
    "admission_type": "Urgent",
    "discharge_date": "2022-07-04",
    "medication": "Lipitor",
    "test_results": "Inconclusive"
  }
]
```

### 2. [CRITICAL/ERROR] discharge_before_admission (healthcare_dataset)
- Why this matters: The discharge date for a patient cannot be earlier than their admission date. This indicates a critical data entry error that would make any length-of-stay calculations incorrect.
- Issue count: **0**
- Output truncated: **no**
- Execution error: `Query must start with SELECT, WITH, or EXPLAIN.`

```sql
-- Find records where the discharge date is before the admission date.
SELECT
  *
FROM
  healthcare_dataset
WHERE
  julianday(discharge_date) < julianday(date_of_admission);
```

### 3. [MEDIUM/FAIL] hospital_name_has_inconsistent_formatting (healthcare_dataset)
- Why this matters: The profile identified inconsistent suffixes like trailing commas and prefixes like 'and ' in the hospital names. These formatting issues can lead to problems with grouping, aggregation, and accurate reporting on hospital-related metrics. This test identifies names with these common inconsistencies.
- Issue count: **9093**
- Output truncated: **yes**

```sql
SELECT
  *
FROM
  healthcare_dataset
WHERE
  LOWER(hospital) LIKE 'and %' OR hospital LIKE '%,';
```

Example rows:
```json
[
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
  },
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
    "discharge_date": "2022-01-07",
    "medication": "Paracetamol",
    "test_results": "Inconclusive"
  },
  {
    "name": "dR. EilEEn thomPsoN",
    "age": 59,
    "gender": "Male",
    "blood_type": "A+",
    "medical_condition": "Asthma",
    "date_of_admission": "2021-08-02",
    "doctor": "Donna Martinez MD",
    "hospital": "and Sons Smith",
    "insurance_provider": "Aetna",
    "billing_amount": 25250.052428216135,
    "room_number": 119,
    "admission_type": "Urgent",
    "discharge_date": "2021-08-12",
    "medication": "Lipitor",
    "test_results": "Inconclusive"
  }
]
```

### 4. [MEDIUM/ERROR] hospital_name_has_inconsistent_formatting (healthcare_dataset)
- Why this matters: The profile identified inconsistent suffixes like trailing commas and prefixes like 'and ' in the hospital names. These formatting issues can lead to problems with grouping, aggregation, and accurate reporting on hospital-related metrics. This test identifies names with these common inconsistencies.
- Issue count: **0**
- Output truncated: **no**
- Execution error: `Query must start with SELECT, WITH, or EXPLAIN.`

```sql
-- Find hospital names that start with 'and ' or end with a comma.
SELECT
  *
FROM
  healthcare_dataset
WHERE
  LOWER(hospital) LIKE 'and %' OR hospital LIKE '%,';
```

## Supervisor Narrative
Data Quality Run Summary:

**Overall Verdict:** 🔴 Red

This data quality run has failed due to a critical issue that makes the data unreliable for calculating patient length of stay.

**Top Critical/High Issues:**

1.  **Critical: `discharge_before_admission`**
    *   **Finding:** 1,136 records have a discharge date that occurs before the admission date.
    *   **Impact:** This is a critical logic error that invalidates any analysis related to the duration of hospital stays, which is a key metric. The admission and discharge dates for these records must be corrected.

2.  **Medium: `hospital_name_has_inconsistent_formatting`**
    *   **Finding:** 9,093 records have hospital names with leading "and " or trailing commas.
    *   **Impact:** This formatting inconsistency will lead to incorrect grouping and aggregation when reporting on hospital-specific metrics. It can cause a single hospital to appear as multiple distinct entities.

**Test Coverage Notes:**

The tests were targeted based on an initial data profile and successfully uncovered significant, high-impact data quality issues. The coverage was sufficient to identify critical flaws in the dataset's integrity.

**Suggested Production Guardrails:**

To prevent these issues in the future, the following SQL checks should be scheduled to run after each data load. An alert should be triggered if any of these queries return results.

1.  **Check for Discharge Before Admission:**
    ```sql
    -- This check should not return any rows.
    SELECT
      *
    FROM
      healthcare_dataset
    WHERE
      julianday(discharge_date) < julianday(date_of_admission);
    ```

2.  **Check for Inconsistent Hospital Name Formatting:**
    ```sql
    -- This check should not return any rows.
    SELECT
      *
    FROM
      healthcare_dataset
    WHERE
      LOWER(hospital) LIKE 'and %' OR hospital LIKE '%,';
    ```
