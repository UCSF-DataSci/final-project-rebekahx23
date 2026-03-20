# Data Quality Report - dq-manual-simple-p05-flash-20260320T045722Z

Generated at: 2026-03-20 04:58:08 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **1**
- Failed: **1**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P05-FLASH`
- Event log: `runs/dq-manual-simple-p05-flash-20260320T045722Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | discharge_before_admission | 1133 |

## Detailed Findings
### 1. [CRITICAL/FAIL] discharge_before_admission (healthcare_dataset)
- Why this matters: The `discharge_date` must logically occur on or after the `date_of_admission`. If the discharge date precedes the admission date, it indicates a severe logical error in the patient's record, impacting billing, length of stay calculations, and patient timeline. This test also implicitly validates that the date strings are parseable by `julianday()`.
- Issue count: **1133**
- Output truncated: **yes**

```sql
SELECT name, date_of_admission, discharge_date FROM healthcare_dataset WHERE julianday(discharge_date) < julianday(date_of_admission);
```

Example rows:
```json
[
  {
    "name": "Jeffrey tuRNER",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2020-06-01"
  },
  {
    "name": "jEssiCa GoNzAleS",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2023-09-16"
  },
  {
    "name": "dr. MATthEW wilkinS",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2021-07-24"
  }
]
```

## Supervisor Narrative
**Overall Verdict: Red**

**Top Critical/High Issues:**

*   **Critical Failure: `discharge_before_admission` (1133 issues)**
    *   **Description:** The most significant issue identified is 1133 records where the `discharge_date` precedes the `date_of_admission`. This indicates severe logical inconsistencies in the patient records, severely impacting data reliability for critical operations like billing, length-of-stay calculations, and patient timeline analysis. The sample data `date_of_admission: '2099-12-31', discharge_date: '2020-06-01'` suggests a systemic problem, possibly due to placeholder or incorrect future admission dates.

**Test Coverage Notes:**

Out of 2 planned tests, 1 critical test failed and 1 high test passed. The executed tests provided coverage for critical logical date consistency and important categorical value consistency for gender, successfully highlighting a major data integrity problem.

**Suggested Production Guardrails:**

To prevent these critical issues from reoccurring and ensure data quality in future loads, implement the following SQL checks as mandatory guardrails:

*   **For `discharge_before_admission` (Critical):**
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE julianday(discharge_date) < julianday(date_of_admission);
    ```
    *   **Action:** This check must pass with 0 issues. Any records failing this validation indicate fundamental logical errors and should either prevent the data load or be routed to a dedicated quarantine zone for immediate investigation and manual correction. Prioritize identifying the root cause of the `2099-12-31` admission date.

*   **For `inconsistent_gender_values` (High):**
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE LOWER(gender) NOT IN ('male', 'female') OR gender IS NULL;
    ```
    *   **Action:** While this test passed in this run, it's a valuable check to maintain the integrity of categorical data. Schedule this check to ensure all `gender` values conform to 'Male' or 'Female' (case-insensitive) and are not null. Records failing this check should be flagged for correction or standardization.
