# Data Quality Report - dq-manual-simple-p10-flash-20260320T063721Z

Generated at: 2026-03-20 06:38:04 UTC

## Executive Summary
- Overall verdict: **RED**
- Total tests executed: **2**
- Passed: **0**
- Failed: **2**
- Errors: **0**

## Run Metadata
- Database: `sqlite:///./runs/db/healthcare_work.sqlite`
- Prompt: `Manual benchmark simple issues: SIMPLE-P10-FLASH`
- Event log: `runs/dq-manual-simple-p10-flash-20260320T063721Z.jsonl`

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
| CRITICAL | FAIL | healthcare_dataset | age_unrealistic_values | 1133 |
| HIGH | FAIL | healthcare_dataset | discharge_date_before_admission | 1140 |

## Detailed Findings
### 1. [CRITICAL/FAIL] age_unrealistic_values (healthcare_dataset)
- Why this matters: The 'age' column contains values far exceeding a realistic human lifespan (e.g., 32000, 26500, 41000 years). These are clear data entry errors that will severely distort any age-related analysis and demographic insights.
- Issue count: **1133**
- Output truncated: **yes**

```sql
SELECT name, age, date_of_admission FROM healthcare_dataset WHERE age IS NOT NULL AND age > 150;
```

Example rows:
```json
[
  {
    "name": "CHrisTInA MARtinez",
    "age": 20000,
    "date_of_admission": "2021-12-28"
  },
  {
    "name": "sUZaNnE SchNeIder",
    "age": 36000,
    "date_of_admission": "2023-08-25"
  },
  {
    "name": "reBEcCA PARsONs",
    "age": 28500,
    "date_of_admission": "2019-12-02"
  }
]
```

### 2. [HIGH/FAIL] discharge_date_before_admission (healthcare_dataset)
- Why this matters: The 'discharge_date' should logically never precede the 'date_of_admission'. Records where this occurs indicate a critical logical inconsistency, affecting calculations of patient stay duration and overall data integrity related to admission/discharge workflows. This test also implicitly validates that the date strings are in a format parseable by SQLite's date functions.
- Issue count: **1140**
- Output truncated: **yes**

```sql
SELECT name, date_of_admission, discharge_date FROM healthcare_dataset WHERE date_of_admission IS NOT NULL AND discharge_date IS NOT NULL AND date(discharge_date) < date(date_of_admission);
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

## Supervisor Narrative
**Data Quality Report: `healthcare_dataset`**

**Overall Verdict: 🔴 RED**
The data quality run for `healthcare_dataset` has revealed critical and high-severity issues, leading to a RED verdict. Both planned data quality tests failed, indicating significant inconsistencies that require immediate attention.

**Top Critical/High Issues:**

*   **Critical Severity - Unrealistic Age Values (`age_unrealistic_values`):**
    *   **Description:** 1133 records were found where the `age` column contained values greater than 150 years. This indicates substantial data entry or processing errors, as human age rarely exceeds this threshold.
    *   **Impact:** These unrealistic age values will severely skew any demographic analysis, patient stratification, or age-dependent research, leading to inaccurate insights and potentially flawed decision-making.

*   **High Severity - Discharge Date Before Admission Date (`discharge_date_before_admission`):**
    *   **Description:** 1140 records showed a `discharge_date` that chronologically precedes the `date_of_admission`. This is a fundamental logical inconsistency in patient record-keeping.
    *   **Impact:** Such errors invalidate calculations of patient length of stay, disrupt chronological event tracking, and undermine the reliability of medical history and billing processes.

**Test Coverage Notes:**
Two data quality tests were planned and executed, specifically targeting the most critical findings identified during the profiling phase: unrealistic age values and logical inconsistencies in admission/discharge dates. Both tests were successfully run, providing clear insights into the extent of these high-risk data quality problems.

**Suggested Production Guardrails (SQL checks to schedule each load):**
To prevent these issues from recurring and to ensure data integrity for the `healthcare_dataset`, the following SQL checks should be implemented and scheduled to run upon each data load:

1.  **Age Realism Check:**
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE age IS NOT NULL AND age > 150;
    ```
    *   **Expected Outcome:** This query should consistently return `0`. Any non-zero result indicates records with unrealistic age values needing correction.

2.  **Discharge Date Logic Check:**
    ```sql
    SELECT COUNT(*) FROM healthcare_dataset WHERE date_of_admission IS NOT NULL AND discharge_date IS NOT NULL AND date(discharge_date) < date(date_of_admission);
    ```
    *   **Expected Outcome:** This query should consistently return `0`. Any non-zero result signifies records where the discharge date precedes the admission date, which is a logical error.
