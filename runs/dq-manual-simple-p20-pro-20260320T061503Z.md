# Data Quality Report - dq-manual-simple-p20-pro-20260320T061503Z

Generated at: 2026-03-20 06:16:25 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P20-PRO`
- Event log: `runs/dq-manual-simple-p20-pro-20260320T061503Z.jsonl`

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
| HIGH | FAIL | healthcare_dataset | invalid_age_bounds | 1129 |
| MEDIUM | FAIL | healthcare_dataset | malformed_hospital_names | 14802 |

## Detailed Findings
### 1. [HIGH/FAIL] invalid_age_bounds (healthcare_dataset)
- Why this matters: Patient age must be within a realistic human lifespan (0 to 120 years). The profiling revealed extreme anomalies (e.g., 25500, 40000) that need to be filtered out.
- Issue count: **1129**
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

### 2. [MEDIUM/FAIL] malformed_hospital_names (healthcare_dataset)
- Why this matters: Hospital names contain structural artifacts indicative of generation or extraction errors, such as starting with "and", ending with "and", or containing trailing commas.
- Issue count: **14802**
- Output truncated: **yes**

```sql
SELECT *
FROM healthcare_dataset
WHERE TRIM(hospital) LIKE 'and %'
   OR TRIM(hospital) LIKE '%,'
   OR TRIM(hospital) LIKE '% and';
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
    "name": "JASmINe aGuIlaR",
    "age": 82,
    "gender": "Male",
    "blood_type": "AB+",
    "medical_condition": "Asthma",
    "date_of_admission": "2020-07-01",
    "doctor": "Daniel Ferguson",
    "hospital": "Sons Rich and",
    "insurance_provider": "Cigna",
    "billing_amount": 50119.222791548505,
    "room_number": 316,
    "admission_type": "Elective",
    "discharge_date": "2020-07-14",
    "medication": "Aspirin",
    "test_results": "Abnormal"
  }
]
```

## Supervisor Narrative
### Data Quality Execution Report

**Overall Verdict**: 🔴 RED

**Top Critical/High Issues**:
1. **Invalid Age Bounds (High Risk)**: 1,129 patient records contained extreme age anomalies (e.g., `19000`, `41500`, `51000`) well beyond a realistic human lifespan. These invalid ages critically impact any age-based analytical grouping or reporting.
2. **Malformed Hospital Names (Medium Risk)**: 14,802 entries had structural artifacts, trailing commas, or misplaced conjunctions (e.g., `"and Brown Oneal, Shah"`, `"Hernandez Rogers and Vang,"`). This points to major systemic issues during data generation, extraction, or loading and will affect reporting across distinct medical facilities.

**Test Coverage Notes**:
- Tests were run against the `healthcare_dataset` table.
- 2 tests were executed covering numerical boundary validation (on `age`) and text anomaly/format validation (on `hospital`).
- Both tests failed, indicating a pervasive issue with data ingestion or generation. 
- *Note: Further testing is recommended for standardizing the casing of patient names and verifying doctor credentials.*

**Suggested Production Guardrails (SQL Checks)**:
Implement the following SQL checks in your data pipeline to block or flag anomalous records on future loads:

1. **Age Range Guardrail** (Fail load if records fall outside 0-120):
```sql
SELECT COUNT(*)
FROM healthcare_dataset
WHERE age < 0 OR age > 120;
```

2. **Hospital Name Formatting Guardrail** (Flag loads with malformed strings):
```sql
SELECT COUNT(*)
FROM healthcare_dataset
WHERE TRIM(hospital) LIKE 'and %'
   OR TRIM(hospital) LIKE '%,'
   OR TRIM(hospital) LIKE '% and';
```
