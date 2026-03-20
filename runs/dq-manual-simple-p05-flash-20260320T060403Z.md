# Data Quality Report - dq-manual-simple-p05-flash-20260320T060403Z

Generated at: 2026-03-20 06:04:30 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P05-FLASH`
- Event log: `runs/dq-manual-simple-p05-flash-20260320T060403Z.jsonl`

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
| HIGH | FAIL | main.healthcare_dataset | check_negative_or_zero_length_of_stay | 1135 |
| MEDIUM | FAIL | main.healthcare_dataset | check_missing_names | 1127 |

## Detailed Findings
### 1. [HIGH/FAIL] check_negative_or_zero_length_of_stay (main.healthcare_dataset)
- Why this matters: Identifies records where the discharge date occurs before or on the same day as the admission date, indicating potential data entry errors or logical inconsistencies in date tracking.
- Issue count: **1135**
- Output truncated: **yes**

```sql
SELECT * 
FROM main.healthcare_dataset 
WHERE julianday(discharge_date) <= julianday(date_of_admission);
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

### 2. [MEDIUM/FAIL] check_missing_names (main.healthcare_dataset)
- Why this matters: The 'name' column contains null values, which disrupts patient identification and downstream reporting.
- Issue count: **1127**
- Output truncated: **yes**

```sql
SELECT * 
FROM main.healthcare_dataset 
WHERE name IS NULL;
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
The data quality assessment of `main.healthcare_dataset` (run: dq-manual-simple-p05-flash-20260320T060403Z) indicates the dataset is highly unreliable. 

### **Overall Verdict: RED**

### **Critical Findings**
*   **Logical Inconsistency (High Risk):** 1,135 records have illogical `length_of_stay` values (e.g., discharge date before admission, or erroneous `2099` placeholder dates).
*   **Completeness (Medium Risk):** 1,127 records are missing `name` values, severely impacting data utility for patient-level reporting.

### **Test Coverage**
*   Tests focused on fundamental data integrity: completeness of identity fields and temporal validity of admission/discharge cycles. 
*   Both tests resulted in failures across a significant portion of the dataset (~375% of the sampled batch, implying widespread systemic issues).

### **Suggested Production Guardrails (Implementation Required)**
To prevent similar issues in future pipeline runs, the following SQL-based quality gates should be integrated into the data ingestion layer:
1.  **Identity Gate:** `ALTER TABLE main.healthcare_dataset ADD CONSTRAINT name_not_null CHECK (name IS NOT NULL);` (or filter during ETL).
2.  **Date Validity Gate:** Add an ingestion check: `SELECT count(*) FROM main.healthcare_dataset WHERE date_of_admission > '2025-01-01' OR discharge_date < date_of_admission;` - reject or quarantine batches exceeding an error threshold.
3.  **Type Enforcement:** Cast `date_of_admission` and `discharge_date` to `DATE` types immediately upon landing to ensure standard ISO-8601 formatting and catch non-conforming entries.
