# Data Quality Report - dq-manual-simple-p05-pro-20260320T061136Z

Generated at: 2026-03-20 06:13:08 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P05-PRO`
- Event log: `runs/dq-manual-simple-p05-pro-20260320T061136Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | invalid_admission_chronology | 1135 |
| HIGH | FAIL | healthcare_dataset | age_out_of_bounds | 1129 |

## Detailed Findings
### 1. [CRITICAL/FAIL] invalid_admission_chronology (healthcare_dataset)
- Why this matters: A patient's discharge date cannot logically precede their date of admission. Violations indicate corrupted timestamps or systemic data entry errors.
- Issue count: **1135**
- Output truncated: **yes**

```sql
SELECT * FROM healthcare_dataset WHERE date(discharge_date) < date(date_of_admission);
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
    "date_of_admission": "2099-12-31",
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
    "name": "chRiSTOPHer LEe",
    "age": 74,
    "gender": "Female",
    "blood_type": "B-",
    "medical_condition": "Hypertension",
    "date_of_admission": "2099-12-31",
    "doctor": "William Reynolds",
    "hospital": "PLC Young",
    "insurance_provider": "Cigna",
    "billing_amount": 49943.27849878726,
    "room_number": 478,
    "admission_type": "Emergency",
    "discharge_date": "2021-10-05",
    "medication": "Lipitor",
    "test_results": "Normal"
  },
  {
    "name": "kyLE bEnneTT",
    "age": 22,
    "gender": "Male",
    "blood_type": "O+",
    "medical_condition": "Hypertension",
    "date_of_admission": "2099-12-31",
    "doctor": "John Smith",
    "hospital": "Knight and Nguyen, Riggs",
    "insurance_provider": "UnitedHealthcare",
    "billing_amount": 28051.499483946325,
    "room_number": 157,
    "admission_type": "Urgent",
    "discharge_date": "2023-09-23",
    "medication": "Ibuprofen",
    "test_results": "Abnormal"
  }
]
```

### 2. [HIGH/FAIL] age_out_of_bounds (healthcare_dataset)
- Why this matters: The age column contains extreme, biologically impossible outliers (e.g., 21000). Human ages must reasonably fall between 0 and 120.
- Issue count: **1129**
- Output truncated: **yes**

```sql
SELECT * FROM healthcare_dataset WHERE age < 0 OR age > 120;
```

Example rows:
```json
[
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
    "name": "ThOMAS MartInEZ",
    "age": 27000,
    "gender": "Male",
    "blood_type": "B-",
    "medical_condition": "Asthma",
    "date_of_admission": "2019-08-18",
    "doctor": "Jacob Huynh",
    "hospital": "Hart Ltd",
    "insurance_provider": "Cigna",
    "billing_amount": 47909.12880987492,
    "room_number": 371,
    "admission_type": "Urgent",
    "discharge_date": "2019-09-01",
    "medication": "Ibuprofen",
    "test_results": "Inconclusive"
  },
  {
    "name": "Kim ScOtt",
    "age": 41500,
    "gender": "Male",
    "blood_type": "A-",
    "medical_condition": "Asthma",
    "date_of_admission": "2024-04-07",
    "doctor": "Cindy Ellis",
    "hospital": "Scott-Kelly",
    "insurance_provider": "UnitedHealthcare",
    "billing_amount": 39723.16605142787,
    "room_number": 244,
    "admission_type": "Emergency",
    "discharge_date": "2024-05-04",
    "medication": "Ibuprofen",
    "test_results": "Inconclusive"
  }
]
```

## Supervisor Narrative
### Final Data Quality Report

**Overall Verdict:** 🔴 **RED** 
The quality checks revealed widespread systemic issues affecting a large portion of the `healthcare_dataset` data. 

**Top Critical/High Issues:**
1.  **Critical - `invalid_admission_chronology`:** **1,135 rows** were flagged for having an admission date that logically occurs *after* the discharge date. Many of these rows have corrupted admission dates artificially set to `2099-12-31`, rendering the timeline impossible.
2.  **High - `age_out_of_bounds`:** **1,129 rows** were flagged for having extreme, biologically impossible age values (e.g., 29,000 or 51,500). This breaks realistic human bounds (0 - 120 years).

**Test Coverage Notes:**
*   Executed 2 validations addressing numerical bounds constraints and logical date chronology.
*   The tests specifically covered the `age`, `date_of_admission`, and `discharge_date` fields. 
*   Based on these results, we strongly advise revisiting the data extraction or generation process, as the occurrence rate of these anomalies is exceptionally high.

**Suggested Production Guardrails:**
To prevent corrupt records from entering the production warehouse, schedule the following SQL checks to run on every load:

1.  **Age Bounds Check (High):**
    ```sql
    SELECT * FROM healthcare_dataset WHERE age < 0 OR age > 120;
    ```
2.  **Date Chronology Check (Critical):**
    ```sql
    SELECT * FROM healthcare_dataset WHERE date(discharge_date) < date(date_of_admission);
    ```
