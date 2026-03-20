# Data Quality Report - dq-manual-complex-p10-flash-20260320T054910Z

Generated at: 2026-03-20 05:50:20 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **1**
- Errors: **1**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P10-FLASH`
- Event log: `runs/dq-manual-complex-p10-flash-20260320T054910Z.jsonl`

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
| CRITICAL | ERROR | healthcare_dataset | admission_discharge_date_inconsistencies | 0 |
| HIGH | FAIL | healthcare_dataset | patient_name_standardization_issues | 55417 |

## Detailed Findings
### 1. [CRITICAL/ERROR] admission_discharge_date_inconsistencies (healthcare_dataset)
- Why this matters: The `date_of_admission` and `discharge_date` columns are stored as TEXT, carrying a risk of invalid date entries and incorrect date comparisons. This test identifies records where either date is not a valid 'YYYY-MM-DD' format or where the `discharge_date` logically precedes the `date_of_admission`. Such issues can lead to incorrect calculations of stay duration and flawed reporting.
- Issue count: **0**
- Output truncated: **no**
- Execution error: `Only one SQL statement is allowed.`

```sql
SELECT
  name,
  age,
  gender,
  blood_type,
  medical_condition,
  date_of_admission,
  doctor,
  hospital,
  insurance_provider,
  billing_amount,
  room_number,
  admission_type,
  discharge_date,
  medication,
  test_results
FROM healthcare_dataset
WHERE
  date_of_admission IS NULL
  OR discharge_date IS NULL
  OR date(date_of_admission) IS NULL -- Checks for invalid admission date format
  OR date(discharge_date) IS NULL -- Checks for invalid discharge date format
  OR julianday(discharge_date) < julianday(date_of_admission); -- Checks if discharge is before admission
```

### 2. [HIGH/FAIL] patient_name_standardization_issues (healthcare_dataset)
- Why this matters: The `name` field suffers from inconsistent capitalization and contains professional titles (e.g., 'MD', 'DVM', 'Mrs.', 'Mr.') embedded directly within the name. This lack of standardization makes accurate searching, joining, and unique identification of patients difficult, and complicates parsing for structured data extraction.
- Issue count: **55417**
- Output truncated: **yes**

```sql
SELECT
  name,
  age,
  gender,
  blood_type,
  medical_condition,
  date_of_admission,
  doctor,
  hospital,
  insurance_provider,
  billing_amount,
  room_number,
  admission_type,
  discharge_date,
  medication,
  test_results
FROM healthcare_dataset
WHERE
  name IS NOT NULL
  AND (
    (LOWER(name) != name AND UPPER(name) != name) -- Detects mixed casing
    OR LOWER(name) LIKE '% md' -- Detects trailing ' MD'
    OR LOWER(name) LIKE '% dvm' -- Detects trailing ' DVM'
    OR LOWER(name) LIKE 'mrs.%' -- Detects leading 'Mrs.'
    OR LOWER(name) LIKE 'mr.%' -- Detects leading 'Mr.'
  );
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
    "name": "DaNnY sMitH",
    "age": 76,
    "gender": "Female",
    "blood_type": "A-",
    "medical_condition": "Obesity",
    "date_of_admission": "2022-09-22",
    "doctor": "Tiffany Mitchell",
    "hospital": "Cook PLC",
    "insurance_provider": "Aetna",
    "billing_amount": 27955.096078842456,
    "room_number": 205,
    "admission_type": "Emergency",
    "discharge_date": "2022-10-07",
    "medication": "Aspirin",
    "test_results": "Normal"
  }
]
```

## Supervisor Narrative
**Overall Verdict:** Red - Significant data quality issues and a critical test execution error found.

**Top Critical/High Issues:**

1.  **Critical Severity Errored Test: `admission_discharge_date_inconsistencies`**
    *   **Finding:** This essential test, designed to verify the consistency and validity of admission and discharge dates, failed to execute due to a SQL syntax error ("Only one SQL statement is allowed."). This prevents any assessment of critical date logic, such as ensuring `discharge_date` is not before `date_of_admission`.
    *   **Impact:** High risk of undetected logical inconsistencies and invalid date formats in critical patient timeline data, leading to incorrect calculations and reporting.
    *   **Priority:** Immediate fix required for the SQL query to enable this crucial data quality check.

2.  **High Severity Failed Test: `patient_name_standardization_issues`**
    *   **Finding:** Identified **55,417 records** (a significant portion) in the `healthcare_dataset` table where patient names exhibit inconsistent capitalization or contain professional titles (e.g., 'MD', 'DVM', 'Mrs.', 'Mr.').
    *   **Impact:** This severe lack of standardization will hinder accurate patient identification, fuzzy matching, data aggregation, and any attempts at structured data parsing from the name field. It directly impacts the usability and reliability of patient demographics.
    *   **Priority:** High. Requires data cleansing and implementation of strict data entry or transformation rules.

**Test Coverage Notes:**

*   A total of 2 data quality tests were attempted.
*   One critical test (`admission_discharge_date_inconsistencies`) failed to execute, meaning the crucial check for date consistency could not be performed. This is a significant gap in coverage.
*   One high-severity test (`patient_name_standardization_issues`) was executed successfully, revealing widespread issues with patient name standardization.

**Suggested Production Guardrails (SQL checks to schedule with each data load):**

To ensure ongoing data quality, the following checks should be implemented and regularly executed as part of data ingestion or transformation processes:

1.  **Patient Name Standardization:**
    ```sql
    SELECT
      name
    FROM healthcare_dataset
    WHERE
      name IS NOT NULL
      AND (
        (LOWER(name) != name AND UPPER(name) != name) -- Detects mixed casing
        OR LOWER(name) LIKE '% md' -- Detects trailing ' MD'
        OR LOWER(name) LIKE '% dvm' -- Detects trailing ' DVM'
        OR LOWER(name) LIKE 'mrs.%' -- Detects leading 'Mrs.'
        OR LOWER(name) LIKE 'mr.%' -- Detects leading 'Mr.'
      );
    ```
    *   **Action:** Records identified by this query should be reviewed and standardized to a consistent format (e.g., proper case, titles removed or placed in a separate field).

2.  **Admission and Discharge Date Consistency:**
    *   **Note:** The SQL for this check needs to be corrected to resolve the "Only one SQL statement is allowed." error before it can be effectively implemented as a guardrail. Assuming the intent was valid SQL for date validation and comparison within the target system, the corrected query would be:
    ```sql
    SELECT
      date_of_admission,
      discharge_date
    FROM healthcare_dataset
    WHERE
      date_of_admission IS NULL
      OR discharge_date IS NULL
      OR date(date_of_admission) IS NULL -- Checks for invalid admission date format
      OR date(discharge_date) IS NULL -- Checks for invalid discharge date format
      OR julianday(discharge_date) < julianday(date_of_admission); -- Checks if discharge is before admission
    ```
    *   **Action:** After correcting the SQL, schedule this check to flag records with invalid date formats or where the discharge date precedes the admission date. These records require immediate investigation and correction.
