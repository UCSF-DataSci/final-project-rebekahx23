# Data Quality Report - dq-manual-simple-p05-flash-20260320T060203Z

Generated at: 2026-03-20 06:02:44 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P05-FLASH`
- Event log: `runs/dq-manual-simple-p05-flash-20260320T060203Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | test_age_physically_possible | 1139 |
| HIGH | FAIL | healthcare_dataset | test_admission_discharge_chronology | 1135 |

## Detailed Findings
### 1. [CRITICAL/FAIL] test_age_physically_possible (healthcare_dataset)
- Why this matters: Identifies physically impossible age values (e.g., 46,000 and 33,500) observed in profiling. These extreme outliers invalidate demographic analysis and indicate severe data entry or ingestion errors.
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

### 2. [HIGH/FAIL] test_admission_discharge_chronology (healthcare_dataset)
- Why this matters: Validates the logical consistency of stay durations. Patients should not have a discharge date that precedes their admission date. Violations indicate corrupted records or system errors in the source data.
- Issue count: **1135**
- Output truncated: **yes**

```sql
SELECT *
FROM healthcare_dataset
WHERE date(discharge_date) < date(date_of_admission);
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

## Supervisor Narrative
The healthcare_dataset failed critical quality checks with systematic corruption in demographic and temporal fields. Over 1,100 records contain physically impossible ages (up to 52,500) and logical date violations (future placeholder dates of 2099-12-31 used for admissions). These issues suggest a severe failure in the ingestion pipeline or upstream source system mapping. Immediate remediation and the implementation of production guardrails to reject records with age > 120 or inverted date chronologies are required.
