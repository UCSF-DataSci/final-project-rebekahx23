# Data Quality Report - dq-manual-simple-p05-pro-20260320T064340Z

Generated at: 2026-03-20 06:45:02 UTC

## Executive Summary
- Overall verdict: **YELLOW**
- Total tests executed: **2**
- Passed: **1**
- Failed: **1**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P05-PRO`
- Event log: `runs/dq-manual-simple-p05-pro-20260320T064340Z.jsonl`

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
| MEDIUM | FAIL | healthcare_dataset | hospital_name_formatting_issues | 20113 |

## Detailed Findings
### 1. [MEDIUM/FAIL] hospital_name_formatting_issues (healthcare_dataset)
- Why this matters: The profiler identified that the `hospital` column contains values with leading conjunctions (e.g., "and ") and extra punctuation (e.g., trailing commas). This indicates a formatting issue that could affect data presentation and grouping. This test identifies hospital names that start with "and " or contain commas, which are likely signs of data entry or parsing errors.
- Issue count: **20113**
- Output truncated: **yes**

```sql
SELECT
  *
FROM
  healthcare_dataset
WHERE
  LOWER(hospital) LIKE 'and %' OR hospital LIKE '%,%'
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
    "name": "connOR HANsEn",
    "age": 75,
    "gender": "Female",
    "blood_type": "A+",
    "medical_condition": "Diabetes",
    "date_of_admission": "2019-12-12",
    "doctor": "Kenneth Fletcher",
    "hospital": "Powers Miller, and Flores",
    "insurance_provider": "Cigna",
    "billing_amount": 43282.28335770435,
    "room_number": 134,
    "admission_type": "Emergency",
    "discharge_date": "2019-12-28",
    "medication": "Penicillin",
    "test_results": "Abnormal"
  }
]
```

## Supervisor Narrative
- **Overall Verdict:** Yellow
- **Top Issues:** No critical or high-severity issues were found. The most significant finding is a medium-severity issue related to data formatting.
- **Test Coverage:** The run focused on critical data type and formatting issues. The check for valid date formats passed, confirming that all admission and discharge dates are correctly formatted despite being stored as TEXT. However, a significant number of formatting problems were found in the `hospital` column. Coverage could be expanded to include checks for inconsistent capitalization in patient and doctor names, as noted during the initial data profiling.

---

**Highest-Risk Finding:**

- **Test:** `hospital_name_formatting_issues`
- **Severity:** Medium
- **Issues Found:** 20,113
- **Details:** A substantial number of hospital names have formatting errors, such as leading conjunctions (e.g., "and Vang,"), and extraneous commas. These issues can impact reporting, analytics, and record linkage.

---

**Suggested Production Guardrails:**

To maintain data quality in production, the following SQL checks should be scheduled to run after each data load:

1.  **Monitor Hospital Name Formatting:**
    *   **Rationale:** Catches the formatting issues discovered in this run.
    *   **SQL:**
        ```sql
        SELECT hospital FROM healthcare_dataset WHERE LOWER(hospital) LIKE 'and %' OR hospital LIKE '%,%';
        ```

2.  **Ensure Valid Date Formatting:**
    *   **Rationale:** Although no invalid dates were found, storing dates as TEXT is fragile. This guardrail ensures that new data continues to adhere to a valid date format, preventing future processing errors.
    *   **SQL:**
        ```sql
        SELECT date_of_admission, discharge_date FROM healthcare_dataset WHERE date(date_of_admission) IS NULL OR date(discharge_date) IS NULL;
        ```

3.  **Check for Inconsistent Name Capitalization:**
    *   **Rationale:** The profiler identified inconsistent capitalization in the `name` column. This can affect patient matching and user experience. This guardrail detects names that are not in title case.
    *   **SQL:**
        ```sql
        SELECT name FROM healthcare_dataset WHERE name != INITCAP(name);
        ```
