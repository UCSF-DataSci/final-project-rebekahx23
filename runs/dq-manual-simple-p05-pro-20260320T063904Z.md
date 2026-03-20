# Data Quality Report - dq-manual-simple-p05-pro-20260320T063904Z

Generated at: 2026-03-20 06:40:40 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P05-PRO`
- Event log: `runs/dq-manual-simple-p05-pro-20260320T063904Z.jsonl`

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
| HIGH | FAIL | healthcare_dataset | discharge_date_before_admission_date | 1131 |
| MEDIUM | FAIL | healthcare_dataset | doctor_name_contains_titles | 1093 |

## Detailed Findings
### 1. [HIGH/FAIL] discharge_date_before_admission_date (healthcare_dataset)
- Why this matters: Based on the data profile, the `date_of_admission` and `discharge_date` columns are stored as text. This test validates the logical consistency between them, ensuring that a patient's discharge date is not on or before their admission date. Such inconsistencies can lead to incorrect calculations for length of stay and other critical metrics.
- Issue count: **1131**
- Output truncated: **yes**

```sql
SELECT * FROM healthcare_dataset WHERE julianday(discharge_date) <= julianday(date_of_admission);
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

### 2. [MEDIUM/FAIL] doctor_name_contains_titles (healthcare_dataset)
- Why this matters: The data profile sample shows inconsistent formatting in the `doctor` column, including names with titles (e.g., 'Mr. Brian Smith'). This test identifies records where doctor names contain common titles, which should be standardized to ensure accurate aggregation and analysis of data by doctor.
- Issue count: **1093**
- Output truncated: **yes**

```sql
SELECT * FROM healthcare_dataset WHERE LOWER(doctor) LIKE 'mr. %' OR LOWER(doctor) LIKE 'mrs. %' OR LOWER(doctor) LIKE 'ms. %' OR LOWER(doctor) LIKE 'dr. %';
```

Example rows:
```json
[
  {
    "name": "MIChael MIllS",
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
    "name": "ERic riveRa",
    "age": 74,
    "gender": "Female",
    "blood_type": "AB+",
    "medical_condition": "Cancer",
    "date_of_admission": "2024-04-10",
    "doctor": "Mr. Luke Nunez Jr.",
    "hospital": "Gonzalez-Pacheco",
    "insurance_provider": "Blue Cross",
    "billing_amount": 21668.56450834912,
    "room_number": 115,
    "admission_type": "Emergency",
    "discharge_date": "2024-05-03",
    "medication": "Lipitor",
    "test_results": "Abnormal"
  },
  {
    "name": "LisA KENNEdY",
    "age": 42,
    "gender": "Male",
    "blood_type": "B-",
    "medical_condition": "Arthritis",
    "date_of_admission": "2022-12-24",
    "doctor": "Mr. Michael White MD",
    "hospital": "and Dixon Taylor Hunter,",
    "insurance_provider": "Cigna",
    "billing_amount": 10645.565853008928,
    "room_number": 251,
    "admission_type": "Emergency",
    "discharge_date": "2023-01-06",
    "medication": "Ibuprofen",
    "test_results": "Normal"
  }
]
```

## Supervisor Narrative
**Overall Verdict: RED**

Data quality scan failed with 2 out of 2 tests returning critical or high-severity issues. The findings indicate significant data integrity and formatting problems that must be addressed.

**Top Critical/High Issues:**

1.  **Critical: Invalid Admission/Discharge Dates (`discharge_date_before_admission_date`)**
    -   **Finding:** 1,131 records have a discharge date that is on or before the admission date.
    -   **Impact:** This is a major logical error that invalidates any analysis dependent on the patient's length of stay, treatment duration, or general timeline. It is the highest-risk finding from this scan.

2.  **Medium: Inconsistent Doctor Name Formatting (`doctor_name_contains_titles`)**
    -   **Finding:** 1,093 records contain titles (e.g., 'Mr.', 'Dr.', 'PhD') in the `doctor` field.
    -   **Impact:** Prevents accurate grouping and analysis by doctor, leading to fragmented reporting and incorrect metrics.

**Test Coverage Notes:**

-   The executed tests successfully identified critical data issues related to date logic and string formatting, which were flagged as high-risk during the initial data profiling.
-   Future runs should expand coverage to other potential issues noted in the profiling, such as inconsistent casing in patient names (e.g., "jessiCa fARrELl") and validating the value sets for categorical columns like `gender`, `blood_type`, and `medical_condition`.

**Suggested Production Guardrails:**

To prevent these issues in future data loads, the following SQL checks should be integrated into your data pipeline:

1.  **Block loads with invalid date logic:**
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE julianday(discharge_date) <= julianday(date_of_admission);
    ```
    *(This check should fail the data load if the result is greater than 0.)*

2.  **Alert on inconsistent doctor names:**
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE LOWER(doctor) LIKE 'mr. %' OR LOWER(doctor) LIKE 'mrs. %' OR LOWER(doctor) LIKE 'ms. %' OR LOWER(doctor) LIKE 'dr. %';
    ```
    *(This check should trigger an alert if the result is greater than 0, signaling the need for data cleaning.)*
    
    **Remediation:** Data should be cleaned by stripping these titles from the `doctor` column upon ingestion.
