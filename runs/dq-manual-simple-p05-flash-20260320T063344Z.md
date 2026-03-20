# Data Quality Report - dq-manual-simple-p05-flash-20260320T063344Z

Generated at: 2026-03-20 06:34:24 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P05-FLASH`
- Event log: `runs/dq-manual-simple-p05-flash-20260320T063344Z.jsonl`

## Coverage Breakdown
| Severity | Count |
|---|---:|
| Critical | 2 |
| High | 0 |
| Medium | 0 |
| Low | 0 |

## Top Findings
| Severity | Status | Table | Test | Issue Count |
|---|---|---|---|---:|
| CRITICAL | FAIL | healthcare_dataset | discharge_before_admission_date | 1131 |
| CRITICAL | FAIL | healthcare_dataset | age_unrealistic_value | 1130 |

## Detailed Findings
### 1. [CRITICAL/FAIL] discharge_before_admission_date (healthcare_dataset)
- Why this matters: The `discharge_date` should logically always be on or after the `date_of_admission`. Rows where the `discharge_date` is earlier than the `date_of_admission` indicate a critical data inconsistency, impacting the accuracy of patient stay duration and historical records. Dates need to be converted to a comparable format (e.g., Julian day) for accurate comparison.
- Issue count: **1131**
- Output truncated: **yes**

```sql
SELECT name, date_of_admission, discharge_date FROM healthcare_dataset WHERE date_of_admission IS NOT NULL AND discharge_date IS NOT NULL AND julianday(discharge_date) < julianday(date_of_admission);
```

Example rows:
```json
[
  {
    "name": "jOhN hARTmAN",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2023-01-27"
  },
  {
    "name": "wILLIAM hIlL",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2023-06-01"
  },
  {
    "name": "DR. LaUreN ClaRk DDs",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2020-11-17"
  }
]
```

### 2. [CRITICAL/FAIL] age_unrealistic_value (healthcare_dataset)
- Why this matters: The `age` column contains an unrealistic outlier value (e.g., 31500) which indicates severe data entry errors or corrupted data. Human age is typically between 0 and 150 years. Values outside this range are highly suspect.
- Issue count: **1130**
- Output truncated: **yes**

```sql
SELECT name, age FROM healthcare_dataset WHERE age < 0 OR age > 150;
```

Example rows:
```json
[
  {
    "name": "connOR HANsEn",
    "age": 47500
  },
  {
    "name": "Kim ScOtt",
    "age": 41500
  },
  {
    "name": "TInA GriFfin",
    "age": 34500
  }
]
```

## Supervisor Narrative
**Overall Verdict: Red**

**Top Critical Issues:**

*   **age_unrealistic_value**: Found 1130 rows where `age` is unrealistic (outside 0-150 range). This is a critical data entry error or indicates corrupted data.
*   **discharge_before_admission_date**: Found 1131 rows where `discharge_date` is earlier than `date_of_admission`. This is a critical logical inconsistency, impacting the accuracy of patient stay duration and historical records.

**Test Coverage Notes:**

All 2 planned data quality tests completed successfully.

**Suggested Production Guardrails (SQL checks to schedule each load):**

*   **`age` realism check**:
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE age < 0 OR age > 150;
    ```
    (Alert if count > 0)
*   **`discharge_date` vs `date_of_admission` consistency check**:
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE date_of_admission IS NOT NULL AND discharge_date IS NOT NULL AND julianday(discharge_date) < julianday(date_of_admission);
    ```
    (Alert if count > 0)

These critical issues require immediate attention to ensure the reliability and integrity of the `healthcare_dataset`.
