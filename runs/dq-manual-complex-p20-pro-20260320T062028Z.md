# Data Quality Report - dq-manual-complex-p20-pro-20260320T062028Z

Generated at: 2026-03-20 06:21:53 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P20-PRO`
- Event log: `runs/dq-manual-complex-p20-pro-20260320T062028Z.jsonl`

## Coverage Breakdown
| Severity | Count |
|---|---:|
| Critical | 1 |
| High | 0 |
| Medium | 0 |
| Low | 1 |

## Top Findings
| Severity | Status | Table | Test | Issue Count |
|---|---|---|---|---:|
| CRITICAL | FAIL | healthcare_dataset | temporal_logic_discharge_before_admission | 555 |
| LOW | FAIL | healthcare_dataset | hospital_name_format_irregularities | 14525 |

## Detailed Findings
### 1. [CRITICAL/FAIL] temporal_logic_discharge_before_admission (healthcare_dataset)
- Why this matters: Ensures temporal consistency by verifying that a patient's discharge date does not logically occur before their admission date.
- Issue count: **555**
- Output truncated: **yes**

```sql
SELECT * FROM healthcare_dataset WHERE date(discharge_date) < date(date_of_admission);
```

Example rows:
```json
[
  {
    "name": "ChRISTopher mccLAiN",
    "age": 67,
    "gender": "Female",
    "blood_type": "O-",
    "medical_condition": "Arthritis",
    "date_of_admission": "2023-05-17",
    "doctor": "Maria Tran",
    "hospital": "Thomas-Huber",
    "insurance_provider": "Medicare",
    "billing_amount": 27309.436760697274,
    "room_number": 293,
    "admission_type": "Elective",
    "discharge_date": "2023-05-16",
    "medication": "Aspirin",
    "test_results": "Abnormal"
  },
  {
    "name": "jEssiCa GoNzAleS",
    "age": 57,
    "gender": "Female",
    "blood_type": "O+",
    "medical_condition": "Hypertension",
    "date_of_admission": "2023-08-28",
    "doctor": "Kimberly Gonzalez",
    "hospital": "Jones and Jones, Turner",
    "insurance_provider": "Cigna",
    "billing_amount": 20545.871762829884,
    "room_number": 198,
    "admission_type": "Urgent",
    "discharge_date": "2023-08-27",
    "medication": "Penicillin",
    "test_results": "Abnormal"
  },
  {
    "name": "lIsA LeWis",
    "age": 83,
    "gender": "Male",
    "blood_type": "O-",
    "medical_condition": "Asthma",
    "date_of_admission": "2021-11-13",
    "doctor": "Kevin Brown",
    "hospital": "Tran, and Ferrell Garcia",
    "insurance_provider": "Aetna",
    "billing_amount": 18198.058517853886,
    "room_number": 308,
    "admission_type": "Urgent",
    "discharge_date": "2021-11-12",
    "medication": "Ibuprofen",
    "test_results": "Normal"
  }
]
```

### 2. [LOW/FAIL] hospital_name_format_irregularities (healthcare_dataset)
- Why this matters: Identifies hospital names with structural formatting anomalies such as trailing commas or misplaced conjunctions (e.g., starting or ending with 'and').
- Issue count: **14525**
- Output truncated: **yes**

```sql
SELECT * FROM healthcare_dataset WHERE hospital LIKE '%,' OR hospital LIKE '% and' OR LOWER(hospital) LIKE 'and %';
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
# Data Quality Final Report

**Overall Verdict:** 🔴 RED

### Top Critical Issues
* **Temporal Logic Anomalies (`temporal_logic_discharge_before_admission`)**: **555** records were identified in the `healthcare_dataset` table where the `discharge_date` is earlier than the `date_of_admission`. This is a critical data integrity issue indicating systemic errors in data entry or upstream ingestion logic.

### Other Notable Issues
* **Hospital Name Formatting (`hospital_name_format_irregularities`)**: **14,525** records in the `healthcare_dataset` table contained formatting anomalies in the `hospital` column, such as trailing commas or misplaced conjunctions (e.g., starting/ending with "and"). While low severity, the high volume points to a consistent lack of string normalization at the source.

### Test Coverage Notes
* **Coverage**: 2 targeted tests were executed on the `healthcare_dataset` table.
* **Scope**: The tests focused on temporal consistency between patient admission and discharge dates, and structural formatting of hospital names. 
* Both tests failed, highlighting a need for critical pipeline fixes and broader data standardization efforts.

### Suggested Production Guardrails
To prevent these issues from polluting downstream systems, the following guardrails should be scheduled to run on every load:

1. **Temporal Logic Check (Critical Guardrail)**: 
   *Action*: Fail the load or quarantine the failing rows.
   ```sql
   SELECT * FROM healthcare_dataset WHERE date(discharge_date) < date(date_of_admission);
   ```

2. **Hospital Name Standardization (Quality Warning / Transform Check)**:
   *Action*: Issue a warning, or ideally, implement an ETL transformation to clean these fields during ingestion.
   ```sql
   SELECT * FROM healthcare_dataset 
   WHERE hospital LIKE '%,' 
      OR hospital LIKE '% and' 
      OR LOWER(hospital) LIKE 'and %';
   ```
