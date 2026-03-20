# Data Quality Report - dq-manual-complex-p05-pro-20260320T061657Z

Generated at: 2026-03-20 06:18:22 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P05-PRO`
- Event log: `runs/dq-manual-complex-p05-pro-20260320T061657Z.jsonl`

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
| HIGH | FAIL | healthcare_dataset | discharge_date_after_admission_check | 555 |
| MEDIUM | FAIL | healthcare_dataset | hospital_name_malformed_string_check | 14525 |

## Detailed Findings
### 1. [HIGH/FAIL] discharge_date_after_admission_check (healthcare_dataset)
- Why this matters: The discharge date must be greater than or equal to the date of admission. Violations of this rule indicate incorrect chronological temporal logic in the admission records.
- Issue count: **555**
- Output truncated: **yes**

```sql
SELECT *
FROM healthcare_dataset
WHERE date(discharge_date) < date(date_of_admission)
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

### 2. [MEDIUM/FAIL] hospital_name_malformed_string_check (healthcare_dataset)
- Why this matters: Hospital names should not begin or end with conjunctions like 'and' or contain trailing commas, which indicate parsing or concatenation errors during data ingestion.
- Issue count: **14525**
- Output truncated: **yes**

```sql
SELECT *
FROM healthcare_dataset
WHERE LOWER(hospital) LIKE LOWER('and %')
   OR LOWER(hospital) LIKE LOWER('% and')
   OR hospital LIKE '%,'
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
### Data Quality Supervisor Report

**Overall Verdict:** 🔴 RED
The dataset contains a significant number of high-severity logical issues alongside widespread formatting errors. It requires immediate remediation before being promoted to production.

**Top Critical/High Issues:**
1. **Chronological Temporal Logic Failures:** The `discharge_date_after_admission_check` test failed with 555 violations. We found records where the `discharge_date` is earlier than the `date_of_admission` (e.g., admitted `2023-05-17`, discharged `2023-05-16`), which breaks fundamental admission logic and downstream duration analysis.
2. **Malformed Hospital Names:** The `hospital_name_malformed_string_check` flagged 14,525 rows. Hospital names contain parsing or concatenation anomalies (e.g., trailing commas, starting/ending with conjunctions like "and"), requiring a robust string cleansing strategy.
3. **Inconsistent Patient Names:** Profiling uncovered severe capitalization anomalies (e.g., "mARia smITH") requiring Title Case standardizations.

**Test Coverage Notes:**
- We executed tests on chronological temporal logic (discharge date >= admission date) and basic string validations (hospital name malformations).
- Currently untested but recommended for future runs:
  - Validations enforcing standard capitalization for patient names.
  - Referential/domain checks for categorical columns (`medical_condition`, `test_results`, etc.).
  - Range checks for numerical fields like `age` and financial formatting validations for `billing_amount`.

**Suggested Production Guardrails (SQL Checks to Schedule):**
Implement the following checks in your ETL pipeline to block or quarantine bad data:

1. **Chronological Validity Check (Blocker)**
```sql
SELECT count(*) 
FROM healthcare_dataset 
WHERE date(discharge_date) < date(date_of_admission);
```
*(Should return 0 before continuing the load)*

2. **Hospital Name Cleansing Check (Warning/Quarantine)**
```sql
SELECT count(*) 
FROM healthcare_dataset 
WHERE LOWER(hospital) LIKE LOWER('and %') 
   OR LOWER(hospital) LIKE LOWER('% and') 
   OR hospital LIKE '%,';
```
*(Alert on anomalies to drive updates to the upstream parsing logic)*
