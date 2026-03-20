# Data Quality Report - dq-manual-complex-p20-pro-20260320T051402Z

Generated at: 2026-03-20 05:15:20 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P20-PRO`
- Event log: `runs/dq-manual-complex-p20-pro-20260320T051402Z.jsonl`

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
| MEDIUM | FAIL | healthcare_dataset | malformed_hospital_name | 10465 |

## Detailed Findings
### 1. [HIGH/FAIL] discharge_before_admission (healthcare_dataset)
- Why this matters: The discharge date of a patient cannot be before their admission date. This indicates a critical error in data entry or processing, making calculations like length of stay impossible or incorrect. The profile explicitly notes an example of this with patient `LAcEy CLAytON`.
- Issue count: **555**
- Output truncated: **yes**

```sql
SELECT
  *
FROM healthcare_dataset
WHERE
  julianday(discharge_date) < julianday(date_of_admission);
```

Example rows:
```json
[
  {
    "name": "adrIENNE bEll",
    "age": 43,
    "gender": "Female",
    "blood_type": "AB+",
    "medical_condition": "Cancer",
    "date_of_admission": "2022-09-19",
    "doctor": "Kathleen Hanna",
    "hospital": "White-White",
    "insurance_provider": "Aetna",
    "billing_amount": 14238.317813937623,
    "room_number": 458,
    "admission_type": "Urgent",
    "discharge_date": "2022-09-18",
    "medication": "Penicillin",
    "test_results": "Abnormal"
  },
  {
    "name": "DIAnE brAnch",
    "age": 44,
    "gender": "Male",
    "blood_type": "O+",
    "medical_condition": "Obesity",
    "date_of_admission": "2020-05-30",
    "doctor": "Juan Acevedo",
    "hospital": "Perez and Sons",
    "insurance_provider": "Cigna",
    "billing_amount": 22841.363876905678,
    "room_number": 410,
    "admission_type": "Emergency",
    "discharge_date": "2020-05-29",
    "medication": "Aspirin",
    "test_results": "Inconclusive"
  },
  {
    "name": "TrACy BUrke",
    "age": 76,
    "gender": "Male",
    "blood_type": "A+",
    "medical_condition": "Obesity",
    "date_of_admission": "2020-12-05",
    "doctor": "Emily Thomas",
    "hospital": "Wilkins Group",
    "insurance_provider": "Medicare",
    "billing_amount": 5714.748017914666,
    "room_number": 238,
    "admission_type": "Elective",
    "discharge_date": "2020-12-04",
    "medication": "Lipitor",
    "test_results": "Abnormal"
  }
]
```

### 2. [MEDIUM/FAIL] malformed_hospital_name (healthcare_dataset)
- Why this matters: The data profile shows hospital names with leading or trailing text fragments like 'and ' or a trailing comma, suggesting parsing or data extraction errors. These malformed names can hinder analysis, reporting, and linking with other datasets.
- Issue count: **10465**
- Output truncated: **yes**

```sql
SELECT
  *
FROM healthcare_dataset
WHERE
  LOWER(hospital) LIKE 'and %'
  OR hospital LIKE '%,'
  OR hospital LIKE '%, and';
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
**Overall Verdict: Red**

This data quality run on the `healthcare_dataset` has failed due to critical and high-severity issues that compromise the reliability of key healthcare metrics.

**Top Critical/High Issues:**

1.  **Critical (`high`): `discharge_before_admission`**
    -   **Finding:** 555 records have a discharge date that is earlier than the admission date.
    -   **Impact:** This is a critical logical error that makes it impossible to calculate the length of stay for affected patients, a fundamental metric in healthcare analysis.

2.  **High (`medium`): `malformed_hospital_name`**
    -   **Finding:** 10,465 records have hospital names with parsing errors, such as leading "and" or trailing commas.
    -   **Impact:** These formatting issues will lead to incorrect aggregations and difficulty in joining this dataset with other hospital-related data.

**Test Coverage Notes:**

The executed tests focused on critical logical validation and string formatting issues identified during the initial data profiling. However, several other risks were noted in the profile that are not yet covered by tests:
-   Inconsistent `gender` values (e.g., "F" vs. "Female").
-   Inconsistent casing in patient `name` and `doctor` columns.
-   Categorical values in `admission_type`, `test_results`, and `blood_type` are not yet validated against a list of accepted values.

**Suggested Production Guardrails:**

To prevent these issues from recurring in the production environment, the following SQL checks should be scheduled to run after each data load. Any records returned by these queries should be flagged for immediate review.

1.  **Monitor for Invalid Admission/Discharge Dates:**
    ```sql
    SELECT * FROM healthcare_dataset WHERE julianday(discharge_date) < julianday(date_of_admission);
    ```

2.  **Monitor for Malformed Hospital Names:**
    ```sql
    SELECT * FROM healthcare_dataset WHERE LOWER(hospital) LIKE 'and %' OR hospital LIKE '%,';
    ```
