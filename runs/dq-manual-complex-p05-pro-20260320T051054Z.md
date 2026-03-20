# Data Quality Report - dq-manual-complex-p05-pro-20260320T051054Z

Generated at: 2026-03-20 05:12:05 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P05-PRO`
- Event log: `runs/dq-manual-complex-p05-pro-20260320T051054Z.jsonl`

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
| HIGH | FAIL | healthcare_dataset | inconsistent_hospital_name_formatting | 8923 |
| MEDIUM | FAIL | healthcare_dataset | invalid_gender_values | 555 |

## Detailed Findings
### 1. [HIGH/FAIL] inconsistent_hospital_name_formatting (healthcare_dataset)
- Why this matters: The 'hospital' column exhibits inconsistent naming conventions, with some names improperly starting with 'and' or ending with a comma. These formatting issues prevent accurate grouping and analysis by hospital, potentially leading to fragmented reporting. This test identifies records with these specific formatting errors.
- Issue count: **8923**
- Output truncated: **yes**

```sql
SELECT
  *
FROM
  healthcare_dataset
WHERE
  LOWER(hospital) LIKE 'and %'
  OR hospital LIKE '%,';
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

### 2. [MEDIUM/FAIL] invalid_gender_values (healthcare_dataset)
- Why this matters: The 'gender' column contains inconsistent values like 'F' in addition to 'Male' and 'Female'. For accurate demographic analysis and reporting, these values must be standardized. This test identifies all records where the gender is not one of the two expected values.
- Issue count: **555**
- Output truncated: **yes**

```sql
SELECT
  *
FROM
  healthcare_dataset
WHERE
  gender NOT IN ('Male', 'Female');
```

Example rows:
```json
[
  {
    "name": "beThaNY MoOrE",
    "age": 55,
    "gender": "F",
    "blood_type": "A+",
    "medical_condition": "Cancer",
    "date_of_admission": "2023-04-09",
    "doctor": "Penny Pruitt",
    "hospital": "and Montes Graves, Thomas",
    "insurance_provider": "Cigna",
    "billing_amount": 10300.657311375919,
    "room_number": 330,
    "admission_type": "Emergency",
    "discharge_date": "2023-04-21",
    "medication": "Paracetamol",
    "test_results": "Normal"
  },
  {
    "name": "cathERinE gArDnEr",
    "age": 79,
    "gender": "F",
    "blood_type": "A-",
    "medical_condition": "Hypertension",
    "date_of_admission": "2019-08-19",
    "doctor": "David Ruiz",
    "hospital": "James Ltd",
    "insurance_provider": "Medicare",
    "billing_amount": 25503.673806852043,
    "room_number": 144,
    "admission_type": "Elective",
    "discharge_date": "2019-08-26",
    "medication": "Lipitor",
    "test_results": "Abnormal"
  },
  {
    "name": "KAThErInE BARnEtt",
    "age": 25,
    "gender": "M",
    "blood_type": "AB-",
    "medical_condition": "Arthritis",
    "date_of_admission": "2022-03-15",
    "doctor": "Faith Cook",
    "hospital": "Mcdaniel and Sons",
    "insurance_provider": "Medicare",
    "billing_amount": 13854.645763663511,
    "room_number": 328,
    "admission_type": "Elective",
    "discharge_date": "2022-04-10",
    "medication": "Penicillin",
    "test_results": "Inconclusive"
  }
]
```

## Supervisor Narrative
**Overall Verdict: Red**

This data quality run on the `healthcare_dataset` table has failed, with 2 out of 2 tests identifying significant issues. The presence of a high-severity issue necessitates a "Red" verdict, indicating that the data is not reliable for production use without remediation.

**Top Critical/High Issues:**

1.  **`inconsistent_hospital_name_formatting` (High):** A critical issue was found in 8,923 records where hospital names were improperly formatted (e.g., starting with "and" or ending with a comma). This significantly impacts the ability to group and analyze data by facility, leading to inaccurate reporting.
2.  **`invalid_gender_values` (Medium):** A total of 555 records contain gender values other than 'Male' or 'Female'. This inconsistency will skew demographic analysis and reporting.

**Test Coverage Notes:**

The tests effectively targeted and confirmed two major areas of concern initially identified during data profiling: value consistency and formatting. The `inconsistent_hospital_name_formatting` test was crucial in quantifying the impact of the naming convention issue, while the `invalid_gender_values` test highlighted the need for data standardization.

**Suggested Production Guardrails:**

To prevent these issues in future data loads, the following SQL checks should be implemented as production guardrails:

1.  **Block records with invalid gender values:**
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE gender NOT IN ('Male', 'Female');
    ```
2.  **Block records with inconsistent hospital name formatting:**
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE LOWER(hospital) LIKE 'and %' OR hospital LIKE '%,';
    ```

These checks will ensure that new data adheres to the required quality standards before being loaded into the production environment.
