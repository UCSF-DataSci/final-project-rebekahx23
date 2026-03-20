# Data Quality Report - dq-manual-complex-p10-pro-20260320T051217Z

Generated at: 2026-03-20 05:13:50 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark complex issues: COMPLEX-P10-PRO`
- Event log: `runs/dq-manual-complex-p10-pro-20260320T051217Z.jsonl`

## Coverage Breakdown
| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 2 |
| Medium | 0 |
| Low | 0 |

## Top Findings
| Severity | Status | Table | Test | Issue Count |
|---|---|---|---|---:|
| HIGH | FAIL | healthcare_dataset | inconsistent_name_capitalization | 54994 |
| HIGH | FAIL | healthcare_dataset | discharge_before_admission | 555 |

## Detailed Findings
### 1. [HIGH/FAIL] inconsistent_name_capitalization (healthcare_dataset)
- Why this matters: The 'name' and 'doctor' columns show inconsistent capitalization (e.g., 'JEnNIFER bROWn'), which complicates patient and physician identification and can lead to duplicate or fragmented records. This test flags names that are not in a standard proper/title case format by checking for values that are not entirely lowercase, not entirely uppercase, and yet have lowercase letters mixed with uppercase letters in a non-standard way.
- Issue count: **54994**
- Output truncated: **yes**

```sql
SELECT *
FROM healthcare_dataset
WHERE name IS NOT NULL
  AND name <> UPPER(name)
  AND name <> LOWER(name)
  AND (name GLOB '*[A-Z][a-z]*[A-Z]*' OR name GLOB '*[a-z][A-Z]*');
```

Example rows:
```json
[
  {
    "name": "Bobby JacksOn",
    "age": 30,
    "gender": "Male",
    "blood_type": "B-",
    "medical_condition": "Cancer",
    "date_of_admission": "2024-01-31",
    "doctor": "Matthew Smith",
    "hospital": "Sons and Miller",
    "insurance_provider": "Blue Cross",
    "billing_amount": 18856.281305978155,
    "room_number": 328,
    "admission_type": "Urgent",
    "discharge_date": "2024-02-02",
    "medication": "Paracetamol",
    "test_results": "Normal"
  },
  {
    "name": "LesLie TErRy",
    "age": 62,
    "gender": "Male",
    "blood_type": "A+",
    "medical_condition": "Obesity",
    "date_of_admission": "2019-08-20",
    "doctor": "Samantha Davies",
    "hospital": "Kim Inc",
    "insurance_provider": "Medicare",
    "billing_amount": 33643.327286577885,
    "room_number": 265,
    "admission_type": "Emergency",
    "discharge_date": "2019-08-26",
    "medication": "Ibuprofen",
    "test_results": "Inconclusive"
  },
  {
    "name": "DaNnY sMitH",
    "age": 76,
    "gender": "Female",
    "blood_type": "A-",
    "medical_condition": "Obesity",
    "date_of_admission": "2022-09-22",
    "doctor": "Tiffany Mitchell",
    "hospital": "Cook PLC",
    "insurance_provider": "Aetna",
    "billing_amount": 27955.096078842456,
    "room_number": 205,
    "admission_type": "Emergency",
    "discharge_date": "2022-10-07",
    "medication": "Aspirin",
    "test_results": "Normal"
  }
]
```

### 2. [HIGH/FAIL] discharge_before_admission (healthcare_dataset)
- Why this matters: The discharge date cannot be earlier than the admission date. This is a logical impossibility that breaks duration-based calculations like length of stay and indicates a critical data entry error. The date columns are stored as text, requiring conversion for proper comparison.
- Issue count: **555**
- Output truncated: **yes**

```sql
SELECT *
FROM healthcare_dataset
WHERE date_of_admission IS NOT NULL
  AND discharge_date IS NOT NULL
  AND julianday(discharge_date) < julianday(date_of_admission);
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

## Supervisor Narrative
**Overall Verdict: Red**

This data quality run has failed with a verdict of "Red" due to two critical, high-severity issues that significantly impact the reliability of the `healthcare_dataset`. Both tests failed, indicating systemic problems with data integrity and formatting.

**Top Critical/High Issues:**

1.  **`discharge_before_admission` (High Severity):** A critical logical error was found in **555** records where the patient's discharge date occurs before their admission date. This invalidates any analysis dependent on the length of stay and points to fundamental issues in data entry or processing.
2.  **`inconsistent_name_capitalization` (High Severity):** A massive **54,994** records were found with improperly cased patient names. This inconsistency poses a major threat to patient data integrity, making it difficult to accurately track individuals and consolidate their records, which could lead to fragmented patient histories.

**Test Coverage Notes:**

The tests focused on foundational data quality aspects: logical integrity (date sequencing) and string formatting for critical identifiers (patient names). The high failure rates on these basic checks suggest that more subtle issues may exist in other areas of the dataset.

**Suggested Production Guardrails:**

To prevent these issues from recurring, the following SQL checks should be implemented as production guardrails and run on every data load:

1.  **Prevent Invalid Stay Dates:**
    ```sql
    -- This check will fail if any records have a discharge date before the admission date.
    SELECT COUNT(*)
    FROM healthcare_dataset
    WHERE julianday(discharge_date) < julianday(date_of_admission);
    ```

2.  **Enforce Name Standardization:**
    ```sql
    -- This check identifies names that are not in a standard proper case format.
    -- Consider standardizing the 'name' column to proper case upon ingestion.
    SELECT COUNT(*)
    FROM healthcare_dataset
    WHERE name IS NOT NULL
      AND name <> UPPER(name)
      AND name <> LOWER(name)
      AND (name GLOB '*[A-Z][a-z]*[A-Z]*' OR name GLOB '*[a-z][A-Z]*');
    ```
This run signals a need for immediate data cleaning and the implementation of robust, automated checks to ensure the future reliability of this dataset.
