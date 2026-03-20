# Data Quality Report - dq-manual-complex-p50-pro-20260320T062506Z

Generated at: 2026-03-20 06:27:10 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P50-PRO`
- Event log: `runs/dq-manual-complex-p50-pro-20260320T062506Z.jsonl`

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
| HIGH | FAIL | healthcare_dataset | discharge_before_admission | 555 |
| MEDIUM | FAIL | healthcare_dataset | hospital_name_formatting_artifacts | 14525 |

## Detailed Findings
### 1. [HIGH/FAIL] discharge_before_admission (healthcare_dataset)
- Why this matters: Enforces the temporal constraint that a patient's discharge date must be on or after their date of admission. Also flags any improperly formatted date strings that fail SQLite's `date()` parsing.
- Issue count: **555**
- Output truncated: **yes**

```sql
SELECT *
FROM healthcare_dataset
WHERE date(discharge_date) < date(date_of_admission)
   OR (discharge_date IS NOT NULL AND date(discharge_date) IS NULL)
   OR (date_of_admission IS NOT NULL AND date(date_of_admission) IS NULL);
```

Example rows:
```json
[
  {
    "name": "Erin oRTEga",
    "age": 43,
    "gender": "Male",
    "blood_type": "AB-",
    "medical_condition": "Cancer",
    "date_of_admission": "2023-05-24",
    "doctor": "Heather Garcia",
    "hospital": "Lopez-Phillips",
    "insurance_provider": "Medicare",
    "billing_amount": 21185.953530394218,
    "room_number": 494,
    "admission_type": "Elective",
    "discharge_date": "2023-05-23",
    "medication": "Ibuprofen",
    "test_results": "Normal"
  },
  {
    "name": "JENnIfEr mCmillan",
    "age": 84,
    "gender": "Female",
    "blood_type": "A-",
    "medical_condition": "Obesity",
    "date_of_admission": "2022-06-22",
    "doctor": "Joseph Jones",
    "hospital": "Rodriguez and Sons",
    "insurance_provider": "Aetna",
    "billing_amount": 15475.403236542532,
    "room_number": 154,
    "admission_type": "Elective",
    "discharge_date": "2022-06-21",
    "medication": "Ibuprofen",
    "test_results": "Abnormal"
  },
  {
    "name": "mARIA ANDeRsON",
    "age": 79,
    "gender": "Female",
    "blood_type": "O+",
    "medical_condition": "Arthritis",
    "date_of_admission": "2024-03-12",
    "doctor": "Lee Santiago",
    "hospital": "Mack, Wilson and Fowler",
    "insurance_provider": "Blue Cross",
    "billing_amount": 37879.97903164024,
    "room_number": 110,
    "admission_type": "Urgent",
    "discharge_date": "2024-03-11",
    "medication": "Aspirin",
    "test_results": "Abnormal"
  }
]
```

### 2. [MEDIUM/FAIL] hospital_name_formatting_artifacts (healthcare_dataset)
- Why this matters: Identifies synthetic generation or concatenation errors in the hospital string field, specifically looking for leading/trailing commas and out-of-place conjunctions (e.g., names ending or starting with 'and').
- Issue count: **14525**
- Output truncated: **yes**

```sql
SELECT *
FROM healthcare_dataset
WHERE TRIM(hospital) LIKE '%,'
   OR TRIM(hospital) LIKE ',%'
   OR LOWER(TRIM(hospital)) LIKE 'and %'
   OR LOWER(TRIM(hospital)) LIKE '% and';
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
**Overall Verdict:** 🔴 RED (Critical data quality issues detected)

**Top Critical/High Issues:**
1. **Invalid Temporal Logic (High Risk):** The `discharge_before_admission` test failed for **555 rows**. Records contain an invalid chronological sequence where `discharge_date` occurs *before* `date_of_admission` or the strings fail SQLite's `date()` parsing. This completely invalidates core healthcare metrics like length-of-stay and jeopardizes billing integrity.
2. **Formatting Artifacts in Text (Medium Risk):** The `hospital_name_formatting_artifacts` test failed for **14,525 rows**. Nearly half of the dataset contains poorly formed `hospital` strings with trailing/leading commas or out-of-place conjunctions (e.g., names ending or starting with "and"). This heavily implies systemic upstream errors in synthetic data generation or text concatenation.

**Test Coverage Notes:**
- **Temporal Consistency:** Verified logical sequences between admission and discharge dates.
- **String Formatting:** Evaluated the `hospital` column for generation and concatenation artifacts.
- **Pending Checks (from Profile):** Future test implementations should enforce standardized capitalization for patient `name`, extract embedded titles/suffixes from the `name` and `doctor` fields, and add precision rounding validation for `billing_amount`.

**Suggested Production Guardrails:**
To prevent these issues from severely degrading downstream analytical models, schedule the following SQL guardrails on each data load:

*Guardrail 1: Enforce Temporal Consistency (Discharge >= Admission)*
```sql
SELECT *
FROM healthcare_dataset
WHERE date(discharge_date) < date(date_of_admission)
   OR (discharge_date IS NOT NULL AND date(discharge_date) IS NULL)
   OR (date_of_admission IS NOT NULL AND date(date_of_admission) IS NULL);
```

*Guardrail 2: Flag Hospital Name Formatting Artifacts*
```sql
SELECT *
FROM healthcare_dataset
WHERE TRIM(hospital) LIKE '%,'
   OR TRIM(hospital) LIKE ',%'
   OR LOWER(TRIM(hospital)) LIKE 'and %'
   OR LOWER(TRIM(hospital)) LIKE '% and';
```
