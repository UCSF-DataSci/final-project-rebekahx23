# Data Quality Report - dq-manual-simple-p10-flash-20260320T060256Z

Generated at: 2026-03-20 06:03:37 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P10-FLASH`
- Event log: `runs/dq-manual-simple-p10-flash-20260320T060256Z.jsonl`

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
| HIGH | FAIL | main.healthcare_dataset | test_admission_discharge_chronology | 1135 |
| MEDIUM | FAIL | main.healthcare_dataset | test_hospital_name_formatting_artifacts | 9090 |

## Detailed Findings
### 1. [HIGH/FAIL] test_admission_discharge_chronology (main.healthcare_dataset)
- Why this matters: Validates temporal integrity by ensuring that patients are not discharged before they are admitted.
- Issue count: **1135**
- Output truncated: **yes**

```sql
SELECT *
FROM main.healthcare_dataset
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

### 2. [MEDIUM/FAIL] test_hospital_name_formatting_artifacts (main.healthcare_dataset)
- Why this matters: Detects data entry artifacts in hospital names, such as trailing commas or leading 'and' prefixes, which hinder reporting and grouping.
- Issue count: **9090**
- Output truncated: **yes**

```sql
SELECT *
FROM main.healthcare_dataset
WHERE hospital LIKE '%,' 
   OR hospital LIKE '%, '
   OR LOWER(hospital) LIKE 'and %';
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

## Supervisor Narrative
The healthcare_dataset failed critical quality checks with a Red verdict. Major findings include 1,135 records with futuristic admission date placeholders (2099-12-31) and correlated age corruption (values >30,000). Additionally, over 9,000 records contain hospital naming artifacts like trailing commas and leading 'and' prefixes, which will break data aggregation. Investigation into the source system's handling of null or missing dates is required.
