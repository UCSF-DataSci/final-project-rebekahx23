# Data Quality Report - dq-manual-complex-p50-pro-20260320T054633Z

Generated at: 2026-03-20 05:47:56 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P50-PRO`
- Event log: `runs/dq-manual-complex-p50-pro-20260320T054633Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | discharge_before_admission | 555 |
| HIGH | FAIL | healthcare_dataset | inconsistent_gender_values | 555 |

## Detailed Findings
### 1. [CRITICAL/FAIL] discharge_before_admission (healthcare_dataset)
- Why this matters: The discharge date cannot be before the admission date. This is a critical data integrity issue that makes calculating the length of stay impossible and invalidates the record for any time-based analysis. The profile explicitly identified this in the 'High-Risk Areas'.
- Issue count: **555**
- Output truncated: **yes**

```sql
SELECT
  *
FROM
  healthcare_dataset
WHERE
  julianday(discharge_date) < julianday(date_of_admission);
```

Example rows:
```json
[
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
    "discharge_date": "2021-12-27",
    "medication": "Paracetamol",
    "test_results": "Inconclusive"
  },
  {
    "name": "JOsEph fOstER",
    "age": 59,
    "gender": "Female",
    "blood_type": "O+",
    "medical_condition": "Obesity",
    "date_of_admission": "2019-09-11",
    "doctor": "Daniel Smith",
    "hospital": "Alvarado-Deleon",
    "insurance_provider": "Blue Cross",
    "billing_amount": 27385.736227988127,
    "room_number": 427,
    "admission_type": "Emergency",
    "discharge_date": "2019-09-10",
    "medication": "Penicillin",
    "test_results": "Inconclusive"
  },
  {
    "name": "mIcHael anDeRson",
    "age": 64,
    "gender": "Female",
    "blood_type": "AB-",
    "medical_condition": "Arthritis",
    "date_of_admission": "2019-08-16",
    "doctor": "Charles Webb",
    "hospital": "Bass Inc",
    "insurance_provider": "Medicare",
    "billing_amount": 5549.785435792208,
    "room_number": 302,
    "admission_type": "Emergency",
    "discharge_date": "2019-08-15",
    "medication": "Ibuprofen",
    "test_results": "Inconclusive"
  }
]
```

### 2. [HIGH/FAIL] inconsistent_gender_values (healthcare_dataset)
- Why this matters: The 'gender' column contains inconsistent values such as 'Male', 'Female', and 'F'. For accurate demographic analysis and reporting, this field must be standardized. This test identifies any values that are not one of the expected formats ('Male', 'Female').
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
    "name": "TOdd coopeR",
    "age": 55,
    "gender": "F",
    "blood_type": "A+",
    "medical_condition": "Diabetes",
    "date_of_admission": "2022-12-10",
    "doctor": "Jason Price",
    "hospital": "Henderson-Taylor",
    "insurance_provider": "UnitedHealthcare",
    "billing_amount": 21772.341398649638,
    "room_number": 459,
    "admission_type": "Elective",
    "discharge_date": "2022-12-31",
    "medication": "Ibuprofen",
    "test_results": "Normal"
  },
  {
    "name": "PhILLIP lyOnS",
    "age": 53,
    "gender": "M",
    "blood_type": "B-",
    "medical_condition": "Cancer",
    "date_of_admission": "2022-09-14",
    "doctor": "Stephanie Clements",
    "hospital": "Parsons, Hartman Martinez and",
    "insurance_provider": "Blue Cross",
    "billing_amount": 30437.001787641067,
    "room_number": 208,
    "admission_type": "Elective",
    "discharge_date": "2022-09-18",
    "medication": "Aspirin",
    "test_results": "Normal"
  },
  {
    "name": "KaTiE hENry",
    "age": 70,
    "gender": "M",
    "blood_type": "B+",
    "medical_condition": "Diabetes",
    "date_of_admission": "2022-07-08",
    "doctor": "Roberto Petersen",
    "hospital": "Reed LLC",
    "insurance_provider": "Aetna",
    "billing_amount": 7187.272346099509,
    "room_number": 402,
    "admission_type": "Emergency",
    "discharge_date": "2022-07-25",
    "medication": "Aspirin",
    "test_results": "Normal"
  }
]
```

## Supervisor Narrative
### **Overall Verdict: RED**

This data quality run has failed with a **RED** verdict due to critical data integrity violations that fundamentally impact the reliability of the `healthcare_dataset` table.

### Top Critical & High Issues

*   **CRITICAL**: `discharge_before_admission` - 555 records were found where the `discharge_date` is earlier than the `date_of_admission`. This is a logical impossibility and corrupts any analysis dependent on time, such as calculating patient length of stay.
*   **HIGH**: `inconsistent_gender_values` - 555 records contain non-standard gender values like 'M' or 'F' instead of 'Male' or 'Female'. This prevents accurate and reliable demographic analysis.

### Test Coverage Notes

This run focused on the most severe issues identified during the initial data profiling. The two tests executed, `discharge_before_admission` and `inconsistent_gender_values`, successfully confirmed and quantified these high-risk problems.

Other potential issues noted during profiling, such as inconsistent formatting in `name`, `doctor`, and `hospital` fields, were not covered in this run. While less critical, addressing these would significantly improve the ability to perform accurate entity resolution and aggregation.

### Suggested Production Guardrails

To prevent these issues from recurring in production, the following SQL checks should be implemented as blocking guardrails in your data loading pipeline. The pipeline should fail and alert the data owners if either of these queries returns a count greater than 0.

1.  **Check for Invalid Admission/Discharge Dates:**
    ```sql
    SELECT count(*)
    FROM healthcare_dataset
    WHERE julianday(discharge_date) < julianday(date_of_admission);
    ```

2.  **Check for Non-Standard Gender Values:**
    ```sql
    SELECT count(*)
    FROM healthcare_dataset
    WHERE gender NOT IN ('Male', 'Female');
    ```
