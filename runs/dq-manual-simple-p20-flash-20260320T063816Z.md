# Data Quality Report - dq-manual-simple-p20-flash-20260320T063816Z

Generated at: 2026-03-20 06:38:57 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P20-FLASH`
- Event log: `runs/dq-manual-simple-p20-flash-20260320T063816Z.jsonl`

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
| HIGH | FAIL | healthcare_dataset | discharge_before_admission_date | 1140 |
| HIGH | FAIL | healthcare_dataset | future_date_of_admission | 1140 |

## Detailed Findings
### 1. [HIGH/FAIL] discharge_before_admission_date (healthcare_dataset)
- Why this matters: The 'discharge_date' is recorded as being before the 'date_of_admission'. This is a severe logical inconsistency, as a patient cannot be discharged before they are admitted. Such records indicate fundamental data integrity issues that could lead to incorrect medical timelines and operational reporting.
- Issue count: **1140**
- Output truncated: **yes**

```sql
SELECT name, date_of_admission, discharge_date FROM healthcare_dataset WHERE date_of_admission IS NOT NULL AND discharge_date IS NOT NULL AND julianday(discharge_date) < julianday(date_of_admission)
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
    "name": "JOhN eLlis",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2023-06-30"
  },
  {
    "name": "JOsepH SmIth",
    "date_of_admission": "2099-12-31",
    "discharge_date": "2023-05-14"
  }
]
```

### 2. [HIGH/FAIL] future_date_of_admission (healthcare_dataset)
- Why this matters: The 'date_of_admission' column contains dates that are in the future. An admission date should always be in the past or present, indicating a critical data entry error that impacts the accuracy of patient records and operational analysis.
- Issue count: **1140**
- Output truncated: **yes**

```sql
SELECT name, age, date_of_admission FROM healthcare_dataset WHERE date_of_admission IS NOT NULL AND date(date_of_admission) > date('now')
```

Example rows:
```json
[
  {
    "name": "jOhN hARTmAN",
    "age": 27,
    "date_of_admission": "2099-12-31"
  },
  {
    "name": "JOhN eLlis",
    "age": 83,
    "date_of_admission": "2099-12-31"
  },
  {
    "name": "JOsepH SmIth",
    "age": 22,
    "date_of_admission": "2099-12-31"
  }
]
```

## Supervisor Narrative
**Data Quality Report: SIMPLE-P20-FLASH**

**Overall Verdict:** 🔴 Red

**Top Critical/High Issues:**
*   **`future_date_of_admission`**: 1140 records failed this test. The 'date_of_admission' column contains dates in the future, which indicates critical data entry errors. These errors impact the accuracy of patient records and operational analysis.
*   **`discharge_before_admission_date`**: 1140 records failed this test. The 'discharge_date' is recorded as being before the 'date_of_admission'. This is a severe logical inconsistency, as a patient cannot be discharged before they are admitted. Such records indicate fundamental data integrity issues that could lead to incorrect medical timelines and operational reporting.

**Test Coverage Notes:**
All 2 planned data quality tests were executed for the `healthcare_dataset` table, covering critical date integrity checks.

**Suggested Production Guardrails (SQL checks to schedule each load):**

To prevent the recurrence of these high-severity issues, the following SQL checks should be implemented and run as part of your data loading or processing pipeline:

1.  **For `future_date_of_admission`**:
    ```sql
    SELECT name, age, date_of_admission FROM healthcare_dataset WHERE date_of_admission IS NOT NULL AND date(date_of_admission) > date('now')
    ```
    *   **Action**: Records failing this check should be quarantined and investigated immediately. Data entry processes should be reviewed to prevent future date admissions.

2.  **For `discharge_before_admission_date`**:
    ```sql
    SELECT name, date_of_admission, discharge_date FROM healthcare_dataset WHERE date_of_admission IS NOT NULL AND discharge_date IS NOT NULL AND julianday(discharge_date) < julianday(date_of_admission)
    ```
    *   **Action**: Records where the discharge date precedes the admission date are logically impossible and must be corrected. This indicates a severe data entry or system logic flaw that needs urgent attention.
