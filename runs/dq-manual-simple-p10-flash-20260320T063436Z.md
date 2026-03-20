# Data Quality Report - dq-manual-simple-p10-flash-20260320T063436Z

Generated at: 2026-03-20 06:35:11 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P10-FLASH`
- Event log: `runs/dq-manual-simple-p10-flash-20260320T063436Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | age_outlier_check | 1130 |
| HIGH | FAIL | healthcare_dataset | discharge_before_admission_date | 1131 |

## Detailed Findings
### 1. [CRITICAL/FAIL] age_outlier_check (healthcare_dataset)
- Why this matters: An 'age' value of 35000 is physically impossible for a human and represents a severe data entry error. This outlier will skew statistical analysis and any age-based segmentation, making the data unreliable for demographics or health risk assessments.
- Issue count: **1130**
- Output truncated: **yes**

```sql
SELECT name, age, date_of_admission
FROM healthcare_dataset
WHERE age > 150;
```

Example rows:
```json
[
  {
    "name": "connOR HANsEn",
    "age": 47500,
    "date_of_admission": "2019-12-12"
  },
  {
    "name": "Kim ScOtt",
    "age": 41500,
    "date_of_admission": "2024-04-07"
  },
  {
    "name": "TInA GriFfin",
    "age": 34500,
    "date_of_admission": "2022-06-17"
  }
]
```

### 2. [HIGH/FAIL] discharge_before_admission_date (healthcare_dataset)
- Why this matters: A patient's discharge date cannot logically occur before their admission date. This indicates a critical error in data recording, which can lead to incorrect calculations of hospital stay duration, inaccurate billing, and flawed patient journey analysis.
- Issue count: **1131**
- Output truncated: **yes**

```sql
SELECT name, date_of_admission, discharge_date
FROM healthcare_dataset
WHERE julianday(discharge_date) < julianday(date_of_admission);
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

## Supervisor Narrative
**Data Quality Report: SIMPLE-P10-FLASH**

**Overall Verdict: Red**

This run indicates significant data quality issues that require immediate attention. Both critical and high-severity tests failed, impacting key data fields.

**Top Critical/High Issues:**

*   **Critical (1 test):** `age_outlier_check` detected 1130 rows where the age is greater than 150, indicating impossible age values. This is a severe data entry error that will heavily skew any age-related analysis.
*   **High (1 test):** `discharge_before_admission_date` found 1131 instances where the discharge date is earlier than the admission date, pointing to logical errors in date recording. This will lead to incorrect calculations of hospital stay duration and flawed patient journey analysis.

**Test Coverage Notes:**

A total of two data quality tests were executed for the `healthcare_dataset` table, both of which failed, highlighting fundamental data integrity problems.

**Suggested Production Guardrails (SQL checks to schedule each load):**

To prevent these issues from recurring, the following SQL checks should be implemented as guardrails during each data load or update process:

1.  **Age Validity Check:**
    ```sql
    ALTER TABLE healthcare_dataset ADD CONSTRAINT chk_age_valid CHECK (age <= 150);
    ```
    This constraint will ensure that no `age` values exceeding 150 are inserted or updated into the `healthcare_dataset` table.

2.  **Discharge Date Not Before Admission Date:**
    ```sql
    ALTER TABLE healthcare_dataset ADD CONSTRAINT chk_discharge_admission_date CHECK (julianday(discharge_date) >= julianday(date_of_admission));
    ```
    This constraint will enforce that the `discharge_date` is always on or after the `date_of_admission`, preventing logical errors in date recording.
