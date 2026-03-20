# Data Quality Report - dq-manual-simple-p10-pro-20260320T061321Z

Generated at: 2026-03-20 06:14:51 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P10-PRO`
- Event log: `runs/dq-manual-simple-p10-pro-20260320T061321Z.jsonl`

## Coverage Breakdown
| Severity | Count |
|---|---:|
| Critical | 1 |
| High | 0 |
| Medium | 1 |
| Low | 0 |

## Top Findings
| Severity | Status | Table | Test | Issue Count |
|---|---|---|---|---:|
| CRITICAL | FAIL | healthcare_dataset | missing_patient_name | 1130 |
| MEDIUM | FAIL | healthcare_dataset | malformed_hospital_names | 18023 |

## Detailed Findings
### 1. [CRITICAL/FAIL] missing_patient_name (healthcare_dataset)
- Why this matters: The patient name serves as the primary entity identifier. Explicitly missing (NULL) or empty names prevent accurate entity tracking and compromise the overall completeness of the administrative records.
- Issue count: **1130**
- Output truncated: **yes**

```sql
SELECT *
FROM healthcare_dataset
WHERE name IS NULL 
   OR TRIM(name) = '';
```

Example rows:
```json
[
  {
    "name": null,
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
    "name": null,
    "age": 38,
    "gender": "Female",
    "blood_type": "A+",
    "medical_condition": "Cancer",
    "date_of_admission": "2023-05-16",
    "doctor": "Matthew Walker",
    "hospital": "Lindsey Inc",
    "insurance_provider": "Cigna",
    "billing_amount": 39476.94751437997,
    "room_number": 428,
    "admission_type": "Elective",
    "discharge_date": "2023-06-01",
    "medication": "Aspirin",
    "test_results": "Abnormal"
  },
  {
    "name": null,
    "age": 50,
    "gender": "Female",
    "blood_type": "O-",
    "medical_condition": "Obesity",
    "date_of_admission": "2020-10-24",
    "doctor": "Julia Yoder",
    "hospital": "Wright-Alexander",
    "insurance_provider": "UnitedHealthcare",
    "billing_amount": 40133.96739245519,
    "room_number": 130,
    "admission_type": "Urgent",
    "discharge_date": "2020-11-13",
    "medication": "Ibuprofen",
    "test_results": "Normal"
  }
]
```

### 2. [MEDIUM/FAIL] malformed_hospital_names (healthcare_dataset)
- Why this matters: Hospital names exhibit corrupt string patterns characteristic of poor data entry or malformed generation scripts. This test flags strings containing dangling conjunctions (e.g., starting/ending with "and") or misplaced commas.
- Issue count: **18023**
- Output truncated: **yes**

```sql
SELECT *
FROM healthcare_dataset
WHERE LOWER(hospital) LIKE LOWER('% and')
   OR LOWER(hospital) LIKE LOWER('and %')
   OR hospital LIKE '%,'
   OR LOWER(hospital) LIKE LOWER('%, and%');
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
Overall Verdict: RED (Critical Failures Detected)

The quality run for `healthcare_dataset` executed 2 data quality tests, both of which failed, exposing severe ingestion and formatting issues.

Top Findings:
1. [CRITICAL] Missing Patient Identifiers: 1,130 rows lack a patient `name` (NULL or empty string). As this is the primary entity identifier, these records cannot be tied to individual patients, compromising downstream processing and billing.
2. [MEDIUM] Widespread Corrupt Hospital Names: 18,023 rows exhibit syntactically malformed patterns in the `hospital` field, containing dangling conjunctions and trailing commas (e.g., "Sons Rich and"). This indicates a systematic upstream text generation or scraping flaw.

Coverage:
The tests covered identifier completeness and string formatting integrity.

Recommendations:
Implement production SQL guardrails to halt loads containing NULL patient names, and quarantine records containing known malformed hospital string patterns until the upstream ingestion bug is resolved.
